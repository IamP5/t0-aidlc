import json
import tomllib
from pathlib import Path

import pytest

from t0 import gen
from t0.gen import GenContext, Scope

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
VERSION = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
MCP = {"mcpServers": {"t0-kb": {"command": "t0", "args": ["mcp"]}}}


@pytest.fixture
def src(tmp_path):
    d = tmp_path / "plugin"
    (d / "skills/bet-use").mkdir(parents=True)
    (d / "skills/bet-use/SKILL.md").write_text("---\nname: bet-use\ndescription: troca a bet\n---\ncorpo\n")
    (d / "skills/bet-use/refs/x.md").parent.mkdir()
    (d / "skills/bet-use/refs/x.md").write_text("ref")
    (d / "skills/_shared").mkdir()
    (d / "skills/_shared/header.md").write_text("não é skill")
    (d / ".mcp.json").write_text(json.dumps(MCP))
    return d


def test_plugin_scope_renders_every_adapter(src, tmp_path):
    out = tmp_path / "out"
    assert gen.run(scope="plugin", src=src, out=out) == 0
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    assert files == sorted([
        ".claude-plugin/plugin.json", "hooks/hooks.json", "plugin.json", "mcp.json", ".github/hooks/t0.json",
        ".vscode/mcp.json", ".github/copilot-instructions.md", ".kiro/steering/t0.md", ".kiro/settings/mcp.json",
        ".kiro/hooks/t0.json", ".kiro/skills/bet-use/SKILL.md", ".kiro/skills/bet-use/refs/x.md"])
    claude = json.loads((out / ".claude-plugin/plugin.json").read_text())
    assert claude["name"] == "t0" and claude["version"] == VERSION
    agent = json.loads((out / "plugin.json").read_text())
    assert {"$schema", "name", "version", "description", "author", "keywords"} <= agent.keys()
    assert json.loads((out / ".kiro/settings/mcp.json").read_text()) == MCP
    assert json.loads((out / ".vscode/mcp.json").read_text()) == {
        "servers": {"t0-kb": {"type": "stdio", "command": "t0", "args": ["mcp"]}}}
    steering = (out / ".kiro/steering/t0.md").read_text()
    assert steering.startswith("---\ninclusion: always\n---\n") and "#[[file:.t0/context.md]]" in steering


def test_hook_registrations_per_tool(src, tmp_path):
    out = tmp_path / "out"
    gen.run(scope="plugin", src=src, out=out)
    claude = json.loads((out / "hooks/hooks.json").read_text())["hooks"]
    assert claude["PreToolUse"][0]["matcher"] == "Bash|Edit|Write|MultiEdit|NotebookEdit|Read|Grep|Glob"
    assert claude["PreToolUse"][0]["hooks"][0]["command"] == "t0 hook pre-tool"
    assert claude["SessionStart"][0]["matcher"] == "startup|resume|clear|compact"
    assert set(claude) == {"SessionStart", "SubagentStart", "UserPromptSubmit", "PreToolUse", "Stop"}
    copilot = json.loads((out / ".github/hooks/t0.json").read_text())
    assert copilot["version"] == 1
    assert copilot["hooks"]["preToolUse"][0]["bash"] == "t0 hook pre-tool --tool copilot"
    assert set(copilot["hooks"]) == {"sessionStart", "userPromptSubmitted", "preToolUse", "agentStop"}
    kiro = json.loads((out / ".kiro/hooks/t0.json").read_text())
    assert {h["command"] for h in kiro["hooks"]} >= {"t0 hook pre-tool --tool kiro"}


def test_check_detects_drift_and_write_is_idempotent(src, tmp_path):
    out = tmp_path / "out"
    assert gen.run(scope="plugin", src=src, out=out, check=True) == 1
    gen.run(scope="plugin", src=src, out=out)
    assert gen.run(scope="plugin", src=src, out=out, check=True) == 0
    ctx = GenContext(out, Scope.PLUGIN, src)
    assert gen.write(ctx, gen.generate(ctx)) == []
    (out / "hooks/hooks.json").write_text("{}")
    (src / "skills/bet-use/SKILL.md").write_text("mudou")
    drift = {(d.path, d.reason) for d in gen.check_drift(ctx)}
    assert drift == {("hooks/hooks.json", "differs"), (".kiro/skills/bet-use/SKILL.md", "differs")}


def test_missing_mcp_source_is_an_error(src, tmp_path):
    (src / ".mcp.json").unlink()
    assert gen.run(scope="plugin", src=src, out=tmp_path / "o") == 2


def test_kb_profile_md_ignores_timestamp_drift(tmp_path):
    ctx1 = GenContext(tmp_path, Scope.KB, facts={"now": "2026-10-27T10:00:00+00:00"})
    gen.write(ctx1, gen.generate(ctx1))
    text = (tmp_path / "profile.md").read_text()
    assert "type: OKF Profile" in text and "| Slice | slice | knowledge |" in text
    assert "| G2 | Spec aprovado | Spec |" in text
    ctx2 = GenContext(tmp_path, Scope.KB, facts={"now": "2026-12-01T10:00:00+00:00"})
    assert gen.check_drift(ctx2) == []
    assert gen.write(ctx2, gen.generate(ctx2)) == []
    assert (tmp_path / "profile.md").read_text() == text
