"""KB -> Jira mirror (methodology §5.5). Planner is pure; executor is the only caller of Tracker writes.

Ownership per field (single source each):
  content (title, description, AC, labels, Blocks links, parent)  KB -> Jira; Jira edits reverted + commented
  jira key                                                       Jira -> KB once, via JIRA_LINKED record
  story status                                                   G4/G5 (CI_GATE events) -> Jira transition;
                                                                 human Jira transition -> JIRA_STATUS record
                                                                 (fold: blocked / conflict per state machine)
  comments                                                       append-only both ways (JIRA_COMMENT records)
  intake                                                         Jira-only issues -> Idea CREATED records

Write-back happens ONLY as records (AddRecord via KB.record); never by editing frontmatter.
Runs ONLY in KB CI (token lives in KB secrets). Locally: `t0 jira sync` == --plan.
Idempotency: create() is guarded by find(kb_uid) (label t0-uid:<uid>) so a crash after create but
before the JIRA_LINKED record lands converges on the next run without duplicates. Every action has a
dedup key '<action>:<uid>:<content_hash|status>' -> re-running a plan that already ran emits nothing.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..view import View
from ..write import Plan
from .port import IssueDraft, IssueKey, RemoteComment, RemoteIssue, Tracker


class ActionKind(Enum):
    CREATE = "create"; UPDATE = "update"; REVERT_EDIT = "revert-edit"; TRANSITION = "transition"
    LINK = "link"; PUSH_COMMENT = "push-comment"; IMPORT_STATUS = "import-status"
    IMPORT_COMMENT = "import-comment"; INTAKE = "intake"; CONFLICT = "conflict"


@dataclass(frozen=True)
class SyncAction:
    kind: ActionKind
    kb_uid: str | None
    key: IssueKey | None
    draft: IssueDraft | None = None
    to_status: str | None = None
    comment: RemoteComment | None = None
    dedup: str = ""
    reason_pt: str = ""


@dataclass(frozen=True)
class RemoteSnapshot:
    issues: dict[str, RemoteIssue]          # by kb_uid (found via label) or by key for linked ones
    comments: dict[IssueKey, tuple[RemoteComment, ...]]
    intake: tuple[RemoteIssue, ...]


@dataclass(frozen=True)
class SyncPlan:
    actions: tuple[SyncAction, ...]
    drift: tuple[str, ...]                  # human-readable drift lines for the digest


def snapshot(tracker: Tracker, view: View, *, reconcile: bool) -> RemoteSnapshot:
    """Reads only what the plan needs: issues of active bets (all bets on --reconcile)."""
    raise NotImplementedError


def drafts(view: View) -> dict[str, IssueDraft]:
    """Desired Jira state per bet/slice uid, rendered from the View (pt-BR, AC bullets, Tier, KB link)."""
    raise NotImplementedError


def plan_sync(view: View, remote: RemoteSnapshot) -> SyncPlan:
    """Pure diff: desired (drafts) vs remote. Status contradicting a gate (Done without merged PR,
    Story moving before G3) -> TRANSITION back + comment; ambiguous -> CONFLICT action."""
    raise NotImplementedError


def execute(plan: SyncPlan, tracker: Tracker) -> Plan:
    """Performs tracker writes in dependency order (features, stories, links, transitions, comments) and
    returns the records to append (JIRA_LINKED, JIRA_STATUS, JIRA_COMMENT, CREATED intake, drift digest
    input). Partial failure: returns the records for completed actions + raises after; the next run
    converges (find(kb_uid) + dedup)."""
    raise NotImplementedError
