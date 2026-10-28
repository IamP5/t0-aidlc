"""Deterministic redaction boundary. Runs BEFORE any model sees transcript text, and as the
records-lane / transcript secret+PII scan in kb check (same ruleset, same version string).

Boundary rules:
  - Raw inputs live in ~/.t0/inbox/ (outside every repo). The PreToolUse hook denies agent reads of
    that directory and of *.vtt/*.srt/*.docx anywhere outside it -> the agent only ever reads output.
  - `Redacted` can only be produced by redact(). rituals.Close.transcript is typed Redacted, and the
    Transcript type is only ever written by rituals.close -> no code path persists unredacted text.
  - Off-record spans: lines between markers '[[off]]' and '[[/off]]' (or the meeting tool's equivalent
    mapped by the ritual) are removed; only their count is kept.
  - DRY_RUN (policy-transcript-retention.thresholds.persist == false, days 0-30): redact() runs, the
    report is printed, NOTHING is persisted to the KB.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Pattern

RULESET_VERSION = "t0-redact/1"


class RuleKind(Enum):
    SECRET = "secret"        # tokens, keys, private keys, JWT, connection strings (gitleaks-derived regexes)
    CPF = "cpf"              # 11 digits with/without punctuation, VALID check digits only (cuts false positives)
    CNPJ = "cnpj"            # check digits validated
    CARD = "card"            # 13-19 digits, Luhn-valid
    ACCOUNT = "account"      # agência/conta patterns near keywords ('ag', 'agência', 'conta', 'c/c')
    EMAIL = "email"
    PHONE = "phone"          # BR formats (+55, DDD, 9-digit mobile)


@dataclass(frozen=True)
class Rule:
    kind: RuleKind
    pattern: Pattern[str]
    validator: str | None    # 'cpf' | 'cnpj' | 'luhn' | None
    replacement: str         # '[CPF]', '[SEGREDO]', ...


@dataclass(frozen=True)
class Finding:
    kind: RuleKind
    line: int
    col: int


class Redacted(str):
    """Text that passed redact(). Do not construct directly (tests assert no other constructor site)."""


@dataclass(frozen=True)
class RedactionReport:
    version: str
    counts: dict[RuleKind, int]
    off_record_spans: int


DEFAULT_RULES: tuple[Rule, ...] = ()   # implementation: ordered; SECRET first


def scan(text: str, rules: tuple[Rule, ...] = DEFAULT_RULES) -> tuple[Finding, ...]:
    """Detect only (kb check SCAN.*, new_record guard, handoff)."""
    raise NotImplementedError


def redact(raw: str, rules: tuple[Rule, ...] = DEFAULT_RULES) -> tuple[Redacted, RedactionReport]:
    """Remove off-record spans, then replace every finding. Idempotent: redact(redact(x)) == redact(x)."""
    raise NotImplementedError
