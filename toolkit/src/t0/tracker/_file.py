"""File-backed fake Tracker for tests, evals and offline demos. Private: reach it via
open_tracker(TrackerConfig(kind='file', file_dir=...)).

Layout: <dir>/<PROJECT>/<KEY>.json (one issue per file: fields + status + labels + blocks + comments),
<dir>/_seq.json (last number per project), <dir>/_journal.jsonl (every write, for assertions).
Behaves like Jira where it matters for sync: label search for t0-uid, workflow transitions validated
against a small default workflow, comments with author/time, intake = issues without t0-uid label.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..okf.document import Instant
from .port import (
    UID_LABEL, IssueDraft, IssueKey, IssueKind, RemoteComment, RemoteIssue, content_hash, draft_hash,
)

WORKFLOW: dict[str, frozenset[str]] = {
    "To Do": frozenset({"In Progress", "Blocked"}),
    "In Progress": frozenset({"In Review", "Blocked", "To Do"}),
    "In Review": frozenset({"Done", "In Progress", "Blocked"}),
    "Blocked": frozenset({"To Do", "In Progress"}),
    "Done": frozenset({"In Progress"}),
}
ACTOR = "process:t0-sync"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class FileTracker:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ storage
    def _path(self, key: IssueKey) -> Path:
        return self.root / key.split("-")[0] / f"{key}.json"

    def _load(self, key: IssueKey) -> dict[str, Any]:
        p = self._path(key)
        if not p.is_file():
            raise KeyError(key)
        return json.loads(p.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, Any], op: str) -> None:
        p = self._path(data["key"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(p)
        with (self.root / "_journal.jsonl").open("a", encoding="utf-8") as j:
            j.write(json.dumps({"op": op, "key": data["key"]}) + "\n")

    def _all(self) -> list[dict[str, Any]]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.root.glob("*/*.json"))]

    def _remote(self, d: dict[str, Any]) -> RemoteIssue:
        uid = next((l[len(UID_LABEL):] for l in d["labels"] if l.startswith(UID_LABEL)), None)
        return RemoteIssue(
            key=d["key"], kb_uid=uid, kind=IssueKind(d["kind"]), title=d["title"], description_md=d["description_md"],
            status=d["status"], status_changed_by=d.get("status_changed_by"),
            status_changed_at=d.get("status_changed_at"), blocks=tuple(d.get("blocks", ())),
            content_hash=content_hash(d["title"], d["description_md"], tuple(d["acceptance"]), tuple(d["labels"])))

    # ------------------------------------------------------------ Tracker port
    def find(self, kb_uid: str) -> RemoteIssue | None:
        label = UID_LABEL + kb_uid
        return next((self._remote(d) for d in self._all() if label in d["labels"]), None)

    def get(self, key: IssueKey) -> RemoteIssue:
        return self._remote(self._load(key))

    def create(self, draft: IssueDraft) -> IssueKey:
        seq_path = self.root / "_seq.json"
        seq = json.loads(seq_path.read_text()) if seq_path.is_file() else {}
        seq[draft.project] = seq.get(draft.project, 0) + 1
        seq_path.write_text(json.dumps(seq))
        key = f"{draft.project}-{seq[draft.project]}"
        self._save({"key": key, "status": "To Do", "blocks": [], "comments": [], **self._fields(draft),
                    "labels": [*draft.labels, UID_LABEL + draft.kb_uid]}, "create")
        return key

    def _fields(self, d: IssueDraft) -> dict[str, Any]:
        return {"kind": d.kind.value, "project": d.project, "title": d.title, "description_md": d.description_md,
                "acceptance": list(d.acceptance), "parent": d.parent, "kb_link": d.kb_link, "points": d.points,
                "hash": draft_hash(d)}

    def update(self, key: IssueKey, draft: IssueDraft) -> None:
        data = self._load(key)
        uid_labels = [l for l in data["labels"] if l.startswith(UID_LABEL)]
        data.update(self._fields(draft), labels=[*draft.labels, *uid_labels])
        self._save(data, "update")

    def transition(self, key: IssueKey, to_status: str) -> None:
        data = self._load(key)
        if to_status not in WORKFLOW.get(data["status"], frozenset()):
            raise ValueError(f"transição inválida {data['status']} -> {to_status}")
        data.update(status=to_status, status_changed_by=ACTOR, status_changed_at=_now())
        self._save(data, "transition")

    def link_blocks(self, blocker: IssueKey, blocked: IssueKey) -> None:
        data = self._load(blocker)
        if blocked not in data["blocks"]:
            data["blocks"].append(blocked)
            self._save(data, "link")

    def comment(self, key: IssueKey, body_md: str) -> None:
        data = self._load(key)
        data["comments"].append({"id": str(len(data["comments"]) + 1), "author": ACTOR, "at": _now(), "body_md": body_md})
        self._save(data, "comment")

    def comments_since(self, key: IssueKey, since: Instant | None) -> tuple[RemoteComment, ...]:
        return tuple(RemoteComment(c["id"], key, c["author"], c["at"], c["body_md"])
                     for c in self._load(key)["comments"] if since is None or c["at"] > since)

    def intake(self, project: str, since: Instant | None) -> tuple[RemoteIssue, ...]:
        return tuple(self._remote(d) for d in self._all()
                     if d["project"] == project and not any(l.startswith(UID_LABEL) for l in d["labels"]))
