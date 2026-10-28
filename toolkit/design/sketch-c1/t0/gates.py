"""Gate evaluation. Pure. GateSpec (data) + CHECKS (one function per CheckId) + approver resolution.

`t0 gate <G> <ref>`:
  HUMAN_PR gates -> GateDecision.ok -> KB.gate builds a KnowledgeChange adding the gate file
                    (path = idempotency key; if already on main -> AlreadyDone; if open PR -> Pending).
  CI gates (G4, G5) -> evidence comes from the CI caller (CiEvidence) -> a CI_GATE Step record,
                    written by the KB-writer App (records lane). Never a knowledge PR.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .okf.document import Actor
from .profile.spec import ApproverRule, CheckId, GateSpec
from .view import Concept, View


@dataclass(frozen=True)
class CheckResult:
    check: CheckId
    passed: bool
    detail_pt: str                # e.g. "2 marcadores [PRECISA ESCLARECER] abertos (linhas 41, 58)"


@dataclass(frozen=True)
class CiEvidence:
    """Parsed from CI environment by the shell (cli/hooks), never from the agent."""
    ci_green: bool
    review_agent_findings_open: int
    pr_ref: str                   # 't0/payments-api#412'
    approvals: tuple[Actor, ...]  # human approvers of the product PR (G5)
    audit_path: str | None        # '.audit/PAY-131.tsv' if committed


@dataclass(frozen=True)
class Target:
    gate: GateSpec
    primary: Concept              # the concept the ref resolved to (or the bet's Spec/Plan for G2/G3)
    bet: Concept | None
    moves: tuple[tuple[Concept, str], ...]   # every (concept, to-state) this gate will produce
    to: str | None                # G6: shipped|killed|extended


@dataclass(frozen=True)
class GateDecision:
    target: Target
    results: tuple[CheckResult, ...]
    approvers: tuple[Actor, ...]  # resolved humans to request review from (bet owner, lead, preceptor ...)
    approver_problems: tuple[str, ...]   # e.g. junior sole approver, missing domain expert
    already: str | None           # 'approved' (gate file on main) | 'pending' (open PR) | None

    @property
    def ok(self) -> bool:
        return all(r.passed for r in self.results) and not self.approver_problems


CheckFn = Callable[[View, Target, CiEvidence | None], CheckResult]
CHECKS: Mapping[CheckId, CheckFn] = {}
# Implementation registers one function per CheckId. Import-time assertion:
#   assert set(CHECKS) == set(CheckId), "every CheckId needs an implementation"


def resolve_target(view: View, gate: GateSpec, ref_concept: Concept, to: str | None) -> Target:
    """Maps the user's ref to the gate's target_type: `gate G2 BET-042` resolves to BET-042's Spec;
    expands Move scopes ('bet-children:Slice') into concrete (concept, to) pairs; refuses moves the
    state machine does not allow from the current derived state."""
    raise NotImplementedError


def resolve_approvers(view: View, rule: ApproverRule, target: Target) -> tuple[tuple[Actor, ...], tuple[str, ...]]:
    """Roles -> humans: bet_owner = bet.decision_by; lead/aiva/flow_steward/preceptor from Accountability
    and Rotation concepts (current assignment); domain_expert from Product.domain_contacts.
    tier2_adds when target tier == 2 (or bet_type plataforma); junior_owner_adds when owner Person has
    `junior: true`. Problems are returned, not raised."""
    raise NotImplementedError


def evaluate(view: View, gate: GateSpec, ref_concept: Concept, *, to: str | None = None,
             ci: CiEvidence | None = None) -> GateDecision:
    """Runs every check in gate.checks. Checks that need a KB Policy (G7/G8) read thresholds from
    view.resolve(Ref(gate.policy_uid))['thresholds']; a missing or non-in-force policy fails the check
    with a message naming the policy (numbers are never hard-coded)."""
    raise NotImplementedError
