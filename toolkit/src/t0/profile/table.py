"""THE profile table (t0-team, v2). Single source for types, fields, state machines, gates and tracks.

Self-tests live in tests/test_profile.py: every state maps to a status, every via_gate names a gate,
every gate move is a legal transition, every CheckId has an implementation, path -> type is a function.
"""
from __future__ import annotations

import re
from functools import cached_property

from .spec import (
    ApproverRule, CheckId as C, EventKind as E, Field as F, GateSpec, IdScheme, Kind as K, Lane, LeadWhen,
    Move, StateMachine, StateOwner, Status as S, TrackSpec, Transition as T, TypeSpec,
)

PROFILE = "t0-team"
PROFILE_VERSION = "1.0"     # v2 methodology: G0..G8, bet types, Plan/Assessment/Bugfix/Contract removed

COMMON_FIELDS: tuple[F, ...] = (
    F("type", K.STR, required=True),
    F("title", K.STR, required=True, doc_pt="Título curto"),
    F("description", K.STR, required=True, doc_pt="Uma frase; vira a linha do index"),
    F("tags", K.LIST_STR),
    F("uid", K.UID, required=True, doc_pt="Id estável, kebab-case, único no bundle"),
    F("owner", K.ACTOR, required=True, doc_pt="Dono: human:, team:, role: ou process:"),
    F("generated", K.MAP, required=True, doc_pt="{ by: <ator>, at: <data com offset> }"),
    F("relations", K.MAP),
    F("stale_after", K.INSTANT),
)
STATEFUL_DERIVED: tuple[F, ...] = (
    F("state", K.ENUM, derived=True),
    F("status", K.ENUM, enum=("draft", "stable", "deprecated"), derived=True),
    F("verified", K.LIST_MAP, derived=True),
)

_D, _ST, _DEP = S.DRAFT, S.STABLE, S.DEPRECATED


def _sm(initial: str, status: dict[str, S], *ts: T, owner: StateOwner = StateOwner.DECISION) -> StateMachine:
    return StateMachine(initial, tuple(ts), status, owner)


def _t(frm: str, to: str, *, gate: str | None = None, event: E | None = None, cmd: str | None = None) -> T:
    return T(frozenset(frm.split("|")), to, gate, event, cmd)


# Body headings the toolkit reads; the body is their only home (matched ignoring case and accents).
ACCEPTANCE, VERIFY, RAPIDA_SECTIONS = "Critérios de aceite", "Como verificar", ("Atual", "Esperado", "Não muda")
_SLICE_BODY = "## O que muda\n\n## Critérios de aceite\n\n- \n\n## Como verificar\n"
RAPIDA_SLICE_BODY = ("## Atual\n\n## Esperado\n\n## Não muda\n\n- \n\n## Critérios de aceite\n\n- \n\n"
                     "## Como verificar\n\n<!-- o teste que fica vermelho hoje e verde depois -->\n")

TYPES: tuple[TypeSpec, ...] = (
    TypeSpec(
        "Idea", "idea", ("/ideas/{id}.md",), Lane.KNOWLEDGE,
        fields=(F("source", K.ENUM, True, ("human", "squad", "transcript", "jira"), doc_pt="De onde veio"),
                F("product", K.STR, doc_pt="Pod: dev-tooling, paco ou portal-metricas"),
                F("verdict", K.ENUM, enum=("segue", "ajusta", "mata"), doc_pt="Veredito do protótipo"),
                F("prototype_ref", K.STR, doc_pt="Onde está o protótipo (branch, gist, pasta fora do main)"),
                F("decided_at", K.INSTANT, doc_pt="Quando o veredito saiu"),
                F("bet", K.STR, doc_pt="BET-NNN quando a ideia virou bet")),
        states=_sm("new", {"new": _D, "prototyped": _ST, "promoted": _ST, "killed": _DEP},
                   _t("new|prototyped", "prototyped", cmd="idea prototype"),
                   _t("new|prototyped", "killed", cmd="idea prototype"),
                   _t("new|prototyped", "promoted", cmd="new bet")),
        ids=IdScheme("seq", "IDEA-{n:04}"), index_section_pt="Ideias",
        template_body_pt="## Problema\n\n## Para quem\n\n## Evidência\n",
    ),
    TypeSpec(
        "Bet", "bet", ("/products/{product}/bets/{bet}/bet.md",), Lane.KNOWLEDGE,
        fields=(F("track", K.ENUM, True, ("rapida", "bet"), doc_pt="rapida: um slice, sem spec; bet: protótipo, spec, slices"),
                F("appetite", K.DURATION, True, doc_pt="ISO 8601: rapida até P1D, bet até P2W"),
                F("hypothesis", K.TEXT, doc_pt="Se fizermos X, Y acontece"),
                F("kill_criteria", K.TEXT, doc_pt="O que faz a gente parar"),
                F("success_metric", K.TEXT, doc_pt="Número e onde ele é medido"),
                F("decision_by", K.ACTOR, True, doc_pt="Quem aprova a aposta (Bet Owner, ou Flow Steward na rápida)"),
                F("idea", K.STR, doc_pt="IDEA-NNNN de origem"),
                F("pods", K.LIST_STR, doc_pt="Pods que a bet toca; mais de um exige o Lead"),
                F("tier", K.INT, doc_pt="Tier de review padrão (2 exige o Lead)"),
                F("cycle_end", K.INSTANT, doc_pt="Fim do apetite"),
                F("jira", K.JIRA_KEY, derived=True, doc_pt="Feature no Jira, gravada pelo sync")),
        states=_sm("proposed", {"proposed": _D, "active": _ST, "shipped": _ST, "killed": _DEP},
                   _t("proposed", "active", gate="aposta"),
                   _t("active", "shipped", cmd="bet ship"),
                   _t("proposed|active", "killed", cmd="log kill")),
        ids=IdScheme("seq", "BET-{n:03}"), index_section_pt="Bets",
        template_body_pt="## Intenção\n\n## Apetite e critério de kill\n\n## Fora de escopo\n\n## Aprendizado\n",
    ),
    TypeSpec(
        "Spec", "spec", ("/products/{product}/bets/{bet}/spec.md",), Lane.KNOWLEDGE,
        fields=(F("bet", K.STR, True, doc_pt="BET-NNN"),
                F("seams", K.LIST_STR, doc_pt="Costuras onde os testes entram"),
                F("tier", K.INT, True, doc_pt="0, 1 ou 2"),
                F("markers_open", K.INT, derived=True, doc_pt="[PRECISA ESCLARECER] abertos, contado pelo kb-render")),
        states=_sm("draft", {"draft": _D, "approved": _ST, "frozen": _ST},
                   _t("draft", "approved", gate="spec"),
                   _t("approved", "frozen", cmd="bet ship")),
        ids=IdScheme("fixed"), index_section_pt="Specs",
        template_body_pt=("## Contexto\n\n## Critérios de aceite\n\n- \n\n## Como verificar\n\n## Costuras\n\n"
                          "## Plano (opcional)\n\n## Design (opcional)\n\n## Fora de escopo\n"),
    ),
    TypeSpec(
        "Slice", "slice", ("/products/{product}/bets/{bet}/slices/{slice}.md",), Lane.KNOWLEDGE,
        fields=(F("bet", K.STR, True, doc_pt="BET-NNN"),
                F("repo", K.STR, True, doc_pt="Nome do repo no workspace.md; um slice é um repo e um PR"),
                F("tier", K.INT, True, doc_pt="0, 1 ou 2"),
                F("depends_on", K.LIST_STR, doc_pt="Slices (NN-slug) que entram antes"),
                F("jira", K.JIRA_KEY, derived=True, doc_pt="Story no Jira"),
                F("pr", K.STR, derived=True, doc_pt="PR do slice"),
                F("audit", K.STR, derived=True, doc_pt="Caminho do .audit/<KEY>.tsv"),
                F("builder", K.ACTOR, derived=True, doc_pt="Quem abriu o PR"),
                F("blocked_by", K.STR, derived=True)),
        states=_sm("ready",
                   {"ready": _ST, "building": _ST, "in-review": _ST, "done": _ST, "blocked": _ST, "conflict": _ST},
                   _t("ready|blocked", "building", event=E.PR_OPENED),
                   _t("building", "in-review", event=E.CI_GATE),
                   _t("ready|building|in-review", "done", event=E.PR_MERGED),
                   _t("ready|building|in-review", "blocked", event=E.JIRA_STATUS),
                   _t("blocked", "ready", event=E.JIRA_STATUS),
                   _t("ready|building|in-review|done", "conflict", event=E.JIRA_STATUS),
                   owner=StateOwner.RENDER),
        ids=IdScheme("seq", "{n:02}-{slug}"), index_section_pt="Slices", template_body_pt=_SLICE_BODY,
    ),
    TypeSpec(
        "ADR", "adr", ("/methodology/adr/{id}.md", "/products/{product}/adr/{id}.md"), Lane.KNOWLEDGE,
        fields=(F("number", K.INT, True), F("deciders", K.LIST_ACTOR, True, doc_pt="Quem decide"),
                F("decided_at", K.INSTANT)),
        states=_sm("proposed", {"proposed": _D, "accepted": _ST, "superseded": _DEP, "rejected": _DEP},
                   _t("proposed", "accepted", cmd="pr"), _t("proposed", "rejected", cmd="pr"),
                   _t("accepted", "superseded", cmd="pr")),
        ids=IdScheme("seq", "ADR-{n:04}-{slug}"), index_section_pt="Decisões (ADR)",
        template_body_pt="## Contexto\n\n## Decisão\n\n## Consequências\n\n## Alternativas\n",
    ),
    TypeSpec(
        "Ritual", "ritual", ("/rituals/{slug}/ritual.md",), Lane.KNOWLEDGE,
        fields=(F("cadence", K.STR, True), F("duration", K.DURATION, True), F("facilitator", K.ACTOR, True),
                F("participants", K.LIST_ACTOR), F("inputs", K.LIST_MAP, True, doc_pt="{id, source, desc}; source kb:<Tipo> chave=valor"),
                F("outputs", K.LIST_STR), F("command", K.STR, True), F("recorded", K.BOOL, True),
                F("transcribable", K.BOOL)),
        states=_sm("active", {"active": _ST, "paused": _ST, "retired": _DEP},
                   _t("active", "paused", cmd="pr"), _t("paused", "active", cmd="pr"),
                   _t("active|paused", "retired", cmd="pr")),
        index_section_pt="Rituais",
    ),
    TypeSpec(
        "Ritual Record", "ritual-record", ("/rituals/{slug}/{date}.md",), Lane.KNOWLEDGE,
        fields=(F("ritual", K.STR, True), F("date", K.INSTANT, True), F("facilitator", K.ACTOR, True),
                F("attended", K.LIST_ACTOR), F("decisions", K.LIST_MAP, doc_pt="{text, owner, due, kind}"),
                F("transcript", K.PATH), F("harness_accepted", K.LIST_STR), F("rotation", K.MAP)),
        index_section_pt="Registros de ritual",
    ),
    TypeSpec(
        "Transcript", "transcript", ("/transcripts/{name}.md",), Lane.KNOWLEDGE,
        fields=(F("ritual", K.STR, True), F("redaction", K.STR, True, doc_pt="Versão do redator"),
                F("off_record_spans", K.INT, True), F("participants", K.LIST_ACTOR)),
        stale_required=True, index_section_pt="Transcrições",
    ),
    TypeSpec(
        "Harness Item", "harness", ("/harness/{id}.md",), Lane.KNOWLEDGE,
        fields=(F("pattern", K.TEXT, True, doc_pt="O erro do agente, em uma frase"),
                F("ladder_step", K.ENUM, enum=("sensor", "area-rule", "skill", "agents-md")),
                F("occurrences", K.LIST_STR, doc_pt="Onde aconteceu (PR, KEY, sessão)"),
                F("accepted", K.BOOL, doc_pt="Aceito no Harness Health"),
                F("pr", K.STR, derived=True, doc_pt="PR do conserto, do registro `t0 ci HI-NNNN`")),
        states=_sm("open", {"open": _D, "fixed": _ST, "wontfix": _DEP},
                   _t("open", "open", event=E.PR_OPENED), _t("open", "fixed", event=E.PR_MERGED),
                   _t("open", "wontfix", event=E.DECISION),
                   owner=StateOwner.RENDER),
        ids=IdScheme("seq", "HI-{n:04}"), index_section_pt="Harness",
        template_body_pt="## O que o agente fez\n\n## O que devia ter feito\n\n## Degrau da escada\n",
    ),
    TypeSpec(
        "Product", "product", ("/products/{product}/product.md",), Lane.KNOWLEDGE,
        fields=(F("stage", K.ENUM, True, ("pre-pmf", "crescimento", "maduro")),
                F("adoption_stage", K.INT, doc_pt="1, 2 ou 3; muda só pelo gate degrau (v0.2)"),
                F("repos", K.LIST_STR, True), F("domain_contacts", K.LIST_ACTOR), F("eval_owner", K.ACTOR)),
        states=_sm("discovery", {"discovery": _D, "live": _ST, "sunset": _DEP},
                   _t("discovery", "live", cmd="pr"), _t("live", "sunset", cmd="pr")),
        index_section_pt="Produtos",
    ),
    TypeSpec("Workspace", "workspace", ("/products/{product}/workspace.md",), Lane.KNOWLEDGE,
             fields=(F("workspace", K.MAP, True),), index_section_pt="Workspaces"),
    TypeSpec("Eval Suite", "evals", ("/products/{product}/evals.md",), Lane.KNOWLEDGE,
             fields=(F("repo_path", K.STR, True), F("metric", K.ENUM, True, ("pass@1", "pass^3")),
                     F("regression_pass", K.STR), F("last_run", K.INSTANT)), index_section_pt="Evals"),
    TypeSpec(
        "Adoption Report", "adoption", ("/products/{product}/adoption/{week}.md",), Lane.KNOWLEDGE,
        fields=(F("adoption_stage", K.INT, True), F("wau", K.INT), F("retention_4w", K.STR), F("repeat_use", K.STR)),
        states=_sm("open", {"open": _D, "passed": _ST, "failed": _ST},
                   _t("open", "passed", cmd="gate degrau"), _t("open", "failed", cmd="gate degrau")),
        index_section_pt="Adoção",
    ),
    TypeSpec(
        "Policy", "policy", ("/methodology/policies/{slug}.md",), Lane.KNOWLEDGE,
        fields=(F("effective_from", K.INSTANT), F("approved_by", K.ACTOR),
                F("thresholds", K.MAP, doc_pt="Os números que os gates e o `t0` leem")),
        states=_sm("proposed", {"proposed": _D, "in-force": _ST, "retired": _DEP},
                   _t("proposed", "in-force", cmd="pr"), _t("in-force", "retired", cmd="pr")),
        stale_required=True, index_section_pt="Políticas",
    ),
    TypeSpec("Template", "template", ("/templates/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("template_for", K.STR, True, doc_pt="O tipo que este esqueleto cria"),
                     F("skeleton", K.MAP)), index_section_pt="Templates"),
    TypeSpec(
        "Person", "person", ("/team/people/{slug}.md",), Lane.KNOWLEDGE,
        fields=(F("handle", K.STR, True, doc_pt="Igual ao <handle> de human:<handle>"),
                F("pods", K.LIST_STR), F("roles", K.LIST_STR, doc_pt="Slugs de /team/roles/ fixos (lead, bet-owner)"),
                F("junior", K.BOOL)),
        states=_sm("active", {"active": _ST, "alumni": _DEP}, _t("active", "alumni", cmd="pr")),
        index_section_pt="Pessoas",
    ),
    TypeSpec("Role", "role", ("/team/roles/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("responsibilities", K.LIST_STR), F("rotates", K.BOOL),
                     F("holders", K.LIST_ACTOR, doc_pt="Quem tem o papel fixo (lead)")), index_section_pt="Papéis"),
    TypeSpec("Rotation", "rotation", ("/team/rotations/{slug}.md",), Lane.KNOWLEDGE,
             fields=(F("role", K.PATH, True), F("cadence", K.DURATION, True), F("roster", K.LIST_ACTOR, True),
                     F("assignments", K.LIST_MAP, True, doc_pt="{who, from, to}; a Demo acrescenta")),
             stale_required=True, index_section_pt="Rodízios"),
    TypeSpec("Glossary Term", "term", ("/glossary/{slug}.md", "/products/{product}/glossary/{slug}.md"), Lane.KNOWLEDGE,
             fields=(F("term", K.STR, True), F("term_en", K.STR), F("aliases", K.LIST_STR), F("avoid", K.LIST_STR),
                     F("scope", K.STR)), index_section_pt="Glossário"),
    TypeSpec(
        "Step", "step", ("/steps/{unique}.md", "/products/{product}/bets/{bet}/steps/{unique}.md"), Lane.RECORDS,
        fields=(F("kind", K.ENUM, True, tuple(e.value for e in E)),
                F("bet", K.STR), F("story", K.STR), F("repo", K.STR), F("refs", K.LIST_STR),
                F("target", K.STR), F("to", K.STR), F("dedup", K.STR), F("on_behalf_of", K.ACTOR),
                F("payload", K.MAP)),
        ids=IdScheme("unique"), index_section_pt="Registros",
    ),
    # OKF's own types and the profile concept
    TypeSpec("Reference", "reference", (), Lane.KNOWLEDGE, fields=(), index_section_pt="Referência"),
    TypeSpec("Log", "log", (), Lane.DERIVED, fields=()),
    TypeSpec("OKF Profile", "profile", ("/profile.md",), Lane.DERIVED,
             fields=(F("profile", K.STR, True), F("profile_version", K.STR, True),
                     F("timestamps", K.STR, True), F("link_style", K.STR, True))),
)

DOMAIN_TYPES = tuple(t.name for t in TYPES if t.name not in ("Reference", "Log", "OKF Profile"))

# ---------------------------------------------------------------- the two v0.1 decisions (methodology §2.2)
GATES: tuple[GateSpec, ...] = (
    GateSpec("aposta", "Aposta", "Bet",
             (Move("Bet", "active"),),
             (C.BET_FIELDS_COMPLETE, C.RAPIDA_SLICE_COMPLETE),
             ApproverRule(("bet_owner",), (LeadWhen.CROSS_POD, LeadWhen.TIER2, LeadWhen.APPETITE_OVER), "P1W")),
    GateSpec("spec", "Spec aprovado", "Spec",
             (Move("Spec", "approved"),),
             (C.BET_ACTIVE, C.MARKERS_ZERO, C.ACCEPTANCE_BULLETS, C.VERIFY_HOW_PRESENT, C.SLICES_READY),
             ApproverRule(("bet_owner",), (LeadWhen.TIER2,))),
)

TRACKS: tuple[TrackSpec, ...] = (
    TrackSpec("rapida", ("aposta",), ("Bet", "Slice"), "P1D", 1, False, ("appetite", "decision_by")),
    TrackSpec("bet", ("aposta", "spec"), ("Bet", "Spec", "Slice"), "P2W", 1, False,
              ("appetite", "decision_by", "hypothesis", "kill_criteria")),
)


def _pattern_re(p: str) -> re.Pattern[str]:
    out, pos = "", 0
    for m in re.finditer(r"\{(\w+)\}", p):
        out += re.escape(p[pos:m.start()]) + f"(?P<{m.group(1)}>[^/]+)"
        pos = m.end()
    return re.compile("^" + out + re.escape(p[pos:]) + "$")


class Registry:
    """Read-only index over TYPES/GATES/TRACKS."""

    @cached_property
    def _by_name(self) -> dict[str, TypeSpec]:
        return {t.name: t for t in TYPES}

    @cached_property
    def _patterns(self) -> list[tuple[TypeSpec, re.Pattern[str]]]:
        return [(t, _pattern_re(p)) for t in TYPES for p in t.paths]

    def type_named(self, name: str) -> TypeSpec | None:
        return self._by_name.get(name)

    def type_for_slug(self, slug: str) -> TypeSpec | None:
        return next((t for t in TYPES if t.slug == slug), None)

    def type_for_path(self, path: str) -> tuple[TypeSpec, dict[str, str]] | None:
        for t, rx in self._patterns:
            m = rx.match(path)
            if m:
                return t, m.groupdict()
        return None

    def path_ok(self, t: TypeSpec, path: str) -> bool:
        return not t.paths or any(rx.match(path) for tt, rx in self._patterns if tt is t)

    def fields(self, t: TypeSpec) -> tuple[F, ...]:
        return COMMON_FIELDS + (STATEFUL_DERIVED if t.states else ()) + t.fields

    def render_keys(self, t: TypeSpec) -> frozenset[str]:
        """Keys only kb-render writes: type-specific derived fields, `status` and `verified` (from approvals) for
        every machine, and `state` for RENDER machines."""
        keys = {f.name for f in t.fields if f.derived}
        if t.states:
            keys |= {"status", "verified"}
            if t.states.owner is StateOwner.RENDER:
                keys.add("state")
        return frozenset(keys)

    def derived_keys(self, t: TypeSpec) -> frozenset[str]:
        """Keys nobody edits by hand (hooks): render keys plus decision-owned state/verified."""
        return frozenset({f.name for f in t.fields if f.derived} | ({f.name for f in STATEFUL_DERIVED} if t.states else set()))

    def gate(self, gid: str) -> GateSpec | None:
        return next((g for g in GATES if g.id == gid), None)

    def track(self, name: str) -> TrackSpec | None:
        return next((t for t in TRACKS if t.name == name), None)


REGISTRY = Registry()
