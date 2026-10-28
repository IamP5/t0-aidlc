"""File-backed fake Tracker for tests, evals and offline demos. Private: reach it via
open_tracker(TrackerConfig(kind='file', file_dir=...)).

Layout: <dir>/<PROJECT>/<KEY>.yaml (one issue per file: fields + status + labels + comments[]),
<dir>/_seq.yaml (next number per project), <dir>/_journal.jsonl (every write, for assertions).
Behaves like Jira where it matters for sync: label search for t0-uid, workflow transitions validated
against a small default workflow (To Do -> In Progress -> In Review -> Done, Blocked), comments with
author/time, intake = issues without t0-uid label.

The SAME contract test suite (tests/tracker/test_contract.py) runs against this fake and against
JiraRest with recorded HTTP cassettes (cloud + dc), so the fake cannot drift from the adapter.
"""
from __future__ import annotations

from pathlib import Path


class FileTracker:
    def __init__(self, root: Path) -> None:
        raise NotImplementedError
    # implements tracker.port.Tracker
