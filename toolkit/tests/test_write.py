import json
import subprocess

import pytest

from t0 import write as W
from t0.okf.document import Actor
from t0.profile.spec import EventKind
from test_check import build

NOW = "2026-10-28T10:00:00-03:00"


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("T0_NOW", NOW)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("T0_FORGE", raising=False)


def rec(body="feito", **kw):
    return W.new_record(EventKind.PROGRESS, type_name="Step", fields={"kind": "progress", **kw}, body=body,
                        actor=Actor("human:ana"), handle="ana", where={"repo": "kb", "bet_folder": "/products/p/bets/BET-001"})


def git(kb, *a):
    return subprocess.run(["git", "-C", str(kb), *a], capture_output=True, text=True, check=True).stdout


def test_record_is_uniquely_named_and_refuses_secrets():
    r = rec()
    assert r.doc.path.startswith("/products/p/bets/BET-001/steps/20261028T130000Z-ana-kb-") and r.doc.path.endswith(".md")
    assert rec().doc.path != r.doc.path
    with pytest.raises(W.SecretFound) as e:
        rec("senha: hunter2abc cpf 529.982.247-25")
    assert "cpf" in str(e.value) and "529" not in str(e.value)


def test_lane_types_cannot_be_built_by_hand():
    with pytest.raises(TypeError):
        W.AddRecord(W.RenderedDoc("/steps/x.md", ""), "x")
    with pytest.raises(TypeError):
        W.DerivedChange(())


def test_push_commits_spool_by_plumbing_and_is_idempotent(tmp_path):
    kb = build(tmp_path)
    W.apply(W.Plan(records=(rec(), rec("outro"))), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    applied, msgs = W.push_spool(kb_dir=kb, handle="ana", mode="batch", landed=frozenset())
    branch = "rec/ana/2026-10-28"
    files = git(kb, "ls-tree", "-r", "--name-only", branch).split()
    assert applied.branch == branch and sum("/steps/2026" in f for f in files) == 2
    assert git(kb, "status", "--porcelain") == "" and git(kb, "branch", "--show-current").strip() == "main"
    again, msgs = W.push_spool(kb_dir=kb, handle="ana", mode="batch", landed=frozenset())
    assert again.commit is None and "já tinha" in msgs[0]
    landed = frozenset("/" + f for f in files)
    W.push_spool(kb_dir=kb, handle="ana", mode="batch", landed=landed)
    assert not list(W.spool_dir(kb).rglob("*.md"))


def test_record_with_known_dedup_is_skipped(tmp_path):
    kb = build(tmp_path)
    r = rec()
    out = W.apply(W.Plan(records=(r,)), mode=W.ApplyMode.LOCAL, kb_dir=kb, known_dedup=frozenset({r.dedup}))
    assert out.spooled == () and out.skipped == (r.dedup,)


def test_knowledge_change_is_a_branch_from_main_with_one_commit(tmp_path):
    kb = build(tmp_path)
    k = W.KnowledgeChange("kb/ana/x", "Título", "corpo", (W.RenderedDoc("/glossary/novo.md", "---\ntype: X\n---\n"),))
    out = W.apply(W.Plan(knowledge=k), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    assert out.branch == "kb/ana/x" and out.commit and out.pr_url is None
    assert git(kb, "log", "--format=%s", "-1").strip() == "Título"
    same = W.apply(W.Plan(knowledge=k), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    assert same.commit is None


def test_switch_refuses_dirty_tree_off_main(tmp_path):
    kb = build(tmp_path)
    W.switch(kb, "kb/ana/a")
    (kb / "glossary/limite.md").write_text("mudou")
    with pytest.raises(W.ApplyError, match="suja"):
        W.switch(kb, "kb/ana/b")


def test_switch_from_origin_main_never_writes_git_config(tmp_path):
    kb = build(tmp_path)
    subprocess.run(["git", "clone", "-q", "--bare", str(kb), str(tmp_path / "origin.git")], check=True)
    git(kb, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(kb, "fetch", "-q", "origin")
    git(kb, "switch", "-q", "--detach")
    git(kb, "branch", "-qD", "main")
    config = (kb / ".git/config").read_bytes()
    W.switch(kb, "kb/ana/x")
    assert W.current_branch(kb) == "kb/ana/x"
    assert (kb / ".git/config").read_bytes() == config


def test_derived_change_only_on_main(tmp_path):
    kb = build(tmp_path)
    d = W.derived_change((W.RenderedDoc("/log.md", "---\ntype: Log\n---\n"),))
    with pytest.raises(W.ApplyError):
        W.apply(W.Plan(derived=d), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    W.switch(kb, "kb/ana/x")
    with pytest.raises(W.ApplyError, match="só no main"):
        W.apply(W.Plan(derived=d), mode=W.ApplyMode.KB_RENDER, kb_dir=kb)


def test_file_forge_opens_draft_pr_and_records_pr_with_auto_merge(tmp_path, monkeypatch):
    kb = build(tmp_path)
    monkeypatch.setenv("T0_FORGE", f"file:{tmp_path / 'forge'}")
    k = W.KnowledgeChange("kb/ana/x", "T", "b", (W.RenderedDoc("/glossary/n.md", "x"),), (Actor("human:bia"),))
    out = W.apply(W.Plan(knowledge=k), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    W.apply(W.Plan(knowledge=k), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    prs = json.loads((tmp_path / "forge/prs.json").read_text())
    assert out.pr_url and len(prs) == 1 and prs[0]["draft"] is True and prs[0]["reviewers"] == ["human:bia"]
    W.switch(kb, "main")
    W.apply(W.Plan(records=(rec(),)), mode=W.ApplyMode.LOCAL, kb_dir=kb)
    W.push_spool(kb_dir=kb, handle="ana", mode="auto", landed=frozenset())
    rp = json.loads((tmp_path / "forge/prs.json").read_text())[1]
    assert rp["head"].startswith("rec/") and rp["draft"] is False and rp["auto_merge"] is True


def test_auto_merge_only_for_records_pr(tmp_path):
    from t0 import _forge

    f = _forge.Forge("file", str(tmp_path))
    pr = _forge.open_pr(f, head="kb/x", base="main", title="t", body="b", reviewers=())
    with pytest.raises(_forge.ForgeError):
        _forge.enable_auto_merge(f, pr)
    with pytest.raises(_forge.ForgeError):
        _forge.open_records_pr(f, head="kb/x", base="main", title="t", body="b")
