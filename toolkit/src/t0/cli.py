"""`t0` command surface (DESIGN §10). argparse (stdlib). Every mutating command gets a Plan | Refusal from
KB; this dispatcher alone prints the plan, honours --dry-run and calls KB.apply.
Exit codes: 0 ok or no-op, 1 refusal or check failure, 2 usage, 3 KB unavailable (skills stop on 3).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from .profile.table import GATES, REGISTRY
from .write import Applied, Plan, Refusal

EXIT_OK, EXIT_REFUSED, EXIT_USAGE, EXIT_NO_KB = 0, 1, 2, 3
NEW_TYPES = ("idea", "bet", "spec", "slice", "adr", "harness")


def _out(s: str = "") -> None:
    sys.stdout.write(s + "\n")


def _err(s: str) -> None:
    sys.stderr.write(s + "\n")


# ------------------------------------------------------------------ plan printing


def describe(plan: Plan, kb_root: Path | None, *, dry: bool) -> list[str]:
    lines = [f"Plano{' (dry-run, nada foi escrito)' if dry else ''}:"]
    if plan.records:
        lines.append(f"  registros (spool): {len(plan.records)}")
        lines += [f"    + {r.doc.path}" for r in plan.records]
    k = plan.knowledge
    if k is not None:
        lines.append(f"  conhecimento: branch {k.branch}, PR draft \"{k.title_pt}\"")
        for d in k.puts:
            exists = kb_root is not None and (kb_root / d.path.lstrip("/")).is_file()
            lines.append(f"    {'altera' if exists else 'novo  '} {d.path}")
        lines += [f"    inclui {p} (editado à mão)" for p in k.include if p not in {d.path for d in k.puts}]
        if k.commit_all:
            lines.append("    todas as mudanças da árvore do KB")
        if k.reviewers:
            lines.append("    revisores: " + ", ".join(k.reviewers))
    if plan.derived is not None:
        lines.append(f"  derivado (kb-render): {len(plan.derived.puts)} arquivo(s)")
        lines += [f"    ~ {d.path}" for d in plan.derived.puts]
    if plan.empty:
        lines.append("  nada a escrever")
    lines += [f"  - {m}" for m in plan.messages_pt]
    return lines


def describe_applied(a: Applied) -> list[str]:
    out = []
    if a.spooled:
        out.append(f"no spool: {len(a.spooled)} registro(s); `t0 kb push` leva ao KB")
    if a.skipped:
        out.append(f"já registrado: {len(a.skipped)}")
    if a.branch and a.pr_url:
        out.append(f"PR draft: {a.pr_url} (branch {a.branch})")
    elif a.branch == "main":
        out.append(f"kb-render: commit {a.commit or '(sem mudança nova)'} no main")
    elif a.branch:
        out.append(f"commit {a.commit or '(sem mudança nova)'} no branch local {a.branch}; sem forge: o merge no main é a aprovação")
    if a.tree:
        out.append(f"worktree do branch: {a.tree}")
    return out


def run_plan(kb: Any, result: Plan | Refusal, dry: bool, *, mode: Any = None) -> int:
    if isinstance(result, Refusal):
        _out("recusado:")
        for r in result.reasons_pt:
            _out(f"  - {r}")
        return EXIT_REFUSED
    for l in describe(result, kb.tree if kb else None, dry=dry):
        _out(l)
    if dry or result.empty:
        return EXIT_OK
    from .write import ApplyError, ApplyMode

    try:
        applied = kb.apply(result, mode=mode or ApplyMode.LOCAL)
    except ApplyError as e:
        _out(f"recusado:\n  - {e}")
        return EXIT_REFUSED
    for l in describe_applied(applied):
        _out(l)
    return EXIT_OK


def _kb(a: argparse.Namespace, **kw: Any) -> Any:
    from .kb import KB

    return KB.open(Path(a.kb) if a.kb else None, dry=getattr(a, "dry_run", False), **kw)


# ------------------------------------------------------------------ kb


def cmd_kb_check(a: argparse.Namespace) -> int:
    from .check import Level

    kb = _kb(a)
    try:
        rep = kb.check(Level[a.level], changed_from=a.changed_from)
    except ValueError as e:
        _err(str(e))
        return EXIT_USAGE
    _out(rep.format(a.format))
    return EXIT_OK if rep.ok else EXIT_REFUSED


def cmd_kb_find(a: argparse.Namespace) -> int:
    from .kb import Query

    hits = _kb(a).find(Query(text=a.text or a.words, type=a.type, product=a.product, bet=a.bet, state=a.state, limit=a.limit))
    if a.json:
        _out(json.dumps([h.__dict__ for h in hits], ensure_ascii=False, indent=2))
    else:
        for h in hits:
            _out(f"{h.path}  [{h.type}{', ' + h.state if h.state else ''}]  {h.title}")
        if not hits:
            _out("nada encontrado")
    return EXIT_OK


def cmd_kb_get(a: argparse.Namespace) -> int:
    from .view import Ref

    c = _kb(a).get(Ref(a.ref))
    if c is None:
        _out(f"{a.ref} não encontrado no KB")
        return EXIT_REFUSED
    if a.json:
        _out(json.dumps({"path": c.path, "frontmatter": c.fm, "derived": sorted(c.derived), "body": c.doc.body},
                        ensure_ascii=False, indent=2, default=str))
    else:
        _out(f"# {c.path}  ({c['type']}, {c.state or 'sem estado'}, {c.trust()})")
        _out(c.doc.raw if not c.derived else _with_derived(c))
    return EXIT_OK


def _with_derived(c: Any) -> str:
    from .render import set_keys

    upd = {k: v for k, v in c.derived.items() if c.doc.frontmatter.get(k) != v}
    return set_keys(c.doc.raw, upd) if upd and c.doc.has_frontmatter else c.doc.raw


def cmd_kb_render(a: argparse.Namespace) -> int:
    from .write import ApplyMode

    kb = _kb(a)
    return run_plan(kb, kb.render(), a.dry_run, mode=ApplyMode.KB_RENDER)


def cmd_kb_push(a: argparse.Namespace) -> int:
    from .write import spool_dir

    kb = _kb(a)
    if a.dry_run:
        sp = spool_dir(kb.root)
        files = sorted(sp.rglob("*.md")) if sp.is_dir() else []
        _out(f"Plano (dry-run, nada foi escrito):\n  registros no spool: {len(files)}")
        for f in files:
            _out(f"    + /{f.relative_to(sp)}")
        _out(f"  - modo da raia de registros: {kb.records_mode()}")
        return EXIT_OK
    applied, msgs = kb.push(if_due=a.if_due)
    for m in msgs:
        _out(m)
    if applied.pr_url:
        _out(f"PR de registros: {applied.pr_url}")
    return EXIT_OK


def template_dir() -> Path | None:
    here = Path(__file__).resolve().parent
    for p in (here / "_data" / "okf-template", here.parents[2] / "okf-template"):
        if (p / "index.md").is_file():
            return p
    return None


def cmd_kb_init(a: argparse.Namespace) -> int:
    from . import gen

    src = template_dir()
    if src is None:
        _out("recusado:\n  - okf-template não encontrado no pacote")
        return EXIT_REFUSED
    dest = Path(a.dir)
    todo = [p for p in sorted(src.rglob("*")) if p.is_file() and not (dest / p.relative_to(src)).exists()]
    ctx = gen.GenContext(dest, gen.Scope.KB)
    prof = not (dest / "profile.md").exists()
    _out(f"Plano{' (dry-run, nada foi escrito)' if a.dry_run else ''}:")
    _out(f"  copiar do okf-template: {len(todo)} arquivo(s) novos (nenhum existente é sobrescrito)")
    _out(f"  profile.md: {'gerar' if prof else 'já existe'}")
    git = not (dest / ".git").exists()
    _out(f"  git: {'init no main + commit inicial' if git else 'repo existente, commit do que faltava'}")
    if a.dry_run:
        return EXIT_OK
    for p in todo:
        t = dest / p.relative_to(src)
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, t)
    if prof:
        gen.write(ctx, gen.generate(ctx))
    if git:
        subprocess.run(["git", "init", "-q", "-b", "main", str(dest)], check=True)
    from .write import _commit

    c = _commit(dest, None, "t0 kb init: KB a partir do okf-template")
    _out(f"KB pronto em {dest}" + (f" (commit {c})" if c else " (já estava)"))
    return EXIT_OK


def cmd_kb_propose(a: argparse.Namespace) -> int:
    kb = _kb(a)
    return run_plan(kb, kb.propose(a.message), a.dry_run)


# ------------------------------------------------------------------ new / idea / log / gate


def _body(a: argparse.Namespace) -> str | None:
    if not getattr(a, "body_file", None):
        return None
    return sys.stdin.read() if a.body_file == "-" else Path(a.body_file).read_text(encoding="utf-8")


def cmd_new(a: argparse.Namespace) -> int:
    kb = _kb(a)
    sets = list(a.set or [])
    for k in ("source",):
        if getattr(a, k, None):
            sets.append(f"{k}={getattr(a, k)}")
    if a.type == "idea" and a.product:
        sets.append(f"product={a.product}")
    res = kb.new(a.type, title=a.title, description=a.description, body=_body(a), sets=sets,
                 ref=getattr(a, "ref", None), track=getattr(a, "track", None),
                 product=getattr(a, "product", None) if a.type != "idea" else None,
                 repo=getattr(a, "repo", None), tier=getattr(a, "tier", None), pattern=getattr(a, "pattern", None),
                 occurrence=getattr(a, "occurrence", None), depends_on=getattr(a, "depends_on", None) or ())
    return run_plan(kb, res, a.dry_run)


def cmd_idea_prototype(a: argparse.Namespace) -> int:
    kb = _kb(a)
    return run_plan(kb, kb.idea_prototype(a.idea, a.verdict, a.ref), a.dry_run)


def cmd_adr_accept(a: argparse.Namespace) -> int:
    kb = _kb(a)
    return run_plan(kb, kb.adr_accept(a.adr), a.dry_run)


def cmd_log(a: argparse.Namespace) -> int:
    from .profile.spec import EventKind
    from .view import Ref

    kb = _kb(a)
    res = kb.record(EventKind(a.kind), a.text, bet=Ref(a.bet) if a.bet else None, story=a.story, refs=tuple(a.ref or ()))
    return run_plan(kb, res, a.dry_run)


def cmd_gate(a: argparse.Namespace) -> int:
    from .view import Ref

    kb = _kb(a)
    res = kb.gate(a.gate, Ref(a.ref), ci=a.ci)
    if a.ci:
        lines = res.reasons_pt if isinstance(res, Refusal) else res.messages_pt
        _out(f"gate {a.gate} {a.ref}: {'FALHOU' if isinstance(res, Refusal) else 'ok'}")
        for l in lines:
            _out(f"  {l}")
        return EXIT_REFUSED if isinstance(res, Refusal) else EXIT_OK
    return run_plan(kb, res, a.dry_run)


# ------------------------------------------------------------------ ritual / transcript


def _redact_file(path: str) -> tuple[Any, Any]:
    from .redact import redact

    return redact(Path(path).expanduser().read_text(encoding="utf-8"))


def cmd_ritual(a: argparse.Namespace) -> int:
    from . import rituals

    kb = _kb(a)
    if a.action == "open":
        res = rituals.open_agenda(kb.view(), a.slug, kb.now)
        if isinstance(res, Refusal):
            return run_plan(kb, res, True)
        _out(res.rstrip())
        return EXIT_OK
    try:
        inp = rituals.parse_decisions(Path(a.decisions).read_text(encoding="utf-8")) if a.decisions else rituals.CloseInput()
    except (OSError, ValueError) as e:
        return run_plan(kb, Refusal((f"--decisions: {e}",)), True)
    transcript = _redact_file(a.transcript) if a.transcript else None
    branch = f"kb/{kb.handle}/ritual-{a.slug}-{kb.now[:10]}"
    if (r := kb.checkout(branch)):
        return run_plan(kb, r, True)
    return run_plan(kb, rituals.close(kb.view(), a.slug, inp, now=kb.now, handle=kb.handle, transcript=transcript), a.dry_run)


def cmd_transcript_redact(a: argparse.Namespace) -> int:
    text, rep = _redact_file(a.file)
    counts = ", ".join(f"{k.value}={v}" for k, v in sorted(rep.counts.items(), key=lambda kv: kv[0].value)) or "nada"
    _err(f"redator {rep.version}: {counts}; {rep.off_record_spans} trecho(s) fora do registro")
    _out(str(text).rstrip("\n"))
    if not a.dry_run:
        out = Path.home() / ".t0" / "redacted" / (Path(a.file).stem + ".md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(str(text), encoding="utf-8")
        _err(f"texto redigido gravado em {out}")
    return EXIT_OK


# ------------------------------------------------------------------ slice / bet / ci


def _ws(kb: Any = None) -> Any:
    from . import ws

    return kb.workspace() if kb is not None else ws.locate(Path.cwd())


def cmd_slice(a: argparse.Namespace) -> int:
    kb = _kb(a)
    dor = kb.slice_dor(a.key)
    if a.action == "dor" or isinstance(dor, Refusal):
        return run_plan(kb, dor, True)
    from . import ws
    from .view import Ref

    w = _ws(kb)
    if w is None:
        return run_plan(kb, Refusal(("sem workspace (.t0/workspace.json); rode a partir do workspace do produto",)), True)
    if a.dry_run:
        return run_plan(kb, Plan(messages_pt=dor.messages_pt + (f"criaria o branch do slice no repo `{kb.get(Ref(a.key))['repo']}`",)), True)
    return run_plan(kb, ws.slice_start(kb, w, a.key), False)


def cmd_bet(a: argparse.Namespace) -> int:
    from . import ws

    if a.action == "detect":
        d = ws.detect(Path.cwd())
        if a.json:
            _out(json.dumps(d.__dict__, ensure_ascii=False))
        else:
            _out(f"bet: {d.bet or '-'}  story: {d.story or '-'}  regra: {d.rule}" + (f"  produto: {d.product}" if d.product else ""))
        return EXIT_OK
    kb = _kb(a)
    if not a.ref:
        _err(f"`t0 bet {a.action}` precisa de <BET|KEY>")
        return EXIT_USAGE
    if a.action == "ship":
        return run_plan(kb, kb.bet_ship(a.ref), a.dry_run)
    w = _ws(kb)
    if w is None:
        return run_plan(kb, Refusal(("sem workspace (.t0/workspace.json)",)), True)
    if a.dry_run:
        return run_plan(kb, Plan(messages_pt=(f"gravaria .t0/bet.json com {a.ref} e o AGENTS.md",)), True)
    res = ws.bet_use(kb, w, a.ref)
    code = run_plan(kb, res, False)
    if code == EXIT_OK:
        from .context import CardFormat

        card = kb.context(None, CardFormat.AGENTS)
        if card is not None and ws.write_if_changed(w.root / "AGENTS.md", card.text):
            _out("AGENTS.md atualizado")
    return code


def cmd_ci(a: argparse.Namespace) -> int:
    kb = _kb(a)
    pr = a.pr or os.environ.get("T0_PR")
    state = a.state or os.environ.get("T0_PR_STATE")
    approvals = list(a.approval or []) or [x for x in os.environ.get("T0_APPROVALS", "").split(",") if x]
    if not pr or not state:
        _err("`t0 ci <KEY>` precisa de --pr e --state (ou T0_PR e T0_PR_STATE)")
        return EXIT_USAGE
    res = kb.ci(a.key, pr=pr, state=state, approvals=approvals, audit=a.audit or os.environ.get("T0_AUDIT"),
                author=a.author or os.environ.get("T0_PR_AUTHOR"))
    return run_plan(kb, res, a.dry_run)


# ------------------------------------------------------------------ jira / context / edges


def cmd_jira_sync(a: argparse.Namespace) -> int:
    from .tracker import TrackerConfig, execute, open_tracker, plan_sync, snapshot
    from .tracker.sync import SyncIncomplete

    if not a.tracker or not a.tracker.startswith("file:"):
        _out("recusado:\n  - Jira REST é v0.2 (Cloud ou DC em aberto); use --tracker file:<dir>")
        return EXIT_REFUSED
    kb = _kb(a)
    t = open_tracker(TrackerConfig(kind="file", file_dir=Path(a.tracker[5:])))
    view = kb.view()
    sp = plan_sync(view, snapshot(t, view))
    _out(f"Plano do sync{'' if a.apply else ' (sem --apply, nada foi escrito)'}:")
    for act in sp.actions:
        _out(f"  {act.kind.value} {act.kb_uid or ''} {act.key or ''} {act.reason_pt}".rstrip())
    for d in sp.drift:
        _out(f"  drift: {d}")
    if not sp.actions:
        _out("  nada a sincronizar")
    if not a.apply:
        return EXIT_OK
    try:
        plan = execute(sp, t)
    except SyncIncomplete as e:
        run_plan(kb, e.plan, False)
        _out(f"recusado:\n  - {e}")
        return EXIT_REFUSED
    return run_plan(kb, plan, False)


def cmd_context(a: argparse.Namespace) -> int:
    from .context import CardFormat
    from .view import Ref

    card = _kb(a).context(Ref(a.ref) if a.ref else None, CardFormat(a.format))
    _out(card.text.rstrip("\n") if card else "t0: card em dia.")
    return EXIT_OK


def cmd_gen(a: argparse.Namespace) -> int:
    from . import gen

    return gen.run(scope=a.scope, out=Path(a.out) if a.out else None, src=Path(a.src) if a.src else None, check=a.check)


def cmd_hook(a: argparse.Namespace) -> int:
    from .hooks import run_hook

    code, out, err = run_hook(a.event, sys.stdin.buffer.read(), tool=a.tool)
    sys.stdout.write(out)
    sys.stderr.write(err)
    return code


def cmd_mcp(a: argparse.Namespace) -> int:
    from .mcp_server import serve

    serve(Path(a.kb) if a.kb else None, read_only=a.read_only)
    return EXIT_OK


def cmd_setup(a: argparse.Namespace) -> int:
    from . import setup

    return setup.run(repo=Path(a.repo) if a.repo else None, check=a.check)


def _shared_kb_rows(kb: Any) -> list[tuple[str, bool | None, str]]:
    """Several workspaces, one KB clone: `<ws>/kb` is a symlink to config `kb:`, and Claude Code may open the
    workspaces' parent, the KB and its worktrees without asking. Reads only."""
    import yaml

    from . import ws
    from .write import worktree_root

    w = ws.locate(Path.cwd())
    if w is None:
        return []
    rows: list[tuple[str, bool | None, str]] = []
    cfg = Path.home() / ".t0/config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) if cfg.is_file() else None
    shared = Path(str(data["kb"])).expanduser().resolve() if isinstance(data, dict) and data.get("kb") else None
    if shared is not None and w.kb_dir.exists():
        same = w.kb_dir.resolve() == shared
        rows.append(("KB compartilhado", True if same else None, f"{w.kb_dir} -> {shared}" if same else
                     f"{w.kb_dir} é {w.kb_dir.resolve()}, o config aponta {shared}: mova a pasta e rode `ln -s {shared} {w.kb_dir}`"))
    claude = Path.home() / ".claude"
    if claude.is_dir():
        try:
            settings = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            settings = {}
        perms = settings.get("permissions") if isinstance(settings, dict) else None
        dirs = perms.get("additionalDirectories") if isinstance(perms, dict) else None
        have = [Path(d) for d in dirs or () if isinstance(d, str) and d.startswith("/")]
        need = [w.root.parent.resolve()]
        if kb is not None:
            need += [kb.root, worktree_root(kb.root)]
        missing = []
        for d in need:
            if not any(d == h or h in d.parents for h in have + missing):
                missing.append(d)
        rows.append(("Claude Code additionalDirectories", True if not missing else None,
                     "cobre " + ", ".join(map(str, need)) if not missing else
                     "adicione em ~/.claude/settings.json: \"permissions\": {\"additionalDirectories\": "
                     + json.dumps([str(d) for d in missing]) + "} (caminho absoluto, sem ~)"))
    return rows


def cmd_doctor(a: argparse.Namespace) -> int:
    from . import _forge
    from .check import Level

    rows: list[tuple[str, bool | None, str]] = [
        ("python >= 3.11", sys.version_info >= (3, 11), sys.version.split()[0]),
        ("git", shutil.which("git") is not None, shutil.which("git") or "ausente"),
        ("t0 no PATH", shutil.which("t0") is not None, shutil.which("t0") or "hooks e MCP chamam `t0`"),
    ]
    kb = None
    try:
        kb = _kb(a)
        rep = kb.check(Level.L1)
        errs = sum(f.severity.value == "error" for f in rep.findings)
        rows.append(("KB", True, str(kb.root)))
        rows.append(("kb check L1", rep.ok, f"{errs} erro(s)"))
    except Exception as e:
        rows.append(("KB", False, str(e)))
    try:
        f = _forge.configured()
        rows.append(("forge", True, f"{f.kind}:{f.target}" if f else "nenhum (branch local + commit)"))
    except _forge.ForgeError as e:
        rows.append(("forge", False, str(e)))
    w = _ws(kb)
    rows.append(("workspace", True, str(w.root) if w else "nenhum (.t0/workspace.json)"))
    rows += _shared_kb_rows(kb)
    for name, ok, detail in rows:
        _out(f"{'ok   ' if ok else 'aviso' if ok is None else 'FALHA'} {name}: {detail}")
    return EXIT_OK if all(ok is not False for _, ok, _ in rows) else EXIT_REFUSED


# ------------------------------------------------------------------ parser


def _fields_help(slug: str) -> str:
    from .kb import T0_KEYS
    spec = REGISTRY.type_for_slug(slug)
    lines = [f"Chaves de {spec.name} (defina com --set chave=valor; derivadas o t0 escreve):"]
    for f in REGISTRY.fields(spec):
        if f.name in ("type",):
            continue
        tag = "o t0 escreve" if f.derived or f.name in T0_KEYS else ("obrigatória" if f.required else "opcional")
        enum = f" [{'|'.join(f.enum)}]" if f.enum else ""
        lines.append(f"  {f.name:<16} {f.kind.value}{enum}, {tag}" + (f": {f.doc_pt}" if f.doc_pt else ""))
    if spec.states:
        lines.append(f"Estados: {' | '.join(spec.states.status_of)} (inicial {spec.states.initial})")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--kb", help="pasta do KB (padrão: T0_KB, o workspace, ou o KB onde você está)")
    dry = argparse.ArgumentParser(add_help=False)
    dry.add_argument("--dry-run", action="store_true", help="mostra o plano sem escrever")
    p = argparse.ArgumentParser(prog="t0", description="t0: KB OKF, decisões, rituais e adaptadores de agente")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(parent: Any, name: str, fn: Callable[[argparse.Namespace], int], *, mut: bool = False, **kw: Any) -> argparse.ArgumentParser:
        sp = parent.add_parser(name, parents=[common] + ([dry] if mut else []), **kw)
        sp.set_defaults(fn=fn)
        return sp

    se = sub.add_parser("setup", help="AGENTS.md, ponteiros, hooks e links das skills verify-* no repo de produto")
    se.set_defaults(fn=cmd_setup)
    se.add_argument("--repo")
    se.add_argument("--check", action="store_true", help="só confere; exit 1 se há mudança pendente")

    kb = sub.add_parser("kb", help="KB: check, find, get, render, push, init, propose").add_subparsers(dest="kbcmd", required=True)
    c = add(kb, "check", cmd_kb_check, help="conformidade OKF + profile t0-team")
    c.add_argument("--level", choices=["L0", "L1", "L2"], default="L1")
    c.add_argument("--format", choices=["text", "github", "json"], default="text")
    c.add_argument("--changed-from", metavar="REF")
    f = add(kb, "find", cmd_kb_find, help="busca por texto e frontmatter")
    f.add_argument("words", nargs="?", metavar="texto", help="o mesmo que --text")
    for opt in ("--text", "--type", "--state", "--product", "--bet"):
        f.add_argument(opt)
    f.add_argument("--limit", type=int, default=20)
    f.add_argument("--json", action="store_true")
    g = add(kb, "get", cmd_kb_get, help="lê um concept (uid, caminho, chave Jira, BET-NNN, IDEA-NNNN)")
    g.add_argument("ref")
    g.add_argument("--json", action="store_true")
    add(kb, "render", cmd_kb_render, mut=True, help="derivados: chaves, index.md, log.md, changeset.md, profile.md (no main)")
    pu = add(kb, "push", cmd_kb_push, mut=True, help="leva o spool de registros ao KB")
    pu.add_argument("--if-due", action="store_true")
    i = add(kb, "init", cmd_kb_init, mut=True, help="cria um KB a partir do okf-template")
    i.add_argument("dir")
    pr = add(kb, "propose", cmd_kb_propose, mut=True, help="PR draft de conhecimento do branch atual")
    pr.add_argument("-m", "--message", required=True)

    new = sub.add_parser("new", help="cria idea, bet, spec, slice, adr ou harness").add_subparsers(dest="type", required=True)
    for slug in NEW_TYPES:
        n = add(new, slug, cmd_new, mut=True, help=f"novo {REGISTRY.type_for_slug(slug).name}",
                epilog=_fields_help(slug), formatter_class=argparse.RawDescriptionHelpFormatter)
        n.add_argument("--title")
        n.add_argument("--description")
        n.add_argument("--body-file", help="corpo em markdown (- para stdin); padrão: o Template do KB")
        n.add_argument("--set", action="append", metavar="CHAVE=VALOR")
        if slug == "idea":
            n.add_argument("--source", choices=["human", "squad", "transcript", "jira"])
            n.add_argument("--product")
        if slug == "bet":
            n.add_argument("ref", nargs="?", metavar="IDEA|texto", help="IDEA-NNNN, ou texto livre na trilha rápida")
            n.add_argument("--track", choices=["rapida", "bet"], required=True)
            n.add_argument("--product")
            n.add_argument("--repo", help="repo do slice único (rápida)")
            n.add_argument("--tier", type=int, choices=[0, 1, 2])
        if slug in ("spec", "slice"):
            n.add_argument("ref", nargs="?", metavar="BET")
        if slug == "slice":
            n.add_argument("--repo")
            n.add_argument("--tier", type=int, choices=[0, 1, 2])
            n.add_argument("--depends-on", action="append")
        if slug == "adr":
            n.add_argument("--product")
        if slug == "harness":
            n.add_argument("--pattern")
            n.add_argument("--occurrence")

    idea = sub.add_parser("idea", help="veredito do protótipo").add_subparsers(dest="ideacmd", required=True)
    ip = add(idea, "prototype", cmd_idea_prototype, mut=True)
    ip.add_argument("idea")
    ip.add_argument("--verdict", choices=["segue", "ajusta", "mata"], required=True)
    ip.add_argument("--ref", help="onde está o protótipo (fora do main)")

    adr = sub.add_parser("adr", help="aceite de ADR").add_subparsers(dest="adrcmd", required=True)
    add(adr, "accept", cmd_adr_accept, mut=True, help="ADR `accepted` num PR de conhecimento").add_argument("adr")

    lg = add(sub, "log", cmd_log, mut=True, help="registro de passo (raia de registros)")
    lg.add_argument("kind", choices=["progress", "decision", "blocker", "kill"])
    lg.add_argument("text")
    lg.add_argument("--bet")
    lg.add_argument("--story")
    lg.add_argument("--ref", action="append")

    ga = add(sub, "gate", cmd_gate, mut=True, help="decisão aposta ou spec no PR")
    ga.add_argument("gate", choices=[g.id for g in GATES])
    ga.add_argument("ref")
    ga.add_argument("--ci", action="store_true", help="só confere no head do PR; não escreve")

    ri = add(sub, "ritual", cmd_ritual, mut=True, help="abre ou fecha um ritual")
    ri.add_argument("slug")
    ri.add_argument("action", choices=["open", "close"])
    ri.add_argument("--decisions", metavar="FILE", help="YAML ou Markdown com presentes, decisões, bloqueios, rodízio")
    ri.add_argument("--transcript", metavar="F")

    tr = sub.add_parser("transcript", help="redação determinística").add_subparsers(dest="trcmd", required=True)
    rd = add(tr, "redact", cmd_transcript_redact, mut=True)
    rd.add_argument("file")

    sl = add(sub, "slice", cmd_slice, mut=True, help="DoR e branch do slice")
    sl.add_argument("action", choices=["dor", "start"])
    sl.add_argument("key")

    bt = add(sub, "bet", cmd_bet, mut=True, help="bet ativa e ship")
    bt.add_argument("action", choices=["detect", "use", "ship"])
    bt.add_argument("ref", nargs="?")
    bt.add_argument("--json", action="store_true")

    ci = add(sub, "ci", cmd_ci, mut=True, help="evidência do CI do produto -> registros do slice")
    ci.add_argument("key")
    ci.add_argument("--pr")
    ci.add_argument("--state", choices=["draft", "ready", "merged"])
    ci.add_argument("--approval", action="append", metavar="human:<handle>")
    ci.add_argument("--audit")
    ci.add_argument("--author")

    ji = sub.add_parser("jira", help="espelho no Jira").add_subparsers(dest="jcmd", required=True)
    js = add(ji, "sync", cmd_jira_sync)
    js.add_argument("--apply", action="store_true")
    js.add_argument("--tracker", metavar="file:<dir>")

    cx = add(sub, "context", cmd_context, help="card de contexto")
    cx.add_argument("ref", nargs="?")
    cx.add_argument("--format", choices=["agents", "delta", "subagent", "json"], default="agents")

    ge = sub.add_parser("gen", help="arquivos gerados")
    ge.set_defaults(fn=cmd_gen)
    ge.add_argument("--check", action="store_true")
    ge.add_argument("--scope", choices=["plugin", "kb"], default="plugin")
    ge.add_argument("--src")
    ge.add_argument("--out")

    ho = sub.add_parser("hook", help="entrada única dos hooks (stdin JSON, exit 2 bloqueia)")
    ho.set_defaults(fn=cmd_hook)
    ho.add_argument("event")
    ho.add_argument("--tool", choices=["claude", "copilot", "kiro"])

    mc = add(sub, "mcp", cmd_mcp, help="servidor MCP t0-kb (stdio)")
    mc.add_argument("--read-only", action="store_true")

    add(sub, "doctor", cmd_doctor, help="confere a instalação")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    from .kb import KBUnavailable

    args = build_parser().parse_args(argv)
    try:
        return int(args.fn(args))
    except KBUnavailable as e:
        _err(str(e))
        return EXIT_NO_KB


if __name__ == "__main__":
    raise SystemExit(main())
