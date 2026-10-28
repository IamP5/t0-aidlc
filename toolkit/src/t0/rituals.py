"""Rituals. The Ritual concept is the data (inputs, recorded, transcribable); code adds what a concept
cannot say: OPENERS (computed agenda items) and CLOSERS (per-ritual close rules).

open:  agenda = each `inputs` entry ({id, source, desc}; source `kb:<Tipo> chave=v1|v2`) queried over the
       View, plus the opener (daily-time digest, harness-health repeated errors). No writes.
close: decisions from `--decisions FILE` plus the day's `t0 log decision|blocker` records -> ONE knowledge
       change: Ritual Record (+ redacted Transcript once the LGPD sign-off exists) + closer files.
       Every decision needs an owner; a blocker may be `unassigned` (`dono: a definir` or no owner), and the
       next daily-time digest lists it. Re-running with the same input yields the same branch and bytes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable, Mapping

import yaml

from .okf.document import dump, duration, instant, to_dt
from .redact import Redacted, RedactionReport
from .render import set_keys
from .reports import digest
from .view import Concept, View
from .write import KnowledgeChange, Plan, Refusal, RenderedDoc

UNASSIGNED = "unassigned"
_NOBODY = {"a definir", "ninguém", "ninguem", "?", UNASSIGNED}
_OWNER = re.compile(r"\((?:dono|owner):\s*([^,)]+)(?:,\s*prazo:\s*([^)]+))?\)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Decision:
    text: str
    owner: str | None
    due: str | None = None
    kind: str = "decision"           # decision | blocker

    def as_map(self) -> dict[str, Any]:
        return {k: v for k, v in (("text", self.text), ("owner", self.owner), ("due", self.due), ("kind", self.kind)) if v}


@dataclass(frozen=True)
class CloseInput:
    attended: tuple[str, ...] = ()
    decisions: tuple[Decision, ...] = ()
    rotation: Mapping[str, str] = field(default_factory=dict)     # rotation slug -> human:<handle>
    accepted: tuple[str, ...] = ()                                # HI-NNNN accepted in harness-health
    facilitator: str | None = None


def _human(x: str) -> str:
    x = x.strip()
    if x.lower() in _NOBODY:
        return UNASSIGNED
    return x if ":" in x else f"human:{x}"


def _decision(raw: Any, kind: str) -> Decision:
    d = _parsed(raw, kind)
    return Decision(d.text, UNASSIGNED, d.due, kind) if kind == "blocker" and not d.owner else d


def _parsed(raw: Any, kind: str) -> Decision:
    if isinstance(raw, dict):
        return Decision(str(raw.get("text", "")).strip(), _human(str(raw["owner"])) if raw.get("owner") else None,
                        str(raw["due"]) if raw.get("due") else None, kind)
    text = str(raw).strip()
    m = _OWNER.search(text)
    if m:
        return Decision(text[:m.start()].strip(), _human(m.group(1)), m.group(2).strip() if m.group(2) else None, kind)
    return Decision(text, None, None, kind)


_MD_SECTIONS = {"presentes": "attended", "presença": "attended", "decisões": "decisions", "decisoes": "decisions",
                "bloqueios": "blockers", "rodízio": "rotation", "rodizio": "rotation", "aceitos": "accepted",
                "facilitador": "facilitator"}


def parse_decisions(text: str) -> CloseInput:
    """YAML ({attended, decisions, blockers, rotation, accepted, facilitator}) or Markdown with
    '## Presentes|Decisões|Bloqueios|Rodízio|Aceitos' sections of bullets."""
    data: dict[str, Any]
    if re.search(r"(?m)^##\s", text):
        data = {}
        cur = None
        for line in text.splitlines():
            h = re.match(r"^##\s+(.+?)\s*$", line)
            if h:
                cur = _MD_SECTIONS.get(h.group(1).strip().lower())
                continue
            b = re.match(r"^\s*[-*]\s+(.+)$", line)
            if cur and b:
                item = b.group(1).strip()
                if cur == "rotation":
                    k, _, v = item.partition(":")
                    data.setdefault("rotation", {})[k.strip()] = v.strip()
                elif cur == "facilitator":
                    data["facilitator"] = item
                else:
                    data.setdefault(cur, []).append(item)
    else:
        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError("arquivo de decisões precisa ser um mapa YAML ou Markdown com seções ##")
        data = loaded
    decs = tuple(_decision(d, "decision") for d in data.get("decisions") or []) + \
        tuple(_decision(d, "blocker") for d in data.get("blockers") or [])
    rot = {str(k): _human(str(v)) for k, v in (data.get("rotation") or {}).items()}
    return CloseInput(tuple(_human(str(a)) for a in data.get("attended") or []), decs, rot,
                      tuple(str(x).split()[0] for x in data.get("accepted") or []),
                      _human(str(data["facilitator"])) if data.get("facilitator") else None)


# ------------------------------------------------------------------ open


def ritual_concept(view: View, slug: str) -> Concept | None:
    return view.at(f"/rituals/{slug}/ritual.md")


def last_record(view: View, slug: str) -> Concept | None:
    recs = [c for c in view.of_type("Ritual Record") if c.path.startswith(f"/rituals/{slug}/")]
    return recs[-1] if recs else None


def _query(view: View, source: str) -> list[Concept] | None:
    m = re.match(r"^kb:([A-Za-zÀ-ú ]+?)((?:\s+\w+=\S+)*)$", source.strip())
    if not m:
        return None
    type_name, conds = m.group(1).strip(), re.findall(r"(\w+)=(\S+)", m.group(2))
    out = []
    for c in view.of_type(type_name):
        if all(k == "since" or str(c.state if k == "state" else c[k]) in v.split("|") for k, v in conds):
            out.append(c)
    return out


def _harness_open(view: View, now: str) -> list[str]:
    rep = [c for c in view.of_type("Harness Item") if c.state == "open" and len(c["occurrences"] or []) >= 2]
    stale = [c for c in view.concepts.values() if c.stale(now)]
    lines = ["## Erros repetidos (2+ ocorrências)"] + ([f"- {c.kb_id}: {c['pattern']} ({len(c['occurrences'])}x)" for c in rep] or ["- nenhum"])
    lines += ["", f"## Concepts vencidos no KB: {len(stale)}"] + [f"- {c.path}" for c in stale[:10]]
    return lines


def _unowned_blockers(view: View, since: str) -> list[str]:
    out = []
    for rec in view.of_type("Ritual Record"):
        if not instant(rec["date"]) or to_dt(rec["date"]) < to_dt(since):
            continue
        out += [f"- {d.get('text')} ({rec['ritual']} de {str(rec['date'])[:10]})" for d in rec["decisions"] or []
                if isinstance(d, dict) and d.get("kind") == "blocker" and d.get("owner") == UNASSIGNED]
    return ["", "### Bloqueios sem dono"] + (out or ["- nenhum"])


def _daily_time_open(view: View, now: str) -> list[str]:
    since = _since(view, "daily-time", now)
    return digest(view, now, since=since) + _unowned_blockers(view, since)


OPENERS: Mapping[str, Callable[[View, str], list[str]]] = {
    "daily-time": _daily_time_open,
    "harness-health": _harness_open,
}


def _since(view: View, slug: str, now: str) -> str:
    last = last_record(view, slug)
    if last is not None and instant(last["date"]):
        return str(last["date"])
    return (to_dt(now) - timedelta(days=1)).isoformat()


def open_agenda(view: View, slug: str, now: str) -> str | Refusal:
    r = ritual_concept(view, slug)
    if r is None:
        return Refusal((f"ritual `{slug}` não existe em /rituals/{slug}/ritual.md",))
    if r.state not in (None, "active"):
        return Refusal((f"ritual `{slug}` está `{r.state}`",))
    lines = [f"# {r['title']} ({now[:10]})", "", f"Facilita: {r['facilitator']}. Duração: {r['duration']}.", ""]
    lines += OPENERS[slug](view, now) + [""] if slug in OPENERS else []
    missing: list[str] = []
    for inp in r["inputs"] or []:
        if not isinstance(inp, dict):
            continue
        source = str(inp.get("source", ""))
        hits = _query(view, source)
        if hits is None:
            kind = source.split(":", 1)[0]
            missing += [] if kind == "kb" or kind in missing else [kind]
            continue
        lines.append(f"- {inp.get('desc') or inp.get('id')}: {len(hits)}")
        lines += [f"  - {c.kb_id} {c['title']} ({c.state})" for c in hits[:10]]
    lines += [f"- {UNAVAILABLE.get(k, f'{k}: sem fonte configurada')}, não consultados" for k in missing]
    return "\n".join(lines).rstrip() + "\n"


UNAVAILABLE = {"forge": "Merges e reviews: sem forge configurado",
               "metrics": "Painel de métricas: sem fonte configurada",
               "telemetry": "Uso de skills: sem telemetria configurada"}


# ------------------------------------------------------------------ close


@dataclass(frozen=True)
class Ctx:
    view: View
    slug: str
    now: str
    input: CloseInput
    handle: str


def _harness_health(ctx: Ctx) -> tuple[list[RenderedDoc], dict[str, Any]] | Refusal:
    items = {c.kb_id: c for c in ctx.view.of_type("Harness Item")}
    accepted = list(dict.fromkeys(list(ctx.input.accepted) + [k for k, c in items.items() if c["accepted"] is True and c.state == "open"]))
    missing = [a for a in accepted if a not in items]
    no_pr = [a for a in accepted if a in items and not items[a]["pr"]]
    if missing or no_pr:
        return Refusal(tuple([f"{a} não existe em /harness/" for a in missing] +
                             [f"{a} foi aceito e não tem PR: abra com a skill harness-fix e registre com `t0 ci {a} --pr <url>`"
                              for a in no_pr]))
    return [], {"harness_accepted": accepted}


def _demo(ctx: Ctx) -> tuple[list[RenderedDoc], dict[str, Any]] | Refusal:
    rots = {c.kb_id: c for c in ctx.view.of_type("Rotation")}
    given = dict(ctx.input.rotation)
    reasons = [f"falta o rodízio novo de `{slug}` (seção Rodízio: `{slug}: <handle>`)" for slug in rots if slug not in given]
    reasons += [f"rodízio `{s}` não existe em /team/rotations/" for s in given if s not in rots]
    if len(set(given.values())) < len(given):
        reasons.append("ninguém segura dois papéis ao mesmo tempo")
    reasons += [f"{who} não está no roster de {s}" for s, who in given.items()
                if s in rots and who not in (rots[s]["roster"] or [])]
    if reasons:
        return Refusal(tuple(reasons))
    puts: list[RenderedDoc] = []
    now = to_dt(ctx.now)
    for s, who in sorted(given.items()):
        c = rots[s]
        cadence = duration(c["cadence"]) or timedelta(days=14)
        assigns = [dict(a) for a in c["assignments"] or [] if isinstance(a, dict)]
        if assigns and assigns[-1].get("who") == who and assigns[-1].get("from", "")[:10] == ctx.now[:10]:
            continue
        for a in assigns:
            if instant(a.get("to")) and instant(a.get("from")) and to_dt(a["from"]) <= now < to_dt(a["to"]):
                a["to"] = ctx.now
        end = (now + cadence).isoformat()
        assigns.append({"who": who, "from": ctx.now, "to": end})
        puts.append(RenderedDoc(c.path, set_keys(c.doc.raw, {"assignments": assigns, "stale_after": end})))
    return puts, {"rotation": given}


CLOSERS: Mapping[str, Callable[[Ctx], tuple[list[RenderedDoc], dict[str, Any]] | Refusal]] = {
    "harness-health": _harness_health,
    "demo": _demo,
}


def _logged_today(view: View, day: str) -> list[Decision]:
    out = []
    for ev in view.events:
        if ev.kind.value in ("decision", "blocker") and ev.at[:10] == day:
            src = view.at(ev.source.value)
            if src is not None:
                out.append(_decision(src.doc.body.strip() or src["title"], ev.kind.value))
    return out


def transcript_persists(view: View) -> bool:
    p = view.at("/methodology/policies/transcript-retention.md")
    return p is not None and bool(p["lgpd_signoff"]) and p["persist"] != "dry-run"


def close(view: View, slug: str, inp: CloseInput, *, now: str, handle: str,
          transcript: tuple[Redacted, RedactionReport] | None = None) -> Plan | Refusal:
    r = ritual_concept(view, slug)
    if r is None:
        return Refusal((f"ritual `{slug}` não existe em /rituals/{slug}/ritual.md",))
    day = now[:10]
    decisions = list(dict.fromkeys(list(inp.decisions) + _logged_today(view, day)))
    seen: set[str] = set()
    uniq = []
    for d in decisions:
        if d.text and d.text not in seen:
            seen.add(d.text)
            uniq.append(d)
    reasons = [f"sem dono: {d.text[:60]!r}; toda decisão tem dono. No --decisions: `- {d.text[:60]} (dono: <pessoa>)`"
               for d in uniq if d.kind == "decision" and d.owner in (None, UNASSIGNED)]
    if transcript is not None and (r["recorded"] is False or r["transcribable"] is False):
        reasons.append(f"`{slug}` não é transcrito; feche sem --transcript")
    if reasons:
        return Refusal(tuple(reasons))
    ctx = Ctx(view, slug, now, inp, handle)
    extra_puts: list[RenderedDoc] = []
    extra_fm: dict[str, Any] = {}
    if slug in CLOSERS:
        res = CLOSERS[slug](ctx)
        if isinstance(res, Refusal):
            return res
        extra_puts, extra_fm = res
    msgs: list[str] = []
    rec_path = f"/rituals/{slug}/{day}.md"
    fm: dict[str, Any] = {
        "type": "Ritual Record", "title": f"{r['title']} de {day}",
        "description": f"Registro de {r['title']} em {day}: {len(uniq)} decisão(ões) e bloqueio(s).",
        "uid": f"ritual-{slug}-{day}", "owner": inp.facilitator or str(r["facilitator"]), "tags": ["ritual", slug],
        "generated": {"by": f"human:{handle}", "at": now}, "ritual": slug, "date": now,
        "facilitator": inp.facilitator or str(r["facilitator"]), "attended": list(inp.attended),
        "decisions": [d.as_map() for d in uniq]}
    puts: list[RenderedDoc] = []
    if transcript is not None:
        text, rep = transcript
        tpath = f"/transcripts/{day}-{slug}.md"
        msgs.append(f"transcrição redigida ({rep.version}): {rep.total} trecho(s) trocados, {rep.off_record_spans} fora do registro")
        if transcript_persists(view):
            pol = view.at("/methodology/policies/transcript-retention.md")
            keep = duration(((pol["thresholds"] or {}) if pol else {}).get("retention", "P180D")) or timedelta(days=180)
            tfm = {"type": "Transcript", "title": f"Transcrição de {r['title']} de {day}",
                   "description": f"Transcrição redigida de {r['title']} em {day}.", "uid": f"transcript-{slug}-{day}",
                   "owner": fm["owner"], "generated": {"by": "process:t0-redact", "at": now}, "ritual": slug,
                   "redaction": rep.version, "off_record_spans": rep.off_record_spans,
                   "participants": list(inp.attended), "stale_after": (to_dt(now) + keep).isoformat()}
            puts.append(RenderedDoc(tpath, dump(tfm, str(text).rstrip("\n") + "\n")))
            fm["transcript"] = tpath
        else:
            msgs.append("transcrição em dry-run: nada persiste até a Policy transcript-retention registrar o aval de LGPD")
    fm.update(extra_fm)
    body = [f"# {r['title']} de {day}", "", "## Decisões e bloqueios", ""]
    body += [f"- {'Bloqueio' if d.kind == 'blocker' else 'Decisão'}: {d.text} (dono: {'a definir' if d.owner == UNASSIGNED else d.owner}" + (f", prazo: {d.due}" if d.due else "") + ")"
             for d in uniq] or ["- nenhuma"]
    existing = view.at(rec_path)
    text = dump(fm, "\n".join(body) + "\n")
    if existing is not None:
        old = dict(existing.doc.frontmatter)
        if {k: v for k, v in old.items() if k not in ("generated", "date")} == {k: v for k, v in fm.items() if k not in ("generated", "date")}:
            text = existing.doc.raw
    puts.insert(0, RenderedDoc(rec_path, text))
    puts += extra_puts
    branch = f"kb/{handle}/ritual-{slug}-{day}"
    return Plan(knowledge=KnowledgeChange(branch, f"Ritual {slug} de {day}",
                                          f"Ritual Record de `{slug}` com {len(uniq)} decisão(ões).", tuple(puts)),
                messages_pt=tuple(msgs))
