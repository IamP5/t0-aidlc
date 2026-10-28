"""OKF document parsing with the reference agent's exact semantics.

Invariants (copied from open-knowledge-format/src/reference_agent/bundle/document.py):
- Line 1 != '---'  -> document has no frontmatter (body only). L0 fails it for concepts.
- No closing '---' -> ParseError("Unterminated YAML frontmatter block").
- yaml SafeLoader with the timestamp implicit resolver REMOVED: datetimes stay strings and
  round-trip byte-for-byte. We never let PyYAML produce datetime objects.
- Non-mapping YAML -> ParseError. (We fix issue #38: falsy non-mappings like `[]` or `0`
  are errors too, not `or {}`.)
- `verified` is normalized only by readers (view.py), never rewritten on disk.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, NewType

import yaml

_SEGMENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")
_OFFSET_DT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$")
_ACTOR = re.compile(r"^(human|team|role|process):[a-z0-9][a-z0-9._-]*$|^[a-z0-9-]+(/[A-Za-z0-9._-]+)?/[A-Za-z0-9._-]+$")


class _NoTimestampSafeLoader(yaml.SafeLoader):
    """SafeLoader minus the timestamp resolver (reference semantics)."""
    # TODO: copy yaml_implicit_resolvers dict and drop every 'tag:yaml.org,2002:timestamp' entry.


@dataclass(frozen=True)
class BundlePath:
    """Bundle-absolute path ('/products/p/bets/BET-042/spec.md'). Segment grammar from paths.py.

    Construct only via BundlePath.parse; the raw constructor is for trusted internal use.
    """
    value: str

    @staticmethod
    def parse(raw: str) -> "BundlePath":
        """Accepts '/x/y.md' or bundle-relative 'x/y.md'; rejects '..', empty and bad segments."""
        raise NotImplementedError

    @property
    def concept_id(self) -> str:
        """Path minus leading '/' and '.md' (OKF §2 Concept ID)."""
        raise NotImplementedError

    @property
    def is_reserved(self) -> bool:
        """index.md or log.md at any level."""
        raise NotImplementedError


Instant = NewType("Instant", str)
"""ISO 8601 datetime string WITH explicit offset. Kept as str (round-trip); compare via to_utc()."""

Actor = NewType("Actor", str)
"""human:<h> | team:<s> | role:<s> | process:<id> | <agent>/<version>."""


def instant(raw: Any) -> Instant | None:
    """Validate offset-required datetime (profile pins post-2026-08-21 rule). None if invalid."""
    raise NotImplementedError


def actor(raw: Any) -> Actor | None:
    raise NotImplementedError


@dataclass(frozen=True)
class Document:
    path: BundlePath
    frontmatter: Mapping[str, Any]   # raw; timestamps are str; unknown keys preserved
    body: str
    has_frontmatter: bool
    raw: str                          # exact bytes decoded; used for no-op detection on writes


@dataclass(frozen=True)
class ParseError:
    path: BundlePath
    message: str
    line: int | None = None


def parse(path: BundlePath, text: str) -> Document | ParseError:
    """Reference OKFDocument.parse, returning a value instead of raising."""
    raise NotImplementedError


def dump(frontmatter: Mapping[str, Any], body: str) -> str:
    """Deterministic serializer used by every writer: key order = registry field order, then
    unknown keys in original order; block style; strings that look like timestamps stay quoted
    only if they were quoted. Golden-tested: parse(dump(x)) == x and dump(parse(f)) == f for
    every fixture written by the toolkit."""
    raise NotImplementedError
