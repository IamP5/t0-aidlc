"""Shapes of the one profile table. No data here; data lives in table.py.

Everything that lists types, fields, states, gates, tracks, event kinds or checks anywhere in the
toolkit (validation, templates, index sections, derived-key guard, profile.md) is derived from the
table. A second hand-written list is a bug.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Lane(Enum):
    RECORDS = "records"       # add-only, uniquely named, no human review
    KNOWLEDGE = "knowledge"   # draft PR with CODEOWNERS
    DERIVED = "derived"       # only kb-render writes


class Status(Enum):           # OKF §5.4, derived from state
    DRAFT = "draft"
    STABLE = "stable"
    DEPRECATED = "deprecated"


class Kind(Enum):
    STR = "str"; TEXT = "text"; INT = "int"; BOOL = "bool"
    INSTANT = "instant"; DURATION = "duration"; ACTOR = "actor"; PATH = "path"; UID = "uid"
    ENUM = "enum"; LIST_STR = "list[str]"; LIST_ACTOR = "list[actor]"
    MAP = "map"; LIST_MAP = "list[map]"; JIRA_KEY = "jira-key"


@dataclass(frozen=True)
class Field:
    name: str
    kind: Kind
    required: bool = False
    enum: tuple[str, ...] = ()
    derived: bool = False          # written only by kb-render; hooks and check reject hand edits
    doc_pt: str = ""


class EventKind(Enum):
    """`kind` of a Step record (records lane)."""
    PROGRESS = "progress"; DECISION = "decision"; BLOCKER = "blocker"; KILL = "kill"
    HANDOFF = "handoff"; SESSION = "session"
    PR_OPENED = "pr-opened"; PR_MERGED = "pr-merged"; CI_GATE = "ci-gate"
    JIRA_LINKED = "jira-linked"; JIRA_STATUS = "jira-status"; INTEGRATION = "integration"


class StateOwner(Enum):
    DECISION = "decision"     # `state`/`verified` change only in the decision PR (t0 gate, t0 idea, t0 bet ship)
    RENDER = "render"         # after the authored initial state, kb-render folds `state` from records


@dataclass(frozen=True)
class Transition:
    from_states: frozenset[str]
    to: str
    via_gate: str | None = None
    via_event: EventKind | None = None
    via_command: str | None = None


@dataclass(frozen=True)
class StateMachine:
    initial: str
    transitions: tuple[Transition, ...]
    status_of: Mapping[str, Status]
    owner: StateOwner = StateOwner.DECISION

    def allows(self, frm: str, to: str) -> bool:
        return any(frm in t.from_states and t.to == to for t in self.transitions)

    def by_event(self, frm: str, kind: EventKind, to: str | None) -> str | None:
        if to is None and kind in (EventKind.DECISION, EventKind.JIRA_STATUS):
            return None
        for t in self.transitions:
            if t.via_event is kind and frm in t.from_states and (to is None or t.to == to):
                return t.to
        return None


@dataclass(frozen=True)
class IdScheme:
    """seq: 'BET-{n:03}' numbered by max existing + 1 across main and every branch.
    slug: from the title. unique: '<utc-ts>-<handle>-<repo|kb>-<rand4>' (records). fixed: path has no id."""
    style: str
    pattern: str = ""


@dataclass(frozen=True)
class TypeSpec:
    name: str
    slug: str
    paths: tuple[str, ...]                   # '/products/{product}/bets/{bet}/bet.md'; () = any path
    lane: Lane
    fields: tuple[Field, ...]
    states: StateMachine | None = None
    stale_required: bool = False
    ids: IdScheme = IdScheme("slug")
    index_section_pt: str = ""
    template_body_pt: str = ""


class CheckId(Enum):
    """Closed set of gate checks. gates.CHECKS implements every member."""
    BET_FIELDS_COMPLETE = "bet_fields_complete"
    RAPIDA_SLICE_COMPLETE = "rapida_slice_complete"
    BET_ACTIVE = "bet_active"
    MARKERS_ZERO = "markers_zero"
    ACCEPTANCE_BULLETS = "acceptance_bullets"
    VERIFY_HOW_PRESENT = "verify_how_present"
    SLICES_READY = "slices_ready"


class GateWriter(Enum):
    HUMAN_PR = "human-pr"       # the gate writes state + verified into the decision PR; approving it decides


@dataclass(frozen=True)
class Move:
    type_name: str
    to: str
    scope: str = "target"       # 'target' | 'bet-children:<Type>'


class LeadWhen(Enum):
    CROSS_POD = "cross-pod"
    TIER2 = "tier2"
    APPETITE_OVER = "appetite-over"   # appetite above ApproverRule.appetite_limit


@dataclass(frozen=True)
class ApproverRule:
    roles: tuple[str, ...]                     # 'bet_owner' (= Bet.decision_by), 'lead', 'flow_steward'
    lead_when: tuple[LeadWhen, ...] = ()
    appetite_limit: str = "P1W"


@dataclass(frozen=True)
class GateSpec:
    id: str
    title_pt: str
    target_type: str
    moves: tuple[Move, ...]
    checks: tuple[CheckId, ...]
    approvers: ApproverRule
    writer: GateWriter = GateWriter.HUMAN_PR


@dataclass(frozen=True)
class TrackSpec:
    """A bet track (DESIGN §2). Attribute names match gen.profile_md's table."""
    name: str                                  # rapida | bet
    gates: tuple[str, ...]
    artifacts: tuple[str, ...]
    appetite_max: str
    tier_default: int
    eval_required: bool
    required_fields: tuple[str, ...] = ()      # Bet keys the aposta gate requires on this track
