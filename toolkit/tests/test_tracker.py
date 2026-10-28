import json

import pytest

from t0.okf.document import BundlePath, Document
from t0.tracker import TrackerConfig, open_tracker
from t0.tracker.port import IssueKind
from t0.tracker.sync import ActionKind, SyncIncomplete, execute, plan_sync, snapshot
from t0.view import Concept, View

BET = "/products/payments/bets/BET-042"


def _c(path, fm, derived=None):
    return Concept(Document(BundlePath(path), fm, "", True, ""), None, derived or {}, ())


def make_view(keys=None):
    keys = keys or {}
    concepts = [
        _c("/products/payments/workspace.md", {"type": "Workspace", "uid": "ws-payments",
                                               "workspace": {"product": "payments", "jira_project": "PAY"}}),
        _c(f"{BET}/bet.md", {"type": "Bet", "uid": "bet-042", "title": "Limites", "description": "Limite diário"},
           {"state": "active", "jira": keys.get("bet-042")}),
        _c(f"{BET}/slices/01-ledger.md", {"type": "Slice", "uid": "s-01", "title": "Ledger", "tier": 2,
                                          "acceptance": ["saldo bloqueia"]}, {"jira": keys.get("s-01")}),
        _c(f"{BET}/slices/02-api.md", {"type": "Slice", "uid": "s-02", "title": "API", "tier": 2,
                                       "acceptance": ["retorna 422"], "depends_on": ["01-ledger"]},
           {"jira": keys.get("s-02")}),
        _c("/products/payments/bets/BET-050/bet.md", {"type": "Bet", "uid": "bet-050", "title": "Proposta"},
           {"state": "proposed"}),
    ]
    return View({c.doc.path.value: c for c in concepts}, {}, {}, (), "abc", 0)


def sync(view, tracker):
    return execute(plan_sync(view, snapshot(tracker, view)), tracker)


def creates(root):
    return [l for l in (root / "_journal.jsonl").read_text().splitlines() if json.loads(l)["op"] == "create"]


@pytest.fixture
def tracker(tmp_path):
    return open_tracker(TrackerConfig(kind="file", file_dir=tmp_path))


def test_first_run_creates_feature_stories_and_links(tracker, tmp_path):
    plan = sync(make_view(), tracker)
    feat, s1, s2 = (tracker.find(u) for u in ("bet-042", "s-01", "s-02"))
    assert feat.kind is IssueKind.FEATURE and feat.title == "BET-042 Limites"
    assert json.loads((tmp_path / f"PAY/{s2.key}.json").read_text())["parent"] == feat.key
    assert s1.blocks == (s2.key,)
    assert sorted(plan.messages_pt) == sorted(f"jira-linked {u} {tracker.find(u).key}" for u in ("bet-042", "s-01", "s-02"))
    assert tracker.find("bet-050") is None


def test_rerun_before_records_land_relinks_without_duplicates(tracker, tmp_path):
    sync(make_view(), tracker)
    second = plan_sync(make_view(), snapshot(tracker, make_view()))
    assert {a.kind for a in second.actions} == {ActionKind.RECORD_LINK}
    plan = execute(second, tracker)
    assert len(creates(tmp_path)) == 3
    assert len(plan.messages_pt) == 3


def test_converged_run_plans_nothing(tracker):
    sync(make_view(), tracker)
    keys = {u: tracker.find(u).key for u in ("bet-042", "s-01", "s-02")}
    assert plan_sync(make_view(keys), snapshot(tracker, make_view(keys))).actions == ()


def test_jira_side_edit_is_reverted(tracker, tmp_path):
    sync(make_view(), tracker)
    keys = {u: tracker.find(u).key for u in ("bet-042", "s-01", "s-02")}
    f = tmp_path / f"PAY/{keys['s-01']}.json"
    data = json.loads(f.read_text())
    data["title"] = "editado no Jira"
    f.write_text(json.dumps(data))
    plan = plan_sync(make_view(keys), snapshot(tracker, make_view(keys)))
    assert [a.kind for a in plan.actions] == [ActionKind.UPDATE]
    execute(plan, tracker)
    assert tracker.get(keys["s-01"]).title == "Ledger"


def test_crash_mid_run_converges(tracker, tmp_path):
    class Flaky:
        def __init__(self, inner):
            self.inner, self.n = inner, 0

        def __getattr__(self, name):
            return getattr(self.inner, name)

        def create(self, draft):
            self.n += 1
            if self.n == 2:
                raise RuntimeError("timeout")
            return self.inner.create(draft)

    flaky = Flaky(tracker)
    with pytest.raises(SyncIncomplete) as exc:
        sync(make_view(), flaky)
    assert exc.value.plan.messages_pt == (f"jira-linked bet-042 {tracker.find('bet-042').key}",)
    sync(make_view(), tracker)
    assert len(creates(tmp_path)) == 3
    assert tracker.find("s-01").blocks == (tracker.find("s-02").key,)


def test_key_mismatch_is_a_conflict(tracker):
    sync(make_view(), tracker)
    view = make_view({"bet-042": "PAY-999"})
    kinds = {a.kind for a in plan_sync(view, snapshot(tracker, view)).actions if a.kb_uid == "bet-042"}
    assert kinds == {ActionKind.CONFLICT}


def test_jira_rest_is_not_wired():
    t = open_tracker(TrackerConfig(kind="jira-dc", base_url="https://jira.example"))
    with pytest.raises(NotImplementedError):
        t.find("x")


def test_file_tracker_workflow_and_intake(tracker):
    from t0.tracker.port import IssueDraft

    key = tracker.create(IssueDraft(IssueKind.STORY, "PAY", "u", "t", "", (), (), None, ""))
    tracker.transition(key, "In Progress")
    with pytest.raises(ValueError):
        tracker.transition(key, "Done")
    tracker.comment(key, "oi")
    assert [c.body_md for c in tracker.comments_since(key, None)] == ["oi"]
    assert tracker.intake("PAY", None) == ()
