import json
import shutil
import subprocess
from pathlib import Path

import pytest

from t0 import gen
from t0.check import RULES, Level
from t0.kb import KB

FIX = Path(__file__).parent / "fixtures" / "kb-negative"
NOW = "2026-10-28T10:00:00-03:00"
RULE_IDS = sorted(r.id for r in RULES)


def git(d, *a):
    subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)


def build(tmp_path, rule=None):
    """_base (+ rule/base) committed on main, then rule/files on top: check runs in PR mode against main."""
    kb = tmp_path / "kb"
    shutil.copytree(FIX / "_base", kb)
    ctx = gen.GenContext(kb, gen.Scope.KB, facts={"now": NOW})
    gen.write(ctx, gen.generate(ctx))
    if rule and (FIX / rule / "base").is_dir():
        shutil.copytree(FIX / rule / "base", kb, dirs_exist_ok=True)
    git(kb, "init", "-q", "-b", "main")
    git(kb, "add", "-A")
    git(kb, "commit", "-qm", "base")
    if rule:
        shutil.copytree(FIX / rule / "files", kb, dirs_exist_ok=True)
    return kb


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("T0_NOW", NOW)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("T0_ROLE", raising=False)


def run(kb):
    return KB.open(kb).check(Level.L2, changed_from="main")


def test_every_rule_has_exactly_one_negative_fixture():
    dirs = sorted(p.name for p in FIX.iterdir() if p.is_dir() and not p.name.startswith("_"))
    assert dirs == RULE_IDS


def test_base_fixture_is_clean_at_l2(tmp_path):
    rep = run(build(tmp_path))
    assert rep.findings == (), rep.format()


@pytest.mark.parametrize("rule", RULE_IDS)
def test_negative_fixture_trips_its_rule(tmp_path, rule):
    rep = run(build(tmp_path, rule))
    assert rule in rep.rules(), rep.format()
    errors = {f.rule for f in rep.findings if f.severity.value == "error"}
    if rule.startswith("L2."):
        assert rule not in errors
    else:
        assert rule in errors and not rep.ok


def test_lane_rules_need_pr_mode(tmp_path):
    kb = build(tmp_path, "LANE.records-add-only")
    rep = KB.open(kb).check(Level.L2)
    assert not any(f.rule.startswith("LANE.") for f in rep.findings)


def test_kb_render_role_may_touch_derived_files(tmp_path, monkeypatch):
    kb = build(tmp_path, "LANE.derived-untouched")
    monkeypatch.setenv("T0_ROLE", "kb-render")
    assert "LANE.derived-untouched" not in run(kb).rules()


def test_state_transition_passes_when_gate_holds_without_verified(tmp_path):
    kb = build(tmp_path)
    bet = kb / "products/p/bets/BET-001/bet.md"
    bet.write_text(bet.read_text().replace("state: proposed\nstatus: draft", "state: active\nstatus: stable"))
    assert "LANE.state-transition" not in run(kb).rules()


def test_hand_written_verified_on_a_decision_is_derived_untouched(tmp_path):
    kb = build(tmp_path)
    bet = kb / "products/p/bets/BET-001/bet.md"
    bet.write_text(bet.read_text().replace("state: proposed\nstatus: draft",
                   "state: active\nstatus: stable\nverified:\n  - {by: human:ana, at: 2026-10-28T09:00:00-03:00}"))
    assert "LANE.derived-untouched" in run(kb).rules()


def test_formats(tmp_path):
    rep = run(build(tmp_path, "L1.required-fields"))
    data = json.loads(rep.format("json"))
    assert data["ok"] is False and data["findings"][0]["rule"] == "L1.required-fields"
    assert rep.format("github").startswith("::error file=glossary/x.md::L1.required-fields")
    assert "1 erro(s)" in rep.format("text")


def test_level_l0_skips_profile_rules(tmp_path):
    kb = build(tmp_path, "L1.type-registered")
    assert KB.open(kb).check(Level.L0).findings == ()
