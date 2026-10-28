"""Workspace + bet resolution + slice branches + product PRs (workspace-pattern §2-3).

Reads the Workspace concept (`workspace:` block) through KB; writes only local generated files (via gen)
and git operations in product clones. Never writes the KB except through KB.record (pr-opened etc.).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .context import ResolvedBet, WorkspaceFacts
from .kb import KB
from .write import Plan, Refusal

BRANCH_RE = r"^bet/(BET-\d+)/([A-Z][A-Z0-9]+-\d+)-"


@dataclass(frozen=True)
class RepoSpec:
    name: str
    url: str
    role: str
    kind: str
    optional: bool
    tier: int
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class Workspace:
    root: Path                 # ~/ws/<product> or ~/ws/<product>@BET-NNN
    product: str
    repos: tuple[RepoSpec, ...]
    absent: frozenset[str]
    isolated_bet: str | None

    def facts(self) -> WorkspaceFacts: raise NotImplementedError


def locate(cwd: Path) -> Workspace | None:
    """Walk up to .t0/workspace.json."""
    raise NotImplementedError


def init(kb: KB, product: str, *, group: str | None = None) -> Workspace:
    """Clone kb (if missing) + repos as siblings; 403 -> absent; render workspace scope via gen."""
    raise NotImplementedError


def sync(ws: Workspace, *, quick: bool = False) -> list[str]:
    """fetch (3 s timeout) + ff-only on clean default branches and kb/; re-render AGENTS.md."""
    raise NotImplementedError


def detect_bet(kb: KB, cwd: Path, *, task_text: str | None = None) -> ResolvedBet | None:
    """T0_BET env -> branch regex -> .t0/bet.json -> Jira key in task text (lookup by derived jira) -> None."""
    raise NotImplementedError


def bet_start(kb: KB, ws: Workspace, bet: str, *, isolate: bool = False, repos: tuple[str, ...] = ()) -> Workspace:
    raise NotImplementedError


def slice_start(kb: KB, ws: Workspace, story: str) -> Plan | Refusal:
    """DoR check (methodology §6.1) from the View; refuses dirty tree; creates bet/<BET>/<KEY>-<slug> in the
    slice's repo. Writes no KB record: the slice enters `building` on PR_OPENED (table), so starting a
    branch and abandoning it leaves no false state. Returns an empty Plan with messages, or a Refusal
    listing the missing DoR items."""
    raise NotImplementedError


def pr_open(kb: KB, ws: Workspace, *, verify: bool = False) -> Plan | Refusal:
    """Draft PR with trailers (Bet, Story, Jira-Feature, Depends-on, Merge-order, KB-Context) via _forge;
    emits PR_OPENED record. Refuses a card older than 24 h without --force."""
    raise NotImplementedError


def pr_check(kb: KB, *, repo: str, pr_body: str, head_ref: str) -> tuple[bool, list[str]]:
    """Product CI: trailers present, Story resolves, depends_on merged per the KB changeset (KB read-only
    token; never another product repo's API); posts t0/merge-order status."""
    raise NotImplementedError
