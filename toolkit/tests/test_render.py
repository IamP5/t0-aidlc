import pytest

from t0.check import Level
from t0.kb import KB
from t0.render import set_keys
from t0.write import ApplyMode
from test_check import build
from test_kb import _activate, env  # noqa: F401  (autouse env fixture)


def render(kb):
    k = KB.open(kb)
    plan = k.render()
    if not plan.empty:
        k.apply(plan, mode=ApplyMode.KB_RENDER)
    return plan


def test_render_materializes_records_and_converges(tmp_path):
    kb = build(tmp_path)
    _activate(kb)
    KB.open(kb).push()
    import subprocess

    subprocess.run(["git", "-C", str(kb), "merge", "-q", "rec/ana/2026-10-28"], check=True)
    first = render(kb)
    assert first.derived is not None
    assert render(kb).empty and render(kb).messages_pt == ("derivados em dia",)
    sl = (kb / "products/p/bets/BET-001/slices/01-api.md").read_text()
    assert "jira: PAY-7" in sl and "## Como verificar\n\npytest -k limite" in sl
    idx = (kb / "index.md").read_text()
    assert idx.startswith('---\nokf_version: "0.2"\n---') and "* [bet-001](/products/p/bets/BET-001/bet.md) - Descrição de bet-001." in idx
    log = (kb / "log.md").read_text()
    assert "## 2026-10-28" in log and "**Jira** por process:t0-sync" in log
    assert (kb / "products/p/bets/BET-001/changeset.md").is_file()
    assert KB.open(kb).check(Level.L2).findings == ()


def test_render_refuses_off_main(tmp_path):
    from t0.write import ApplyError, switch

    kb = build(tmp_path)
    switch(kb, "kb/ana/x")
    k = KB.open(kb)
    with pytest.raises(ApplyError):
        k.apply(k.render(), mode=ApplyMode.KB_RENDER)


def test_set_keys_keeps_other_lines_byte_for_byte():
    raw = "---\ntype: X\nrelations: { a: /b.md }\nstate: ready\nlist:\n  - x\n---\ncorpo\n"
    out = set_keys(raw, {"state": "done", "list": ["y"], "pr": "r#1"})
    assert out == "---\ntype: X\nrelations: { a: /b.md }\nstate: done\nlist: [y]\npr: r#1\n---\ncorpo\n"
