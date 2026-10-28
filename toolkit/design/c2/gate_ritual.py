"""t0.core.gate and t0.core.ritual: the two generic engines every gate/ritual skill calls.

gate.plan() is pure (no I/O beyond reading bundle + optional forge snapshot); gate.apply() writes
through Writer.propose. Running apply twice yields a noop ProposeResult.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from .checks import Finding
from .okf import Bundle, BundlePath, Doc
from .profile import GateSpec, Profile
from .redact import RedactionReport
from .writes import ChangeSet, Step, Writer


# ----------------------------------------------------------------------------- gate

@dataclass(frozen=True)
class GatePlan:
    gate: GateSpec
    target: Doc
    status: Literal["ready", "blocked", "already"]   # already = target is past this transition
    findings: tuple[Finding, ...]                     # from gate.checks
    approvers_required: frozenset[str]                # from approver rule
    approvers_present: frozenset[str]                 # from `by` + forge approvals when re-planned on a PR
    patch: ChangeSet | None                           # state + verified entry (+ Bet close fields) ; None if blocked
    step: Step | None                                 # log_step record
    jira: tuple[tuple[str, str], ...]                 # (key, status) emitted via render after merge

    def explain(self) -> str:
        """pt-BR, one line per finding and per missing approver; what the skill prints."""
        raise NotImplementedError


def plan(bundle: Bundle, profile: Profile, gate_id: str, target: Doc | str, *, by: str,
         now: str, extra: Mapping[str, str] | None = None) -> GatePlan:
    """target may be a Doc, a bet id (G1/G2/G3/G6 -> the bet's spec/plan/bet), a slice jira key (G4/G5)
    or a product id (G7/G8); resolution uses profile.gates[gate_id].target + bundle.bet()/by_jira().
    `extra` carries gate-specific inputs (G6: verdict shipped|killed|extended + aprendizado;
    G5: PR id to copy approvals; G4: CI run url)."""
    raise NotImplementedError


def apply(gp: GatePlan, writer: Writer) -> str:
    """Open the gate PR (knowledge lane) with the patch, spool the log_step.
    For G4/G5 (CI-driven, approver process:ci) the caller is the KB workflow and the PR is
    auto-merged by the KB-writer App. Returns the PR id."""
    raise NotImplementedError


def resolve_target(bundle: Bundle, profile: Profile, gate_id: str, ref: str) -> Doc:
    """BET-042 -> spec.md for G2, plan.md for G3, bet.md for G1/G6; PAY-131 -> slice; payments -> product.md."""
    raise NotImplementedError


# ----------------------------------------------------------------------------- ritual

@dataclass(frozen=True)
class Agenda:
    ritual: Doc                                   # the Ritual concept
    date: str
    cycle: str
    inputs: tuple[Doc, ...]                       # resolved from Ritual.inputs globs/types
    facilitator: str
    pre: Mapping[str, str]                        # ritual-specific computed items (review queue, archetype coverage, stale rotations)
    cancel: str | None                            # set when Ritual.cancel_rule says it cancels today

    def markdown(self) -> str: raise NotImplementedError


def open(bundle: Bundle, profile: Profile, slug: str, *, bet: str | None, now: str) -> Agenda:
    """Read /methodology/rituals/<slug>.md, resolve `inputs`, compute `pre` by slug
    (betting: archetype coverage + 3-cycle streak; bloqueios: review queue; limpeza: sweep)."""
    raise NotImplementedError


@dataclass(frozen=True)
class Decision:
    text: str
    owner: str
    due: str | None


@dataclass(frozen=True)
class CloseInput:
    slug: str
    bet: str | None
    attended: tuple[str, ...]
    decisions: tuple[Decision, ...]
    transcript_raw: str | None                    # None when the ritual is not recorded (preceptoria must be None)
    gates: tuple[tuple[str, str, Mapping[str, str]], ...]   # (gate id, target ref, extra) the ritual decided
    cycle_record: Mapping[str, object] | None     # betting: archetypes/rotations; demo: close
    cancelled: str | None


@dataclass(frozen=True)
class CloseResult:
    changeset: ChangeSet                          # Ritual Record (+ Transcript, Cycle Record)
    redaction: RedactionReport | None
    gate_plans: tuple[GatePlan, ...]
    blocked: tuple[str, ...]                      # e.g. harness-retro: "item HI-0007 aceito sem PR"


def close(bundle: Bundle, profile: Profile, ci: CloseInput, *, by: str, now: str) -> CloseResult:
    """Scaffold the Ritual Record (and Transcript via redact(), stale_after +180d, no verified),
    enforce per-ritual rules (preceptoria: transcript forbidden; harness-retro: every accepted item has a PR;
    betting: block 4th consecutive archetype without justification), plan the gates.
    Pure except redact(); caller applies via Writer.propose + gate.apply."""
    raise NotImplementedError
