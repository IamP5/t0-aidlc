"""The View: documents + fold(Step records). The single computation of every render-owned key.

Invariant: for every concept c and every render key k of its type, materialized(c)[k] == fold(c)[k].
kb-render establishes it (render.materialize); kb check L2.derived-drift reports lag; LANE.derived-untouched
rejects hand edits in PRs; the pre-tool hook blocks them locally.

Fold rules:
- Steps sorted by (generated.at, path). Duplicate `dedup` keys: first wins.
- A Step moves a RENDER-owned machine (Slice, Harness Item) iff the table allows (state, kind, to);
  otherwise it becomes an Anomaly, never applied silently.
- `jira-linked` sets `jira` once; a different second key is an Anomaly.
- `markers_open` counts '[PRECISA ESCLARECER]' in the body; `status` = status_of[state].
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Iterator, Mapping

from .okf.document import Actor, BundlePath, Document, Instant, instant, to_dt
from .profile.spec import EventKind, StateOwner, TypeSpec
from .profile.table import REGISTRY

MARKER = "[PRECISA ESCLARECER]"
_KB_ID = re.compile(r"^(BET-\d+|IDEA-\d+|ADR-\d+|HI-\d+)$")
_SLICE_SHORT = re.compile(r"^(BET-\d+)/(\d+)$")


@dataclass(frozen=True)
class Ref:
    """User-facing reference: uid, bundle path, Jira key, KB id (BET-042, IDEA-0057, ADR-0004, HI-0001),
    or 'BET-042/02' slice shorthand."""
    raw: str


@dataclass(frozen=True)
class Event:
    at: Instant
    actor: Actor
    kind: EventKind
    target: str               # uid
    to: str | None
    dedup: str
    source: BundlePath
    payload: Mapping[str, Any]
    pending: bool = False
    refs: tuple[str, ...] = ()


class AnomalyKind(Enum):
    ILLEGAL_TRANSITION = "illegal-transition"
    JIRA_KEY_CHANGED = "jira-key-changed"
    UNKNOWN_TARGET = "unknown-target"


@dataclass(frozen=True)
class Anomaly:
    kind: AnomalyKind
    target: str
    detail: str
    source: BundlePath


@dataclass(frozen=True)
class Concept:
    doc: Document
    spec: TypeSpec | None
    derived: Mapping[str, Any]
    history: tuple[Event, ...]

    @property
    def fm(self) -> Mapping[str, Any]:
        return {**dict(self.doc.frontmatter), **dict(self.derived)}

    @property
    def uid(self) -> str:
        return str(self.doc.frontmatter.get("uid") or self.doc.path.concept_id)

    @property
    def path(self) -> str:
        return self.doc.path.value

    @property
    def state(self) -> str | None:
        return self.fm.get("state") or (self.spec.states.initial if self.spec and self.spec.states else None)

    @property
    def kb_id(self) -> str:
        """BET-042 for a bet.md, IDEA-0001, ADR-0001-x, HI-0001, NN-slug for a slice."""
        p = self.doc.path
        return p.segments[-2] if p.name in ("bet.md", "spec.md", "ritual.md") else p.name.removesuffix(".md")

    def __getitem__(self, key: str) -> Any:
        return self.fm.get(key)

    def trust(self) -> str:
        v = self.fm.get("verified") or []
        v = [v] if isinstance(v, dict) else v
        bys = [str(x.get("by", "")) for x in v if isinstance(x, dict)]
        if not bys:
            return "unverified"
        return "human-reviewed" if any(b.startswith("human:") for b in bys) else "machine-confirmed"

    def stale(self, now: str) -> bool:
        s = self.fm.get("stale_after")
        return bool(instant(s)) and to_dt(s) <= to_dt(now)


def bet_folder(path: str) -> str | None:
    m = re.match(r"^(/products/[^/]+/bets/BET-\d+)/", path)
    return m.group(1) if m else None


@dataclass(frozen=True)
class View:
    concepts: Mapping[str, Concept]            # by uid
    by_path: Mapping[str, str]                 # path -> uid
    by_jira: Mapping[str, str]                 # jira key -> uid
    anomalies: tuple[Anomaly, ...]
    kb_sha: str
    pending: int
    events: tuple[Event, ...] = field(default=())

    def of_type(self, type_name: str) -> Iterator[Concept]:
        return (c for c in sorted(self.concepts.values(), key=lambda c: c.path) if c.fm.get("type") == type_name)

    def at(self, path: str) -> Concept | None:
        uid = self.by_path.get(path)
        return self.concepts.get(uid) if uid else next((c for c in self.concepts.values() if c.path == path), None)

    def bet_of(self, c: Concept) -> Concept | None:
        folder = bet_folder(c.path)
        return self.at(folder + "/bet.md") if folder else None

    def children(self, bet: Concept, type_name: str) -> tuple[Concept, ...]:
        folder = bet_folder(bet.path)
        return tuple(c for c in self.of_type(type_name) if folder and c.path.startswith(folder + "/"))

    def spec_of(self, bet: Concept) -> Concept | None:
        folder = bet_folder(bet.path)
        return self.at(folder + "/spec.md") if folder else None

    def resolve_ref(self, raw: str) -> Concept | None:
        return self.resolve(Ref(raw))

    def resolve(self, ref: Ref) -> Concept | None:
        raw = ref.raw.strip()
        if raw in self.concepts:
            return self.concepts[raw]
        if raw in self.by_jira:
            return self.concepts.get(self.by_jira[raw])
        if "/" in raw and not _SLICE_SHORT.match(raw):
            p = "/" + raw.lstrip("./").lstrip("/")
            return self.at(p if p.endswith(".md") else p + ".md") or self.at(p + "/bet.md")
        m = _SLICE_SHORT.match(raw)
        if m:
            bet = self.resolve(Ref(m.group(1)))
            nn = m.group(2).zfill(2)
            return next((s for s in (self.children(bet, "Slice") if bet else ()) if s.kb_id.startswith(nn + "-")), None)
        if _KB_ID.match(raw):
            for c in sorted(self.concepts.values(), key=lambda c: c.path):
                if c.fm.get("type") == "Step":
                    continue
                if c.kb_id == raw and (raw.startswith("BET-") is (c.doc.path.name == "bet.md")):
                    return c
                if not raw.startswith("BET-") and c.kb_id.startswith(raw + "-"):
                    return c
        return None


def _event(doc: Document, pending: bool) -> tuple[Event | None, str | None]:
    fm = doc.frontmatter
    try:
        kind = EventKind(fm.get("kind"))
    except ValueError:
        return None, None
    gen = fm.get("generated") if isinstance(fm.get("generated"), dict) else {}
    target = str(fm.get("target") or "")
    payload = fm.get("payload") if isinstance(fm.get("payload"), dict) else {}
    ev = Event(Instant(str(gen.get("at", ""))), Actor(str(fm.get("on_behalf_of") or gen.get("by", ""))), kind,
               target, fm.get("to"), str(fm.get("dedup") or doc.path.value), doc.path, payload, pending,
               tuple(str(r) for r in fm.get("refs") or [] if isinstance(fm.get("refs"), list)))
    return ev, (str(fm["story"]) if fm.get("story") else None)


_RANK = {EventKind.JIRA_LINKED: 0, EventKind.PR_OPENED: 2, EventKind.CI_GATE: 3, EventKind.PR_MERGED: 4}


def _sort_key(ev: Event) -> tuple[float, int, str]:
    """Time, then lifecycle order (a CI run emits pr-opened, ci-gate and pr-merged in the same second)."""
    try:
        t = to_dt(ev.at).timestamp()
    except ValueError:
        t = 0.0
    return t, _RANK.get(ev.kind, 1), ev.source.value


def fold(docs: Iterable[Document], *, kb_sha: str, overlay: Iterable[Document] = ()) -> View:
    """Pure. Same input, same View. Duplicate records (same dedup) fold once."""
    base: dict[str, tuple[Document, TypeSpec | None]] = {}
    raw_events: list[tuple[Event, str | None]] = []
    seen_paths: set[str] = set()
    for pending, group in ((False, docs), (True, overlay)):
        for d in group:
            if d.path.value in seen_paths or d.path.is_reserved or not d.has_frontmatter:
                continue
            seen_paths.add(d.path.value)
            spec = REGISTRY.type_named(str(d.frontmatter.get("type", "")))
            uid = str(d.frontmatter.get("uid") or d.path.concept_id)
            base.setdefault(uid, (d, spec))
            if spec is not None and spec.name == "Step":
                ev, story = _event(d, pending)
                if ev is not None:
                    raw_events.append((ev, story))

    raw_events.sort(key=lambda e: _sort_key(e[0]))
    dedup: set[str] = set()
    events: list[tuple[Event, str | None]] = []
    for ev, story in raw_events:
        if ev.dedup in dedup:
            continue
        dedup.add(ev.dedup)
        events.append((ev, story))

    derived: dict[str, dict[str, Any]] = {}
    history: dict[str, list[Event]] = {}
    anomalies: list[Anomaly] = []
    by_jira: dict[str, str] = {}

    for uid, (d, spec) in base.items():
        if spec is None:
            continue
        dv: dict[str, Any] = {}
        if spec.states and spec.states.owner is StateOwner.RENDER:
            dv["state"] = spec.states.initial
            dv["verified"] = []
        if spec.name == "Spec":
            dv["markers_open"] = d.body.count(MARKER)
        derived[uid] = dv

    ids: dict[str, str] = {}
    for u, (d, spec) in sorted(base.items(), key=lambda kv: kv[1][0].path.value):
        if spec is not None and spec.name != "Step":
            kid = Concept(d, None, {}, ()).kb_id
            ids.setdefault(kid, u)
            m = re.match(r"^((?:IDEA|ADR|HI)-\d+)-", kid)
            if m:
                ids.setdefault(m.group(1), u)

    def resolve_target(ev: Event, story: str | None) -> str | None:
        if ev.target and ev.target in base:
            return ev.target
        if ev.target and ev.target in ids:
            return ids[ev.target]
        if story and story in by_jira:
            return by_jira[story]
        return None

    for ev, story in events:
        if ev.kind is EventKind.JIRA_LINKED:
            pairs = list(ev.payload["keys"].items()) if isinstance(ev.payload.get("keys"), dict) else [(ev.target, ev.payload.get("key"))]
            for tgt, key in pairs:
                uid = tgt if tgt in base else ids.get(str(tgt))
                if uid is None or not key:
                    anomalies.append(Anomaly(AnomalyKind.UNKNOWN_TARGET, str(tgt), "jira-linked sem alvo", ev.source))
                    continue
                have = derived[uid].get("jira")
                if have and have != key:
                    anomalies.append(Anomaly(AnomalyKind.JIRA_KEY_CHANGED, uid, f"{have} -> {key}", ev.source))
                    continue
                derived[uid]["jira"] = str(key)
                by_jira[str(key)] = uid
                history.setdefault(uid, []).append(ev)

    for ev, story in events:
        if ev.kind is EventKind.JIRA_LINKED:
            continue
        uid = resolve_target(ev, story)
        if uid is None:
            if ev.target or ev.kind in (EventKind.PR_OPENED, EventKind.PR_MERGED, EventKind.CI_GATE):
                anomalies.append(Anomaly(AnomalyKind.UNKNOWN_TARGET, ev.target or str(story), ev.kind.value, ev.source))
            continue
        d, spec = base[uid]
        history.setdefault(uid, []).append(ev)
        if ev.kind is EventKind.PR_MERGED and spec is not None and spec.states and spec.states.owner is StateOwner.DECISION:
            derived[uid]["verified"] = [{"by": a, "at": ev.at} for a in ev.payload.get("approvals") or []]
        if spec is None or not spec.states or spec.states.owner is not StateOwner.RENDER:
            continue
        dv = derived[uid]
        nxt = spec.states.by_event(dv["state"], ev.kind, ev.to)
        if nxt is None:
            if ev.kind in (EventKind.PR_OPENED, EventKind.PR_MERGED, EventKind.CI_GATE, EventKind.JIRA_STATUS) or ev.to:
                anomalies.append(Anomaly(AnomalyKind.ILLEGAL_TRANSITION, uid,
                                         f"{dv['state']} -> {ev.to or ev.kind.value} por {ev.kind.value}", ev.source))
            continue
        dv["state"] = nxt
        pr = ev.payload.get("pr") or (ev.refs[0] if ev.refs else None)
        if pr:
            dv["pr"] = str(pr)
        if ev.kind is EventKind.PR_OPENED and spec.name == "Slice":
            dv["builder"] = ev.actor
        if ev.payload.get("audit"):
            dv["audit"] = str(ev.payload["audit"])
        if ev.kind is EventKind.JIRA_STATUS:
            if nxt == "blocked" and ev.payload.get("by"):
                dv["blocked_by"] = str(ev.payload["by"])
            elif nxt != "blocked":
                dv.pop("blocked_by", None)
        if ev.kind is EventKind.PR_MERGED:
            dv["verified"] = [{"by": a, "at": ev.at} for a in ev.payload.get("approvals") or []]

    concepts: dict[str, Concept] = {}
    for uid, (d, spec) in base.items():
        dv = derived.get(uid, {})
        if spec is not None and spec.states:
            st = dv.get("state") or d.frontmatter.get("state") or spec.states.initial
            status = spec.states.status_of.get(str(st))
            if status is not None:
                dv["status"] = status.value
        concepts[uid] = Concept(d, spec, dv, tuple(history.get(uid, ())))
    return View(concepts, {c.path: u for u, c in concepts.items()}, by_jira, tuple(anomalies), kb_sha,
                sum(1 for e, _ in events if e.pending), tuple(e for e, _ in events))
