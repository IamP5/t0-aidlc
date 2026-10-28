"""The one writer of derived content. Runs on the KB's main branch (kb-render workflow, or `t0 kb render`).

materialize(view) produces:
  - render-owned keys on every concept (status, jira, pr, audit, markers_open, Slice/Harness Item state ...),
    edited in place so the rest of the human-written frontmatter keeps its formatting;
  - the root index.md (sections kept when they only list subdirectories, then one section per type);
  - each bet's log.md and changeset.md, and the bundle /log.md (records outside a bet).
Outputs carry no wall-clock time, so re-running on an unchanged main yields an empty DerivedChange.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

import yaml

from .okf.document import Document
from .profile.table import REGISTRY, TYPES
from .view import Concept, Event, View, bet_folder
from .write import DerivedChange, RenderedDoc, derived_change

VERBS = {"progress": "Progresso", "decision": "Decisão", "blocker": "Bloqueio", "kill": "Kill", "handoff": "Handoff",
         "session": "Sessão", "pr-opened": "PR aberto", "pr-merged": "Merge", "ci-gate": "CI",
         "jira-linked": "Jira", "jira-status": "Status no Jira", "integration": "Integração"}
_SKIP_INDEX = {"Step", "Log", "OKF Profile"}


def set_keys(raw: str, updates: Mapping[str, Any]) -> str:
    """Replace or append top-level frontmatter keys without reformatting the others."""
    lines = raw.split("\n")
    end = next(i for i, l in enumerate(lines[1:], 1) if l.rstrip() == "---")
    fm = lines[1:end]
    for key, val in updates.items():
        if isinstance(val, (list, dict)) and val:
            new = yaml.safe_dump({key: val}, default_flow_style=None, sort_keys=False, allow_unicode=True, width=10000).rstrip("\n")
        else:
            scalar = yaml.safe_dump(val, default_flow_style=True, allow_unicode=True, width=10000)
            new = f"{key}: " + scalar.strip().removesuffix("...").strip()
        idx = next((i for i, l in enumerate(fm) if re.match(rf"^{re.escape(key)}:(\s|$)", l)), None)
        if idx is None:
            fm.extend(new.split("\n"))
            continue
        stop = idx + 1
        while stop < len(fm) and (fm[stop].startswith((" ", "\t", "-")) or not fm[stop].strip()):
            stop += 1
        fm[idx:stop] = new.split("\n")
    return "\n".join(["---", *fm, *lines[end:]])


def render_log_line(ev: Event, view: View) -> str:
    """Same function for render and previews, so the preview equals the result."""
    src = view.at(ev.source.value)
    title = str(src["title"]) if src is not None else ev.kind.value
    return f"* **{VERBS.get(ev.kind.value, ev.kind.value)}** por {ev.actor}: {title} ([registro]({ev.source.value}))"


def _log_doc(path: str, uid: str, title: str, desc: str, events: list[Event], view: View) -> str:
    events = sorted(events, key=lambda e: (e.at, e.source.value), reverse=True)
    at = events[0].at if events else "2026-01-01T00:00:00+00:00"
    fm = {"type": "Log", "title": title, "description": desc, "uid": uid, "owner": "process:kb-render",
          "generated": {"by": "process:kb-render", "at": at}}
    body: list[str] = [""]
    day = None
    for ev in events:
        if ev.at[:10] != day:
            day = ev.at[:10]
            body += ["", f"## {day}", ""] if len(body) > 1 else [f"## {day}", ""]
        body.append(render_log_line(ev, view))
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---\n" + "\n".join(body).lstrip("\n") + ("\n" if events else "")


def _changeset(bet: Concept, view: View) -> str:
    folder = bet_folder(bet.path) or ""
    fm = {"type": "Reference", "title": f"Change set da {bet.kb_id}",
          "description": f"Slices da {bet.kb_id} por repo, com estado e PR; gerado pelo kb-render.",
          "uid": f"{bet.uid}-changeset", "owner": "process:kb-render",
          "generated": {"by": "process:kb-render", "at": max([e.at for s in view.children(bet, "Slice") for e in s.history]
                                                             or [str((bet["generated"] or {}).get("at", ""))])}}
    rows = ["| slice | repo | estado | PR | Jira |", "|---|---|---|---|---|"]
    for s in view.children(bet, "Slice"):
        rows.append(f"| [{s.kb_id}]({s.path}) | {s['repo'] or '-'} | {s.state} | {s['pr'] or '-'} | {s['jira'] or '-'} |")
    return ("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n"
            + f"# Change set da {bet.kb_id}\n\nOrdem de merge: a ordem dos repos no workspace.md. Raiz: [{folder}/bet.md]({folder}/bet.md).\n\n"
            + "\n".join(rows) + "\n")


def _index(view: View, current: Document | None) -> str:
    kept: list[str] = []
    if current is not None:
        for block in re.split(r"(?m)^(?=# )", current.body):
            entries = [l for l in block.splitlines()[1:] if l.strip()]
            if block.startswith("# ") and entries and all(re.search(r"\]\([^)]*/\)", l) for l in entries):
                kept.append(block.strip())
    out = ['---\nokf_version: "0.2"\n---'] + kept
    for t in TYPES:
        if t.name in _SKIP_INDEX:
            continue
        items = [c for c in view.of_type(t.name) if not c.path.endswith("/changeset.md")]
        if not items:
            continue
        out.append(f"# {t.index_section_pt or t.name}\n\n" + "\n".join(
            f"* [{c['title']}]({c.path}) - {c['description']}" for c in items))
    return "\n\n".join(out) + "\n"


def materialize(view: View, docs: Iterable[Document] = ()) -> DerivedChange:
    by_path = {d.path.value: d for d in docs}
    puts: list[RenderedDoc] = []

    def put(path: str, text: str) -> None:
        cur = by_path.get(path)
        if cur is None or cur.raw != text:
            puts.append(RenderedDoc(path, text))

    for c in sorted(view.concepts.values(), key=lambda c: c.path):
        if c.spec is None or c.doc.path.is_reserved or not c.doc.has_frontmatter:
            continue
        upd = {k: c.derived[k] for k in sorted(REGISTRY.render_keys(c.spec))
               if k in c.derived and c.doc.frontmatter.get(k) != c.derived[k]
               and not (k == "verified" and not c.derived[k] and c.doc.frontmatter.get(k) is None)}
        if upd:
            put(c.path, set_keys(c.doc.raw, upd))

    put("/index.md", _index(view, by_path.get("/index.md")))
    loose = [e for e in view.events if bet_folder(e.source.value) is None and not e.pending]
    put("/log.md", _log_doc("/log.md", "log-root", "Log do KB", "Histórico de mudanças do KB, do mais novo para o mais antigo.",
                            loose, view))
    for bet in view.of_type("Bet"):
        folder = bet_folder(bet.path)
        evs = [e for e in view.events if not e.pending and bet_folder(e.source.value) == folder]
        put(f"{folder}/log.md", _log_doc(f"{folder}/log.md", f"{bet.uid}-log", f"Log da {bet.kb_id}",
                                         f"Passos da {bet.kb_id}, do mais novo para o mais antigo.", evs, view))
        put(f"{folder}/changeset.md", _changeset(bet, view))
    return derived_change(tuple(puts))
