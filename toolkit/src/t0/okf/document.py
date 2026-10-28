"""OKF document parsing with the reference agent's semantics.

- Line 1 != '---' -> no frontmatter (body only). L0 fails it for concepts.
- No closing '---' -> ParseError("frontmatter YAML sem '---' de fechamento").
- SafeLoader without the timestamp resolver: datetimes stay strings and round-trip.
- Non-mapping YAML (including falsy `[]` or `0`) -> ParseError.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Mapping, NewType

import yaml

_SEGMENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")
_OFFSET_DT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$")
_ACTOR = re.compile(r"^(human|team|role|process):[a-z0-9][a-z0-9._-]*$|^[a-z0-9-]+(/[A-Za-z0-9._-]+)?/[A-Za-z0-9._-]+$")
_DURATION = re.compile(r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")


class _NoTimestampSafeLoader(yaml.SafeLoader):
    pass


_NoTimestampSafeLoader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class _Dumper(yaml.SafeDumper):
    pass


def _str_rep(d: yaml.SafeDumper, s: str) -> yaml.Node:
    style = "|" if "\n" in s else None
    return d.represent_scalar("tag:yaml.org,2002:str", s, style=style)


_Dumper.add_representer(str, _str_rep)


@dataclass(frozen=True)
class BundlePath:
    """Bundle-absolute path ('/products/p/bets/BET-042/spec.md')."""
    value: str

    @staticmethod
    def parse(raw: str) -> "BundlePath":
        s = raw.strip()
        if s.startswith("./"):
            s = s[2:]
        s = "/" + s.lstrip("/")
        parts = s.split("/")[1:]
        if not parts or any(p in ("", ".", "..") for p in parts):
            raise ValueError(f"caminho inválido: {raw!r}")
        return BundlePath(s)

    @property
    def segments(self) -> tuple[str, ...]:
        return tuple(self.value.strip("/").split("/"))

    @property
    def segments_ok(self) -> bool:
        return all(_SEGMENT.fullmatch(p.removesuffix(".md")) for p in self.segments)

    @property
    def concept_id(self) -> str:
        return self.value.lstrip("/").removesuffix(".md")

    @property
    def name(self) -> str:
        return self.segments[-1]

    @property
    def is_reserved(self) -> bool:
        return self.name in ("index.md", "log.md")


Instant = NewType("Instant", str)
Actor = NewType("Actor", str)


def instant(raw: Any) -> Instant | None:
    return Instant(raw) if isinstance(raw, str) and _OFFSET_DT.match(raw) else None


def to_dt(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def actor(raw: Any) -> Actor | None:
    return Actor(raw) if isinstance(raw, str) and _ACTOR.match(raw) else None


def duration(raw: Any) -> timedelta | None:
    """ISO 8601 duration; months count 30 days and years 365 (enough to compare appetites)."""
    m = _DURATION.match(raw) if isinstance(raw, str) and raw != "P" else None
    if not m or not any(m.groups()):
        return None
    y, mo, w, d, h, mi, s = (int(g or 0) for g in m.groups())
    return timedelta(days=365 * y + 30 * mo + 7 * w + d, hours=h, minutes=mi, seconds=s)


@dataclass(frozen=True)
class Document:
    path: BundlePath
    frontmatter: Mapping[str, Any]
    body: str
    has_frontmatter: bool
    raw: str


@dataclass(frozen=True)
class BodySection:
    """A '## <title>' section of a body, with comments, empty bullets and '<placeholder>' lines removed."""
    text: str
    bullets: tuple[str, ...]


def _fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().casefold().strip()


_HEADING = re.compile(r"^(#{1,2})\s+(.*?)\s*#*\s*$")
_PLACEHOLDER = re.compile(r"^\s*(?:[-*]\s+)?<[^>]*>\s*$")
_BULLET = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")


def section(body: str, title: str) -> BodySection:
    """Text and bullets under the first '## <title>' heading; title match ignores case and accents."""
    want, lines, inside = _fold(title), [], False
    for line in body.splitlines():
        m = _HEADING.match(line)
        if m:
            if inside:
                break
            inside = len(m.group(1)) == 2 and _fold(m.group(2)) == want
        elif inside:
            lines.append(line)
    text = re.sub(r"<!--.*?-->", "", "\n".join(lines), flags=re.DOTALL)
    kept = [l for l in text.splitlines() if not _PLACEHOLDER.match(l) and not re.fullmatch(r"\s*[-*]\s*", l)]
    bullets = tuple(m.group(1) for l in kept if (m := _BULLET.match(l)))
    return BodySection("\n".join(kept).strip(), bullets)


@dataclass(frozen=True)
class ParseError:
    path: BundlePath
    message: str
    line: int | None = None


def parse(path: BundlePath, text: str) -> Document | ParseError:
    lines = text.split("\n")
    if lines[0].rstrip("\r") != "---":
        return Document(path, {}, text, False, text)
    end = next((i for i, l in enumerate(lines[1:], 1) if l.rstrip("\r") == "---"), None)
    if end is None:
        return ParseError(path, "frontmatter YAML sem '---' de fechamento", 1)
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=_NoTimestampSafeLoader)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        return ParseError(path, f"YAML inválido: {getattr(e, 'problem', e)}", (mark.line + 2) if mark else None)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return ParseError(path, "frontmatter precisa ser um mapa YAML", 2)
    return Document(path, data, "\n".join(lines[end + 1:]), True, text)


def dump(frontmatter: Mapping[str, Any], body: str) -> str:
    """Deterministic serializer: key order as given, block style, unicode kept."""
    fm = yaml.dump(dict(frontmatter), Dumper=_Dumper, sort_keys=False, allow_unicode=True,
                   default_flow_style=False, width=1000)
    return f"---\n{fm}---\n{body}"
