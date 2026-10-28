import json
import subprocess

import pytest

from t0 import ws
from t0.okf.document import BundlePath, Document
from t0.view import Concept, View
from t0.write import Plan, Refusal

MANIFEST = """---
type: Workspace
title: "Workspace do payments"
uid: ws-payments
workspace:
  schema: 1
  product: payments
  jira_project: PAY
  default_branch: main
  repos:
    - {name: ledger, url: git@x:t0/ledger.git, role: "Ledger", kind: service, optional: false, tier: 2, depends_on: []}
    - {name: api, url: git@x:t0/api.git, role: "API REST", kind: service, optional: false, tier: 2, depends_on: [ledger]}
---
notas
"""


def _c(path, fm, derived=None):
    return Concept(Document(BundlePath(path), fm, "", True, ""), None, derived or {}, ())


class FakeKB:
    """Resolves Ref by KB id folder or derived jira key, like KB.get."""

    def __init__(self, concepts):
        self._v = View({c.doc.path.value: c for c in concepts}, {}, {}, (), "abc", 0)

    def view(self):
        return self._v

    def get(self, ref):
        for c in self._v.concepts.values():
            fm = {**c.doc.frontmatter, **c.derived}
            if fm.get("jira") == ref.raw and fm.get("type") == "Slice":
                return c
            if c.doc.path.value.endswith(f"/{ref.raw}/bet.md"):
                return c
        return None


BET = "/products/payments/bets/BET-042"
KB = FakeKB([
    _c(f"{BET}/bet.md", {"type": "Bet", "title": "Limites"}, {"jira": "PAY-123", "state": "active"}),
    _c(f"{BET}/slices/01-ledger-limits.md", {"type": "Slice", "repo": "ledger", "acceptance": ["a"]},
       {"jira": "PAY-130", "state": "ready"}),
    _c(f"{BET}/slices/02-api-limits.md", {"type": "Slice", "repo": "api", "acceptance": ["b"]},
       {"jira": "PAY-131", "state": "ready"}),
    _c(f"{BET}/slices/03-web.md", {"type": "Slice", "repo": "web", "acceptance": ["c"]},
       {"jira": "PAY-132", "state": "proposed"}),
])


def git(d, *a):
    subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t"}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("T0_BET", raising=False)
    (tmp_path / ".t0").mkdir()
    (tmp_path / ".t0/workspace.json").write_text(json.dumps({"schema": 1, "product": "payments", "absent": ["ledger"]}))
    (tmp_path / "kb/products/payments").mkdir(parents=True)
    (tmp_path / "kb/products/payments/workspace.md").write_text(MANIFEST)
    api = tmp_path / "api"
    api.mkdir()
    git(api, "init", "-q", "-b", "main")
    (api / "README").write_text("x")
    git(api, "add", ".")
    git(api, "commit", "-qm", "init")
    return tmp_path


def test_read_manifest_parses_repos(workspace):
    m = ws.read_manifest(workspace / "kb", "payments")
    assert [r.name for r in m.repos] == ["ledger", "api"]
    assert m.repos[1].depends_on == ("ledger",)
    assert m.jira_project == "PAY"


def test_read_manifest_rejects_product_mismatch(tmp_path):
    (tmp_path / "products/other").mkdir(parents=True)
    (tmp_path / "products/other/workspace.md").write_text(MANIFEST)
    with pytest.raises(ws.ManifestError):
        ws.read_manifest(tmp_path, "other")


def test_locate_walks_up_and_marks_absent(workspace):
    w = ws.locate(workspace / "api")
    assert w.root == workspace and w.product == "payments" and w.absent == {"ledger"}
    facts = w.facts()
    assert facts.repos == (("ledger", "Ledger", "-", True), ("api", "API REST", "main", False))


def test_detect_chain_order(workspace):
    api = workspace / "api"
    assert ws.detect(api, {}).rule == "none"
    (workspace / ".t0/bet.json").write_text(json.dumps({"bet": "BET-042", "active_story": "PAY-131"}))
    assert ws.detect(api, {}) == ws.Detection("BET-042", "PAY-131", "bet.json", None)
    git(api, "switch", "-qc", "bet/BET-051/PAY-200-x")
    assert ws.detect(api, {}) == ws.Detection("BET-051", "PAY-200", "branch", None)
    assert ws.divergence(api, {}) == "branch é BET-051, card é BET-042: rode `t0 bet use BET-051`"
    assert ws.detect(api, {"T0_BET": "BET-007"}).rule == "env"


def test_bet_use_writes_marker_idempotently(workspace):
    w = ws.locate(workspace)
    plan = ws.bet_use(KB, w, "PAY-131")
    assert isinstance(plan, Plan) and plan.empty
    data = json.loads((workspace / ".t0/bet.json").read_text())
    assert data["bet"] == "BET-042" and data["jira"] == "PAY-123" and data["active_story"] == "PAY-131"
    assert data["stories"] == ["PAY-130", "PAY-131", "PAY-132"]
    assert data["repos"] == ["api", "ledger", "web"]
    again = ws.bet_use(KB, w, "PAY-131")
    assert "(já estava)" in again.messages_pt[0]
    assert isinstance(ws.bet_use(KB, w, "BET-999"), Refusal)


def test_slice_start_creates_branch_then_noop(workspace):
    w = ws.locate(workspace)
    plan = ws.slice_start(KB, w, "PAY-131")
    assert isinstance(plan, Plan), plan
    assert ws.current_branch(workspace / "api") == "bet/BET-042/PAY-131-api-limits"
    assert "já em" in ws.slice_start(KB, w, "PAY-131").messages_pt[0]


def test_slice_start_refusals(workspace):
    w = ws.locate(workspace)
    assert any("DoR" in r for r in ws.slice_start(KB, w, "PAY-132").reasons_pt)
    assert ws.slice_start(KB, w, "PAY-130").reasons_pt == ("repo `ledger` ausente no workspace",)
    (workspace / "api/dirty.txt").write_text("x")
    assert "árvore suja" in ws.slice_start(KB, w, "PAY-131").reasons_pt[0]
    assert ws.current_branch(workspace / "api") == "main"
