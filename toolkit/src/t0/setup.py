"""`t0 setup [--repo DIR] [--check]`: wires a product repo for the three agent tools.

It converges the repo to one end state, so a second run changes nothing:
  AGENTS.md                 a pointer block between BEGIN/END, the rest of the file untouched
  .claude/settings.json     the gen Claude hook map merged in (other hooks and keys kept)
  .github/hooks/t0.json     the gen Copilot hook file
  .kiro/hooks/t0.json       the gen Kiro hook file
  <tool>/skills/verify-*    relative symlinks to each .t0/skills/verify-*; stale ones removed
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import gen

BEGIN = "<!-- t0:begin (gerado por `t0 setup`; edite fora deste bloco) -->"
END = "<!-- t0:end -->"

POINTER = f"""{BEGIN}
## t0

Este repo é trabalhado pelo fluxo t0. O conhecimento do produto (bets, specs, slices, ADRs) mora no KB, não aqui.

- Antes de trabalhar, leia o card t0 do workspace (`AGENTS.md` na raiz do workspace) ou peça `kb_context` ao MCP `t0-kb`. Sem KB disponível, pare e diga "KB indisponível".
- Fluxo e travas: skill `t0`. Todo PR nasce e fica em draft; marcar pronto e fazer merge são do humano ou do CI.
- Provar comportamento no app: `.t0/skills/verify-<app>/SKILL.md`. Sem ela, rode a skill `verify-setup`.
{END}
"""

SKILLS_SRC = ".t0/skills"
SKILL_DIRS = (
    ".claude/skills",
    ".github/skills",   # Copilot lê .github/skills pelas docs; seguir link simbólico (não verificado)
    ".kiro/skills",     # Kiro lê .kiro/skills pelas docs; seguir link simbólico (não verificado)
)
CLAUDE_SETTINGS = ".claude/settings.json"
HOOK_FILES = {".github/hooks/t0.json": gen.copilot_hooks, ".kiro/hooks/t0.json": gen.kiro_hooks}


@dataclass(frozen=True)
class WriteFile:
    path: str
    text: str


@dataclass(frozen=True)
class Link:
    path: str
    target: str                 # relative to the link's directory


@dataclass(frozen=True)
class Unlink:
    path: str


@dataclass(frozen=True)
class Conflict:
    path: str
    reason_pt: str


Action = WriteFile | Link | Unlink


@dataclass(frozen=True)
class SetupPlan:
    actions: tuple[Action, ...]     # only the changes; empty means the repo is already set up
    conflicts: tuple[Conflict, ...]


# ------------------------------------------------------------------ pure renderers


def agents_md(old: str | None) -> str:
    if old is None:
        return POINTER
    if BEGIN in old and END in old:
        head, rest = old.split(BEGIN, 1)
        tail = rest.split(END, 1)[1].removeprefix("\n")
        return head + POINTER + tail
    return old.rstrip("\n") + "\n\n" + POINTER


def _is_t0_group(group: Any) -> bool:
    hooks = group.get("hooks") if isinstance(group, dict) else None
    return bool(hooks) and all(isinstance(h, dict) and str(h.get("command", "")).startswith("t0 hook ")
                               for h in hooks)


def claude_settings(old: dict[str, Any]) -> dict[str, Any]:
    """Drops every matcher group made only of `t0 hook` commands, then appends the gen map."""
    ours = gen.claude_hook_events()
    hooks: dict[str, Any] = dict(old.get("hooks") or {})
    for event in [*hooks, *(e for e in ours if e not in hooks)]:
        groups = [g for g in hooks.get(event) or [] if not _is_t0_group(g)] + ours.get(event, [])
        if groups:
            hooks[event] = groups
        else:
            hooks.pop(event, None)
    return {**old, "hooks": hooks}


# ------------------------------------------------------------------ plan (reads the repo, writes nothing)


def _read(p: Path) -> str | None:
    return p.read_text(encoding="utf-8") if p.is_file() else None


def plan(repo: Path) -> SetupPlan:
    actions: list[Action] = []
    conflicts: list[Conflict] = []

    def want_file(rel: str, text: str) -> None:
        if _read(repo / rel) != text:
            actions.append(WriteFile(rel, text))

    want_file("AGENTS.md", agents_md(_read(repo / "AGENTS.md")))

    raw = _read(repo / CLAUDE_SETTINGS)
    try:
        settings = json.loads(raw) if raw else {}
    except json.JSONDecodeError as e:
        settings = None
        conflicts.append(Conflict(CLAUDE_SETTINGS, f"JSON inválido ({e.msg}, linha {e.lineno}); corrija à mão"))
    if settings is not None:
        if isinstance(settings, dict):
            want_file(CLAUDE_SETTINGS, json.dumps(claude_settings(settings), indent=2, ensure_ascii=False) + "\n")
        else:
            conflicts.append(Conflict(CLAUDE_SETTINGS, "não é um objeto JSON; corrija à mão"))

    for rel, render in HOOK_FILES.items():
        want_file(rel, render())

    src = repo / SKILLS_SRC
    skills = sorted(p.name for p in src.glob("verify-*") if p.is_dir()) if src.is_dir() else []
    for d in SKILL_DIRS:
        for name in skills:
            rel = f"{d}/{name}"
            target = os.path.relpath(src / name, repo / d)
            p = repo / rel
            if p.is_symlink():
                if os.readlink(p) != target:
                    actions.append(Link(rel, target))
            elif p.exists():
                conflicts.append(Conflict(rel, f"já existe e não é link; apague ou mova para `{SKILLS_SRC}/{name}`"))
            else:
                actions.append(Link(rel, target))
        for p in sorted((repo / d).glob("verify-*")) if (repo / d).is_dir() else []:
            if p.is_symlink() and p.name not in skills and SKILLS_SRC in os.readlink(p):
                actions.append(Unlink(f"{d}/{p.name}"))
    return SetupPlan(tuple(actions), tuple(conflicts))


# ------------------------------------------------------------------ effects


def apply(repo: Path, actions: tuple[Action, ...]) -> None:
    for a in actions:
        p = repo / a.path
        if isinstance(a, WriteFile):
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_name(p.name + ".t0tmp")
            tmp.write_text(a.text, encoding="utf-8")
            tmp.replace(p)
        elif isinstance(a, Link):
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.is_symlink():
                p.unlink()
            p.symlink_to(a.target, target_is_directory=True)
        else:
            p.unlink()


def _describe(a: Action) -> str:
    if isinstance(a, WriteFile):
        return f"escrever: {a.path}"
    if isinstance(a, Link):
        return f"ligar: {a.path} -> {a.target}"
    return f"remover link: {a.path}"


def run(*, repo: Path | None = None, check: bool = False) -> int:
    """Entry for `t0 setup`. Exit 0 set up (or nothing to do), 1 changes pending (with --check),
    2 conflicts or no such repo. Conflicts block nothing else: the other actions still apply."""
    root = (repo or Path.cwd()).resolve()
    if not root.is_dir():
        print(f"t0 setup: diretório não existe: {root}", file=sys.stderr)
        return 2
    p = plan(root)
    for a in p.actions:
        print(("pendente " if check else "") + _describe(a))
    for c in p.conflicts:
        print(f"conflito: {c.path}: {c.reason_pt}", file=sys.stderr)
    if not check:
        apply(root, p.actions)
    if p.conflicts:
        return 2
    return 1 if check and p.actions else 0
