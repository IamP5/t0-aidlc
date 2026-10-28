import subprocess

import pytest

from t0.check import Level
from t0.kb import KB
from t0.okf.document import BundlePath, Document
from t0.profile.spec import EventKind
from t0.view import AnomalyKind, Ref, fold
from t0.write import Plan, Refusal
from test_check import build

NOW = "2026-10-28T10:00:00-03:00"
BETF = "products/p/bets/BET-001"


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("T0_NOW", NOW)
    monkeypatch.setenv("T0_HANDLE", "ana")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("T0_FORGE", raising=False)
    monkeypatch.delenv("T0_BET", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.chdir(tmp_path)


def git(kb, *a):
    return subprocess.run(["git", "-C", str(kb), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def do(kb_dir, fn, *a, **kw):
    kb = KB.open(kb_dir)
    res = getattr(kb, fn)(*a, **kw)
    if isinstance(res, Plan) and not res.empty:
        kb.apply(res)
    return res


def on(kb, branch):
    """The KB as read from a knowledge branch's worktree, `<kb>.wt/<branch>`."""
    return KB.open(kb.parent / f"{kb.name}.wt" / branch)


def approve(kb, branch):
    git(kb, "switch", "-q", "main")
    git(kb, "merge", "-q", "--no-ff", branch, "-m", f"merge {branch}")


def step(path, kind, at, **fm):
    extra = "".join(f"{k}: {v}\n" for k, v in fm.items())
    return Document(BundlePath(path), {"type": "Step", "kind": kind, "generated": {"by": "human:ana", "at": at},
                                       **{k: v for k, v in fm.items()}}, "", True, extra)


def slice_doc(state=None):
    fm = {"type": "Slice", "uid": "s1"} | ({"state": state} if state else {})
    return Document(BundlePath(f"/{BETF}/slices/01-a.md"), fm, "", True, "")


# ------------------------------------------------------------------ fold


def test_fold_moves_slice_from_records_and_ignores_duplicates():
    docs = [slice_doc(),
            step("/s/1.md", "pr-opened", "2026-10-28T10:00:00Z", target="s1", refs=["r#1"], dedup="o"),
            step("/s/2.md", "pr-opened", "2026-10-28T10:01:00Z", target="s1", refs=["r#1"], dedup="o"),
            step("/s/3.md", "pr-merged", "2026-10-28T11:00:00Z", target="s1", payload={"approvals": ["human:bia"]})]
    v = fold(docs, kb_sha="x")
    c = v.concepts["s1"]
    assert c.derived["state"] == "done" and c.derived["pr"] == "r#1" and c.derived["status"] == "stable"
    assert c.derived["verified"] == [{"by": "human:bia", "at": "2026-10-28T11:00:00Z"}] and not v.anomalies


def test_fold_ignores_a_hand_written_state_and_reports_illegal_moves():
    docs = [slice_doc("done"), step("/s/1.md", "ci-gate", "2026-10-28T10:00:00Z", target="s1", to="in-review")]
    v = fold(docs, kb_sha="x")
    assert v.concepts["s1"].derived["state"] == "ready"
    assert [a.kind for a in v.anomalies] == [AnomalyKind.ILLEGAL_TRANSITION]


def test_jira_key_is_written_once():
    docs = [slice_doc(), step("/s/1.md", "jira-linked", "2026-10-28T10:00:00Z", target="s1", payload={"key": "PAY-1"}),
            step("/s/2.md", "jira-linked", "2026-10-28T10:01:00Z", target="s1", payload={"key": "PAY-9"})]
    v = fold(docs, kb_sha="x")
    assert v.concepts["s1"].derived["jira"] == "PAY-1" and v.resolve(Ref("PAY-1")).uid == "s1"
    assert [a.kind for a in v.anomalies] == [AnomalyKind.JIRA_KEY_CHANGED]


def test_refs_resolve_by_kb_id_shorthand_and_path(tmp_path):
    kb = KB.open(build(tmp_path))
    assert kb.get(Ref("BET-001")).path.endswith("/bet.md")
    assert kb.get(Ref("BET-001/1")).kb_id == "01-api"
    assert kb.get(Ref(f"{BETF}/spec")).uid == "bet-001-spec"
    assert kb.get(Ref("BET-999")) is None


# ------------------------------------------------------------------ new


def test_idea_ids_are_reserved_across_branches_and_titles_dedup(tmp_path):
    kb = build(tmp_path)
    do(kb, "new", "idea", title="Alerta de limite")
    git(kb, "switch", "-q", "main")
    p = do(kb, "new", "idea", title="Outra ideia")
    assert p.knowledge.puts[0].path == "/ideas/IDEA-0002.md"
    approve(kb, "kb/ana/IDEA-0002")
    dup = KB.open(kb).new("idea", title="outra  IDEIA")
    assert isinstance(dup, Refusal) and "IDEA-0002" in dup.reasons_pt[0]


def test_two_sessions_reserving_at_once_get_different_ids(tmp_path):
    import threading

    kb = build(tmp_path)
    first = KB.open(kb)
    a = first.new("idea", title="Primeira")
    second = {}
    t = threading.Thread(target=lambda: second.update(p=do(kb, "new", "idea", title="Segunda")))
    t.start()
    t.join(0.5)
    assert t.is_alive()
    first.apply(a)
    t.join(10)
    assert a.knowledge.puts[0].path == "/ideas/IDEA-0001.md" and second["p"].knowledge.puts[0].path == "/ideas/IDEA-0002.md"


def test_rapida_free_text_creates_idea_bet_and_slice_on_one_branch(tmp_path):
    kb = build(tmp_path)
    p = do(kb, "new", "bet", track="rapida", ref="Corrigir fuso", product="p", repo="api")
    assert p.knowledge.branch == "bet/BET-002/ana"
    paths = sorted(d.path for d in p.knowledge.puts)
    assert paths == ["/ideas/IDEA-0001.md", "/products/p/bets/BET-002/bet.md", "/products/p/bets/BET-002/slices/01-corrigir-fuso.md"]
    v = on(kb, "bet/BET-002/ana").view()
    assert v.resolve(Ref("IDEA-0001")).state == "promoted" and v.resolve(Ref("BET-002"))["track"] == "rapida"
    assert git(kb, "status", "--porcelain") == "" and git(kb, "branch", "--show-current") == "main"


def test_new_bet_proposes_the_pod_bet_owner_as_decider(tmp_path):
    kb = build(tmp_path)
    bia = (kb / "team/people/ana.md").read_text().replace("ana", "bia").replace("pods: [p]", "pods: [p]\nroles: [bet-owner]")
    (kb / "team/people/bia.md").write_text(bia)
    git(kb, "add", "-A")
    git(kb, "commit", "-qm", "bia")
    do(kb, "new", "bet", track="rapida", ref="Corrigir fuso", product="p", repo="api")
    assert KB.open(kb).get(Ref("BET-002"))["decision_by"] == "human:bia"


def test_bet_track_needs_a_prototyped_idea(tmp_path):
    kb = build(tmp_path)
    assert isinstance(KB.open(kb).new("bet", track="bet", ref="texto", product="p"), Refusal)
    do(kb, "new", "idea", title="Ideia", sets=["product=p"])
    approve(kb, "kb/ana/IDEA-0001")
    r = KB.open(kb).new("bet", track="bet", ref="IDEA-0001")
    assert isinstance(r, Refusal) and "veredito" in r.reasons_pt[0]
    do(kb, "idea_prototype", "IDEA-0001", "segue", "gist:1")
    approve(kb, "kb/ana/IDEA-0001")
    p = do(kb, "new", "bet", track="bet", ref="IDEA-0001")
    assert {d.path for d in p.knowledge.puts} == {"/products/p/bets/BET-002/bet.md", "/ideas/IDEA-0001.md"}


def test_adr_accept_opens_a_knowledge_pr_to_the_deciders(tmp_path):
    kb = build(tmp_path)
    p = do(kb, "new", "adr", title="Busca no forge", sets=["deciders=[human:ana]"])
    branch = p.knowledge.branch
    approve(kb, branch)
    assert KB.open(kb).get(Ref("ADR-0001")).state == "proposed"
    p = do(kb, "adr_accept", "ADR-0001")
    assert p.knowledge.reviewers == ("human:ana",) and git(kb, "status", "--porcelain") == ""
    assert KB.open(kb).get(Ref("ADR-0001")).state == "proposed"
    adr = on(kb, p.knowledge.branch).get(Ref("ADR-0001"))
    assert adr.state == "accepted" and adr["decided_at"] == NOW and "verified" not in adr.doc.frontmatter
    assert "LANE.state-transition" not in on(kb, p.knowledge.branch).check(Level.L2, changed_from="main").rules()
    approve(kb, p.knowledge.branch)
    assert "já está `accepted`" in KB.open(kb).adr_accept("ADR-0001").messages_pt[0]
    assert isinstance(KB.open(kb).adr_accept("BET-001"), Refusal)


def test_set_rejects_unknown_and_derived_keys(tmp_path):
    r = KB.open(build(tmp_path)).new("idea", title="x", sets=["jira=PAY-1", "nada=1"])
    assert isinstance(r, Refusal) and len(r.reasons_pt) == 2


def test_set_refuses_provenance_and_malformed_values(tmp_path):
    kb = build(tmp_path)
    r = KB.open(kb).new("harness", title="x", pattern="p", occurrence="o",
                        sets=["generated={by: claude-code/opus-5.5, at: 2026-10-28 09:30:00-03:00}", "owner=ninguém"])
    assert isinstance(r, Refusal) and len(r.reasons_pt) == 2
    assert "`owner` precisa ser" in r.reasons_pt[1]
    assert not isinstance(KB.open(kb).new("harness", title="x", pattern="p", occurrence="o",
                                          sets=["owner=role:harness-keeper"]), Refusal)


def test_dry_run_neither_switches_nor_writes(tmp_path):
    kb = build(tmp_path)
    res = KB.open(kb, dry=True).new("idea", title="x")
    assert res.knowledge is not None and git(kb, "branch", "--show-current") == "main" and git(kb, "status", "--porcelain") == ""


# ------------------------------------------------------------------ log, dor, ci, ship


def test_log_spools_a_record_and_kill_opens_the_decision_pr(tmp_path):
    kb = build(tmp_path)
    p = do(kb, "record", EventKind.PROGRESS, "avancei", bet=Ref("BET-001"))
    assert p.knowledge is None and len(p.records) == 1
    assert KB.open(kb).view().pending == 1
    k = do(kb, "record", EventKind.KILL, "ninguém quer", bet=Ref("BET-001"))
    assert k.records and k.knowledge.branch == "bet/BET-001/ana"
    bet = on(kb, "bet/BET-001/ana").get(Ref("BET-001"))
    assert bet.state == "killed" and "ninguém quer" in bet.doc.body


def _activate(kb, jira="PAY-7"):
    for rel in (f"{BETF}/bet.md",):
        p = kb / rel
        p.write_text(p.read_text().replace("state: proposed\nstatus: draft", "state: active\nstatus: stable"))
    p = kb / f"{BETF}/spec.md"
    p.write_text(p.read_text().replace("state: draft\nstatus: draft", "state: approved\nstatus: stable"))
    git(kb, "commit", "-qam", "active")
    k = KB.open(kb)
    from t0.write import new_record
    from t0.okf.document import Actor

    r = new_record(EventKind.JIRA_LINKED, type_name="Step", fields={"target": "bet-001-slice-01", "payload": {"key": jira}},
                   body="link", actor=Actor("process:t0-sync"), handle="t0-sync", where={"repo": "kb"})
    k.apply(Plan(records=(r,)))


def test_slice_dor_lists_every_gap_then_passes(tmp_path):
    kb = build(tmp_path)
    r = KB.open(kb).slice_dor("BET-001/01")
    assert isinstance(r, Refusal) and any("aposta" in x for x in r.reasons_pt) and any("Jira" in x for x in r.reasons_pt)
    _activate(kb)
    assert isinstance(KB.open(kb).slice_dor("PAY-7"), Plan)


def test_slice_dor_enforces_wip_from_policy(tmp_path):
    kb = build(tmp_path)
    _activate(kb)
    pol = kb / "methodology/policies/wip.md"
    pol.parent.mkdir(parents=True)
    pol.write_text("---\ntype: Policy\ntitle: WIP\ndescription: d\nuid: policy-wip\nowner: role:x\n"
                   "generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }\nthresholds: { slices_building_per_person: 1 }\n"
                   "stale_after: 2027-01-01T00:00:00-03:00\n---\n")
    for n in ("02-b", "03-c"):
        s = kb / f"{BETF}/slices/{n}.md"
        s.write_text((kb / f"{BETF}/slices/01-api.md").read_text().replace("bet-001-slice-01", f"bet-001-slice-{n[:2]}"))
    git(kb, "add", "-A")
    git(kb, "commit", "-qm", "wip")
    do(kb, "ci", "BET-001/02", pr="api#2", state="draft")
    r = KB.open(kb).slice_dor("PAY-7")
    assert isinstance(r, Refusal) and "WIP" in r.reasons_pt[-1] and "limite 1 (Policy wip)" in r.reasons_pt[-1]


def test_ci_chain_needs_audit_and_tier_approvals_and_ends_done(tmp_path):
    kb = build(tmp_path)
    _activate(kb)
    assert "audit" in KB.open(kb).ci("PAY-7", pr="api#9", state="ready").reasons_pt[0]
    (tmp_path / ".audit").mkdir()
    (tmp_path / ".audit/PAY-7.tsv").write_text("x")
    do(kb, "ci", "PAY-7", pr="api#9", state="ready")
    assert KB.open(kb).get(Ref("PAY-7")).state == "in-review"
    assert isinstance(KB.open(kb).ci("PAY-7", pr="api#9", state="merged"), Refusal)
    p = do(kb, "ci", "PAY-7", pr="api#9", state="merged", approvals=["human:bia"])
    s = KB.open(kb).get(Ref("PAY-7"))
    assert s.state == "done" and s["audit"] == ".audit/PAY-7.tsv" and s["verified"][0]["by"] == "human:bia"
    assert "bet ship BET-001" in p.messages_pt[-1]
    assert do(kb, "ci", "PAY-7", pr="api#9", state="merged", approvals=["human:bia"]).records
    assert len([e for e in KB.open(kb).view().events if e.kind is EventKind.PR_MERGED]) == 1


def test_ci_on_merged_decision_pr_derives_verified_from_approvals(tmp_path):
    kb = build(tmp_path)
    do(kb, "gate", "aposta", Ref("BET-001"))
    approve(kb, "bet/BET-001/ana")
    assert KB.open(kb).ci("BET-001", pr="kb#3", state="merged", approvals=["human:bia"]).reasons_pt == (
        "falta a aprovação de human:ana",)
    do(kb, "ci", "BET-001", pr="kb#3", state="merged", approvals=["human:ana"])
    bet = KB.open(kb).get(Ref("BET-001"))
    assert bet.state == "active" and bet["verified"] == [{"by": "human:ana", "at": NOW}]
    assert KB.open(kb).ci("BET-001", pr="kb#3", state="draft").records == ()


def test_bet_ship_freezes_spec_and_updates_living_spec(tmp_path):
    kb = build(tmp_path)
    _activate(kb)
    assert isinstance(KB.open(kb).bet_ship("BET-001"), Refusal)
    do(kb, "ci", "PAY-7", pr="api#9", state="merged", approvals=["human:bia"])
    p = do(kb, "bet_ship", "BET-001")
    v = on(kb, "bet/BET-001/ana").view()
    assert v.resolve(Ref("BET-001")).state == "shipped" and v.resolve(Ref(f"{BETF}/spec")).state == "frozen"
    assert "### BET-001" in (kb.parent / "kb.wt/bet/BET-001/ana/products/p/product.md").read_text()
    assert KB.open(kb).bet_ship("BET-001").empty


def test_harness_pr_is_derived_from_ci_records(tmp_path):
    kb = build(tmp_path)
    do(kb, "new", "harness", pattern="agente esquece fuso", occurrence="api#1")
    approve(kb, "kb/ana/HI-0001")
    again = do(kb, "new", "harness", pattern="Agente esquece fuso", occurrence="api#2")
    assert "2ª ocorrência" in again.messages_pt[0]
    approve(kb, "kb/ana/HI-0001")
    do(kb, "ci", "HI-0001", pr="api#3", state="draft")
    hi = KB.open(kb).get(Ref("HI-0001"))
    assert hi["pr"] == "api#3" and hi.state == "open"
    do(kb, "ci", "HI-0001", pr="api#3", state="merged")
    assert KB.open(kb).get(Ref("HI-0001")).state == "fixed"


# ------------------------------------------------------------------ propose / gate


def test_propose_commits_hand_edits_on_the_bet_branch_and_refuses_derived_edits(tmp_path):
    kb = build(tmp_path)
    spec = kb / f"{BETF}/spec.md"
    spec.write_text(spec.read_text() + "\nMais contexto.\n")
    p = do(kb, "propose", "Spec mais clara")
    assert p.knowledge.branch == "bet/BET-001/ana" and git(kb, "status", "--porcelain") == ""
    prod = kb / "products/p/product.md"
    prod.write_text(prod.read_text().replace("status: draft", "status: stable"))
    r = KB.open(kb).propose("mexe derivado")
    assert isinstance(r, Refusal) and "LANE.derived-untouched" in r.reasons_pt[0]


def test_propose_finds_the_worktree_with_edits_and_refuses_to_guess_between_main_and_a_branch(tmp_path):
    kb = build(tmp_path)
    do(kb, "gate", "aposta", Ref("BET-001"))
    wt = kb.parent / "kb.wt/bet/BET-001/ana"
    bet = wt / f"{BETF}/bet.md"
    bet.write_text(bet.read_text() + "\nMais hipótese.\n")
    p = do(kb, "propose", "Hipótese mais clara")
    assert p.knowledge.branch == "bet/BET-001/ana" and p.messages_pt == (f"incluído: /{BETF}/bet.md",)
    assert git(wt, "status", "--porcelain") == "" and "Mais hipótese." in git(kb, "show", f"bet/BET-001/ana:{BETF}/bet.md")
    spec = kb / f"{BETF}/spec.md"
    spec.write_text(spec.read_text() + "\nNo main.\n")
    r = KB.open(kb).propose("no main")
    assert isinstance(r, Refusal) and str(wt) in r.reasons_pt[0] and "No main." in spec.read_text()
    assert "já está `active`" in KB.open(kb).gate("aposta", Ref("BET-001")).messages_pt[0]
    s = KB.open(kb).new("slice", ref="BET-001", title="Outro", repo="api")
    assert isinstance(s, Refusal) and f"{BETF}/spec.md" in s.reasons_pt[0] and str(wt) in s.reasons_pt[0]
    assert git(kb, "branch", "--show-current") == "main"


def test_propose_from_inside_a_worktree_commits_on_its_branch(tmp_path, monkeypatch):
    kb = build(tmp_path)
    do(kb, "new", "harness", pattern="esquece fuso")
    wt = kb.parent / "kb.wt/kb/ana/HI-0001"
    (wt / "glossary/fuso.md").write_text((kb / "glossary/limite.md").read_text().replace("limite", "fuso"))
    do(kb, "new", "idea", title="Outra")
    (kb.parent / "kb.wt/kb/ana/IDEA-0001/glossary/outra.md").write_text("x")
    assert "mais de um worktree" in KB.open(kb).propose("qual?").reasons_pt[0]
    monkeypatch.chdir(wt / "glossary")
    p = do(None, "propose", "Glossário de fuso")
    assert p.knowledge.branch == "kb/ana/HI-0001" and "glossary/fuso.md" in git(kb, "show", "--stat", "kb/ana/HI-0001")


def test_gate_writes_state_but_not_verified_into_the_decision_pr(tmp_path):
    kb = build(tmp_path)
    p = do(kb, "gate", "aposta", Ref("BET-001"))
    assert p.knowledge.branch == "bet/BET-001/ana" and p.knowledge.reviewers == ("human:ana",)
    bet = on(kb, "bet/BET-001/ana").get(Ref("BET-001"))
    assert bet.state == "active" and bet["status"] == "stable" and "verified" not in bet.doc.frontmatter
    assert isinstance(KB.open(kb).gate("aposta", Ref("BET-001"), ci=True), Plan)
    assert KB.open(kb).gate("aposta", Ref("BET-001")).empty
    assert isinstance(KB.open(kb).gate("degrau", Ref("BET-001")), Refusal)
