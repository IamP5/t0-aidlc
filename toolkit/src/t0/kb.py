"""The facade. CLI, MCP server, hooks and rituals call only this (plus profile for enums).

Hides: view sources (git show origin/main | work tree | spool overlay), reference parse, fold, lane
routing, record naming, gate checks + approvers, card budgets, render, idempotency. Every mutating
method returns Plan | Refusal; it never performs I/O beyond reading. `apply` is the one effect.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

from .check import Level, Report
from .context import Card, CardFormat
from .gates import CiEvidence, GateDecision
from .profile.spec import EventKind, Lane
from .view import Concept, Ref, View
from .write import Applied, ApplyMode, Plan, Refusal


class Source(Enum):
    MAIN = "main"                      # `git show origin/main:<path>` of the kb clone (card, MCP, CI agents)
    MAIN_PLUS_SPOOL = "main+spool"     # MAIN + local pending records overlaid (dev default)
    WORKTREE = "worktree"              # files on disk (kb check in a PR, editing a spec on a branch)


@dataclass(frozen=True)
class Hit:
    uid: str
    path: str
    type: str
    title: str
    description: str
    state: str | None
    snippet: str


@dataclass(frozen=True)
class Query:
    text: str | None = None            # substring/ripgrep over title, description, body
    type: str | None = None            # validated against REGISTRY
    product: str | None = None
    bet: str | None = None
    state: str | None = None
    tags: tuple[str, ...] = ()
    limit: int = 20


class KB:
    @classmethod
    def open(cls, kb_dir: Path | None = None, *, source: Source = Source.MAIN_PLUS_SPOOL) -> "KB":
        """kb_dir: explicit (--kb, CI '.kb'), else walk up from cwd to '.t0/workspace.json' -> '<ws>/kb',
        else '~/.t0/config.yaml' default product. Raises KBUnavailable with the pt-BR stop message."""
        raise NotImplementedError

    # ------------------------------------------------------------- read
    def view(self) -> View: raise NotImplementedError
    def find(self, q: Query) -> list[Hit]: raise NotImplementedError
    def get(self, ref: Ref) -> Concept: raise NotImplementedError

    def check(self, level: Level = Level.L1, *, changed_from: str | None = None,
              lane: Lane | None = None) -> Report:
        """changed_from: git rev for PR mode (lane rules on the diff). lane None = infer from branch."""
        raise NotImplementedError

    def context(self, ref: Ref | None, fmt: CardFormat) -> Card | None:
        """ref None -> bet from detect chain. DELTA returns None when the card is fresh."""
        raise NotImplementedError

    # ------------------------------------------------------------- plan (pure; caller applies)
    def new(self, type_slug: str, fields: dict[str, object], *, body: str | None = None,
            from_ref: Ref | None = None) -> Plan | Refusal:
        """Template from REGISTRY (fields + template_body_pt); id by IdScheme; lane by TypeSpec.lane.
        RECORDS types -> AddRecord (spooled on apply). KNOWLEDGE types -> files written into the kb work
        tree on the bet/topic branch (checked out/created by apply); the skill fills the body and finishes
        with `t0 kb propose`. on_create scaffolds expand here. from_ref (IDEA) adds a TRANSITION(promoted)
        record."""
        raise NotImplementedError

    def propose(self, title_pt: str) -> Plan | Refusal:
        """THE one way to change knowledge: agents/humans edit files in the kb clone on a branch
        ('bet/<BET>/<handle>' or 'kb/<handle>/<topic>'), then `t0 kb propose`. Builds a KnowledgeChange from
        the work-tree diff vs origin/main; refuses derived keys/files, L1 errors, records-lane paths.
        Re-running updates the same draft PR (same branch) - idempotent."""
        raise NotImplementedError

    def gate(self, gate_id: str, ref: Ref, *, to: str | None = None,
             ci: CiEvidence | None = None) -> Plan | Refusal:
        """HUMAN_PR gates evaluate the CURRENT kb branch (WORKTREE source): `t0 gate G2 BET-042` on
        'bet/BET-042/ana' adds gates/G2.md to that branch, so the spec content and its approval are one PR,
        one review. kb check L1.gate-checks-hold re-runs the checks at PR head in KB CI (no stale evidence).
        Reviewers requested = decision.approvers; CODEOWNERS on **/gates/** is the enforcement.
        CI gates (G4/G5): CI_GATE record (ApplyMode.CI_RECORDS).
        Refusal lists every failed check and approver problem; nothing is written."""
        raise NotImplementedError

    def decide(self, gate_id: str, ref: Ref, *, to: str | None = None) -> GateDecision:
        """Dry evaluation for skills/rituals that want to show the checklist before asking a human."""
        raise NotImplementedError

    def record(self, kind: EventKind, text: str, *, bet: Ref | None = None, story: str | None = None,
               refs: Sequence[str] = (), target: Ref | None = None, to: str | None = None) -> Plan:
        """`t0 log` and MCP kb_record. Bet defaults to detect chain; no bet -> cycle steps dir."""
        raise NotImplementedError

    def render(self) -> Plan:
        """kb-render only: DerivedChange (indexes, log.md, changeset.md, derived keys, profile.md)."""
        raise NotImplementedError

    # ------------------------------------------------------------- effect
    def apply(self, plan: Plan, *, mode: ApplyMode = ApplyMode.LOCAL) -> Applied:
        raise NotImplementedError

    def push(self, *, if_due: bool = False) -> Applied:
        raise NotImplementedError


class KBUnavailable(Exception):
    """Message is the card-mandated stop: 'KB indisponível: rode `t0 ws sync` ou passe --kb. Pare.'"""
