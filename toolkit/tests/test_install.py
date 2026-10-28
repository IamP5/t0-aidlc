import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from t0 import cli, install
from t0.install import Host, InstallArgs, run_install, ws_init

REPO = Path(__file__).resolve().parents[2]


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True)


def bare_repo(tmp, name):
    src = tmp / "src" / name
    src.mkdir(parents=True)
    git(src, "init", "-q", "-b", "main")
    (src / "README.md").write_text(name)
    git(src, "add", "-A")
    git(src, "commit", "-qm", "init")
    bare = tmp / "remotes" / f"{name}.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(src), str(bare)], check=True)
    return bare


@pytest.fixture
def env(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("T0_HANDLE", raising=False)
    monkeypatch.delenv("T0_KB", raising=False)
    monkeypatch.delenv("T0_BET", raising=False)
    monkeypatch.chdir(tmp_path)
    for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t"}.items():
        monkeypatch.setenv(k, v)
    return tmp_path


def make_kb(tmp, repos):
    kb = tmp / "team-kb"
    assert cli.main(["kb", "init", str(kb)]) == 0
    f = kb / "products/exemplo/workspace.md"
    text = f.read_text()
    head, rest = text.split("  repos:\n", 1)
    tail = rest[rest.index("  groups:"):]
    lines = "".join(f"    - {{name: {n}, url: \"{u}\", role: \"{n}\", kind: service, optional: false, tier: 1, depends_on: []}}\n"
                    for n, u in repos)
    f.write_text(head + "  repos:\n" + lines + tail)
    git(kb, "commit", "-qam", "manifesto local")
    return kb


class FakeClaude:
    """`claude` on PATH that records argv and remembers what was added; everything else runs for real."""

    def __init__(self, present=True):
        self.present = present
        self.calls = []
        self.state = set()

    def which(self, name):
        if name == "claude":
            return "/fake/claude" if self.present else None
        if name == "gh":
            return None
        return shutil.which(name)

    def run(self, argv):
        argv = tuple(argv)
        if argv[0] != "claude":
            return install._run(argv)
        self.calls.append(argv)
        if argv[1:4] == ("plugin", "marketplace", "add"):
            self.state.add("t0-aidlc")
        elif argv[1:3] == ("plugin", "install"):
            self.state.add(argv[3])
        return subprocess.CompletedProcess(argv, 0, "\n".join(sorted(self.state)), "")

    def host(self):
        return Host(which=self.which, run=self.run)


def snapshot(root):
    return {str(p.relative_to(root)): (os.readlink(p) if p.is_symlink() else p.read_text(errors="replace"))
            for p in sorted(root.rglob("*")) if (p.is_symlink() or p.is_file()) and ".git" not in p.parts}


def test_install_from_empty_home(env, capsys):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot"))])
    home = Path(os.environ["HOME"])
    fake = FakeClaude(present=False)
    assert run_install(InstallArgs(kb=str(kb), products=("exemplo",), plugin_source=str(REPO)), host=fake.host()) == 0
    out = capsys.readouterr().out
    cfg = yaml.safe_load((home / ".t0/config.yaml").read_text())
    assert cfg["kb"] == str(kb.resolve()) and cfg["ws_root"] == str((home / "ws").resolve())
    assert cfg["handle"] and "forge" not in cfg
    assert "`claude` fora do PATH" in out and "claude plugin install t0@t0-aidlc" in out
    assert not (home / ".claude").exists()
    w = home / "ws/exemplo"
    assert (w / "status-bot/.git").is_dir() and (w / "status-bot/README.md").read_text() == "status-bot"
    assert os.readlink(w / "kb") == str(kb.resolve())
    assert json.loads((w / ".t0/workspace.json").read_text()) == {"product": "exemplo", "absent": []}
    assert "<!-- t0:card" in (w / "AGENTS.md").read_text() and "status-bot" in (w / "AGENTS.md").read_text()
    assert (w / ".t0/env.sh").read_text() == f"export COPILOT_CUSTOM_INSTRUCTIONS_DIRS={w.resolve()}\n"
    assert "sem bloco t0 no AGENTS.md: status-bot" in out
    assert f"próximo passo: abra {w.resolve()}" in out


def test_second_run_is_a_no_op(env, capsys):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot"))])
    home = Path(os.environ["HOME"])
    (home / ".claude").mkdir()
    fake = FakeClaude()
    args = InstallArgs(kb=str(kb), products=("exemplo",), plugin_source=str(REPO))
    assert run_install(args, host=fake.host()) == 0
    before = snapshot(home)
    capsys.readouterr()
    assert run_install(args, check=True, host=fake.host()) == 0
    assert "pendente" not in capsys.readouterr().out
    assert run_install(args, host=fake.host()) == 0
    assert snapshot(home) == before


def test_check_reports_without_writing(env, capsys):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot"))])
    home = Path(os.environ["HOME"])
    assert run_install(InstallArgs(kb=str(kb), products=("exemplo",)), check=True, host=FakeClaude(False).host()) == 1
    out = capsys.readouterr().out
    assert "pendente escrever:" in out and "pendente clonar:" in out
    assert list(home.iterdir()) == []


def test_config_merge_keeps_unknown_keys_and_forge(env):
    kb = make_kb(env, [])
    home = Path(os.environ["HOME"])
    (home / ".t0").mkdir()
    (home / ".t0/config.yaml").write_text("team: payments\nforge: file:/tmp/prs\nhandle: ana-exemplo\n")
    fake = FakeClaude(False)
    assert run_install(InstallArgs(kb=str(kb)), host=fake.host()) == 0
    cfg = yaml.safe_load((home / ".t0/config.yaml").read_text())
    assert cfg["team"] == "payments" and cfg["forge"] == "file:/tmp/prs" and cfg["handle"] == "ana-exemplo"
    assert cfg["kb"] == str(kb.resolve())


def test_forge_comes_from_a_github_remote_only():
    assert install.forge_from_remote("git@github.example.bank:t0/t0-kb.git") == "github:t0/t0-kb"
    assert install.forge_from_remote("https://github.com/t0/t0-kb") == "github:t0/t0-kb"
    assert install.forge_from_remote("/srv/git/t0-kb.git") is None


def test_settings_merge_keeps_other_keys_and_writes_absolute_paths(env):
    kb = make_kb(env, [])
    home = Path(os.environ["HOME"])
    (home / ".claude").mkdir()
    old = {"model": "opus", "permissions": {"allow": ["Bash(ls)"], "additionalDirectories": ["/opt/other", "~/x"]},
           "pluginConfigs": {"other@m": {"options": {"a": 1}}}}
    (home / ".claude/settings.json").write_text(json.dumps(old))
    assert run_install(InstallArgs(kb=str(kb)), host=FakeClaude(False).host()) == 0
    text = (home / ".claude/settings.json").read_text()
    s = json.loads(text)
    assert s["model"] == "opus" and s["permissions"]["allow"] == ["Bash(ls)"]
    assert s["pluginConfigs"]["other@m"] == {"options": {"a": 1}}
    assert s["pluginConfigs"]["cc-plugin-agents-md@builtin"]["options"]["instructionFiles"] == "claude-md-and-agents-md"
    kbr = kb.resolve()
    assert s["permissions"]["additionalDirectories"] == [
        "/opt/other", "~/x", str((home / "ws").resolve()), str(kbr), str(kbr.with_name(kbr.name + ".wt"))]
    assert text.count("~") == 1


def test_settings_keep_a_chosen_instruction_files_value(env, capsys):
    kb = make_kb(env, [])
    home = Path(os.environ["HOME"])
    (home / ".claude").mkdir()
    old = {"pluginConfigs": {"agents-md@builtin": {"options": {"instructionFiles": "claude-md"}}}}
    (home / ".claude/settings.json").write_text(json.dumps(old))
    assert run_install(InstallArgs(kb=str(kb)), host=FakeClaude(False).host()) == 0
    s = json.loads((home / ".claude/settings.json").read_text())
    assert s["pluginConfigs"] == old["pluginConfigs"]
    assert "instructionFiles já é `claude-md`" in capsys.readouterr().out


def test_claude_on_path_adds_marketplace_and_installs_once(env):
    kb = make_kb(env, [])
    fake = FakeClaude()
    args = InstallArgs(kb=str(kb), plugin_source=str(REPO))
    assert run_install(args, host=fake.host()) == 0
    changes = [c for c in fake.calls if c[2:3] != ("list",) and c[3:4] != ("list",)]
    assert changes == [("claude", "plugin", "marketplace", "add", str(REPO)), ("claude", "plugin", "install", "t0@t0-aidlc")]
    fake.calls.clear()
    assert run_install(args, host=fake.host()) == 0
    assert all("list" in c for c in fake.calls)


def test_ws_init_bad_url_lands_in_absent_and_rerun_retries_only_it(env, capsys):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot")), ("ledger", env / "remotes/nao-existe.git")])
    root = env / "ws"
    clones = []

    def run(argv):
        if argv[:2] == ("git", "clone"):
            clones.append(argv[-2])
        return install._run(argv)

    host = Host(run=run)
    assert ws_init("exemplo", root=root, kb_dir=kb, host=host) == 0
    w = root / "exemplo"
    assert (w / "status-bot/.git").is_dir() and not (w / "ledger").exists()
    assert json.loads((w / ".t0/workspace.json").read_text())["absent"] == ["ledger"]
    assert "ausente: ledger" in capsys.readouterr().out
    clones.clear()
    assert ws_init("exemplo", root=root, kb_dir=kb, host=host) == 0
    assert clones == [str(env / "remotes/nao-existe.git")]


def test_ws_init_rerun_clones_nothing_and_keeps_files(env):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot"))])
    root = env / "ws"
    clones = []

    def run(argv):
        if argv[:2] == ("git", "clone"):
            clones.append(argv)
        return install._run(argv)

    assert ws_init("exemplo", root=root, kb_dir=kb, host=Host(run=run)) == 0
    before = snapshot(root)
    clones.clear()
    assert ws_init("exemplo", root=root, kb_dir=kb, check=True, host=Host(run=run)) == 0
    assert ws_init("exemplo", root=root, kb_dir=kb, host=Host(run=run)) == 0
    assert clones == [] and snapshot(root) == before


def test_ws_init_refuses_unknown_product_listing_known(env, capsys):
    kb = make_kb(env, [])
    assert cli.main(["ws", "init", "nope", "--kb", str(kb), "--root", str(env / "ws")]) == 2
    err = capsys.readouterr().err
    assert "`nope`" in err and "exemplo" in err and "paco" in err
    assert not (env / "ws").exists()


def test_install_refuses_without_any_kb(env, capsys):
    assert run_install(InstallArgs(), host=FakeClaude(False).host()) == 1
    assert "t0 kb init <pasta>" in capsys.readouterr().err
    assert not (Path(os.environ["HOME"]) / ".t0").exists()


def test_products_default_to_the_person_pods(env):
    kb = make_kb(env, [("status-bot", bare_repo(env, "status-bot"))])
    home = Path(os.environ["HOME"])
    assert run_install(InstallArgs(kb=str(kb), handle="ana-exemplo"), host=FakeClaude(False).host()) == 0
    assert (home / "ws/exemplo/status-bot/.git").is_dir()
