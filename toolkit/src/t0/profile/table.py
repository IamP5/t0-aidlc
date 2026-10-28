"""THE profile table (t0-team). Single source for types, fields, state machines, gates, bet types.

Self-tests (tests/test_table.py) assert, at build time:
- every StateMachine maps every state to a Status, every Transition has exactly one of via_gate/via_event,
  every via_gate names a GATES id, every state is reachable from `initial`;
- every GateSpec.moves[*] is a legal transition of that type's machine (from some state, via that gate);
- every gate id appears in at least one BET_TYPES[*].gates, or is a product gate (G7, G8);
- every CheckId has an implementation in gates.CHECKS and every on_create names a write.SCAFFOLDS entry;
- every path pattern is unique per type and no two types' patterns overlap (path -> type is a function);
- PROFILE_VERSION bumps (major) whenever a field is removed or a state renamed (golden of the table).

Abbreviated below for non-load-bearing types ("..." in fields); the full table is mechanical transcription
of methodology §5.4 + workspace-pattern §2.2/§4.
"""
from __future__ import annotations

from .spec import (
    ApproverRule, BetTypeSpec, CheckId as C, EventKind as E, Field as F, GateSpec, GateWriter,
    IdScheme, Kind as K, Lane, Move, StalePolicy, Staleness, StateMachine, Status as S,
    Transition as T, TypeSpec,
)

PROFILE = "t0-team"
PROFILE_VERSION = "0.2"     # 0.1 was the research proposal; 0.2 adds Step/Gate/Changeset/Workspace + derived keys

# Common keys. `state`, `status`, `verified` are DERIVED on every type that has a state machine.
COMMON_FIELDS: tuple[F, ...] = (
    F("type", K.STR, required=True),
    F("title", K.STR, required=True, doc_pt="Título curto"),
    F("description", K.STR, required=True, doc_pt="Uma frase; vira a linha do index"),
    F("tags", K.LIST_STR),
    F("uid", K.UID, required=True, doc_pt="Id estável, kebab-case, único no bundle"),
    F("owner", K.ACTOR, required=True),
    F("generated", K.MAP, required=True),
    F("relations", K.MAP),
    F("stale_after", K.INSTANT),
)
STATEFUL_DERIVED: tuple[F, ...] = (
    F("state", K.ENUM, derived=True),
    F("status", K.ENUM, enum=("draft", "stable", "deprecated"), derived=True),
    F("verified", K.LIST_MAP, derived=True),
)

_D, _ST, _DEP = S.DRAFT, S.STABLE, S.DEPRECATED


def _sm(initial: str, status: dict[str, S], *ts: T) -> StateMachine:
    return StateMachine(initial, tuple(ts), status)


def _t(frm: str, to: str, *, gate: str | None = None, event: E | None = None) -> T:
    return T(frozenset(frm.split("|")), to, gate, event)


TYPES: tuple[TypeSpec, ...] = (
    # ---------------------------------------------------------------- cycle artifacts
    TypeSpec(
        "Idea", "idea", ("/ideas/{id}.md",), Lane.RECORDS,
        fields=(F("source", K.ENUM, True, ("human", "squad", "transcript", "jira")),
                F("product", K.STR), F("bet", K.UID, derived=True)),
        states=_sm("new", {"new": _D, "triaged": _ST, "parked": _ST, "rejected": _DEP, "promoted": _ST},
                   _t("new", "triaged", gate="G0"),
                   _t("new|triaged", "parked", gate="G0"),
                   _t("new|triaged", "rejected", gate="G0"),
                   _t("triaged", "promoted", event=E.TRANSITION)),   # emitted by `t0 new bet --from IDEA`
        ids=IdScheme("seq", "IDEA-{n:04}-{slug}"),
        index_section_pt="Ideias",
        template_body_pt="## Problema\n\n## Para quem\n\n## Evidência\n",
    ),
    TypeSpec(
        "Bet", "bet", ("/products/{product}/bets/{bet}/bet.md",), Lane.KNOWLEDGE,
        fields=(F("bet_type", K.ENUM, True, ("exploratoria", "entrega", "bugfix", "plataforma")),
                F("appetite", K.DURATION, True), F("hypothesis", K.TEXT), F("kill_criteria", K.TEXT),
                F("success_metric", K.TEXT), F("cycle_start", K.INSTANT), F("cycle_end", K.INSTANT),
                F("decision_by", K.ACTOR, True), F("tier_default", K.INT),
                F("jira", K.JIRA_KEY, derived=True)),
        states=_sm("proposed", {"proposed": _D, "active": _ST, "shipped": _ST, "killed": _DEP, "extended": _ST},
                   _t("proposed|extended", "active", gate="G1"),
                   _t("active", "shipped", gate="G6"),    # G6 gate file carries `to:` (one of three)
                   _t("active", "killed", gate="G6"),
                   _t("active", "extended", gate="G6"),
                   _t("active", "shipped", gate="G5")),   # bugfix only: the CI G5 record closes the bet
        stale=Staleness(StalePolicy.FROM_FIELD, "cycle_end"),
        ids=IdScheme("seq", "BET-{n:03}"),
        index_section_pt="Bets",
        template_body_pt="## Problema\n\n## Para quem\n\n## Apetite e critério de kill\n\n## Fora de escopo\n",
        # no on_create: log.md, changeset.md and index.md of the bet folder are DERIVED (kb-render).
    ),
    TypeSpec(
        "Bugfix", "bugfix", ("/products/{product}/bets/{bet}/bugfix.md",), Lane.KNOWLEDGE,
        fields=(F("current", K.TEXT, True), F("expected", K.TEXT, True), F("unchanged", K.LIST_STR, True)),
        states=_sm("draft", {"draft": _D, "approved": _ST}, _t("draft", "approved", gate="G1")),
        ids=IdScheme("fixed"), index_section_pt="Bugfix",
        on_create="bugfix_single_slice",   # bet-new bugfix: Bet + Bugfix + slices/01-fix.md in ONE knowledge PR
    ),
    TypeSpec(
        "Assessment", "assessment", ("/products/{product}/bets/{bet}/assessment.md",), Lane.KNOWLEDGE,
        fields=(F("prototypes", K.LIST_MAP, True), F("verdict", K.ENUM, True, ("go", "needs-clarification", "kill")),
                F("kill_reason", K.TEXT)),
        ids=IdScheme("fixed"), index_section_pt="Assessments",
    ),
    TypeSpec(
        "Spec", "spec", ("/products/{product}/bets/{bet}/spec.md", "/products/{product}/spec.md"), Lane.KNOWLEDGE,
        fields=(F("bet", K.UID), F("acceptance", K.LIST_STR, True), F("verify_how", K.TEXT, True),
                F("seams", K.LIST_STR), F("tier", K.INT, True), F("markers_open", K.INT, derived=True)),
        # markers_open is DERIVED (counted from body by render) -> nobody can "set it to 0".
        states=_sm("draft", {"draft": _D, "approved": _ST, "frozen": _ST, "superseded": _DEP},
                   _t("draft", "approved", gate="G2"),
                   _t("approved", "frozen", event=E.TRANSITION),          # bet-ship
                   _t("approved", "superseded", event=E.TRANSITION)),     # product live spec
        ids=IdScheme("fixed"), index_section_pt="Specs",
        template_body_pt="## Contexto\n\n## Critérios de aceite\n\n- \n\n## Como verificar\n\n## Costuras (seams)\n\n## Fora de escopo\n",
    ),
    TypeSpec(
        "Plan", "plan", ("/products/{product}/bets/{bet}/plan.md",), Lane.KNOWLEDGE,
        fields=(F("bolts", K.LIST_MAP, True), F("checks", K.MAP, True), F("integration", K.STR)),
        states=_sm("draft", {"draft": _D, "approved": _ST}, _t("draft", "approved", gate="G3")),
        ids=IdScheme("fixed"), index_section_pt="Planos",
    ),
    TypeSpec(
        "Contract", "contract", ("/products/{product}/contracts/{slug}.md",), Lane.KNOWLEDGE,
        fields=(F("surface", K.ENUM, True, ("mcp", "cli", "skill", "api")), F("version", K.STR, True),
                F("consumers", K.LIST_STR), F("breaking_requires", K.STR)),
        states=_sm("proposed", {"proposed": _D, "approved": _ST, "published": _ST, "deprecated": _DEP},
                   _t("proposed", "approved", gate="G3"),
                   _t("approved", "published", event=E.TRANSITION),
                   _t("published", "deprecated", event=E.TRANSITION)),
        index_section_pt="Contratos",
    ),
    TypeSpec(
        "Slice", "slice", ("/products/{product}/bets/{bet}/slices/{slice}.md",), Lane.KNOWLEDGE,
        fields=(F("bet", K.UID, True), F("bolt", K.STR), F("repo", K.STR, True), F("tier", K.INT, True),
                F("acceptance", K.LIST_STR, True), F("verify_how", K.TEXT, True), F("depends_on", K.LIST_UID),
                F("mode", K.ENUM, enum=("tutor",)),
                F("jira", K.JIRA_KEY, derived=True), F("pr", K.STR, derived=True),
                F("audit", K.STR, derived=True), F("blocked_by", K.STR, derived=True)),
        states=_sm("proposed",
                   {"proposed": _D, "ready": _ST, "building": _ST, "in-review": _ST, "done": _ST,
                    "blocked": _ST, "conflict": _ST},
                   _t("proposed", "ready", gate="G3"),
                   _t("proposed", "ready", gate="G1"),                    # bugfix single slice
                   _t("ready", "building", event=E.PR_OPENED),
                   _t("building", "in-review", gate="G4"),
                   _t("in-review", "done", gate="G5"),
                   _t("ready|building|in-review", "blocked", event=E.JIRA_STATUS),
                   _t("blocked", "ready", event=E.JIRA_STATUS),   # unblock returns to ready; PR_OPENED re-enters building
                   _t("ready|building|in-review|done", "conflict", event=E.JIRA_STATUS)),
        ids=IdScheme("seq", "{n:02}-{slug}"), index_section_pt="Slices",
        template_body_pt="## O que muda\n\n## Critérios de aceite\n\n- \n\n## Como verificar\n",
    ),
    TypeSpec(
        "ADR", "adr", ("/methodology/adr/{id}.md", "/products/{product}/adr/{id}.md"), Lane.KNOWLEDGE,
        fields=(F("number", K.INT, True), F("deciders", K.LIST_ACTOR, True), F("decided_at", K.INSTANT)),
        states=_sm("proposed", {"proposed": _D, "accepted": _ST, "superseded": _DEP, "rejected": _DEP},
                   _t("proposed", "accepted", event=E.GATE_APPROVED),   # merge of the ADR's knowledge PR
                   _t("proposed", "rejected", event=E.TRANSITION),
                   _t("accepted", "superseded", event=E.TRANSITION)),      # emitted when a new ADR supersedes
        ids=IdScheme("seq", "ADR-{n:04}-{slug}"), index_section_pt="Decisões (ADR)",
    ),
    # ---------------------------------------------------------------- event + derived types
    TypeSpec(
        "Step", "step",
        ("/products/{product}/bets/{bet}/steps/{unique}.md", "/cycles/{cycle}/steps/{unique}.md"), Lane.RECORDS,
        fields=(F("kind", K.ENUM, True, tuple(e.value for e in E if e is not E.GATE)),
                F("bet", K.STR), F("story", K.JIRA_KEY), F("repo", K.STR), F("refs", K.LIST_STR),
                F("target", K.UID), F("to", K.STR), F("dedup", K.STR), F("on_behalf_of", K.ACTOR),
                F("payload", K.MAP)),
        ids=IdScheme("unique"), index_section_pt="Registros",
    ),
    TypeSpec(
        "Gate", "gate", ("/products/{product}/bets/{bet}/gates/{gate}.md", "/ideas/gates/{idea}-G0.md",
                         "/products/{product}/gates/{gate}-{n}.md"), Lane.KNOWLEDGE,
        fields=(F("gate", K.ENUM, True, ("G0", "G1", "G2", "G3", "G6", "G7", "G8")),
                F("target", K.UID, True), F("to", K.STR), F("requested_by", K.ACTOR, True),
                F("evidence", K.LIST_MAP, True)),   # snapshot of check results at request time
        ids=IdScheme("fixed"), index_section_pt="Gates",
    ),
    TypeSpec("Changeset", "changeset", ("/products/{product}/bets/{bet}/changeset.md",), Lane.DERIVED,
             fields=(F("changes", K.LIST_MAP, derived=True), F("tested_together", K.MAP, derived=True))),
    TypeSpec("Log", "log", ("/log.md", "/products/{product}/bets/{bet}/log.md"), Lane.DERIVED, fields=()),
    # ---------------------------------------------------------------- rituals, cycles, team, product
    TypeSpec("Ritual", "ritual", ("/methodology/rituals/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("cadence", K.STR, True), F("duration", K.DURATION, True), F("facilitator", K.ACTOR, True),
                     F("participants", K.LIST_ACTOR), F("inputs", K.LIST_MAP, True), F("outputs", K.LIST_STR),
                     F("command", K.STR, True), F("cancel_rule", K.TEXT), F("recorded", K.BOOL, True)),
             stale=Staleness(StalePolicy.REQUIRED)),
    TypeSpec("Ritual Record", "ritual-record", ("/cycles/{cycle}/rituals/{date}-{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("ritual", K.UID, True), F("date", K.INSTANT, True), F("facilitator", K.ACTOR, True),
                     F("attended", K.LIST_ACTOR), F("decisions", K.LIST_MAP), F("transcript", K.PATH),
                     F("cancelled", K.TEXT))),
    TypeSpec("Transcript", "transcript", ("/cycles/{cycle}/transcripts/{date}-{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("ritual", K.UID, True), F("redaction", K.STR, True), F("off_record_spans", K.INT, True),
                     F("participants", K.LIST_ACTOR)),
             stale=Staleness(StalePolicy.TTL, ttl="P180D", policy_uid="policy-transcript-retention")),
    TypeSpec("Cycle Record", "cycle", ("/cycles/{cycle}/cycle.md",), Lane.KNOWLEDGE,
             fields=(F("bets", K.LIST_UID), F("archetypes", K.LIST_MAP), F("rotations", K.LIST_MAP),
                     F("tutor_slices", K.LIST_UID)),
             states=_sm("active", {"active": _ST, "closed": _ST}, _t("active", "closed", event=E.TRANSITION))),
    TypeSpec("Metric Snapshot", "metrics", ("/cycles/{cycle}/report.md", "/cycles/{cycle}/digests/{date}.md",
                                            "/harness/trust.md", "/harness/budget.md"), Lane.KNOWLEDGE,
             fields=(F("period", K.STR, True), F("metrics", K.MAP, True), F("source", K.STR, True))),
    TypeSpec("Product", "product", ("/products/{product}/product.md",), Lane.KNOWLEDGE,
             fields=(F("stage", K.ENUM, True, ("pre-pmf", "crescimento", "maduro")),
                     F("adoption_stage", K.INT, derived=True), F("eval_owner", K.ACTOR),
                     F("domain_contacts", K.LIST_ACTOR), F("repos", K.LIST_STR, True)),
             states=_sm("discovery", {"discovery": _D, "live": _ST, "sunset": _DEP},
                        _t("discovery", "live", event=E.TRANSITION), _t("live", "sunset", event=E.TRANSITION))),
    TypeSpec("Workspace", "workspace", ("/products/{product}/workspace.md",), Lane.KNOWLEDGE,
             fields=(F("workspace", K.MAP, True),)),
    TypeSpec("Adoption Report", "adoption", ("/products/{product}/adoption/{week}.md",), Lane.KNOWLEDGE,
             fields=(F("adoption_stage", K.INT, True), F("wau", K.INT), F("target_cohort", K.INT),
                     F("retention_4w", K.STR), F("repeat_use", K.STR)),
             states=_sm("open", {"open": _D, "passed": _ST, "failed": _ST},
                        _t("open", "passed", event=E.TRANSITION), _t("open", "failed", event=E.TRANSITION))),
    TypeSpec("Eval Suite", "evals", ("/products/{product}/evals.md",), Lane.KNOWLEDGE,
             fields=(F("repo_path", K.STR, True), F("metric", K.ENUM, True, ("pass@1", "pass^3")),
                     F("regression_size", K.INT, derived=True), F("regression_pass", K.STR, derived=True),
                     F("last_run", K.INSTANT, derived=True))),
    TypeSpec("Harness Item", "harness", ("/harness/{id}.md",), Lane.KNOWLEDGE,
             fields=(F("pattern", K.TEXT, True), F("ladder_step", K.ENUM, enum=("sensor", "area-rule", "skill", "agents-md")),
                     F("occurrences", K.LIST_STR, derived=True), F("pr", K.STR)),
             states=_sm("open", {"open": _D, "fixed": _ST, "wontfix": _DEP},
                        _t("open", "fixed", event=E.TRANSITION), _t("open", "wontfix", event=E.TRANSITION)),
             ids=IdScheme("seq", "HI-{n:04}")),
    TypeSpec("Rotation", "rotation", ("/team/rotations/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("role", K.PATH, True), F("cadence", K.DURATION, True), F("roster", K.LIST_ACTOR, True),
                     F("assignments", K.LIST_MAP, True)),
             stale=Staleness(StalePolicy.REQUIRED)),
    TypeSpec("Policy", "policy", ("/methodology/policies/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("effective_from", K.INSTANT), F("approved_by", K.ACTOR), F("thresholds", K.MAP)),
             # thresholds: the ONLY home of gate numbers (adoption floors, eval >=95%, trust 20 PRs, retention 180d)
             states=_sm("proposed", {"proposed": _D, "in-force": _ST, "retired": _DEP},
                        _t("proposed", "in-force", event=E.GATE_APPROVED), _t("in-force", "retired", event=E.TRANSITION)),
             stale=Staleness(StalePolicy.REQUIRED)),
    TypeSpec("OKF Profile", "profile", ("/profile.md",), Lane.DERIVED,   # body+keys generated by `t0 gen`
             fields=(F("profile", K.STR, True), F("profile_version", K.STR, True),
                     F("timestamps", K.STR, True), F("link_style", K.STR, True))),
    # Person, Role Archetype, Accountability, Principle, Practice, Playbook, Glossary Term, PI Outcome,
    # Research, Reference: transcribed from methodology §5.4 / okf.md §5.4, same pattern ...
)

# ---------------------------------------------------------------- gates (methodology §2.2)
_OWNER = ApproverRule(("bet_owner",))
GATES: tuple[GateSpec, ...] = (
    GateSpec("G0", "Ideia triada", "Idea", (Move("Idea", "triaged"),), (),
             ApproverRule(("lead|aiva",)), GateWriter.HUMAN_PR),
    GateSpec("G1", "Bet apostada", "Bet",
             (Move("Bet", "active"), Move("Bugfix", "approved", "bet-children:Bugfix"),
              Move("Slice", "ready", "bet-children:Slice")),          # last two only for bugfix bets
             (C.BET_FIELDS_COMPLETE, C.BUGFIX_UNCHANGED_LISTED),
             ApproverRule(("lead",)),                                   # bugfix: flow_steward (BetTypeSpec override below)
             GateWriter.HUMAN_PR),
    GateSpec("G2", "Spec aprovado", "Spec", (Move("Spec", "approved"),),
             (C.MARKERS_ZERO, C.ACCEPTANCE_BULLETS, C.VERIFY_HOW_PRESENT),
             ApproverRule(("bet_owner", "domain_expert?"), tier2_adds=("lead",), junior_owner_adds=("preceptor",)),
             GateWriter.HUMAN_PR),
    GateSpec("G3", "Pronto para construir", "Plan",
             (Move("Plan", "approved"), Move("Contract", "approved", "bet-children:Contract"),
              Move("Slice", "ready", "bet-children:Slice")),
             (C.PLAN_CHECKS_PASS, C.CONTRACT_APPROVED_IF_SURFACE, C.SLICES_READY_WITH_JIRA, C.ACCEPTANCE_BULLETS),
             _OWNER, GateWriter.HUMAN_PR),
    GateSpec("G4", "Pronto para review", "Slice", (Move("Slice", "in-review"),),
             (C.CI_GREEN, C.REVIEW_AGENT_CLEAN), ApproverRule(()), GateWriter.CI),
    GateSpec("G5", "Merge (DoD)", "Slice", (Move("Slice", "done"),),
             (C.PR_APPROVALS_BY_TIER, C.AUDIT_TRAIL_PRESENT, C.TRACE_CHAIN_COMPLETE), ApproverRule(()), GateWriter.CI),
    GateSpec("G6", "Bet encerrada", "Bet", (Move("Bet", "{to}"),),      # {to} in {shipped,killed,extended}, from gate file
             (C.ALL_SLICES_DONE, C.ASSESSMENT_VERDICT), ApproverRule(("bet_owner", "lead")), GateWriter.HUMAN_PR),
    GateSpec("G7", "Degrau 1 -> 2", "Product", (Move("Product", "adoption_stage:2", "product"),),
             (C.ADOPTION_PASSED, C.EVAL_REGRESSION_PASS), ApproverRule(("aiva", "eval_owner")),
             GateWriter.HUMAN_PR, policy_uid="policy-adoption-floors"),
    GateSpec("G8", "Degrau 2 -> 3", "Product", (Move("Product", "adoption_stage:3", "product"),),
             (C.ADOPTION_PASSED, C.EVAL_REGRESSION_PASS), ApproverRule(("aiva", "lead", "eval_owner")),
             GateWriter.HUMAN_PR, policy_uid="policy-adoption-floors"),
)

# ---------------------------------------------------------------- bet types (methodology §2.3)
BET_TYPES: tuple[BetTypeSpec, ...] = (
    BetTypeSpec("exploratoria", ("G0", "G1", "G6"), ("Bet", "Assessment"), "P1W", 1, False),
    BetTypeSpec("entrega", ("G0", "G1", "G2", "G3", "G4", "G5", "G6"), ("Bet", "Spec", "Plan", "Slice"), "P2W", 1, False),
    BetTypeSpec("bugfix", ("G1", "G4", "G5"), ("Bet", "Bugfix", "Slice"), "P2D", 0, False),
    BetTypeSpec("plataforma", ("G0", "G1", "G2", "G3", "G4", "G5", "G6"),
                ("Bet", "Spec", "Plan", "Contract", "Slice"), "P2W", 2, True),
)
# Approver override that is data, not code: bugfix G1 is approved by the Flow Steward.
GATE_APPROVER_OVERRIDES: dict[tuple[str, str], ApproverRule] = {
    ("bugfix", "G1"): ApproverRule(("flow_steward",)),
}


class Registry:
    """Read-only index over TYPES/GATES/BET_TYPES. Built once at import; O(1) lookups."""

    def type_named(self, name: str) -> TypeSpec: raise NotImplementedError
    def type_for_slug(self, slug: str) -> TypeSpec: raise NotImplementedError
    def type_for_path(self, path: str) -> tuple[TypeSpec, dict[str, str]] | None:
        """Match path patterns; returns the spec and captured vars ({product, bet, ...})."""
        raise NotImplementedError
    def fields(self, t: TypeSpec) -> tuple[F, ...]:
        """COMMON_FIELDS + (STATEFUL_DERIVED if t.states) + t.fields, in serialization order."""
        raise NotImplementedError
    def derived_keys(self, t: TypeSpec) -> frozenset[str]: raise NotImplementedError
    def lane_for_write(self, path: str, *, creating: bool) -> Lane:
        """creating + type lane RECORDS -> RECORDS; reserved/derived files -> DERIVED; else KNOWLEDGE."""
        raise NotImplementedError
    def gate(self, gid: str) -> GateSpec: raise NotImplementedError
    def gates_for(self, bet_type: str) -> tuple[GateSpec, ...]: raise NotImplementedError
    def approvers(self, bet_type: str | None, gid: str) -> ApproverRule: raise NotImplementedError


REGISTRY = Registry()
