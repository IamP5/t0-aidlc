"""KB -> Jira mirror (methodology §5.5). Planner is pure; executor is the only caller of Tracker writes.

v0.1 ownership implemented:
  content (title, description, AC, labels, parent)  KB -> Jira (CREATE / UPDATE)
  Blocks links from slice depends_on                KB -> Jira (LINK)
  jira key                                          Jira -> KB once, as a `jira-linked` record
Deferred to v0.2: status transitions from gates, human status import, comments, intake.

Idempotency: create() is guarded by find(kb_uid) (label t0-uid:<uid>), so a crash after create but
before the jira-linked record lands converges on the next run without duplicates (RECORD_LINK).
Every action has a dedup key; re-running a plan that already ran plans nothing.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from ..okf.document import Actor
from ..profile.spec import EventKind
from ..write import Plan, new_record
from .port import IssueDraft, IssueKey, IssueKind, RemoteComment, RemoteIssue, Tracker, draft_hash


class ActionKind(Enum):
    CREATE = "create"; UPDATE = "update"; LINK = "link"; RECORD_LINK = "record-link"; CONFLICT = "conflict"


@dataclass(frozen=True)
class SyncAction:
    kind: ActionKind
    kb_uid: str | None
    key: IssueKey | None
    draft: IssueDraft | None = None
    parent_uid: str | None = None       # story -> its bet, resolved to a key by the executor
    other_uid: str | None = None        # LINK: the blocked slice
    comment: RemoteComment | None = None
    dedup: str = ""
    reason_pt: str = ""


@dataclass(frozen=True)
class RemoteSnapshot:
    issues: dict[str, RemoteIssue]      # by kb_uid (found via label)
    comments: dict[IssueKey, tuple[RemoteComment, ...]]
    intake: tuple[RemoteIssue, ...]


@dataclass(frozen=True)
class SyncPlan:
    actions: tuple[SyncAction, ...]
    drift: tuple[str, ...]


@dataclass(frozen=True)
class Linked:
    """A key to write back as a `jira-linked` record (target uid, key)."""
    kb_uid: str
    key: IssueKey


@dataclass(frozen=True)
class _Item:
    uid: str
    draft: IssueDraft
    known_key: str | None
    parent_uid: str | None
    depends_on: tuple[str, ...]


def _fm(c: Any) -> Mapping[str, Any]:
    return {**dict(c.doc.frontmatter), **dict(c.derived)}


def _items(view: Any, kb_base_url: str = "") -> list[_Item]:
    concepts = list(view.concepts.values())
    projects = {_fm(c).get("workspace", {}).get("product"): _fm(c)["workspace"].get("jira_project")
                for c in concepts if _fm(c).get("type") == "Workspace" and isinstance(_fm(c).get("workspace"), dict)}
    items: list[_Item] = []
    for bet in sorted((c for c in concepts if _fm(c).get("type") == "Bet" and _fm(c).get("state") == "active"),
                      key=lambda c: c.doc.path.value):
        bfm, folder = _fm(bet), bet.doc.path.value.rsplit("/", 1)[0]
        project = projects.get(folder.split("/")[2])
        if not project:
            continue
        bet_id = folder.rsplit("/", 1)[1]
        items.append(_Item(bfm["uid"], IssueDraft(
            IssueKind.FEATURE, project, bfm["uid"], f"{bet_id} {bfm.get('title', '')}".strip(),
            str(bfm.get("description", "")), (), ("t0",), None, kb_base_url + bet.doc.path.value), bfm.get("jira"), None, ()))
        slices = sorted((c for c in concepts if _fm(c).get("type") == "Slice"
                         and c.doc.path.value.startswith(folder + "/slices/")), key=lambda c: c.doc.path.value)
        by_name = {c.doc.path.value.rsplit("/", 1)[1].removesuffix(".md"): _fm(c)["uid"] for c in slices}
        for s in slices:
            sfm = _fm(s)
            labels = ("t0", f"tier-{sfm['tier']}") if sfm.get("tier") is not None else ("t0",)
            items.append(_Item(sfm["uid"], IssueDraft(
                IssueKind.STORY, project, sfm["uid"], str(sfm.get("title", "")), str(sfm.get("description", "")),
                tuple(sfm.get("acceptance") or ()), labels, bfm.get("jira"), kb_base_url + s.doc.path.value),
                sfm.get("jira"), bfm["uid"], tuple(by_name.get(d, d) for d in sfm.get("depends_on") or ())))
    return items


def drafts(view: Any, *, kb_base_url: str = "") -> dict[str, IssueDraft]:
    """Desired Jira content per active bet and its slices (project from the product's workspace manifest)."""
    return {i.uid: i.draft for i in _items(view, kb_base_url)}


def snapshot(tracker: Tracker, view: Any, *, reconcile: bool = False) -> RemoteSnapshot:
    issues = {uid: r for uid in drafts(view) if (r := tracker.find(uid)) is not None}
    return RemoteSnapshot(issues, {}, ())


def plan_sync(view: Any, remote: RemoteSnapshot, *, kb_base_url: str = "") -> SyncPlan:
    """Pure diff of desired (drafts) vs remote."""
    items = _items(view, kb_base_url)
    actions: list[SyncAction] = []
    drift: list[str] = []
    for it in items:
        r = remote.issues.get(it.uid)
        if r is None:
            actions.append(SyncAction(ActionKind.CREATE, it.uid, None, it.draft, it.parent_uid, dedup=f"create:{it.uid}"))
            continue
        if it.known_key and it.known_key != r.key:
            actions.append(SyncAction(ActionKind.CONFLICT, it.uid, r.key, dedup=f"conflict:{it.uid}:{r.key}",
                                      reason_pt=f"KB diz {it.known_key}, Jira tem {r.key} com o label de {it.uid}"))
            continue
        if r.content_hash != draft_hash(it.draft):
            actions.append(SyncAction(ActionKind.UPDATE, it.uid, r.key, it.draft, it.parent_uid,
                                      dedup=f"update:{it.uid}:{draft_hash(it.draft)}"))
            drift.append(f"{r.key}: conteúdo divergia do KB, revertido")
        if it.known_key is None:
            actions.append(SyncAction(ActionKind.RECORD_LINK, it.uid, r.key, dedup=f"jira-linked:{it.uid}:{r.key}"))
    for it in items:
        for blocker in it.depends_on:
            br, me = remote.issues.get(blocker), remote.issues.get(it.uid)
            if br is not None and me is not None and me.key in br.blocks:
                continue
            actions.append(SyncAction(ActionKind.LINK, blocker, None, other_uid=it.uid, dedup=f"link:{blocker}:{it.uid}"))
    return SyncPlan(tuple(actions), tuple(drift))


class SyncIncomplete(Exception):
    """Raised after a partial run; `.plan` carries the records for the actions that completed."""

    def __init__(self, plan: Plan, cause: Exception) -> None:
        super().__init__(f"jira sync parou: {cause}")
        self.plan = plan


def _records(linked: list[Linked]) -> Plan:
    """jira-linked records through the core write API; until it lands, messages in the Plan."""
    try:
        recs = tuple(new_record(
            EventKind.JIRA_LINKED, type_name="Step",
            fields={"kind": EventKind.JIRA_LINKED.value, "target": l.kb_uid, "payload": {"key": l.key}},
            body=f"{l.kb_uid} -> {l.key}", actor=Actor("process:t0-sync"), handle="t0-sync",
            where={"repo": "kb"}, dedup=f"jira-linked:{l.kb_uid}:{l.key}") for l in linked)
        return Plan(records=recs, messages_pt=tuple(f"jira-linked {l.kb_uid} {l.key}" for l in linked))
    except NotImplementedError:
        return Plan(messages_pt=tuple(f"jira-linked {l.kb_uid} {l.key}" for l in linked))


def execute(plan: SyncPlan, tracker: Tracker) -> Plan:
    """Tracker writes in dependency order (features, stories, updates, links) and returns a Plan with
    one jira-linked record per new or newly found key. Partial failure raises SyncIncomplete."""
    order = {ActionKind.CREATE: 0, ActionKind.UPDATE: 1, ActionKind.RECORD_LINK: 2, ActionKind.LINK: 3,
             ActionKind.CONFLICT: 4}
    actions = sorted(plan.actions, key=lambda a: (order[a.kind], a.draft is not None and a.draft.kind is IssueKind.STORY))
    keys: dict[str, IssueKey] = {}
    linked: list[Linked] = []

    def key_of(uid: str) -> IssueKey | None:
        if uid not in keys and (r := tracker.find(uid)) is not None:
            keys[uid] = r.key
        return keys.get(uid)

    try:
        for a in actions:
            if a.kind is ActionKind.CREATE:
                draft = a.draft
                if draft.kind is IssueKind.STORY and draft.parent is None and a.parent_uid:
                    draft = replace(draft, parent=key_of(a.parent_uid))
                existing = tracker.find(a.kb_uid)
                keys[a.kb_uid] = existing.key if existing else tracker.create(draft)
                linked.append(Linked(a.kb_uid, keys[a.kb_uid]))
            elif a.kind is ActionKind.UPDATE:
                draft = a.draft if a.draft.parent or not a.parent_uid else replace(a.draft, parent=key_of(a.parent_uid))
                tracker.update(a.key, draft)
            elif a.kind is ActionKind.RECORD_LINK:
                linked.append(Linked(a.kb_uid, a.key))
            elif a.kind is ActionKind.LINK:
                blocker, blocked = key_of(a.kb_uid), key_of(a.other_uid)
                if blocker and blocked:
                    tracker.link_blocks(blocker, blocked)
    except Exception as e:
        raise SyncIncomplete(_records(linked), e) from e
    return _records(linked)
