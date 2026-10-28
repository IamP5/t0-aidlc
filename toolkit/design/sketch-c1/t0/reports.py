"""Read-mostly folds over the View + external sources (git, CI, telemetry). One noun: `t0 report <kind>`.
Each kind returns text (stdout) or a Plan writing a Metric Snapshot (`--commit`, CI only).
Anti-vanity rule encoded: ReportKind rows never include per-person volume metrics; the per-person view
is only in-progress/blocked items (test asserts no 'tokens'/'prs' per actor key in any snapshot schema).
"""
from __future__ import annotations

from enum import Enum

from .view import View
from .write import Plan


class ReportKind(Enum):
    DIGEST = "digest"              # daily Metric Snapshot cycles/<C>/digests/<date>.md (CI 9h)
    CYCLE = "cycle"                # metrics-snapshot at Demo close -> cycles/<C>/report.md
    ADOPTION = "adoption"          # Adoption Report vs KB Policy adoption-floors
    SWEEP = "sweep"                # sunset candidates, stale_after, drift, AGENTS.md lines, hooks count
    REVIEW_QUEUE = "review-queue"  # PRs + gate PRs waiting, age vs 4h SLO
    BUDGET = "budget"              # harness/budget.md
    TRACE = "trace"                # auditor JSON: requirement -> slice -> PR -> test (stdout only, never in KB)


def report(view: View, kind: ReportKind, *, commit: bool = False, **sources: object) -> str | Plan:
    raise NotImplementedError
