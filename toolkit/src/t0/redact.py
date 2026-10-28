"""Deterministic redaction boundary. Runs BEFORE any model sees transcript text, and as the
records-lane / transcript secret+PII scan in kb check (same ruleset, same version string).

Boundary rules:
  - Raw inputs live in ~/.t0/inbox/ (outside every repo). The PreToolUse hook denies agent reads of
    that directory, so the agent only ever reads redact() output.
  - `Redacted` can only be produced by redact(); no code path persists unredacted text as Redacted.
  - Off-record spans: text between '[fora do registro]' and '[/fora do registro]' (case-insensitive,
    may span lines) is removed; only their count is kept. An unclosed marker removes to the end.
    An utterance whose text opens with "fora do registro" plus ':' or ',' (`[09:34] Ana: fora do
    registro: ...`) is one span too: the timestamp and speaker stay, the rest of the line goes.
  - Rules run on the off-record-free text; findings never overlap (earlier rule wins), SECRET first.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Pattern

RULESET_VERSION = "t0-redact/1"
KNOWN_RULESETS = frozenset({RULESET_VERSION})

OFF_RECORD_OPEN = "[fora do registro]"
OFF_RECORD_CLOSE = "[/fora do registro]"
OFF_RECORD_PLACEHOLDER = "[trecho fora do registro removido]"


class RuleKind(Enum):
    SECRET = "secret"
    CPF = "cpf"
    CNPJ = "cnpj"
    CARD = "card"
    ACCOUNT = "account"
    EMAIL = "email"
    PHONE = "phone"


@dataclass(frozen=True)
class Rule:
    kind: RuleKind
    pattern: Pattern[str]
    validator: str | None    # 'cpf' | 'cnpj' | 'luhn' | None
    replacement: str
    group: int = 0           # which group is the sensitive value (key=value rules keep the key)


@dataclass(frozen=True)
class Finding:
    kind: RuleKind
    line: int                # 1-based
    col: int                 # 1-based
    start: int
    end: int


class _Token: ...


_TOKEN = _Token()


class Redacted(str):
    """Text that passed redact(). Constructing it anywhere else raises TypeError."""

    def __new__(cls, value: str, _token: object = None) -> "Redacted":
        if _token is not _TOKEN:
            raise TypeError("Redacted só é produzido por redact()")
        return super().__new__(cls, value)


@dataclass(frozen=True)
class RedactionReport:
    version: str
    counts: dict[RuleKind, int]
    off_record_spans: int

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def _digits(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())


def _cpf_ok(raw: str) -> bool:
    d = [int(c) for c in _digits(raw)]
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for n in (9, 10):
        s = sum(d[i] * (n + 1 - i) for i in range(n))
        if (s * 10 % 11) % 10 != d[n]:
            return False
    return True


def _cnpj_ok(raw: str) -> bool:
    d = [int(c) for c in _digits(raw)]
    if len(d) != 14 or len(set(d)) == 1:
        return False
    for n, weights in ((12, (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)), (13, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))):
        r = sum(a * b for a, b in zip(d[:n], weights)) % 11
        if (0 if r < 2 else 11 - r) != d[n]:
            return False
    return True


def _luhn_ok(raw: str) -> bool:
    d = [int(c) for c in _digits(raw)]
    if not 13 <= len(d) <= 19:
        return False
    total = 0
    for i, x in enumerate(reversed(d)):
        if i % 2:
            x = x * 2 - 9 if x > 4 else x * 2
        total += x
    return total % 10 == 0


_VALIDATORS = {"cpf": _cpf_ok, "cnpj": _cnpj_ok, "luhn": _luhn_ok}

_SECRET_KEYS = (r"password|passwd|pwd|senha|secret|segredo|token|api[_-]?key|apikey|access[_-]?key"
                r"|client[_-]?secret|private[_-]?key")
_SECRET_VALUE = r"(?![\[$<{%])[^\s\"',;]{4,}"


def _r(kind: RuleKind, pattern: str, replacement: str, *, validator: str | None = None, group: int = 0,
       flags: int = 0) -> Rule:
    return Rule(kind, re.compile(pattern, flags), validator, replacement, group)


_S = "[SEGREDO]"

DEFAULT_RULES: tuple[Rule, ...] = (
    _r(RuleKind.SECRET, r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----", _S),
    _r(RuleKind.SECRET, r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", _S),
    _r(RuleKind.SECRET, r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", _S),
    _r(RuleKind.SECRET, r"\bgithub_pat_[A-Za-z0-9_]{22,}", _S),
    _r(RuleKind.SECRET, r"\bxox[abprs]-[A-Za-z0-9-]{10,}", _S),
    _r(RuleKind.SECRET, r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", _S),
    _r(RuleKind.SECRET, r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}", _S),
    _r(RuleKind.SECRET, r"\bAIza[0-9A-Za-z_-]{35}", _S),
    _r(RuleKind.SECRET, r"\bATATT3[A-Za-z0-9_=-]{20,}", _S),
    _r(RuleKind.SECRET, r"(?i)\bbearer\s+([A-Za-z0-9._~+/-]{20,}=*)", _S, group=1),
    _r(RuleKind.SECRET, r"\b[a-z][a-z0-9+.-]*://[^\s:/@]+:((?!\[SEGREDO\]@)[^\s@/]+)@", _S, group=1),
    _r(RuleKind.SECRET, rf"(?i)\b(?:{_SECRET_KEYS})\b[\"']?\s*[:=]\s*[\"']?({_SECRET_VALUE})", _S, group=1),
    _r(RuleKind.CNPJ, r"(?<![\d.])\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?![\d])", "[CNPJ]", validator="cnpj"),
    _r(RuleKind.CPF, r"(?<![\d.])\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?![\d])", "[CPF]", validator="cpf"),
    _r(RuleKind.CARD, r"(?<!\d)[2-6]\d{3}(?:[ -]?\d{3,4}){2,4}(?:[ -]?\d{1,4})?(?!\d)", "[CARTAO]",
       validator="luhn"),
    _r(RuleKind.ACCOUNT, r"(?i)\b(?:ag[êe]ncia|ag\.?)\s*(?:n[º°o.]\s*)?[:\-]?\s*(\d{3,5}(?:-[\dxX])?)\b",
       "[CONTA]", group=1),
    _r(RuleKind.ACCOUNT,
       r"(?i)\b(?:conta(?:\s+corrente|\s+poupan[çc]a)?|c/c)\s*(?:n[º°o.]\s*)?[:\-]?\s*(\d{3,12}-[\dxX]|\d{5,12})\b",
       "[CONTA]", group=1),
    _r(RuleKind.EMAIL, r"\b(?!git@)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]"),
    _r(RuleKind.PHONE, r"(?:\+55\s?)?(?:\(\s?[1-9]{2}\s?\)|(?<![\d/.-])[1-9]{2})\s?9?\d{4}[-\s]?\d{4}(?![\d])",
       "[TELEFONE]"),
)


def _line_col(text: str, pos: int) -> tuple[int, int]:
    line = text.count("\n", 0, pos) + 1
    return line, pos - (text.rfind("\n", 0, pos) + 1) + 1


def scan(text: str, rules: tuple[Rule, ...] = DEFAULT_RULES) -> tuple[Finding, ...]:
    """Detect only (kb check SCAN.*, new_record guard, kb_record refusal). Findings carry no text."""
    claimed: list[tuple[int, int]] = []
    found: list[Finding] = []
    for rule in rules:
        check = _VALIDATORS.get(rule.validator) if rule.validator else None
        for m in rule.pattern.finditer(text):
            start, end = m.span(rule.group)
            if check and not check(m.group(rule.group)):
                continue
            if any(start < e and s < end for s, e in claimed):
                continue
            claimed.append((start, end))
            found.append(Finding(rule.kind, *_line_col(text, start), start, end))
    return tuple(sorted(found, key=lambda f: f.start))


_OFF_RECORD = re.compile(
    re.escape(OFF_RECORD_OPEN) + r"[\s\S]*?(?:" + re.escape(OFF_RECORD_CLOSE) + r"|\Z)", re.IGNORECASE)
_STRAY_CLOSE = re.compile(re.escape(OFF_RECORD_CLOSE), re.IGNORECASE)
_OFF_RECORD_UTTERANCE = re.compile(
    r"^(?P<head>[ \t]*(?:\[[^\]\n]*\][ \t]*)?(?:[^\n:\[\]]{1,60}:[ \t]*)?)fora do registro[ \t]*[:,][^\n]*",
    re.IGNORECASE | re.MULTILINE)


def _drop_off_record(raw: str) -> tuple[str, int]:
    text, spans = _OFF_RECORD.subn(OFF_RECORD_PLACEHOLDER, raw)
    text, inline = _OFF_RECORD_UTTERANCE.subn(lambda m: m["head"] + OFF_RECORD_PLACEHOLDER, text)
    return _STRAY_CLOSE.sub("", text), spans + inline


def redact(raw: str, rules: tuple[Rule, ...] = DEFAULT_RULES) -> tuple[Redacted, RedactionReport]:
    """Remove off-record spans, then replace every finding. Idempotent: redact(redact(x)) == redact(x)."""
    text, spans = _drop_off_record(raw)
    findings = scan(text, rules)
    replacement = {r.kind: r.replacement for r in rules}
    counts: dict[RuleKind, int] = {}
    out: list[str] = []
    pos = 0
    for f in findings:
        out.append(text[pos:f.start])
        out.append(replacement[f.kind])
        pos = f.end
        counts[f.kind] = counts.get(f.kind, 0) + 1
    out.append(text[pos:])
    return Redacted("".join(out), _TOKEN), RedactionReport(RULESET_VERSION, counts, spans)
