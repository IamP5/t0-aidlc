"""The View: documents + fold(events). The single owner of every derived key.

Central invariant: for every concept c and every derived key k of c's type,
    materialized(c)[k] == fold(main)[c][k]
kb-render establishes it (render.materialize); kb check L1 verifies it; hooks forbid hand edits of k.

Event sources (both are plain OKF documents):
  - Step records (records lane): kind in EventKind, `target` uid, optional `to`, `dedup` key.
  - Gate files `.../gates/<G>.md` on main (knowledge lane): presence == human approval of that gate.
    Approver identities arrive as a GATE_APPROVED Step written by the kb-render workflow from the
    merged PR's reviews; until then verified = [] and the concept shows `attestation: pending`.

Fold rules:
  - Events sorted by (at, path). Duplicate `dedup` keys -> first wins (idempotent re-emission).
  - A transition applies iff the table's StateMachine allows (current_state, to) via that gate/event;
    otherwise it becomes an Anomaly (never silently applied, never silently dropped).
  - JIRA_LINKED sets `jira` once; a second different key for the same uid -> Anomaly('jira-key-changed').
  - `markers_open` = count of '[PRECISA ESCLARECER]' in body (derived from content, not events).
  - `status` = StateMachine.status_of[state].
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Iterator, Mapping

from .okf.document import Actor, BundlePath, Document, Instant
from .profile.spec import EventKind, TypeSpec


@dataclass(frozen=True)
class Ref:
    """User-facing reference. Resolves, in order: uid, bundle path, Jira key (derived `jira`),
    KB id ('BET-042', 'IDEA-0057', 'ADR-0004'), 'BET-042/02' slice shorthand."""
    raw: str


@dataclass(frozen=True)
class Event:
    at: Instant
    actor: Actor
    kind: EventKind
    target: str               # uid
    to: str | None
    dedup: str                # idempotency key; default = path
    source: BundlePath
    payload: Mapping[str, Any]
    pending: bool = False     # True when it comes from the local spool overlay, not main


class AnomalyKind(Enum):
    ILLEGAL_TRANSITION = "illegal-transition"
    JIRA_KEY_CHANGED = "jira-key-changed"
    UNKNOWN_TARGET = "unknown-target"
    MATERIALIZED_DRIFT = "materialized-drift"   # on-disk derived key != fold
    GATE_WITHOUT_ATTESTATION = "gate-without-attestation"


@dataclass(frozen=True)
class Anomaly:
    kind: AnomalyKind
    target: str
    detail: str
    source: BundlePath


@dataclass(frozen=True)
class Concept:
    """A document plus its derived keys. Field access is checked against the table."""
    doc: Document
    spec: TypeSpec
    derived: Mapping[str, Any]
    history: tuple[Event, ...]     # events applied to this concept, in order (log.md is rendered from these)

    @property
    def uid(self) -> str: raise NotImplementedError
    @property
    def state(self) -> str | None: raise NotImplementedError

    def __getitem__(self, key: str) -> Any:
        """Derived keys come from `derived`, authored keys from frontmatter.
        KeyError if `key` is not a field of this type (catches typos at test time)."""
        raise NotImplementedError

    def trust(self) -> str:
        """OKF §5.3 tier: unverified | machine-confirmed | human-reviewed (from derived verified)."""
        raise NotImplementedError

    def stale(self, now: Instant) -> bool:
        """Reference is_stale semantics: requires 'T' + offset; date-only -> False."""
        raise NotImplementedError


@dataclass(frozen=True)
class View:
    concepts: Mapping[str, Concept]            # by uid
    by_path: Mapping[BundlePath, str]          # path -> uid
    by_jira: Mapping[str, str]                 # jira key -> uid
    anomalies: tuple[Anomaly, ...]
    kb_sha: str                                # sha of main the view was folded from
    pending: int                               # number of spool events overlaid

    def resolve(self, ref: Ref) -> Concept | None: raise NotImplementedError
    def children(self, bet_uid: str, type_name: str) -> tuple[Concept, ...]: raise NotImplementedError
    def bet_of(self, c: Concept) -> Concept | None: raise NotImplementedError
    def of_type(self, type_name: str) -> Iterator[Concept]: raise NotImplementedError


def events_from(docs: Iterable[Document]) -> tuple[list[Document], list[Event]]:
    """Split documents into concepts and events (Step + Gate types become Events too:
    a Step is both an OKF concept and an event; a Gate file is a concept and a GATE event)."""
    raise NotImplementedError


def fold(docs: Iterable[Document], *, kb_sha: str, overlay: Iterable[Event] = ()) -> View:
    """Pure. Same input -> same View. fold(docs + duplicate events) == fold(docs) (property test)."""
    # TODO:
    #   concepts = {uid: doc for non-event docs}; init derived state = spec.states.initial
    #   for ev in sorted(events + overlay, key=(at, path)):
    #       if ev.dedup in seen: continue
    #       apply(ev) via table transitions (gate events expand GateSpec.moves incl. bet-children scope)
    #       else Anomaly
    #   compute markers_open, status, jira, pr, audit, blocked_by, occurrences, adoption_stage
    #   compare with on-disk derived keys -> MATERIALIZED_DRIFT anomalies
    raise NotImplementedError
