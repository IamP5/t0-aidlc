"""GitHub (GHE) adapter. Private to write.py and ws.py. REST via urllib (no `gh` dependency in CI;
`gh auth token` is used locally only to obtain the dev's token).

Two backends behind the same functions, chosen by the Workspace manifest `forge:` key:
  github - GHE REST.   file - writes PRs as YAML under <ws>/.t0/fake-forge/ (tests, evals, offline demos);
  same contract tests as github with recorded cassettes, like tracker/_file.py.

Invariants in signatures:
  - open_pr() has NO draft parameter: every product/knowledge PR is draft. There is no `ready()` and no `merge()`.
  - enable_auto_merge() accepts only RecordsPR, which only open_records_pr() returns.
"""
from __future__ import annotations

from dataclasses import dataclass

from .okf.document import Actor


@dataclass(frozen=True)
class PR:
    repo: str
    number: int
    url: str


@dataclass(frozen=True)
class RecordsPR(PR):
    """Only for rec/* branches on the KB. Constructed only by open_records_pr."""


def open_pr(repo: str, *, head: str, base: str, title: str, body: str, reviewers: tuple[Actor, ...]) -> PR:
    """Always draft. Reuses an open PR with the same head (idempotent)."""
    raise NotImplementedError


def open_records_pr(kb_repo: str, *, head: str, title: str, body: str) -> RecordsPR:
    raise NotImplementedError


def enable_auto_merge(pr: RecordsPR) -> None:
    raise NotImplementedError


def approving_reviews(repo: str, merge_commit: str) -> tuple[Actor, ...]:
    """kb-render: approvers of the PR that produced merge_commit, as human:<handle>."""
    raise NotImplementedError


def set_status(repo: str, sha: str, context: str, state: str, description: str) -> None:
    """`t0/merge-order` and similar commit statuses (product repo token)."""
    raise NotImplementedError
