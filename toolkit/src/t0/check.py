"""Conformance checker. L0 = OKF v0.2 floor (§11), L1 = t0-team profile, L2 = integrity warnings.
Also: lane rules for PRs (records add-only, derived untouched) and the secret/PII scan.

Every rule is a `Rule` with an id; tests enumerate RULES and require one negative fixture per rule
under tests/fixtures/okf/negative/<rule-id>/ (no hand-synced list of fixtures).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Sequence

from .okf.document import BundlePath, Document, ParseError
from .profile.spec import Lane
from .view import View


class Level(Enum):
    L0 = 0
    L1 = 1
    L2 = 2


class Severity(Enum):
    ERROR = "error"      # L0, L1, lane rules: block CI
    WARN = "warn"        # L2: digest only (spec forbids rejecting broken links etc.)


@dataclass(frozen=True)
class Finding:
    rule: str            # 'L0.frontmatter-parse', 'L1.uid-unique', 'LANE.records-add-only', 'SCAN.secret'
    severity: Severity
    path: BundlePath
    message_pt: str      # message written for the agent: says how to fix
    line: int | None = None


@dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]
    @property
    def ok(self) -> bool: return not any(f.severity is Severity.ERROR for f in self.findings)


@dataclass(frozen=True)
class Rule:
    id: str
    level: Level
    run: Callable[["CheckInput"], Iterable[Finding]]


@dataclass(frozen=True)
class CheckInput:
    docs: Sequence[Document | ParseError]
    view: View | None                    # None when L0 failed (no fold on broken input)
    changed: frozenset[BundlePath] | None   # PR mode: only these paths are judged for lane rules
    base_docs: Sequence[Document] | None    # PR mode: docs at merge base (add-only / derived-untouched)
    lane: Lane | None                    # PR mode: declared lane (from branch prefix rec/* or knowledge)


# L0 (spec §11 + reference parse)
#   L0.frontmatter-parse, L0.type-nonempty, L0.index-no-frontmatter (root may carry only okf_version),
#   L0.index-body-shape ('# H' + '* [t](u) - d'), L0.log-date-headings ('## YYYY-MM-DD'; log.md may carry
#   `type: Log` frontmatter, deciding G13 like the official sample), L0.okf-version ("0.2" in root index)
# L1 (profile, all derived from REGISTRY)
#   L1.type-registered, L1.required-fields, L1.field-kind, L1.enum, L1.uid-unique, L1.instant-offset,
#   L1.actor-grammar, L1.path-explicit ('/' or './'), L1.id-segment, L1.path-matches-type,
#   L1.index-description-equals, L1.derived-matches-fold (MATERIALIZED_DRIFT), L1.profile-version,
#   L1.no-gherkin (acceptance bullets), L1.tier2-trace-chain (done Tier 2 slice), L1.product-repos-match-workspace
# L2 (warn)
#   L2.relations-target-exists, L2.relations-body-link, L2.rotation-one-current, L2.stale, L2.person-exists,
#   L2.glossary-avoid, L2.anomaly (illegal transitions etc.), L2.ritual-has-closer, L2.knowledge-pr-stale-48h,
#   L2.card-budget (every active bet's card renders <= 8000)
# LANE (PR mode)
#   LANE.records-add-only (only new files, only Step/Idea/... RECORDS types, path pattern, <=20 KB, generated.by
#   coherent with PR author), LANE.derived-untouched (no edits to derived files/keys by non-render authors),
#   LANE.gate-file-immutable (a gates/<G>.md cannot be modified once on main),
#   L1.gate-checks-hold (a gate file added in a PR: gates.evaluate passes at PR head; evidence re-computed)
# SCAN
#   SCAN.secret, SCAN.pii (records + transcripts): uses redact.scan, same ruleset version.
RULES: tuple[Rule, ...] = ()   # populated in implementation; ids above are the contract


def check(inp: CheckInput, level: Level) -> Report:
    """Runs all rules with rule.level <= level, plus LANE/SCAN rules when inp.changed is set."""
    raise NotImplementedError
