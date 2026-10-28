import json
from pathlib import Path

import pytest

from t0.hooks import HOOKS, run_hook

SPEC = """---
type: Spec
title: "Spec"
uid: spec-1
state: draft
status: draft
---
## Corpo
texto
"""


@pytest.fixture
def env(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".t0/inbox").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("T0_BET", raising=False)
    kb = tmp_path / "ws/kb"
    bet = kb / "products/p/bets/BET-1"
    (bet / "steps").mkdir(parents=True)
    (kb / "index.md").write_text('---\nokf_version: "0.2"\n---\n')
    (bet / "spec.md").write_text(SPEC)
    (bet / "steps/2026-10-27-ana-kb-abcd.md").write_text("---\ntype: Step\nkind: progress\n---\nok\n")
    return tmp_path


def claude(name, cwd, **payload):
    return run_hook(name, json.dumps({"cwd": str(cwd), "hook_event_name": "x", **payload}).encode())


def bash(cmd, cwd):
    return claude("pre-tool", cwd, tool_name="Bash", tool_input={"command": cmd})


BLOCKED_SHELL = [
    "git push --force", "git push -f origin feat", "git push origin +main", "git push --force-with-lease",
    "git push --force-with-lease=main:abc123 origin main", "git push --force-if-includes",
    "git -C ../api push -f", "git -c user.name=x push -uf origin b", "git --git-dir=.git push origin +HEAD:main",
    "git reset --hard HEAD~1", "cd api && git push -f", 'bash -c "git push --force"', "FOO=1 git push -f",
    "sudo git reset --hard", "git status; git -C /tmp/x reset --hard origin/main",
    "cat ~/.t0/inbox/raw.vtt", "head $HOME/.t0/inbox/x.srt", "cp ~/.t0/inbox/a.docx /tmp/",
]
ALLOWED_SHELL = [
    "git push origin feat", "git push -u origin bet/BET-1/PAY-1-x", "git reset --soft HEAD~1",
    'git commit -m "docs: explain push -f"', 'echo "git push -f"', "git log --format=%f", "git fetch -f",
    "git push -o ci.skip origin feat", "t0 transcript redact ~/.t0/inbox/raw.vtt", "ls -la",
]


@pytest.mark.parametrize("cmd", BLOCKED_SHELL)
def test_shell_blocked(env, cmd):
    code, out, err = bash(cmd, env)
    assert code == 2 and err.strip() and out == ""


@pytest.mark.parametrize("cmd", ALLOWED_SHELL)
def test_shell_allowed(env, cmd):
    assert bash(cmd, env) == (0, "", "")


def test_copilot_camelcase_with_json_string_args(env):
    raw = {"cwd": str(env), "toolName": "bash", "toolArgs": json.dumps({"command": "git -C x push --force"})}
    assert run_hook("pre-tool", json.dumps(raw).encode())[0] == 2
    raw["toolArgs"] = json.dumps({"command": "git push"})
    assert run_hook("pre-tool", json.dumps(raw).encode())[0] == 0


def test_kiro_shape_via_tool_override(env):
    raw = {"cwd": str(env), "hook_event_name": "preToolUse", "tool_name": "execute_bash",
           "tool_input": {"command": "git reset --hard"}}
    code, _, err = run_hook("pre-tool", json.dumps(raw).encode(), tool="kiro")
    assert code == 2 and "reset --hard" in err


def edit(env, rel, **ti):
    return claude("pre-tool", env, tool_name=ti.pop("tool", "Edit"), tool_input={"file_path": str(env / rel), **ti})


@pytest.mark.parametrize("rel", ["ws/kb/index.md", "ws/kb/products/p/bets/BET-1/log.md",
                                 "ws/kb/products/p/bets/BET-1/changeset.md", "ws/kb/profile.md"])
def test_derived_files_blocked(env, rel):
    assert edit(env, rel, tool="Write", content="x")[0] == 2


def test_index_outside_kb_allowed(env):
    assert edit(env, "notes/index.md", tool="Write", content="x")[0] == 0


def test_derived_key_edit_blocked_body_edit_allowed(env):
    spec = "ws/kb/products/p/bets/BET-1/spec.md"
    code, _, err = edit(env, spec, old_string="state: draft", new_string="state: approved")
    assert code == 2 and "state" in err
    assert edit(env, spec, old_string="texto", new_string="texto novo")[0] == 0
    assert edit(env, spec, old_string='title: "Spec"', new_string='title: "Spec v2"')[0] == 0


def test_new_slice_with_derived_jira_blocked(env):
    content = "---\ntype: Slice\ntitle: x\njira: PAY-9\n---\n"
    assert edit(env, "ws/kb/products/p/bets/BET-1/slices/01-x.md", tool="Write", content=content)[0] == 2
    ok = "---\ntype: Slice\ntitle: x\nrepo: api\n---\n"
    assert edit(env, "ws/kb/products/p/bets/BET-1/slices/01-x.md", tool="Write", content=ok)[0] == 0


def test_copilot_str_replace_on_derived_key(env):
    raw = {"cwd": str(env), "toolName": "edit", "toolArgs": json.dumps({
        "path": str(env / "ws/kb/products/p/bets/BET-1/spec.md"), "old_str": "status: draft", "new_str": "status: stable"})}
    assert run_hook("pre-tool", json.dumps(raw).encode())[0] == 2


def test_existing_step_immutable_new_step_allowed(env):
    assert edit(env, "ws/kb/products/p/bets/BET-1/steps/2026-10-27-ana-kb-abcd.md", old_string="ok", new_string="x")[0] == 2
    assert edit(env, "ws/kb/products/p/bets/BET-1/steps/new.md", tool="Write", content="---\ntype: Step\n---\n")[0] == 0


def test_read_inbox_blocked(env):
    inbox = Path(env / "home/.t0/inbox/raw.vtt")
    assert claude("pre-tool", env, tool_name="Read", tool_input={"file_path": str(inbox)})[0] == 2
    assert claude("pre-tool", env, tool_name="Grep", tool_input={"pattern": "x", "path": str(inbox.parent)})[0] == 2
    assert claude("pre-tool", env, tool_name="Read", tool_input={"file_path": str(env / "ws/kb/index.md")})[0] == 0


def test_session_start_injects_claude_json_and_writes_context(env):
    t0 = env / "ws/.t0"
    t0.mkdir()
    (t0 / "workspace.json").write_text(json.dumps({"product": "p"}))
    code, out, err = claude("session-start", env / "ws")
    assert code == 0 and err == ""
    payload = json.loads(out)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    text = payload["hookSpecificOutput"]["additionalContext"]
    assert text and (t0 / "context.md").read_text() == text + "\n"


def test_session_start_plain_text_for_copilot(env):
    code, out, _ = run_hook("session-start", json.dumps({"cwd": str(env)}).encode(), tool="copilot")
    assert code == 0 and out.strip() and not out.startswith("{")


def test_prompt_submit_warns_on_foreign_key_only(env):
    t0 = env / "ws/.t0"
    t0.mkdir()
    (t0 / "bet.json").write_text(json.dumps({"bet": "BET-1", "jira": "PAY-123", "stories": ["PAY-130", "PAY-131"]}))
    code, out, _ = claude("prompt-submit", env / "ws", prompt="corrige PAY-200 junto com PAY-131, UTF-8")
    msg = json.loads(out)["systemMessage"]
    assert code == 0 and "PAY-200" in msg and "PAY-131" not in msg and "UTF-8" not in msg
    assert claude("prompt-submit", env / "ws", prompt="segue PAY-131") == (0, "", "")


def test_stop_never_blocks(env):
    assert claude("stop", env)[0] == 0


def test_unknown_hook():
    assert run_hook("nope", b"{}")[0] == 1


def test_hooks_table_covers_every_event():
    from t0.hooks import Event

    assert {h.event for h in HOOKS} == set(Event)


BLOCKED_GH = [
    "gh pr ready", "gh pr ready 12", "gh pr merge 12 --squash", "gh pr merge --auto", "gh pr review 12 --approve",
    "gh pr review -a", 'gh pr create --title x --body "y"', "gh pr create --fill", "gh pr create --draft=false",
    "cd api && gh pr create -t x -b y", "GH_TOKEN=x gh pr merge 3",
]
ALLOWED_GH = [
    "gh pr create --draft --title x --body y", "gh pr create -d -t x -b y", "gh pr create --fill --draft",
    "gh pr ready 12 --undo", "gh pr review 12 --comment -b ok", "gh pr view 12 --json isDraft", "gh pr list",
    'gh pr comment 12 --body "não faça gh pr merge"', "gh issue create -t x",
]


@pytest.mark.parametrize("cmd", BLOCKED_GH)
def test_gh_pr_blocked(env, cmd):
    code, out, err = bash(cmd, env)
    assert code == 2 and "draft" in err and out == ""


@pytest.mark.parametrize("cmd", ALLOWED_GH)
def test_gh_pr_allowed(env, cmd):
    assert bash(cmd, env) == (0, "", "")


def mcp(env, name, **ti):
    return claude("pre-tool", env, tool_name=name, tool_input=ti)


@pytest.mark.parametrize("name, ti", [
    ("mcp__github__create_pull_request", {"title": "x", "head": "b", "base": "main"}),
    ("mcp__github__create_pull_request", {"title": "x", "draft": False}),
    ("mcp__plugin_github_github__merge_pull_request", {"pullNumber": 3}),
    ("mcp__github__merge_pull_request", {"pullNumber": 3, "draft": True}),
    ("mcp__github__update_pull_request", {"pullNumber": 3, "draft": False}),
])
def test_github_mcp_pr_blocked(env, name, ti):
    code, _, err = mcp(env, name, **ti)
    assert code == 2 and name in err and "draft" in err


@pytest.mark.parametrize("name, ti", [
    ("mcp__github__create_pull_request", {"title": "x", "draft": True}),
    ("mcp__github__update_pull_request", {"pullNumber": 3, "title": "novo"}),
    ("mcp__github__update_pull_request", {"pullNumber": 3, "draft": True}),
    ("mcp__github__get_pull_request", {"pullNumber": 3}),
])
def test_github_mcp_pr_allowed(env, name, ti):
    assert mcp(env, name, **ti) == (0, "", "")


def test_copilot_mcp_create_pr_needs_draft(env):
    raw = {"cwd": str(env), "toolName": "github-mcp-server-create_pull_request",
           "toolArgs": json.dumps({"title": "x"})}
    assert run_hook("pre-tool", json.dumps(raw).encode())[0] == 2
    raw["toolArgs"] = json.dumps({"title": "x", "draft": True})
    assert run_hook("pre-tool", json.dumps(raw).encode())[0] == 0


def test_claude_pre_tool_matcher_covers_mcp_tools():
    import re

    matcher = next(h.claude[1] for h in HOOKS if h.claude and h.claude[0] == "PreToolUse")
    assert re.fullmatch(matcher, "mcp__github__create_pull_request")
    assert re.fullmatch(matcher, "Bash")


LAUNCHER = Path(__file__).resolve().parents[2] / "plugin/hooks/t0-hook.sh"


@pytest.mark.parametrize("with_kb", [True, False])
def test_launcher_exports_pinned_bin_and_workspace_kb_on_session_start(tmp_path, with_kb):
    import subprocess

    ws = tmp_path / "ws"
    (ws / ".t0/bin").mkdir(parents=True)
    (ws / ".t0/workspace.json").write_text('{"schema": 1, "product": "p"}')
    stub = ws / ".t0/bin/t0"
    stub.write_text("#!/bin/sh\nexit 0\n")
    stub.chmod(0o755)
    (ws / "api/src").mkdir(parents=True)
    if with_kb:
        (ws / "kb").mkdir()
    env_file = tmp_path / "env.sh"
    p = subprocess.run(["sh", str(LAUNCHER), "session-start"], cwd=ws / "api/src", input="{}", text=True,
                       capture_output=True, env={"PATH": "/usr/bin:/bin", "CLAUDE_ENV_FILE": str(env_file)})
    assert p.returncode == 0, p.stderr
    (tmp_path / "elsewhere").mkdir()
    seen = subprocess.run(["sh", "-c", f'. "{env_file}"; cd "{tmp_path / "elsewhere"}"; command -v t0; echo "kb=${{T0_KB:-}}"'],
                          text=True, capture_output=True, env={"PATH": "/usr/bin:/bin"}).stdout.splitlines()
    assert seen == [str(stub), f"kb={ws / 'kb' if with_kb else ''}"]
