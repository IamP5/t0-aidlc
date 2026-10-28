import subprocess

import pytest

from t0.cli import main, template_dir

NOW = "2026-10-28T10:00:00-03:00"


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("T0_NOW", NOW)
    monkeypatch.setenv("T0_HANDLE", "ana-exemplo")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("GIT_AUTHOR_NAME", "t")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "t@t")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "t")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "t@t")
    for k in ("T0_FORGE", "T0_BET", "T0_KB", "CI"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.chdir(tmp_path)


def t0(capsys, *argv):
    code = main(list(argv))
    out = capsys.readouterr()
    return code, out.out + out.err


def git(kb, *a):
    return subprocess.run(["git", "-C", str(kb), *a], capture_output=True, text=True, check=True).stdout.strip()


def merge(kb, branch):
    git(kb, "switch", "-q", "main")
    git(kb, "merge", "-q", "--no-ff", branch, "-m", f"aprova {branch}")


needs_template = pytest.mark.skipif(template_dir() is None, reason="okf-template ausente")


@needs_template
def test_rapida_end_to_end_without_a_forge(capsys, tmp_path, monkeypatch):
    code, out = t0(capsys, "kb", "init", "kb")
    assert code == 0 and "KB pronto" in out
    kb = tmp_path / "kb"
    assert t0(capsys, "kb", "init", "kb")[1].count("0 arquivo(s) novos") == 1
    monkeypatch.chdir(kb)
    code, out = t0(capsys, "new", "bet", "--track", "rapida", "Corrigir fuso", "--product", "exemplo", "--repo", "status-bot")
    wt = tmp_path / "kb.wt/bet/BET-003/ana-exemplo"
    assert code == 0 and "branch bet/BET-003/ana-exemplo" in out and "sem forge" in out and f"worktree do branch: {wt}" in out
    assert git(kb, "branch", "--show-current") == "main" and not (kb / "products/exemplo/bets/BET-003").exists()
    code, out = t0(capsys, "gate", "aposta", "BET-003")
    assert code == 1 and "rapida_slice_complete" in out
    sl = next((wt / "products/exemplo/bets/BET-003/slices").glob("01-*.md"))
    sl.write_text(sl.read_text().replace("## Atual\n", "## Atual\n\nsai 07:50\n").replace("## Esperado\n", "## Esperado\n\nsai 08:50\n")
                  .replace("## Não muda\n\n- ", "## Não muda\n\n- o canal")
                  .replace("## Critérios de aceite\n\n- ", "## Critérios de aceite\n\n- sai 08:50")
                  .replace("## Como verificar\n", "## Como verificar\n\npytest -k fuso\n"))
    assert t0(capsys, "gate", "aposta", "BET-003")[0] == 0
    assert t0(capsys, "gate", "aposta", "BET-003", "--ci")[0] == 0
    assert "verified" not in git(kb, "show", "bet/BET-003/ana-exemplo:products/exemplo/bets/BET-003/bet.md")
    merge(kb, "bet/BET-003/ana-exemplo")
    code, out = t0(capsys, "ci", "BET-003", "--pr", "kb#1", "--state", "merged", "--approval", "human:ana-exemplo")
    assert code == 0 and "`verified` de human:ana-exemplo via kb-render" in out
    code, out = t0(capsys, "adr", "accept", "ADR-0001")
    assert code == 0 and "já está `accepted`" in out
    code, out = t0(capsys, "jira", "sync", "--tracker", f"file:{tmp_path / 'jira'}", "--apply")
    assert code == 0 and "jira-linked bet-003-slice-01" in out
    assert t0(capsys, "kb", "push")[0] == 0
    merge(kb, "rec/ana-exemplo/2026-10-28")
    assert t0(capsys, "kb", "render")[0] == 0
    key = git(kb, "show", f"HEAD:{sl.relative_to(wt)}").split("jira: ")[1].split("\n")[0]
    assert t0(capsys, "slice", "dor", key)[0] == 0
    (tmp_path / "work/.audit").mkdir(parents=True)
    (tmp_path / "work/.audit" / f"{key}.tsv").write_text("x")
    monkeypatch.chdir(tmp_path / "work")
    assert t0(capsys, "ci", key, "--kb", str(kb), "--pr", "bot#1", "--state", "ready")[0] == 0
    code, out = t0(capsys, "ci", key, "--kb", str(kb), "--pr", "bot#1", "--state", "merged", "--approval", "human:dani-exemplo")
    assert code == 0 and "bet ship BET-003" in out
    monkeypatch.chdir(kb)
    code, out = t0(capsys, "bet", "ship", "BET-003")
    assert code == 0 and "altera /products/exemplo/product.md" in out
    merge(kb, "bet/BET-003/ana-exemplo")
    code, out = t0(capsys, "kb", "get", "BET-003")
    assert "state: shipped" in out


@needs_template
def test_ritual_open_and_close_on_the_template(capsys, tmp_path, monkeypatch):
    t0(capsys, "kb", "init", "kb")
    monkeypatch.chdir(tmp_path / "kb")
    code, out = t0(capsys, "ritual", "daily-time", "open")
    assert code == 0 and "## Digest" in out
    (tmp_path / "d.md").write_text("## Presentes\n- ana-exemplo\n## Decisões\n- review do #31 (dono: caio-exemplo)\n")
    code, out = t0(capsys, "ritual", "daily-time", "close", "--decisions", str(tmp_path / "d.md"), "--dry-run")
    assert code == 0 and "novo   /rituals/daily-time/2026-10-28.md" in out and git(tmp_path / "kb", "branch", "--show-current") == "main"
    code, out = t0(capsys, "ritual", "demo", "close")
    assert code == 1 and "rodízio" in out


def test_new_help_lists_the_type_fields(capsys):
    with pytest.raises(SystemExit):
        main(["new", "slice", "--help"])
    out = capsys.readouterr().out
    assert "Chaves de Slice" in out and "repo" in out and "obrigatória" in out and "jira" in out and "derivada" in out


def test_no_kb_exits_3_and_log_refuses_secrets(capsys, tmp_path):
    assert t0(capsys, "kb", "check")[0] == 3
    kb = tmp_path / "kb"
    (kb).mkdir()
    (kb / "index.md").write_text('---\nokf_version: "0.2"\n---\n')
    code, out = t0(capsys, "log", "progress", "senha: hunter2abcd", "--kb", str(kb))
    assert code == 1 and "secret" in out and "hunter2" not in out


def test_transcript_redact_dry_run_prints_only_redacted_text(capsys, tmp_path):
    raw = tmp_path / "raw.txt"
    raw.write_text("cpf 529.982.247-25 [fora do registro]x[/fora do registro]")
    code, out = t0(capsys, "transcript", "redact", str(raw), "--dry-run")
    assert code == 0 and "529" not in out and "1 trecho(s) fora do registro" in out
    assert not (tmp_path / "home/.t0/redacted").exists()


def test_hook_and_bet_detect_are_wired(capsys, tmp_path, monkeypatch):
    import io
    import sys

    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b'{"tool_name":"Bash","tool_input":{"command":"git push --force"}}')))
    code, out = t0(capsys, "hook", "pre-tool")
    assert code == 2
    code, out = t0(capsys, "bet", "detect")
    assert code == 0 and "regra: none" in out


@needs_template
def test_t0_kb_reaches_the_workspace_kb_from_any_cwd(capsys, tmp_path, monkeypatch):
    (tmp_path / "ws/.t0").mkdir(parents=True)
    (tmp_path / "ws/.t0/workspace.json").write_text('{"schema": 1, "product": "exemplo"}')
    monkeypatch.chdir(tmp_path / "ws")
    assert t0(capsys, "kb", "init", "kb")[0] == 0
    (tmp_path / "elsewhere").mkdir()
    monkeypatch.chdir(tmp_path / "elsewhere")
    assert t0(capsys, "kb", "find", "--text", "fuso")[0] == 3
    monkeypatch.setenv("T0_KB", str(tmp_path / "ws/kb"))
    code, out = t0(capsys, "new", "idea", "--title", "Alerta de fuso no extrato")
    assert code == 0, out
    idea = out.split(" reservada")[0].split()[-1]
    code, out = t0(capsys, "kb", "get", idea)
    assert code == 0 and "Alerta de fuso" in out, out
    code, out = t0(capsys, "kb", "find", "--text", "review parado")
    assert code == 0 and "/ideas/IDEA-0001.md" in out, out
    assert t0(capsys, "kb", "find", "review parado") == (code, out)
    code, out = t0(capsys, "doctor")
    assert f"workspace: {tmp_path / 'ws'}" in out, out


@needs_template
def test_doctor_warns_on_a_second_kb_clone_and_on_claude_dirs_it_cannot_open(capsys, tmp_path, monkeypatch):
    import json

    home = tmp_path / "home"
    t0(capsys, "kb", "init", "kb")
    shared = tmp_path / "kb"
    ws = tmp_path / "ws/exemplo"
    (ws / ".t0").mkdir(parents=True)
    (ws / ".t0/workspace.json").write_text('{"schema": 1, "product": "exemplo"}')
    t0(capsys, "kb", "init", str(ws / "kb"))
    (home / ".t0").mkdir(parents=True)
    (home / ".t0/config.yaml").write_text(f"kb: {shared}\n")
    (home / ".claude").mkdir()
    (home / ".claude/settings.json").write_text(json.dumps({"permissions": {"additionalDirectories": ["~/ws"]}}))
    monkeypatch.chdir(ws)
    code, out = t0(capsys, "doctor")
    assert f"aviso KB compartilhado: {ws / 'kb'} é" in out and f"`ln -s {shared.resolve()} {ws / 'kb'}`" in out
    assert "aviso Claude Code additionalDirectories" in out and json.dumps([str((tmp_path / "ws").resolve())]) in out
    subprocess.run(["rm", "-rf", str(ws / "kb")], check=True)
    (ws / "kb").symlink_to(shared)
    code, out = t0(capsys, "doctor")
    need = [str((tmp_path / "ws").resolve()), str(shared.resolve()), str((tmp_path / "kb.wt").resolve())]
    assert json.dumps(need) in out, out
    assert "aviso Claude Code instructionFiles" in out
    (home / ".claude/settings.json").write_text(json.dumps(
        {"permissions": {"additionalDirectories": [str((tmp_path / "ws").resolve()), str(tmp_path.resolve())]},
         "pluginConfigs": {"cc-plugin-agents-md@builtin": {"options": {"instructionFiles": "claude-md-and-agents-md"}}}}))
    code, out = t0(capsys, "doctor")
    assert f"ok    KB compartilhado: {ws / 'kb'} -> {shared.resolve()}" in out
    assert "ok    Claude Code instructionFiles" in out
    assert "ok    Claude Code additionalDirectories" in out and "aviso" not in out
