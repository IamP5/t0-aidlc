"""Shapes of the one profile table. No data here; data lives in table.py.

Everything that lists types, fields, states, gates, bet types, event kinds or checks anywhere in
the toolkit (validation, templates, index sections, derived-key guard, profile.md, JSON schemas,
MCP enums, docs tables) is DERIVED from REGISTRY. A second hand-written list is a bug.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping


class Lane(Enum):
    RECORDS = "records"       # add-only, uniquely named, auto-merge PR, no human review
    KNOWLEDGE = "knowledge"   # PR with CODEOWNERS
    DERIVED = "derived"       # only kb-render writes (index.md, log.md, changeset.md, derived keys)


class Status(Enum):           # OKF spec §5.4; never stored by humans, derived from state
    DRAFT = "draft"
    STABLE = "stable"
    DEPRECATED = "deprecated"


class Kind(Enum):
    STR = "str"; TEXT = "text"; INT = "int"; BOOL = "bool"
    INSTANT = "instant"; DURATION = "duration"; ACTOR = "actor"; PATH = "path"; UID = "uid"
    ENUM = "enum"; LIST_STR = "list[str]"; LIST_ACTOR = "list[actor]"; LIST_UID = "list[uid]"
    MAP = "map"; LIST_MAP = "list[map]"; JIRA_KEY = "jira-key"


@dataclass(frozen=True)
class Field:
    name: str
    kind: Kind
    required: bool = False
    enum: tuple[str, ...] = ()
    derived: bool = False          # written ONLY by render.materialize; hooks+check reject edits
    doc_pt: str = ""               # one line, pt-BR; goes into profile.md and templates


class EventKind(Enum):
    """Kinds of Step records (records lane) plus GATE (knowledge lane gate files)."""
    PROGRESS = "progress"; DECISION = "decision"; BLOCKER = "blocker"; HANDOFF = "handoff"
    SESSION = "session"; PR_OPENED = "pr-opened"; PR_MERGED = "pr-merged"; PR_CLOSED = "pr-closed"
    JIRA_LINKED = "jira-linked"; JIRA_STATUS = "jira-status"; JIRA_COMMENT = "jira-comment"
    INTEGRATION = "integration"; CI_GATE = "ci-gate"; GATE_APPROVED = "gate-approved"
    TRANSITION = "transition"      # machine transition requested by a command (e.g. slice-build -> building)
    CREATED = "created"            # records-lane creation of an add-only concept (Idea, Harness occurrence)
    GATE = "gate"                  # a gates/<G>.md file present on main


@dataclass(frozen=True)
class Transition:
    from_states: frozenset[str]
    to: str
    via_gate: str | None = None              # 'G2' -> requires gate file on main
    via_event: EventKind | None = None       # e.g. TRANSITION, CI_GATE, JIRA_STATUS
    # Exactly one of via_gate / via_event. Validated by table self-test.


@dataclass(frozen=True)
class StateMachine:
    initial: str
    transitions: tuple[Transition, ...]
    status_of: Mapping[str, Status]           # every state must map; self-test enforces totality


class StalePolicy(Enum):
    NONE = "none"; REQUIRED = "required"; FROM_FIELD = "from-field"; TTL = "ttl"


@dataclass(frozen=True)
class Staleness:
    policy: StalePolicy
    source_field: str | None = None          # FROM_FIELD: e.g. 'cycle_end'
    ttl: str | None = None                   # TTL: ISO 8601 duration, e.g. 'P180D' (but the NUMBER is
                                             # read from a KB Policy when policy_uid is set)
    policy_uid: str | None = None


@dataclass(frozen=True)
class IdScheme:
    """How `t0 new` names the file and uid.
    SEQ: 'BET-{n:03}' numbered by max existing + 1 (collision -> PR conflict, retried by renumbering).
    SLUG: from title. UNIQUE: '<utc-ts>-<handle>-<rand4>' (records lane; never collides)."""
    style: str                               # 'seq' | 'slug' | 'unique' | 'fixed'
    pattern: str = ""


@dataclass(frozen=True)
class TypeSpec:
    name: str                                # OKF `type` string, e.g. 'Bet', 'Ritual Record'
    slug: str                                # CLI noun: `t0 new bet`
    paths: tuple[str, ...]                   # patterns: '/products/{product}/bets/{bet}/bet.md'
    lane: Lane                               # lane for CREATION; later edits of authored keys = KNOWLEDGE
    fields: tuple[Field, ...]                # type-specific; COMMON_FIELDS are prepended by REGISTRY
    states: StateMachine | None = None
    stale: Staleness = Staleness(StalePolicy.NONE)
    ids: IdScheme = IdScheme("slug")
    index_section_pt: str = ""               # heading in generated index.md
    template_body_pt: str = ""               # body skeleton for `t0 new` (headings, bullets, no Gherkin)
    on_create: str | None = None             # name of a scaffold in write.SCAFFOLDS (e.g. bugfix slice)


class CheckId(Enum):
    """Closed set of gate checks. gates.py must implement every member (self-test)."""
    MARKERS_ZERO = "markers_zero"
    ACCEPTANCE_BULLETS = "acceptance_bullets"        # list of bullets, no Gherkin keywords
    VERIFY_HOW_PRESENT = "verify_how_present"
    BET_FIELDS_COMPLETE = "bet_fields_complete"      # appetite, kill_criteria, cycle_end per bet_type
    BUGFIX_UNCHANGED_LISTED = "bugfix_unchanged_listed"
    PLAN_CHECKS_PASS = "plan_checks_pass"            # 4 checks pass | exception:<motivo>
    CONTRACT_APPROVED_IF_SURFACE = "contract_approved_if_surface"
    SLICES_READY_WITH_JIRA = "slices_ready_with_jira"
    CI_GREEN = "ci_green"                            # evidence passed by CI caller
    REVIEW_AGENT_CLEAN = "review_agent_clean"
    PR_APPROVALS_BY_TIER = "pr_approvals_by_tier"    # tier 1: 1 human not junior-only; tier 2: 2 humans incl. bet owner
    AUDIT_TRAIL_PRESENT = "audit_trail_present"
    TRACE_CHAIN_COMPLETE = "trace_chain_complete"    # tier 2 overlay
    ALL_SLICES_DONE = "all_slices_done"
    ASSESSMENT_VERDICT = "assessment_verdict"
    ADOPTION_PASSED = "adoption_passed"              # thresholds from KB Policy adoption-floors
    EVAL_REGRESSION_PASS = "eval_regression_pass"    # threshold from KB Policy eval-gate


class GateWriter(Enum):
    HUMAN_PR = "human-pr"       # t0 gate writes gates/<G>.md via knowledge PR; merge = approval
    CI = "ci"                   # t0 gate --ci emits a CI_GATE record via the KB-writer App


@dataclass(frozen=True)
class Move:
    """One state change a gate performs. G3 moves Plan, Contract(s) and all Slices at once."""
    type_name: str
    to: str
    scope: str = "target"      # 'target' | 'bet-children:<Type>' | 'product'


@dataclass(frozen=True)
class ApproverRule:
    roles: tuple[str, ...]                     # e.g. ('bet_owner', 'domain_expert?') ; '?' = when present
    tier2_adds: tuple[str, ...] = ()           # e.g. ('lead',)
    junior_owner_adds: tuple[str, ...] = ()    # e.g. ('preceptor',)
    junior_cannot_be_sole: bool = True


@dataclass(frozen=True)
class GateSpec:
    id: str                                    # 'G0'..'G8'
    title_pt: str
    target_type: str                           # the type a `t0 gate <G> <ref>` ref must resolve to (or its bet)
    moves: tuple[Move, ...]
    checks: tuple[CheckId, ...]
    approvers: ApproverRule
    writer: GateWriter
    policy_uid: str | None = None              # thresholds live in this KB Policy concept


@dataclass(frozen=True)
class BetTypeSpec:
    name: str                                  # exploratoria | entrega | bugfix | plataforma
    gates: tuple[str, ...]                     # the ONLY source of "which gates apply to which bet type"
    artifacts: tuple[str, ...]                 # type names created/required (Spec, Plan, Assessment, Bugfix...)
    appetite_max: str                          # ISO 8601 duration
    tier_default: int
    eval_required: bool


ScaffoldFn = Callable[..., object]             # see write.SCAFFOLDS; named, not referenced, to keep table pure
