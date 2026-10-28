"""Context card renderer. Budgets are enforced in code: a Card cannot exist above its budget.

Card sections in priority order (workspace-pattern §2.6). Truncation drops whole sections from the
bottom, then trims the acceptance bullets and intent lines of section 2 (never below 3 AC bullets);
sections 1-3 are never dropped. If sections 1-3 alone exceed the budget, render() raises CardOverBudget
(kb check L2.card-budget renders every active bet's card, so this is caught in the KB CI).

The renderer is pure: `facts_from_view` reads only dataclass fields of View/Concept (frontmatter,
derived, path, body); `compose` turns already-built facts into a Card.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping

from .okf.document import section
from .profile.table import ACCEPTANCE

AGENTS_BUDGET = 8000        # root AGENTS.md card, <=150 lines
AGENTS_MAX_LINES = 150
DELTA_BUDGET = 3000
SUBAGENT_BUDGET = 1500
MCP_INSTRUCTIONS_BUDGET = 1500
REPO_BLOCK_BUDGET = 1200
SKILL_DESCRIPTION_MAX = 300
MIN_AC_BULLETS = 3


class CardFormat(Enum):
    AGENTS = "agents"
    DELTA = "delta"
    HOOK = "hook"
    SUBAGENT = "subagent"
    JSON = "json"


BUDGETS = {CardFormat.AGENTS: AGENTS_BUDGET, CardFormat.DELTA: DELTA_BUDGET, CardFormat.HOOK: DELTA_BUDGET,
           CardFormat.SUBAGENT: SUBAGENT_BUDGET, CardFormat.JSON: AGENTS_BUDGET}


class Section(Enum):
    HEADER = 1; BET = 2; REPOS = 3; CHANGESET = 4; OTHER_SLICES = 5; KB_MAP = 6; SKILLS = 7


KEPT = frozenset({Section.HEADER, Section.BET, Section.REPOS})


@dataclass(frozen=True)
class Stamp:
    kb_sha: str
    at: str
    rule: str               # env | branch | bet.json | jira-key | none
    bet: str | None

    def comment(self) -> str:
        return f"<!-- t0:card kb={self.kb_sha} at={self.at} rule={self.rule} -->"


_STAMP_RE = re.compile(r"<!-- t0:card kb=(\S*) at=(\S*) rule=(\S*) -->")


def parse_stamp(text: str) -> tuple[str, str, str] | None:
    """(kb_sha, at, rule) from a rendered card, for freshness comparison."""
    m = _STAMP_RE.search(text)
    return (m.group(1), m.group(2), m.group(3)) if m else None


class CardOverBudget(Exception): ...


@dataclass(frozen=True)
class Card:
    text: str
    budget: int
    stamp: Stamp
    dropped: tuple[Section, ...]

    def __post_init__(self) -> None:
        if len(self.text) > self.budget:
            raise CardOverBudget(f"card com {len(self.text)} chars, teto {self.budget}")


@dataclass(frozen=True)
class ResolvedBet:
    bet: Any                # view.Concept
    story: str | None
    rule: str


@dataclass(frozen=True)
class WorkspaceFacts:
    product: str
    repos: tuple[tuple[str, str, str, bool], ...]   # (name, role, branch, absent)
    kb_rel: str             # './kb' or '.kb'


@dataclass(frozen=True)
class SliceFacts:
    uid: str
    title: str
    repo: str
    state: str
    jira: str | None
    pr: str | None
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class BetFacts:
    id: str
    title: str
    state: str
    appetite: str
    cycle_end: str
    kb_path: str            # '/products/payments/bets/BET-042'
    intent: tuple[str, ...]
    story: str | None
    acceptance: tuple[str, ...]
    slices: tuple[SliceFacts, ...] = ()
    jira: str | None = None


@dataclass(frozen=True)
class CardFacts:
    stamp: Stamp
    ws: WorkspaceFacts | None
    bet: BetFacts | None


# ------------------------------------------------------------------ sections


def _kb(ws: WorkspaceFacts | None) -> str:
    return ws.kb_rel if ws else "./kb"


def _header(f: CardFacts) -> str:
    kb = _kb(f.ws)
    return "\n".join([
        f.stamp.comment(),
        "# t0: contexto do workspace",
        f"KB t0-kb (OKF) em `{kb}`. Raias: registros (`t0 log`), conhecimento (PR revisado), derivado (só kb-render).",
        "O spec é o contrato; pergunte antes de desviar.",
        "Nunca edite index.md, log.md, changeset.md nem chaves derivadas (state, status, verified, jira, pr).",
        "Se `.t0/context.md` for mais novo que este card, leia ele primeiro.",
    ])


def _bet(f: CardFacts, max_ac: int, max_intent: int) -> str:
    b = f.bet
    if b is None:
        return "## Bet ativa\nNenhuma bet resolvida. Pergunte qual bet (`t0 bet use <BET|KEY>`), ou abra uma com `bet-new`. Skills de código se recusam sem bet."
    kb = _kb(f.ws).rstrip("/") + b.kb_path
    lines = [f"## Bet ativa: {b.id} {b.title}",
             f"Estado `{b.state}`, apetite {b.appetite}, ciclo até {b.cycle_end}." + (f" Feature {b.jira}." if b.jira else "")]
    lines += [f"> {x}" for x in b.intent[:max_intent]]
    if b.story:
        lines.append(f"Story ativa {b.story}. Critérios de aceite:")
        lines += [f"- {a}" for a in b.acceptance[:max_ac]]
        if len(b.acceptance) > max_ac:
            lines.append(f"- (+{len(b.acceptance) - max_ac} no slice)")
    lines.append(f"Links: `{kb}/spec.md`, `{kb}/plan.md`, `{kb}/slices/`, `{kb}/adr/`.")
    return "\n".join(lines)


def _repos(f: CardFacts) -> str:
    if f.ws is None:
        return "## Repos\nSem workspace (`.t0/workspace.json` ausente)."
    in_bet = {s.repo for s in f.bet.slices} if f.bet else set()
    lines = ["## Repos (ordem de merge)"]
    for i, (name, role, branch, absent) in enumerate(f.ws.repos, 1):
        tags = (" [bet]" if name in in_bet else "") + (" [ausente: sem acesso]" if absent else "")
        lines.append(f"{i}. `{name}` ({branch}){tags}: {role}")
    return "\n".join(lines[:11])


def _changeset(f: CardFacts) -> str | None:
    if not f.bet or not f.bet.slices:
        return None
    lines = ["## Change set"]
    for s in f.bet.slices[:10]:
        dep = f", depende de {', '.join(s.depends_on)}" if s.depends_on else ""
        lines.append(f"- {s.uid} `{s.repo}` {s.state}" + (f" PR {s.pr}" if s.pr else "") + dep)
    return "\n".join(lines)


def _other_slices(f: CardFacts) -> str | None:
    if not f.bet:
        return None
    others = [s for s in f.bet.slices if s.jira != f.bet.story and s.state not in ("done",)]
    if not others:
        return None
    return "\n".join(["## Outros slices abertos"] + [f"- {s.jira or s.uid}: {s.title}" for s in others[:10]])


def _kb_map(f: CardFacts) -> str:
    kb = _kb(f.ws).rstrip("/")
    p = f.ws.product if f.ws else "<produto>"
    return "\n".join(["## Mapa do KB", f"- `{kb}/index.md` índice raiz", f"- `{kb}/products/{p}/product.md` produto",
                      f"- `{kb}/products/{p}/bets/` bets", f"- `{kb}/methodology/` metodologia, rituais, políticas"])


ENTRY_SKILL = "`/t0` porta de entrada: escolhe o playbook e chama as skills de passo"
NO_BET_SKILLS = ("`bet-new` abre uma bet a partir de uma ideia", "`idea-capture` registra uma ideia nova")
BET_STATE_SKILLS: Mapping[str, tuple[str, ...]] = {
    "proposed": ("`grill` afia a bet antes da aposta",),
    "active": ("`bet-spec` escreve o spec", "`bet-slice` corta o spec em slices",
               "`slice-build <KEY>` constrói um slice pronto"),
}
STORY_SKILLS = ("`slice-build` constrói a story ativa", "`slice-verify` revisa o PR da story")


def card_skills(bet: BetFacts | None) -> tuple[str, ...]:
    """`/t0` first, then the step skills that fit the card's state (names from plugin/skills/)."""
    if bet is None:
        return (ENTRY_SKILL, *NO_BET_SKILLS)
    if bet.story and bet.state == "active":
        return (ENTRY_SKILL, *STORY_SKILLS)
    return (ENTRY_SKILL, *BET_STATE_SKILLS.get(bet.state, NO_BET_SKILLS))


def _skills(f: CardFacts) -> str:
    return "\n".join(["## Skills"] + [f"- {s}" for s in card_skills(f.bet)])


def _sections(f: CardFacts, max_ac: int, max_intent: int) -> list[tuple[Section, str]]:
    raw: list[tuple[Section, str | None]] = [
        (Section.HEADER, _header(f)), (Section.BET, _bet(f, max_ac, max_intent)), (Section.REPOS, _repos(f)),
        (Section.CHANGESET, _changeset(f)), (Section.OTHER_SLICES, _other_slices(f)),
        (Section.KB_MAP, _kb_map(f)), (Section.SKILLS, _skills(f))]
    return [(s, t) for s, t in raw if t]


def _fit(build: Callable[[int, int], list[tuple[Section, str]]], budget: int, max_lines: int,
         n_ac: int, n_intent: int) -> tuple[str, tuple[Section, ...]]:
    def size_ok(text: str) -> bool:
        return len(text) <= budget and text.count("\n") + 1 <= max_lines

    ac, intent = n_ac, n_intent
    dropped: list[Section] = []
    while True:
        secs = [(s, t) for s, t in build(ac, intent) if s not in dropped]
        while True:
            text = "\n\n".join(t for _, t in secs) + "\n"
            if size_ok(text):
                return text, tuple(dropped)
            droppable = [s for s, _ in secs if s not in KEPT]
            if not droppable:
                break
            last = max(droppable, key=lambda s: s.value)
            dropped.append(last)
            secs = [(s, t) for s, t in secs if s is not last]
        if intent > 1:
            intent -= 1
        elif ac > MIN_AC_BULLETS:
            ac -= 1
        else:
            raise CardOverBudget("seções 1 a 3 sozinhas estouram o teto do card")


def compose(facts: CardFacts, fmt: CardFormat, *, changed: frozenset[Section] = frozenset()) -> Card | None:
    budget = BUDGETS[fmt]
    n_ac = len(facts.bet.acceptance) if facts.bet else 0
    n_intent = len(facts.bet.intent) if facts.bet else 0
    if fmt in (CardFormat.DELTA, CardFormat.HOOK):
        if not changed:
            return None
        nums = " e ".join(str(s.value) for s in sorted(changed, key=lambda s: s.value))

        def build_delta(ac: int, intent: int) -> list[tuple[Section, str]]:
            head = (Section.HEADER, f"{facts.stamp.comment()}\nIsto substitui as seções {nums} do AGENTS.md; rode `t0 ws sync`.")
            return [head] + [(s, t) for s, t in _sections(facts, ac, intent) if s in changed and s is not Section.HEADER]

        text, dropped = _fit(build_delta, budget, 10**6, n_ac, n_intent)
    elif fmt is CardFormat.SUBAGENT:
        def build_sub(ac: int, intent: int) -> list[tuple[Section, str]]:
            return [(Section.HEADER, facts.stamp.comment()), (Section.BET, _bet(facts, ac, min(intent, 2)))]

        text, dropped = _fit(build_sub, budget, 10**6, n_ac, n_intent)
    elif fmt is CardFormat.JSON:
        text, dropped = _fit(lambda ac, i: [(Section.HEADER, _json(facts, ac, i))], budget, 10**6, n_ac, n_intent)
    else:
        text, dropped = _fit(lambda ac, i: _sections(facts, ac, i), budget, AGENTS_MAX_LINES, n_ac, n_intent)
    return Card(text, budget, facts.stamp, dropped)


def _json(f: CardFacts, max_ac: int, max_intent: int) -> str:
    b = f.bet
    return json.dumps({
        "stamp": {"kb": f.stamp.kb_sha, "at": f.stamp.at, "rule": f.stamp.rule},
        "bet": None if b is None else {"id": b.id, "title": b.title, "state": b.state, "jira": b.jira,
                                       "story": b.story, "acceptance": list(b.acceptance[:max_ac]),
                                       "intent": list(b.intent[:max_intent]), "kb_path": b.kb_path,
                                       "slices": [s.__dict__ | {"depends_on": list(s.depends_on)} for s in b.slices]},
        "repos": [] if f.ws is None else [{"name": n, "role": r, "branch": br, "absent": a} for n, r, br, a in f.ws.repos],
    }, ensure_ascii=False)


# ------------------------------------------------------------------ view adapter


def _fm(concept: Any) -> Mapping[str, Any]:
    return {**dict(concept.doc.frontmatter), **dict(concept.derived)}


def _intent(body: str) -> tuple[str, ...]:
    return tuple(l.strip() for l in body.splitlines() if l.strip() and not l.lstrip().startswith(("#", "-", "<!--")))[:5]


def facts_from_view(view: Any, bet: ResolvedBet | None) -> BetFacts | None:
    """Reads only dataclass fields of View/Concept, so it works on any folded View."""
    if bet is None:
        return None
    c = bet.bet
    fm = _fm(c)
    path = c.doc.path.value
    folder = path.rsplit("/", 1)[0]
    slices: list[tuple[str, SliceFacts, tuple[str, ...]]] = []
    for other in view.concepts.values():
        ofm = _fm(other)
        opath = other.doc.path.value
        if ofm.get("type") == "Slice" and opath.startswith(folder + "/slices/"):
            name = opath.rsplit("/", 1)[1].removesuffix(".md")
            slices.append((opath, SliceFacts(
                uid=name, title=str(ofm.get("title", name)), repo=str(ofm.get("repo", "?")),
                state=str(ofm.get("state", "proposed")), jira=ofm.get("jira"), pr=ofm.get("pr"),
                depends_on=tuple(ofm.get("depends_on") or ())), section(other.doc.body, ACCEPTANCE).bullets))
    slices.sort(key=lambda t: t[0])
    active = next(((s, ac) for _, s, ac in slices if bet.story and s.jira == bet.story), None)
    return BetFacts(
        id=folder.rsplit("/", 1)[1], title=str(fm.get("title", "")), state=str(fm.get("state", "?")),
        appetite=str(fm.get("appetite", "?")), cycle_end=str(fm.get("cycle_end", "?")), kb_path=folder,
        intent=_intent(c.doc.body), story=bet.story, acceptance=active[1] if active else (),
        slices=tuple(s for _, s, _ in slices), jira=fm.get("jira"))


def render(view: Any, ws: WorkspaceFacts | None, bet: ResolvedBet | None, fmt: CardFormat,
           *, changed: frozenset[Section] = frozenset(), now: str = "") -> Card | None:
    """Pure. For DELTA the caller (KB.context) computes `changed` by comparing the card stamp with the
    last origin/main commit touching the bet folder or workspace.md; empty `changed` -> None."""
    b = facts_from_view(view, bet)
    stamp = Stamp(view.kb_sha, now, bet.rule if bet else "none", b.id if b else None)
    return compose(CardFacts(stamp, ws, b), fmt, changed=changed)
