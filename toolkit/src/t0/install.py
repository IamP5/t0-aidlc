"""`t0 install` and `t0 ws init <produto>`: from zero to a working setup with one command.

Same shape as setup.py: a plan of typed actions read from the machine, an apply that is the only effect,
`--check` prints what is pending (exit 1 if anything is), and a second run finds nothing to do.

  t0 install    ~/.t0/config.yaml (handle, kb, kb_remote, ws_root, forge), the shared KB clone, the Claude
                Code plugin (marketplace add + install, or with --link a symlink ~/.claude/skills/t0 -> the
                clone's plugin/, which Claude Code loads as t0@skills-dir with no cache copy),
                ~/.claude/settings.json (additionalDirectories and instructionFiles), then `ws init` for each
                product the person works in
  t0 ws init    <ws_root>/<p>/: kb -> the shared clone, one clone per manifest repo (a failed clone goes to
                `absent`), .t0/workspace.json, AGENTS.md (the card), .t0/env.sh

ws init lives here, not in ws.py: it is the effectful converge with install's action vocabulary and applier,
while ws.py stays the read side (manifest, locate, bet detection) that hooks and the MCP server import.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml

from . import setup, ws
from .kb import KB, _is_kb, handle as default_handle
from .setup import Link, WriteFile
from .write import worktree_root

MARKETPLACE = "t0-aidlc"
PLUGIN = "t0"
AGENTS_MD_PLUGINS = ("cc-plugin-agents-md@builtin", "agents-md@builtin")   # id since v2.1.285, id before it
INSTRUCTION_FILES = "claude-md-and-agents-md"


@dataclass(frozen=True)
class Clone:
    url: str
    dest: Path


@dataclass(frozen=True)
class Run:
    argv: tuple[str, ...]


@dataclass(frozen=True)
class Skip:
    reason_pt: str


Action = WriteFile | Link | Clone | Run | Skip


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(argv), capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


@dataclass(frozen=True)
class Host:
    """The outside world plan reads and apply runs. Tests swap `claude` out; git stays real."""
    which: Callable[[str], str | None] = shutil.which
    run: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] = _run


def pending(actions: Sequence[Action]) -> list[Action]:
    return [a for a in actions if not isinstance(a, Skip)]


def describe(a: Action) -> str:
    if isinstance(a, WriteFile):
        return f"escrever: {a.path}"
    if isinstance(a, Link):
        return f"ligar: {a.path} -> {a.target}"
    if isinstance(a, Clone):
        return f"clonar: {a.url} -> {a.dest}"
    if isinstance(a, Run):
        return "rodar: " + shlex.join(a.argv)
    return f"pulado: {a.reason_pt}"


def apply(actions: Sequence[Action], host: Host) -> list[str]:
    """Runs every action; returns one line per failed Clone or Run (the rest still run)."""
    failed = []
    for a in actions:
        if isinstance(a, (WriteFile, Link)):
            setup.apply(Path("/"), (a,))
        elif isinstance(a, Clone):
            a.dest.parent.mkdir(parents=True, exist_ok=True)
            p = host.run(("git", "clone", "--quiet", a.url, str(a.dest)))
            if p.returncode != 0:
                failed.append(f"clonar {a.url}: {_last_line(p.stderr)}")
        elif isinstance(a, Run):
            p = host.run(a.argv)
            if p.returncode != 0:
                failed.append(f"{shlex.join(a.argv)}: {_last_line(p.stderr or p.stdout)}")
    return failed


def _last_line(s: str) -> str:
    lines = [l for l in s.strip().splitlines() if l.strip()]
    return lines[-1] if lines else "falhou"


def _print(actions: Sequence[Action], check: bool) -> None:
    for a in actions:
        print(("pendente " if check and not isinstance(a, Skip) else "") + describe(a))


# ------------------------------------------------------------------ files read at the boundary


def config_path() -> Path:
    return Path.home() / ".t0/config.yaml"


def read_config() -> dict[str, Any]:
    p = config_path()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.is_file() else None
    return data if isinstance(data, dict) else {}


def _abs(p: str | Path) -> Path:
    return Path(p).expanduser().resolve()


def _want_text(path: Path, text: str) -> list[Action]:
    old = path.read_text(encoding="utf-8") if path.is_file() else None
    return [] if old == text else [WriteFile(str(path), text)]


# ------------------------------------------------------------------ install: pure merges


def forge_from_remote(remote: str | None) -> str | None:
    """`github:<owner>/<repo>` from a git@host:o/r.git or https://host/o/r remote; None for a local path."""
    if not remote or remote.startswith(("/", "file:", ".", "~")):
        return None
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", remote)
    return f"github:{m.group(1)}/{m.group(2)}" if m else None


def merged_config(old: dict[str, Any], *, handle: str, kb: Path, kb_remote: str | None, ws_root: Path,
                  forge: str | None) -> dict[str, Any]:
    new = {**old, "handle": handle, "kb": str(kb), "ws_root": str(ws_root)}
    if kb_remote:
        new["kb_remote"] = kb_remote
    if forge and not old.get("forge"):
        new["forge"] = forge
    return new


def _covered(d: Path, have: Sequence[Any]) -> bool:
    return any(isinstance(h, str) and h.startswith("/") and (Path(h) == d or Path(h) in d.parents) for h in have)


def instruction_files(settings: dict[str, Any]) -> str | None:
    pc = settings.get("pluginConfigs")
    for pid in AGENTS_MD_PLUGINS:
        entry = pc.get(pid) if isinstance(pc, dict) else None
        opts = entry.get("options") if isinstance(entry, dict) else None
        if isinstance(opts, dict) and opts.get("instructionFiles"):
            return str(opts["instructionFiles"])
    return None


def merged_settings(old: dict[str, Any], dirs: Sequence[Path]) -> dict[str, Any]:
    """additionalDirectories gains each absolute dir not already covered; instructionFiles is set only when
    neither plugin id has one (a value the person chose stays). Every other key is kept."""
    perms = dict(old.get("permissions") or {})
    have = list(perms.get("additionalDirectories") or [])
    for d in dirs:
        if not _covered(d, have):
            have.append(str(d))
    new = {**old, "permissions": {**perms, "additionalDirectories": have}}
    if instruction_files(old) is None:
        pc = dict(old.get("pluginConfigs") or {})
        entry = dict(pc.get(AGENTS_MD_PLUGINS[0]) or {})
        pc[AGENTS_MD_PLUGINS[0]] = {**entry, "options": {**(entry.get("options") or {}), "instructionFiles": INSTRUCTION_FILES}}
        new["pluginConfigs"] = pc
    return new


# ------------------------------------------------------------------ install: plan


@dataclass(frozen=True)
class InstallArgs:
    kb: str | None = None
    handle: str | None = None
    root: str | None = None
    products: tuple[str, ...] = ()
    plugin_source: str | None = None
    link: bool = False


@dataclass(frozen=True)
class KBChoice:
    path: Path
    remote: str | None
    clone: Clone | None


class Refused(Exception): ...


def _origin(repo: Path, host: Host) -> str | None:
    p = host.run(("git", "-C", str(repo), "remote", "get-url", "origin"))
    return (p.stdout.strip() or None) if p.returncode == 0 else None


def choose_kb(flag: str | None, cfg: dict[str, Any], host: Host) -> KBChoice:
    """A local KB dir passed in `--kb` wins; else a valid config `kb` stays; else clone `--kb` (or the config
    `kb_remote`) into the config `kb` path or ~/kb."""
    cfg_kb = _abs(cfg["kb"]) if cfg.get("kb") else None
    if flag and Path(flag).expanduser().is_dir() and _is_kb(Path(flag).expanduser()):
        local = _abs(flag)
        return KBChoice(local, _origin(local, host) or cfg.get("kb_remote"), None)
    url = str(_abs(flag)) if flag and Path(flag).expanduser().exists() else flag
    if cfg_kb and _is_kb(cfg_kb):
        return KBChoice(cfg_kb, cfg.get("kb_remote") or url, None)
    url = url or cfg.get("kb_remote")
    dest = cfg_kb or _abs(Path.home() / "kb")
    if not url:
        if _is_kb(dest):
            return KBChoice(dest, _origin(dest, host), None)
        raise Refused("nenhum KB encontrado: crie um com `t0 kb init <pasta>` (setup do time) ou passe --kb <remote ou pasta>")
    if dest.exists() and any(dest.iterdir()):
        raise Refused(f"{dest} existe e não é um KB; mova a pasta ou passe --kb <pasta do KB>")
    return KBChoice(dest, url, Clone(url, dest))


def marketplace_name(source: str) -> str:
    f = Path(source).expanduser() / ".claude-plugin/marketplace.json"
    try:
        return str(json.loads(f.read_text(encoding="utf-8"))["name"])
    except (OSError, ValueError, KeyError, TypeError):
        return MARKETPLACE


def skills_link() -> Path:
    return Path.home() / ".claude/skills" / PLUGIN


def _link_actions(plugin_dir: Path, ref: str, host: Host) -> list[Action]:
    dest = skills_link()
    out: list[Action] = []
    if dest.is_symlink():
        if dest.resolve() != plugin_dir.resolve():
            out.append(Link(str(dest), str(plugin_dir)))
    elif dest.exists():
        return [Skip(f"{dest} existe e não é um link; mova a pasta e rode de novo")]
    else:
        out.append(Link(str(dest), str(plugin_dir)))
    if host.which("claude") is not None and ref in host.run(("claude", "plugin", "list")).stdout:
        out.append(Run(("claude", "plugin", "uninstall", ref)))
    return out


def plugin_actions(source: str | None, host: Host, link: bool = False) -> list[Action]:
    if not source:
        return [Skip("plugin: passe --plugin-source <pasta do t0-aidlc ou dono/repo> (o install.sh já passa)")]
    name = marketplace_name(source)
    ref = f"{PLUGIN}@{name}"
    plugin_dir = _abs(source) / "plugin"
    shown = str(plugin_dir) if plugin_dir.is_dir() else f"{source} (pasta plugin/)"
    out: list[Action] = []
    if link:
        if not (plugin_dir / ".claude-plugin/plugin.json").is_file():
            return [Skip(f"--link precisa de um clone local do t0-aidlc; {plugin_dir} não tem .claude-plugin/plugin.json")]
        out += _link_actions(plugin_dir, ref, host)
    elif host.which("claude") is None:
        out.append(Skip(f"Claude Code: `claude` fora do PATH; depois de instalar, rode "
                        f"`claude plugin marketplace add {source}` e `claude plugin install {ref}`"))
    else:
        if name not in host.run(("claude", "plugin", "marketplace", "list")).stdout:
            out.append(Run(("claude", "plugin", "marketplace", "add", source)))
        if ref not in host.run(("claude", "plugin", "list")).stdout:
            out.append(Run(("claude", "plugin", "install", ref)))
        if skills_link().is_symlink():
            out.append(Skip(f"{skills_link()} também carrega o plugin (t0@skills-dir); apague o link para não carregar duas vezes"))
    out.append(Skip(f"Copilot CLI: à mão, `copilot plugin install {shown}` (lê o formato Claude; não verificado)"))
    out.append(Skip(f"Kiro: à mão, importe {shown} como power (Agent Plugins 1.0; não verificado)"))
    return out


def settings_actions(dirs: Sequence[Path], host: Host) -> list[Action]:
    claude = Path.home() / ".claude"
    if not claude.is_dir() and host.which("claude") is None:
        return [Skip("~/.claude/settings.json: sem Claude Code nesta máquina")]
    path = claude / "settings.json"
    try:
        old = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except json.JSONDecodeError as e:
        return [Skip(f"{path}: JSON inválido ({e.msg}, linha {e.lineno}); corrija à mão e rode de novo")]
    if not isinstance(old, dict) or not isinstance(old.get("permissions") or {}, dict) \
            or not isinstance(old.get("pluginConfigs") or {}, dict):
        return [Skip(f"{path}: formato inesperado; corrija à mão e rode de novo")]
    new = merged_settings(old, dirs)
    out: list[Action] = [] if new == old else [WriteFile(str(path), json.dumps(new, indent=2, ensure_ascii=False) + "\n")]
    current = instruction_files(new)
    if current != INSTRUCTION_FILES:
        out.append(Skip(f"instructionFiles já é `{current}`; mantido. Com `CLAUDE.md` nos repos, o AGENTS.md do "
                        f"workspace só carrega com `{INSTRUCTION_FILES}`"))
    return out


@dataclass(frozen=True)
class InstallPlan:
    kb: KBChoice
    ws_root: Path
    handle: str
    actions: tuple[Action, ...]


def plan_install(args: InstallArgs, host: Host) -> InstallPlan:
    cfg = read_config()
    kbc = choose_kb(args.kb, cfg, host)
    ws_root = _abs(args.root or cfg.get("ws_root") or Path.home() / "ws")
    handle = args.handle or (str(cfg["handle"]) if cfg.get("handle") else default_handle())
    forge = forge_from_remote(kbc.remote) if host.which("gh") else None
    new_cfg = merged_config(cfg, handle=handle, kb=kbc.path, kb_remote=kbc.remote, ws_root=ws_root, forge=forge)
    actions: list[Action] = []
    if new_cfg != cfg or not config_path().is_file():
        actions.append(WriteFile(str(config_path()), yaml.safe_dump(new_cfg, sort_keys=False, allow_unicode=True)))
    if kbc.clone:
        actions.append(kbc.clone)
    actions += plugin_actions(args.plugin_source, host, args.link)
    actions += settings_actions((ws_root, kbc.path, worktree_root(kbc.path)), host)
    return InstallPlan(kbc, ws_root, handle, tuple(actions))


def products_of(kb_dir: Path) -> list[str]:
    return sorted(p.parent.name for p in (kb_dir / "products").glob("*/workspace.md"))


def person_pods(kb_dir: Path, handle: str) -> list[str]:
    f = kb_dir / "team/people" / f"{handle}.md"
    try:
        pods = ws._frontmatter(f.read_text(encoding="utf-8")).get("pods") if f.is_file() else None
    except ws.ManifestError:
        return []
    return [str(p) for p in pods or ()]


def run_install(args: InstallArgs, *, check: bool = False, host: Host | None = None) -> int:
    host = host or Host()
    try:
        p = plan_install(args, host)
    except Refused as e:
        print(f"t0 install: recusado: {e}", file=sys.stderr)
        return 1
    _print(p.actions, check)
    failed = [] if check else apply(p.actions, host)
    if not check and not _is_kb(p.kb.path):
        for f in failed:
            print(f"falhou: {f}", file=sys.stderr)
        return 1
    kb_ready = _is_kb(p.kb.path)
    todo = bool(pending(p.actions))
    shown: list[str] = []
    if not kb_ready:
        print("pendente produtos: dependem do KB clonado")
    else:
        products = list(args.products)
        if not products:
            known = products_of(p.kb.path)
            pods = person_pods(p.kb.path, p.handle)
            products = [x for x in pods if x in known]
            for x in pods:
                if x not in known:
                    print(f"pulado: pod `{x}` sem /products/{x}/workspace.md no KB")
            if not pods:
                print(f"pulado: nenhum produto; rode `t0 ws init <produto>` (no KB: {', '.join(known) or 'nenhum'}) "
                      f"ou ponha `pods: [<produto>]` em team/people/{p.handle}.md")
        for prod in products:
            code = ws_init(prod, root=p.ws_root, kb_dir=p.kb.path, check=check, host=host)
            todo |= code == 1 and check
            if code == 2:
                return 1
            shown.append(prod)
    for f in failed:
        print(f"falhou: {f}", file=sys.stderr)
    if check:
        return 1 if todo else 0
    print()
    from . import cli

    cli.cmd_doctor(argparse.Namespace(kb=str(p.kb.path)))
    for prod in shown:
        print(f"próximo passo: abra {p.ws_root / prod} e rode /t0:t0")
    return 1 if failed else 0


# ------------------------------------------------------------------ ws init


_STAMP_AT = re.compile(r"(<!-- t0:card [^>]*?) at=\S*")


def _same_card(old: str | None, new: str) -> bool:
    """The card stamp carries the render time; a refresh with nothing else new is not a change."""
    return old is not None and _STAMP_AT.sub(r"\1", old) == _STAMP_AT.sub(r"\1", new)


def clone_actions(m: ws.Manifest, ws_dir: Path) -> list[Action]:
    out: list[Action] = []
    for r in m.repos:
        dest = ws_dir / r.name
        if (dest / ".git").exists():
            continue
        if not r.url:
            out.append(Skip(f"{r.name}: sem url no manifesto"))
        elif dest.exists() and any(dest.iterdir()):
            out.append(Skip(f"{dest} existe e não é um clone git; deixei como está"))
        else:
            out.append(Clone(r.url, dest))
    return out


def file_actions(kb: KB, m: ws.Manifest, ws_dir: Path) -> list[Action]:
    out: list[Action] = []
    link = ws_dir / "kb"
    if link.is_symlink():
        if Path(os.readlink(link)) != kb.root:
            out.append(Link(str(link), str(kb.root)))
    elif link.exists():
        out.append(Skip(f"{link} é uma pasta, não o link para {kb.root}; mova a pasta e rode de novo"))
    else:
        out.append(Link(str(link), str(kb.root)))

    absent = sorted(r.name for r in m.repos if not (ws_dir / r.name / ".git").exists())
    wj = ws_dir / ws.WORKSPACE_JSON
    try:
        old = json.loads(wj.read_text(encoding="utf-8")) if wj.is_file() else {}
    except json.JSONDecodeError:
        old = {}
    data = {**(old if isinstance(old, dict) else {}), "product": m.product, "absent": absent}
    out += _want_text(wj, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    from .context import CardFormat, render as render_card

    w = ws.Workspace(ws_dir, m.product, m.repos, frozenset(absent), data.get("isolated_bet"), m.default_branch)
    card = render_card(kb.view(), w.facts(), ws.detect_bet(kb, ws_dir), CardFormat.AGENTS, now=kb.now)
    agents = ws_dir / "AGENTS.md"
    if card is not None and not _same_card(agents.read_text(encoding="utf-8") if agents.is_file() else None, card.text):
        out.append(WriteFile(str(agents), card.text))

    out += _want_text(ws_dir / ".t0/env.sh", f"export COPILOT_CUSTOM_INSTRUCTIONS_DIRS={shlex.quote(str(ws_dir))}\n")

    for name in absent:
        out.append(Skip(f"ausente: {name} (sem acesso? peça ao dono do repo e rode de novo)"))
    bare = [r.name for r in m.repos if r.name not in absent
            and setup.BEGIN not in ((ws_dir / r.name / "AGENTS.md").read_text(encoding="utf-8")
                                    if (ws_dir / r.name / "AGENTS.md").is_file() else "")]
    if bare:
        out.append(Skip(f"sem bloco t0 no AGENTS.md: {', '.join(bare)} (rode `t0 setup` no repo e commite)"))
    return out


def resolve_kb_dir() -> Path | None:
    cfg = read_config()
    if cfg.get("kb") and _is_kb(_abs(cfg["kb"])):
        return _abs(cfg["kb"])
    from .kb import locate

    found = locate()
    return found.resolve() if found else None


def ws_init(product: str, *, root: Path | None = None, kb_dir: Path | None = None, check: bool = False,
            host: Host | None = None) -> int:
    """Exit 0 done (or nothing to do), 1 pending (with --check), 2 refused."""
    host = host or Host()
    kb_dir = kb_dir or resolve_kb_dir()
    if kb_dir is None:
        print("t0 ws init: recusado: KB não encontrado; rode `t0 install --kb <remote>` antes", file=sys.stderr)
        return 2
    known = products_of(kb_dir)
    if product not in known:
        print(f"t0 ws init: recusado: produto `{product}` não tem /products/{product}/workspace.md no KB. "
              f"Disponíveis: {', '.join(known) or 'nenhum'}", file=sys.stderr)
        return 2
    try:
        m = ws.read_manifest(kb_dir, product)
    except ws.ManifestError as e:
        print(f"t0 ws init: recusado: {e}", file=sys.stderr)
        return 2
    ws_dir = _abs(root or read_config().get("ws_root") or Path.home() / "ws") / product
    print(f"workspace {product}: {ws_dir}")
    clones = clone_actions(m, ws_dir)
    _print(clones, check)
    if not check:
        for f in apply(clones, host):
            print(f"falhou: {f}")
    files = file_actions(KB.open(kb_dir), m, ws_dir)
    _print(files, check)
    if not check:
        apply(files, host)
    return 1 if check and pending([*clones, *files]) else 0
