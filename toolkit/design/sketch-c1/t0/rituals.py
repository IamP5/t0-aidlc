"""Rituals. The Ritual concept in the KB is the data (inputs, outputs, cadence, recorded); code adds only
what a concept cannot express: per-ritual close rules (CLOSERS). kb check L2.ritual-has-closer warns when
a Ritual concept's `command` names a slug with no closer, and a test fails when a closer has no Ritual
concept in templates/okf-kb (no hand-synced list in either direction).

open:  agenda = render inputs declared in the concept (queries over the View) -> markdown (no writes).
close: Decisions (parsed from the facilitator's decisions.yaml or the skill's structured output) ->
       ONE KnowledgeChange: Ritual Record (+ Transcript if recorded and redacted) + gate files decided
       + closer-specific files. Transcript redaction happens before close (redact.Redacted required).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .okf.document import Actor, Instant
from .redact import Redacted, RedactionReport
from .view import View
from .write import Plan, Refusal


@dataclass(frozen=True)
class Decision:
    text: str
    owner: Actor
    due: Instant | None
    gate: tuple[str, str, str | None] | None = None   # (gate id, ref, to) -> gate file in the same PR


@dataclass(frozen=True)
class Close:
    ritual: str                     # slug
    date: Instant
    facilitator: Actor
    attended: tuple[Actor, ...]
    decisions: tuple[Decision, ...]
    transcript: tuple[Redacted, RedactionReport] | None
    extra: Mapping[str, object]     # closer-specific input (archetype declarations, rotations, HI accepted...)
    cancelled: str | None = None


Closer = Callable[[View, Close], Plan | Refusal]
CLOSERS: Mapping[str, Closer] = {}
# 'betting'        : Cycle Record, archetype coverage per pod (warn), 4th consecutive primary -> Refusal unless
#                    justification, G1 gate files, rotate flow-steward + sweeper (Rotation edits)
# 'demo'           : G6 gate files (with `to`), metrics cycle snapshot, Cycle Record closed (TRANSITION record)
# 'harness-retro'  : Refusal unless every accepted Harness Item has a `pr`
# 'preceptoria'    : Refusal if a transcript is passed (never recorded)
# others           : generic (Ritual Record only)


def open_agenda(view: View, ritual_slug: str) -> str:
    raise NotImplementedError


def close(view: View, c: Close) -> Plan | Refusal:
    """Generic record + CLOSERS.get(c.ritual) merged into one KnowledgeChange on branch
    'ritual/<date>-<slug>'. Re-running with the same input yields the same branch and bytes (no-op)."""
    raise NotImplementedError
