import json
import os

import pytest

from t0 import setup
from t0.setup import BEGIN, END


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "api"
    (r / ".t0/skills/verify-api").mkdir(parents=True)
    (r / ".t0/skills/verify-api/SKILL.md").write_text("---\nname: verify-api\n---\n")
    return r


def tree(r):
    return {str(p.relative_to(r)): (os.readlink(p) if p.is_symlink() else p.read_text())
            for p in sorted(r.rglob("*")) if p.is_symlink() or p.is_file()}


def test_fresh_repo_gets_pointer_hooks_and_links(repo):
    assert setup.run(repo=repo) == 0
    assert (repo / "AGENTS.md").read_text().startswith(BEGIN)
    claude = json.loads((repo / ".claude/settings.json").read_text())["hooks"]
    assert claude["PreToolUse"][0]["hooks"][0]["command"] == "t0 hook pre-tool"
    assert "mcp__" in claude["PreToolUse"][0]["matcher"]
    copilot = json.loads((repo / ".github/hooks/t0.json").read_text())
    assert copilot["hooks"]["preToolUse"][0]["bash"] == "t0 hook pre-tool --tool copilot"
    kiro = json.loads((repo / ".kiro/hooks/t0.json").read_text())
    assert any(h["command"] == "t0 hook pre-tool --tool kiro" for h in kiro["hooks"])
    for d in (".claude/skills", ".github/skills", ".kiro/skills"):
        link = repo / d / "verify-api"
        assert link.is_symlink() and os.readlink(link) == "../../.t0/skills/verify-api"
        assert (link / "SKILL.md").read_text().startswith("---\nname: verify-api")


def test_second_run_changes_nothing(repo):
    setup.run(repo=repo)
    before = tree(repo)
    assert setup.run(repo=repo, check=True) == 0
    assert setup.plan(repo).actions == ()
    assert setup.run(repo=repo) == 0
    assert tree(repo) == before


def test_check_reports_without_writing(repo, capsys):
    assert setup.run(repo=repo, check=True) == 1
    assert not (repo / "AGENTS.md").exists() and not (repo / ".claude").exists()
    assert "pendente escrever: AGENTS.md" in capsys.readouterr().out


def test_existing_agents_md_and_settings_are_kept(repo):
    (repo / "AGENTS.md").write_text("# API\n\nregras do time\n")
    (repo / ".claude").mkdir()
    own = {"matcher": "Bash", "hooks": [{"type": "command", "command": "./lint.sh"}]}
    stale = {"matcher": "Bash", "hooks": [{"type": "command", "command": "t0 hook pre-tool-shell"}]}
    (repo / ".claude/settings.json").write_text(json.dumps(
        {"permissions": {"allow": ["Bash(ls)"]}, "hooks": {"PreToolUse": [own, stale], "Notification": [own]}}))
    setup.run(repo=repo)
    md = (repo / "AGENTS.md").read_text()
    assert md.startswith("# API\n\nregras do time\n\n" + BEGIN) and md.count(BEGIN) == 1
    s = json.loads((repo / ".claude/settings.json").read_text())
    assert s["permissions"] == {"allow": ["Bash(ls)"]}
    assert s["hooks"]["Notification"] == [own]
    pre = s["hooks"]["PreToolUse"]
    assert pre[0] == own and [g["hooks"][0]["command"] for g in pre[1:]] == ["t0 hook pre-tool"]


def test_pointer_block_is_replaced_in_place(repo):
    (repo / "AGENTS.md").write_text(f"# API\n\n{BEGIN}\nvelho\n{END}\n\n## Depois\nfim\n")
    setup.run(repo=repo)
    md = (repo / "AGENTS.md").read_text()
    assert "velho" not in md and md.endswith("\n## Depois\nfim\n") and md.count(END) == 1
    assert setup.plan(repo).actions == ()


def test_removed_verify_skill_loses_its_links_and_new_one_gains(repo):
    setup.run(repo=repo)
    (repo / ".t0/skills/verify-api/SKILL.md").unlink()
    (repo / ".t0/skills/verify-api").rmdir()
    (repo / ".t0/skills/verify-web").mkdir()
    setup.run(repo=repo)
    for d in (".claude/skills", ".github/skills", ".kiro/skills"):
        assert not (repo / d / "verify-api").is_symlink()
        assert (repo / d / "verify-web").is_symlink()


def test_real_directory_in_the_way_is_a_conflict(repo, capsys):
    (repo / ".claude/skills/verify-api").mkdir(parents=True)
    assert setup.run(repo=repo) == 2
    assert "conflito: .claude/skills/verify-api" in capsys.readouterr().err
    assert (repo / ".github/skills/verify-api").is_symlink()
    assert not (repo / ".claude/skills/verify-api").is_symlink()


def test_invalid_settings_json_is_not_clobbered(repo):
    (repo / ".claude").mkdir()
    (repo / ".claude/settings.json").write_text("{ nope")
    assert setup.run(repo=repo) == 2
    assert (repo / ".claude/settings.json").read_text() == "{ nope"
    assert (repo / "AGENTS.md").is_file()


def test_missing_repo_is_an_error(tmp_path):
    assert setup.run(repo=tmp_path / "nao-existe") == 2
