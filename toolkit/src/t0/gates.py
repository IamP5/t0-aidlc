"""Gate evaluation. Pure. GateSpec (data) + CHECKS (one function per CheckId) + approver resolution.

`t0 gate aposta|spec <ref>` writes the decision into the decision PR: the target's `state` and `status`,
with the required approvers as reviewers. Approving that PR is the decision. `--ci` re-runs the same checks
at PR head. `verified` is never written here: `t0 ci <ref> --state merged` records the approvals and
kb-render derives it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Mapping

from .okf.document import Actor, duration, instant, section, to_dt
from .profile.spec import CheckId, GateSpec, LeadWhen
from .profile.table import ACCEPTANCE, RAPIDA_SECTIONS, REGISTRY, VERIFY
from .view import Concept, View

GHERKIN = re.compile(r"^\s*(Given|When|Then|And|But|Dado|Dada|Quando|Então|Entao|E|Mas)\b", re.IGNORECASE)


@dataclass(frozen=True)
class CheckResult:
    check: CheckId
    passed: bool
    detail_pt: str


@dataclass(frozen=True)
class Target:
    gate: GateSpec
    primary: Concept
    bet: Concept | None
    moves: tuple[tuple[Concept, str], ...]


@dataclass(frozen=True)
class GateDecision:
    target: Target
    results: tuple[CheckResult, ...]
    approvers: tuple[Actor, ...]
    approver_problems: tuple[str, ...]
    already: str | None            # the target's state when it is already past this gate

    @property
    def ok(self) -> bool:
        return all(r.passed for r in self.results) and not self.approver_problems

    def lines_pt(self) -> list[str]:
        out = [f"{'ok' if r.passed else 'FALHOU'}  {r.check.value}: {r.detail_pt}" for r in self.results]
        out += [f"FALHOU  aprovadores: {p}" for p in self.approver_problems]
        if self.approvers:
            out.append("aprovadores: " + ", ".join(self.approvers))
        return out


def _list(v: object) -> list[str]:
    return [str(x) for x in v] if isinstance(v, list) else []


def empty_sections(c: Concept, *titles: str) -> list[str]:
    """One pt-BR problem naming every '## <title>' section of `c` that is missing or empty."""
    empty = [f"'## {t}'" for t in titles if not section(c.doc.body, t).text]
    if not empty:
        return []
    return [f"{c.path}: seção {empty[0]} vazia ou ausente" if len(empty) == 1
            else f"{c.path}: seções {', '.join(empty)} vazias ou ausentes"]


def acceptance_problems(c: Concept) -> list[str]:
    ac = section(c.doc.body, ACCEPTANCE).bullets
    if not ac:
        return [f"{c.path}: seção '## {ACCEPTANCE}' sem bullets; escreva os critérios de aceite em bullets"]
    bad = [a for a in ac if GHERKIN.match(a)]
    return [f"{c.path}: critério em Gherkin ({bad[0][:40]!r}); escreva como bullet direto"] if bad else []


def rapida_problems(s: Concept) -> list[str]:
    return empty_sections(s, *RAPIDA_SECTIONS, VERIFY)


def _bet_fields(view: View, t: Target) -> CheckResult:
    bet = t.bet
    track = REGISTRY.track(str(bet["track"])) if bet else None
    if bet is None or track is None:
        return CheckResult(CheckId.BET_FIELDS_COMPLETE, False, "bet sem `track` válido (rapida ou bet)")
    missing = [k for k in track.required_fields if not str(bet[k] or "").strip()]
    app, cap = duration(bet["appetite"]), duration(track.appetite_max)
    probs = [f"falta `{k}`" for k in missing]
    if bet["appetite"] and app is None:
        probs.append(f"`appetite` {bet['appetite']!r} não é duração ISO 8601")
    elif app and cap and app > cap:
        probs.append(f"apetite {bet['appetite']} passa do teto {track.appetite_max} da trilha {track.name}")
    if track.name == "bet" and bet["idea"]:
        idea = view.resolve_ref(str(bet["idea"]))
        if idea is not None and idea["verdict"] not in ("segue", "ajusta") and idea.state != "promoted":
            probs.append(f"{bet['idea']} sem veredito segue|ajusta do protótipo")
    return CheckResult(CheckId.BET_FIELDS_COMPLETE, not probs, "; ".join(probs) or f"trilha {track.name}, apetite {bet['appetite']}")


def _rapida_slice(view: View, t: Target) -> CheckResult:
    bet = t.bet
    if bet is None or bet["track"] != "rapida":
        return CheckResult(CheckId.RAPIDA_SLICE_COMPLETE, True, "não se aplica (trilha bet)")
    slices = view.children(bet, "Slice")
    if len(slices) != 1:
        return CheckResult(CheckId.RAPIDA_SLICE_COMPLETE, False, f"a trilha rápida tem um slice; achei {len(slices)}")
    probs = rapida_problems(slices[0]) + ([f"{slices[0].path}: falta `repo`"] if not slices[0]["repo"] else [])
    return CheckResult(CheckId.RAPIDA_SLICE_COMPLETE, not probs, "; ".join(probs) or "atual, esperado, não muda e teste")


def _bet_active(view: View, t: Target) -> CheckResult:
    st = t.bet.state if t.bet else None
    return CheckResult(CheckId.BET_ACTIVE, st == "active", f"bet `{st}`" + ("" if st == "active" else "; a aposta vem antes do spec"))


def _markers(view: View, t: Target) -> CheckResult:
    n = t.primary.doc.body.count("[PRECISA ESCLARECER]")
    lines = [i for i, l in enumerate(t.primary.doc.body.splitlines(), 1) if "[PRECISA ESCLARECER]" in l]
    return CheckResult(CheckId.MARKERS_ZERO, n == 0,
                       "nenhum marcador aberto" if n == 0 else f"{n} marcador(es) [PRECISA ESCLARECER] no corpo (linhas {', '.join(map(str, lines))})")


def _acceptance(view: View, t: Target) -> CheckResult:
    probs = acceptance_problems(t.primary)
    return CheckResult(CheckId.ACCEPTANCE_BULLETS, not probs,
                       "; ".join(probs) or f"{len(section(t.primary.doc.body, ACCEPTANCE).bullets)} critérios")


def _verify(view: View, t: Target) -> CheckResult:
    probs = empty_sections(t.primary, VERIFY)
    return CheckResult(CheckId.VERIFY_HOW_PRESENT, not probs, "; ".join(probs) or "presente")


def _slices_ready(view: View, t: Target) -> CheckResult:
    slices = view.children(t.bet, "Slice") if t.bet else ()
    if not slices:
        return CheckResult(CheckId.SLICES_READY, False, "nenhum slice; o spec e os slices vão no mesmo PR")
    probs: list[str] = []
    for s in slices:
        probs += [] if str(s["repo"] or "").strip() else [f"{s.path}: falta `repo`"]
        probs += empty_sections(s, VERIFY)
        probs += [] if isinstance(s["tier"], int) else [f"{s.path}: `tier` não é 0, 1 ou 2"]
        probs += acceptance_problems(s)
    return CheckResult(CheckId.SLICES_READY, not probs, "; ".join(probs) or f"{len(slices)} slice(s) completos")


CheckFn = Callable[[View, Target], CheckResult]
CHECKS: Mapping[CheckId, CheckFn] = {
    CheckId.BET_FIELDS_COMPLETE: _bet_fields, CheckId.RAPIDA_SLICE_COMPLETE: _rapida_slice,
    CheckId.BET_ACTIVE: _bet_active, CheckId.MARKERS_ZERO: _markers, CheckId.ACCEPTANCE_BULLETS: _acceptance,
    CheckId.VERIFY_HOW_PRESENT: _verify, CheckId.SLICES_READY: _slices_ready,
}
assert set(CHECKS) == set(CheckId), "every CheckId needs an implementation"


def resolve_target(view: View, gate: GateSpec, ref: Concept) -> Target | str:
    bet = ref if ref["type"] == "Bet" else view.bet_of(ref)
    if gate.target_type == "Bet":
        primary = bet
    elif gate.target_type == "Spec":
        primary = ref if ref["type"] == "Spec" else (view.spec_of(bet) if bet else None)
    else:
        primary = None
    if primary is None:
        return f"{ref.kb_id}: não achei o {gate.target_type} deste gate" + (
            "; crie com `t0 new spec <BET>`" if gate.target_type == "Spec" else "")
    moves: list[tuple[Concept, str]] = []
    for mv in gate.moves:
        targets = [primary] if mv.scope == "target" else list(view.children(bet, mv.scope.split(":", 1)[1])) if bet else []
        moves += [(c, mv.to) for c in targets]
    return Target(gate, primary, bet, tuple(moves))


def current_holder(view: View, role: str, now: str) -> list[str]:
    """Fixed roles from Role.holders or Person.roles; rotating roles from the Rotation assignment covering now."""
    rot = view.at(f"/team/rotations/{role}.md")
    if rot is not None:
        for a in rot["assignments"] or []:
            if isinstance(a, dict) and instant(a.get("from")) and instant(a.get("to")) and \
                    to_dt(a["from"]) <= to_dt(now) < to_dt(a["to"]):
                return [str(a.get("who"))]
        return []
    r = view.at(f"/team/roles/{role}.md")
    holders = _list(r["holders"]) if r is not None else []
    holders += [f"human:{p['handle']}" for p in view.of_type("Person") if role in _list(p["roles"])]
    return sorted(set(holders))


def pod_holders(view: View, role: str, pod: str, now: str) -> list[str]:
    """Holders of `role` now, minus people whose `pods` leave this pod out."""
    pods = {f"human:{p['handle']}": _list(p["pods"]) for p in view.of_type("Person")}
    return [h for h in current_holder(view, role, now) if not pods.get(h) or pod in pods[h]]


def lead_reasons(view: View, gate: GateSpec, t: Target) -> list[str]:
    bet, rule = t.bet, gate.approvers
    why: list[str] = []
    if bet is None:
        return why
    if LeadWhen.CROSS_POD in rule.lead_when and len(_list(bet["pods"])) > 1:
        why.append("cruza pods")
    tiers = [bet["tier"], t.primary["tier"]] + [s["tier"] for s in view.children(bet, "Slice")]
    if LeadWhen.TIER2 in rule.lead_when and 2 in tiers:
        why.append("Tier 2")
    app, lim = duration(bet["appetite"]), duration(rule.appetite_limit)
    if LeadWhen.APPETITE_OVER in rule.lead_when and app and lim and app > lim:
        why.append(f"apetite acima de {rule.appetite_limit}")
    return why


def resolve_approvers(view: View, gate: GateSpec, t: Target, now: str) -> tuple[tuple[Actor, ...], tuple[str, ...]]:
    out: list[str] = []
    problems: list[str] = []
    for role in gate.approvers.roles:
        if role == "bet_owner":
            who = t.bet["decision_by"] if t.bet else None
            if who:
                out.append(str(who))
            else:
                problems.append("bet sem `decision_by` (quem aprova)")
    why = lead_reasons(view, gate, t)
    if why:
        leads = current_holder(view, "lead", now)
        if leads:
            out += leads
        else:
            problems.append(f"precisa do Lead ({', '.join(why)}), mas /team/roles/lead.md não tem `holders`")
    approvers = tuple(dict.fromkeys(Actor(a) for a in out))
    if len(approvers) == 1 and "Tier 2" in why:
        problems.append("Tier 2 precisa de dois aprovadores, e o Lead é o próprio dono da bet")
    junior = {f"human:{p['handle']}" for p in view.of_type("Person") if p["junior"] is True}
    if approvers and all(a in junior for a in approvers):
        problems.append("júnior não aprova sozinho")
    return approvers, tuple(problems)


def evaluate(view: View, gate: GateSpec, ref: Concept, *, now: str) -> GateDecision | str:
    t = resolve_target(view, gate, ref)
    if isinstance(t, str):
        return t
    results = tuple(CHECKS[c](view, t) for c in gate.checks)
    approvers, problems = resolve_approvers(view, gate, t, now)
    to = gate.moves[0].to
    st = t.primary.state
    already = st if st == to or (t.primary.spec and t.primary.spec.states and not t.primary.spec.states.allows(str(st), to)) else None
    return GateDecision(t, results, approvers, problems, already)
