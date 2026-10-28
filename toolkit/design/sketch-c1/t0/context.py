"""Context card renderer. Budgets are enforced in code: a Card cannot exist above its budget.

Card sections in priority order (workspace-pattern §2.6). Truncation drops whole sections from the
bottom, then trims bullet lists inside section 2 (never below 3 AC bullets); sections 1-3 are never
dropped. If sections 1-3 alone exceed the budget, render() raises CardOverBudget (kb check L2.card-budget
renders every active bet's card, so this is caught in the KB CI, not in a dev session).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .okf.document import Instant
from .view import Concept, View

AGENTS_BUDGET = 8000        # root AGENTS.md card, <=150 lines
DELTA_BUDGET = 3000
SUBAGENT_BUDGET = 3000
MCP_INSTRUCTIONS_BUDGET = 1500
REPO_BLOCK_BUDGET = 1200    # t0 block in each product repo AGENTS.md
SKILL_DESCRIPTION_MAX = 300


class CardFormat(Enum):
    AGENTS = "agents"       # full card (AGENTS.md), budget 8000
    DELTA = "delta"         # changed sections only, budget 3000; None when fresh
    HOOK = "hook"           # DELTA, or AGENTS when ancestors show AGENTS.md was not loaded
    SUBAGENT = "subagent"   # AC + glossary hits + links, budget 3000
    JSON = "json"           # machine form for skills (same content, structured)


class Section(Enum):
    HEADER = 1; BET = 2; REPOS = 3; CHANGESET = 4; OTHER_SLICES = 5; KB_MAP = 6; SKILLS = 7


@dataclass(frozen=True)
class Stamp:
    kb_sha: str
    at: Instant
    rule: str               # which detect rule chose the bet: env|branch|bet.json|jira-key|none
    bet: str | None


@dataclass(frozen=True)
class Card:
    text: str
    budget: int
    stamp: Stamp
    dropped: tuple[Section, ...]

    def __post_init__(self) -> None:
        if len(self.text) > self.budget:
            raise ValueError("card over budget")   # unreachable from render(); guards hand construction


class CardOverBudget(Exception): ...


@dataclass(frozen=True)
class ResolvedBet:
    bet: Concept
    story: str | None       # active Jira story (slice), if known
    rule: str


@dataclass(frozen=True)
class WorkspaceFacts:
    """What the renderer needs from ws.py, already parsed (no filesystem access in the renderer)."""
    product: str
    repos: tuple[tuple[str, str, str, bool], ...]   # (name, role, branch, absent)
    kb_rel: str             # './kb' or '.kb'


def render(view: View, ws: WorkspaceFacts | None, bet: ResolvedBet | None, fmt: CardFormat,
           *, changed: frozenset[Section] = frozenset()) -> Card | None:
    """Pure. For DELTA the caller (KB.context) computes `changed` by comparing the stamp in the current
    AGENTS.md with the last origin/main commit touching the bet folder or workspace.md (ws.freshness);
    empty `changed` -> None ('card em dia'). Output always starts with the stamp comment
    '<!-- t0:card kb=<sha> at=<instant> rule=<rule> -->'."""
    raise NotImplementedError
