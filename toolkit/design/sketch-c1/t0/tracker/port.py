"""Issue-tracker port. The rest of t0 never sees Jira JSON, ADF, wiki markup, accountIds or API versions.

Implementations (tracker/_jira_rest.py, tracker/_file.py) are private; open_tracker is the only door.
Cloud vs Data Center is a private Flavor strategy inside JiraRest:
  cloud: /rest/api/3, ADF bodies, accountId users, API token (email:token basic) or OAuth
  dc:    /rest/api/2, wiki-markup bodies, username users, PAT bearer
The flavor is CONFIG (KB secrets/vars: T0_JIRA_FLAVOR), discovered at rollout with `t0 doctor --jira`
(calls /rest/api/2/serverInfo -> deploymentType).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from ..okf.document import Instant

IssueKey = str                       # 'PAY-131' (validated by regex at the edge)


class IssueKind(Enum):
    FEATURE = "feature"              # bet
    STORY = "story"                  # slice


@dataclass(frozen=True)
class IssueDraft:
    """Desired content, rendered from the KB. Content is KB-owned; the tracker never edits it."""
    kind: IssueKind
    project: str
    kb_uid: str                      # stored as label 't0-uid:<uid>' -> find() makes create idempotent
    title: str
    description_md: str              # markdown; flavor converts to ADF or wiki markup
    acceptance: tuple[str, ...]      # bullets, never Gherkin
    labels: tuple[str, ...]          # 'ready-for-agent', 'tier-2'
    parent: IssueKey | None          # story -> feature
    kb_link: str                     # URL of the concept in the KB forge
    points: int | None = None        # 1 per slice only if the ART demands


@dataclass(frozen=True)
class RemoteIssue:
    key: IssueKey
    kb_uid: str | None
    kind: IssueKind
    title: str
    description_md: str
    status: str                      # workflow status name
    status_changed_by: str | None    # 'human:<handle>' or 'process:t0-sync'
    status_changed_at: Instant | None
    blocks: tuple[IssueKey, ...]
    content_hash: str                # hash of title+description+acceptance as rendered by us


@dataclass(frozen=True)
class RemoteComment:
    id: str
    key: IssueKey
    author: str
    at: Instant
    body_md: str


class Tracker(Protocol):
    def find(self, kb_uid: str) -> RemoteIssue | None: ...
    def get(self, key: IssueKey) -> RemoteIssue: ...
    def create(self, draft: IssueDraft) -> IssueKey: ...
    def update(self, key: IssueKey, draft: IssueDraft) -> None: ...
    def transition(self, key: IssueKey, to_status: str) -> None: ...
    def link_blocks(self, blocker: IssueKey, blocked: IssueKey) -> None: ...
    def comment(self, key: IssueKey, body_md: str) -> None: ...
    def comments_since(self, key: IssueKey, since: Instant | None) -> tuple[RemoteComment, ...]: ...
    def intake(self, project: str, since: Instant | None) -> tuple[RemoteIssue, ...]:
        """Issues created directly in Jira (no t0-uid label) -> become Idea/bugfix intake records."""
        ...


@dataclass(frozen=True)
class TrackerConfig:
    kind: str                        # 'jira-cloud' | 'jira-dc' | 'file'
    base_url: str | None = None
    token_env: str = "T0_JIRA_TOKEN" # name of env var; the value never touches disk or logs
    file_dir: Path | None = None     # 'file': fixtures dir (tests, evals, dry runs)
    status_map: dict[str, str] | None = None   # KB slice state -> Jira workflow status names (per project)


def open_tracker(cfg: TrackerConfig) -> Tracker:
    raise NotImplementedError
