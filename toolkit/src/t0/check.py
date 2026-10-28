"""Conformance checker. L0 = OKF v0.2 floor (§11), L1 = t0-team profile, L2 = integrity warnings.
LANE rules run in PR mode (`--changed-from REF`): derived untouched, records add-only, legal decisions.

Every rule is a `Rule` row in RULES; tests require one negative fixture per rule id under
tests/fixtures/kb-negative/<rule-id>/ (no hand-synced list).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from .gates import GHERKIN, evaluate
from .okf.document import Document, ParseError, actor, duration, instant, section, to_dt
from .profile.spec import Field, Kind, StateOwner
from .profile.table import ACCEPTANCE, PROFILE_VERSION, REGISTRY
from .redact import KNOWN_RULESETS, scan
from .view import View

DERIVED_FILES = ("index.md", "log.md", "changeset.md")
_INDEX_ENTRY = re.compile(r"^\* \[[^\]]+\]\([^)]+\)( - .+)?$")
_INDEX_LINK = re.compile(r"^\* \[[^\]]+\]\(([^)]+)\)(?: - (.+))?$")
_LOG_DATE = re.compile(r"^## \d{4}-\d{2}-\d{2}$")
_UID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_JIRA = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class Level(Enum):
    L0 = 0
    L1 = 1
    L2 = 2


class Severity(Enum):
    ERROR = "error"
    WARN = "warn"


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: Severity
    path: str
    message_pt: str
    line: int | None = None


@dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]

    @property
    def ok(self) -> bool:
        return not any(f.severity is Severity.ERROR for f in self.findings)

    def rules(self) -> set[str]:
        return {f.rule for f in self.findings}

    def format(self, fmt: str = "text") -> str:
        if fmt == "json":
            return json.dumps({"ok": self.ok, "findings": [
                {"rule": f.rule, "severity": f.severity.value, "path": f.path, "line": f.line, "message": f.message_pt}
                for f in self.findings]}, ensure_ascii=False, indent=2)
        if fmt == "github":
            return "\n".join(
                f"::{'error' if f.severity is Severity.ERROR else 'warning'} file={f.path.lstrip('/')}"
                + (f",line={f.line}" if f.line else "") + f"::{f.rule}: {f.message_pt}" for f in self.findings)
        errs = sum(f.severity is Severity.ERROR for f in self.findings)
        lines = [f"{'ERRO' if f.severity is Severity.ERROR else 'aviso'} {f.rule} {f.path}"
                 + (f":{f.line}" if f.line else "") + f": {f.message_pt}" for f in self.findings]
        lines.append(f"kb check: {errs} erro(s), {len(self.findings) - errs} aviso(s)" if self.findings else "kb check: ok")
        return "\n".join(lines)


@dataclass(frozen=True)
class CheckInput:
    docs: Sequence[Document | ParseError]
    view: View | None
    now: str
    changed: frozenset[str] | None = None            # PR mode: bundle paths changed vs REF (incl. deleted)
    base_docs: Mapping[str, Document] | None = None   # PR mode: docs at REF
    base_view: View | None = None


@dataclass(frozen=True)
class Rule:
    id: str
    level: Level
    run: Callable[[CheckInput], Iterable[Finding]]
    lane: bool = False


def _err(rule: str, path: str, msg: str, line: int | None = None) -> Finding:
    return Finding(rule, Severity.ERROR, path, msg, line)


def _warn(rule: str, path: str, msg: str, line: int | None = None) -> Finding:
    return Finding(rule, Severity.WARN, path, msg, line)


def _docs(inp: CheckInput) -> list[Document]:
    return [d for d in inp.docs if isinstance(d, Document)]


def _concepts(inp: CheckInput) -> list[Document]:
    return [d for d in _docs(inp) if not d.path.is_reserved and d.has_frontmatter]


def _spec_of(d: Document):
    return REGISTRY.type_named(str(d.frontmatter.get("type", "")))


# ------------------------------------------------------------------ L0


def _parse(inp: CheckInput) -> Iterable[Finding]:
    for d in inp.docs:
        if isinstance(d, ParseError):
            yield _err("L0.frontmatter-parse", d.path.value, d.message, d.line)


def _type_nonempty(inp: CheckInput) -> Iterable[Finding]:
    for d in _docs(inp):
        if d.path.is_reserved:
            continue
        t = d.frontmatter.get("type")
        if not d.has_frontmatter:
            yield _err("L0.type-nonempty", d.path.value, "concept sem frontmatter; comece o arquivo com '---' e `type:`", 1)
        elif not isinstance(t, str) or not t.strip():
            yield _err("L0.type-nonempty", d.path.value, "`type` vazio ou ausente", 2)


def _index_fm(inp: CheckInput) -> Iterable[Finding]:
    for d in _docs(inp):
        if d.path.name != "index.md":
            continue
        root = d.path.value == "/index.md"
        extra = set(d.frontmatter) - ({"okf_version"} if root else set())
        if (d.has_frontmatter and not root) or extra:
            yield _err("L0.index-frontmatter", d.path.value,
                       "index.md não tem frontmatter (só o da raiz, e só `okf_version`)", 1)


def _index_shape(inp: CheckInput) -> Iterable[Finding]:
    for d in _docs(inp):
        if d.path.name != "index.md":
            continue
        offset = d.raw.count("\n") - d.body.count("\n")
        for i, line in enumerate(d.body.splitlines(), offset + 1):
            s = line.rstrip()
            if s and not s.startswith("# ") and not _INDEX_ENTRY.match(s):
                yield _err("L0.index-shape", d.path.value, "linha de index fora do formato '# Seção' ou '* [t](u) - d'", i)
                break


def _log_headings(inp: CheckInput) -> Iterable[Finding]:
    for d in _docs(inp):
        if d.path.name != "log.md":
            continue
        if d.has_frontmatter and d.frontmatter.get("type") != "Log":
            yield _err("L0.log-headings", d.path.value, "frontmatter de log.md só com `type: Log`", 1)
        offset = d.raw.count("\n") - d.body.count("\n")
        for i, line in enumerate(d.body.splitlines(), offset + 1):
            if line.startswith("## ") and not _LOG_DATE.match(line.rstrip()):
                yield _err("L0.log-headings", d.path.value, "título de data no log é '## AAAA-MM-DD'", i)


def _okf_version(inp: CheckInput) -> Iterable[Finding]:
    root = next((d for d in _docs(inp) if d.path.value == "/index.md"), None)
    if root is None or str(root.frontmatter.get("okf_version")) != "0.2":
        yield _err("L0.okf-version", "/index.md", 'o index.md da raiz declara `okf_version: "0.2"`')


# ------------------------------------------------------------------ L1


def _type_registered(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        t = d.frontmatter.get("type")
        if isinstance(t, str) and t.strip() and _spec_of(d) is None:
            yield _err("L1.type-registered", d.path.value, f"tipo {t!r} não existe no profile t0-team (veja /profile.md)")


def _required(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        spec = _spec_of(d)
        if spec is None or spec.name in ("Log",):
            continue
        for f in REGISTRY.fields(spec):
            if f.required and d.frontmatter.get(f.name) is None:
                yield _err("L1.required-fields", d.path.value, f"falta `{f.name}` ({f.doc_pt or f.kind.value})")
        if spec.stale_required and d.frontmatter.get("stale_after") is None:
            yield _err("L1.required-fields", d.path.value, f"{spec.name} exige `stale_after`")


def kind_problem(f: Field, v: Any, states: tuple[str, ...]) -> str | None:
    k = f.kind
    if k in (Kind.STR, Kind.TEXT, Kind.PATH):
        if not isinstance(v, str):
            return "texto"
        if k is Kind.PATH and v and not v.startswith(("/", "./", "http")):
            return "caminho começando com / ou ./"
    elif k is Kind.UID:
        return None if isinstance(v, str) and _UID.match(v) else "id [A-Za-z0-9._-]"
    elif k is Kind.INT:
        return None if isinstance(v, int) and not isinstance(v, bool) else "inteiro"
    elif k is Kind.BOOL:
        return None if isinstance(v, bool) else "true ou false"
    elif k is Kind.INSTANT:
        return None if instant(v) else "data ISO 8601 com offset (2026-10-28T10:00:00-03:00)"
    elif k is Kind.DURATION:
        return None if duration(v) else "duração ISO 8601 (P2W, P1D, PT30M)"
    elif k is Kind.ACTOR:
        return None if actor(v) else "ator human:, team:, role:, process: ou agente/versão"
    elif k is Kind.JIRA_KEY:
        return None if isinstance(v, str) and _JIRA.match(v) else "chave Jira (PAY-123)"
    elif k is Kind.ENUM:
        allowed = f.enum or states
        return None if not allowed or v in allowed else "um de: " + ", ".join(allowed)
    elif k is Kind.LIST_STR:
        return None if isinstance(v, list) and all(isinstance(x, str) for x in v) else "lista YAML de textos"
    elif k is Kind.LIST_ACTOR:
        return None if isinstance(v, list) and all(actor(x) for x in v) else "lista de atores"
    elif k is Kind.MAP:
        return None if isinstance(v, dict) else "mapa"
    elif k is Kind.LIST_MAP:
        return None if isinstance(v, list) and all(isinstance(x, dict) for x in v) or isinstance(v, dict) and f.name == "verified" else "lista de mapas"
    return None


def _field_kind(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        spec = _spec_of(d)
        if spec is None:
            continue
        states = tuple(spec.states.status_of) if spec.states else ()
        for f in REGISTRY.fields(spec):
            v = d.frontmatter.get(f.name)
            if v is None:
                continue
            prob = kind_problem(f, v, states if f.name == "state" else ())
            if prob:
                yield _err("L1.field-kind", d.path.value, f"`{f.name}` precisa ser {prob}; está {v!r}"[:300])
        g = d.frontmatter.get("generated")
        if isinstance(g, dict) and (not actor(g.get("by")) or not instant(g.get("at"))):
            yield _err("L1.field-kind", d.path.value, "`generated` é { by: <ator>, at: <data com offset> }")
        ver = d.frontmatter.get("verified")
        for e in ([ver] if isinstance(ver, dict) else ver if isinstance(ver, list) else []):
            if isinstance(e, dict) and (not actor(e.get("by")) or not instant(e.get("at"))):
                yield _err("L1.field-kind", d.path.value, "cada `verified` é { by: <ator>, at: <data com offset> }")


def _uid_unique(inp: CheckInput) -> Iterable[Finding]:
    seen: dict[str, str] = {}
    for d in _concepts(inp):
        uid = d.frontmatter.get("uid")
        if not isinstance(uid, str):
            continue
        if uid in seen:
            yield _err("L1.uid-unique", d.path.value, f"uid {uid!r} já usado em {seen[uid]}; renumere (`t0 new` reserva o próximo)")
        else:
            seen[uid] = d.path.value


def _path_matches(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        spec = _spec_of(d)
        if spec is not None and not REGISTRY.path_ok(spec, d.path.value):
            yield _err("L1.path-matches-type", d.path.value, f"{spec.name} mora em: " + ", ".join(spec.paths))


def _id_segment(inp: CheckInput) -> Iterable[Finding]:
    for d in inp.docs:
        if not d.path.segments_ok:
            yield _err("L1.id-segment", d.path.value, "segmento de caminho fora de [A-Za-z0-9_][A-Za-z0-9_.-]*")


def _index_description(inp: CheckInput) -> Iterable[Finding]:
    by_path = {d.path.value: d for d in _docs(inp)}
    for d in _docs(inp):
        if d.path.name != "index.md":
            continue
        folder = d.path.value.rsplit("/", 1)[0]
        for line in d.body.splitlines():
            m = _INDEX_LINK.match(line.rstrip())
            if not m or not m.group(1).endswith(".md"):
                continue
            url = m.group(1)
            target = url if url.startswith("/") else f"{folder}/{url.removeprefix('./')}"
            t = by_path.get(target)
            if t is not None and m.group(2) is not None and m.group(2) != t.frontmatter.get("description"):
                yield _err("L1.index-description", d.path.value,
                           f"a descrição de {target} no index difere do `description` dela; rode `t0 kb render`")


def _profile_version(inp: CheckInput) -> Iterable[Finding]:
    p = next((d for d in _docs(inp) if d.path.value == "/profile.md"), None)
    if p is None:
        yield _err("L1.profile-version", "/profile.md", "falta /profile.md; rode `t0 gen --scope kb`")
    elif str(p.frontmatter.get("profile_version")) != PROFILE_VERSION:
        yield _err("L1.profile-version", "/profile.md",
                   f"profile_version {p.frontmatter.get('profile_version')!r}, o toolkit é {PROFILE_VERSION}; rode `t0 gen --scope kb`")


def _no_gherkin(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        if d.frontmatter.get("type") in ("Spec", "Slice"):
            for a in section(d.body, ACCEPTANCE).bullets:
                if GHERKIN.match(a):
                    yield _err("L1.no-gherkin", d.path.value, f"critério em Gherkin: {a[:50]!r}; escreva bullet direto")


def _repos_match(inp: CheckInput) -> Iterable[Finding]:
    docs = {d.path.value: d for d in _concepts(inp)}
    for path, d in docs.items():
        if d.frontmatter.get("type") != "Product":
            continue
        ws = docs.get(path.rsplit("/", 1)[0] + "/workspace.md")
        block = ws.frontmatter.get("workspace") if ws else None
        if not isinstance(block, dict):
            continue
        names = sorted(str(r.get("name")) for r in block.get("repos") or [] if isinstance(r, dict))
        have = sorted(str(x) for x in d.frontmatter.get("repos") or [])
        if names != have:
            yield _err("L1.product-repos-match-workspace", path, f"`repos` {have} difere do workspace.md {names}")


def _secret(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        t = d.frontmatter.get("type")
        if t not in ("Step", "Transcript", "Ritual Record"):
            continue
        found = scan(d.raw)
        if found:
            kinds = sorted({f.kind.value for f in found})
            yield _err("SCAN.secret", d.path.value, f"contém {', '.join(kinds)}; remova (registros e transcrições passam pelo redator)",
                       found[0].line)
        if t == "Transcript" and d.frontmatter.get("redaction") not in KNOWN_RULESETS:
            yield _err("SCAN.secret", d.path.value, "transcrição sem `redaction` de um redator conhecido; use `t0 transcript redact`")


# ------------------------------------------------------------------ L2


def _actors(fm: Mapping[str, Any]) -> Iterable[str]:
    for k in ("owner", "decision_by", "facilitator"):
        if isinstance(fm.get(k), str):
            yield fm[k]
    for k in ("roster", "deciders", "attended", "holders"):
        for x in fm.get(k) or []:
            if isinstance(x, str):
                yield x


def _relations(inp: CheckInput) -> Iterable[Finding]:
    paths = {d.path.value for d in inp.docs}
    for d in _concepts(inp):
        rel = d.frontmatter.get("relations")
        if not isinstance(rel, dict):
            continue
        for k, v in rel.items():
            for t in (v if isinstance(v, list) else [v]):
                if isinstance(t, str) and t.startswith("/") and t not in paths:
                    yield _warn("L2.relations-target-exists", d.path.value, f"relations.{k} aponta para {t}, que não existe")


def _stale(inp: CheckInput) -> Iterable[Finding]:
    for d in _concepts(inp):
        s = d.frontmatter.get("stale_after")
        if instant(s) and to_dt(s) <= to_dt(inp.now):
            yield _warn("L2.stale", d.path.value, f"vencido desde {s}; revise ou aposente")


def _rotation_current(inp: CheckInput) -> Iterable[Finding]:
    now = to_dt(inp.now)
    for d in _concepts(inp):
        if d.frontmatter.get("type") != "Rotation":
            continue
        cur = [a for a in d.frontmatter.get("assignments") or [] if isinstance(a, dict) and instant(a.get("from"))
               and instant(a.get("to")) and to_dt(a["from"]) <= now < to_dt(a["to"])]
        if len(cur) != 1:
            yield _warn("L2.rotation-current", d.path.value, f"{len(cur)} atribuições cobrem agora (esperado 1); a Demo grava o rodízio")


def _person_exists(inp: CheckInput) -> Iterable[Finding]:
    handles = {str(d.frontmatter.get("handle")) for d in _concepts(inp) if d.frontmatter.get("type") == "Person"}
    for d in _concepts(inp):
        if d.frontmatter.get("type") == "Step":
            continue
        for a in _actors(d.frontmatter):
            if a.startswith("human:") and a[6:] not in handles:
                yield _warn("L2.person-exists", d.path.value, f"{a} não tem /team/people/<handle>.md")


def _drift(inp: CheckInput) -> Iterable[Finding]:
    if inp.view is None:
        return
    for c in inp.view.concepts.values():
        if c.spec is None:
            continue
        for k in REGISTRY.render_keys(c.spec):
            disk = c.doc.frontmatter.get(k)
            if k == "verified" and isinstance(disk, dict):
                disk = [disk]
            if disk is not None and k in c.derived and disk != c.derived[k]:
                yield _warn("L2.derived-drift", c.path, f"`{k}` no disco é {disk!r}, o fold dá {c.derived[k]!r}; o kb-render corrige")


def _anomaly(inp: CheckInput) -> Iterable[Finding]:
    for a in inp.view.anomalies if inp.view else ():
        yield _warn("L2.anomaly", a.source.value, f"{a.kind.value} em {a.target}: {a.detail}")


# ------------------------------------------------------------------ LANE (PR mode)


def _lane_derived(inp: CheckInput) -> Iterable[Finding]:
    if os.environ.get("T0_ROLE") == "kb-render" or inp.changed is None:
        return
    base = inp.base_docs or {}
    for p in sorted(inp.changed):
        name = p.rsplit("/", 1)[-1]
        if name in DERIVED_FILES or p == "/profile.md":
            yield _err("LANE.derived-untouched", p, f"`{name}` é derivado; só o kb-render (ou `t0 gen`) escreve")
            continue
        c = inp.view.at(p) if inp.view else None
        if c is None or c.spec is None:
            continue
        before = base.get(p)
        for k in REGISTRY.render_keys(c.spec):
            new, old = c.doc.frontmatter.get(k), before.frontmatter.get(k) if before else None
            if new != old and new is not None and new != c.derived.get(k):
                yield _err("LANE.derived-untouched", p, f"`{k}` é derivado e foi editado à mão ({old!r} -> {new!r})")


def _lane_records(inp: CheckInput) -> Iterable[Finding]:
    if inp.changed is None:
        return
    base = inp.base_docs or {}
    for p in sorted(inp.changed):
        old = base.get(p)
        if old is not None and old.frontmatter.get("type") == "Step":
            yield _err("LANE.records-add-only", p, "registro é imutável; registre um novo com `t0 log`")


def _lane_state(inp: CheckInput) -> Iterable[Finding]:
    if inp.changed is None or inp.view is None:
        return
    base = inp.base_docs or {}
    for p in sorted(inp.changed):
        c = inp.view.at(p)
        if c is None or c.spec is None or not c.spec.states or c.spec.states.owner is not StateOwner.DECISION:
            continue
        sm = c.spec.states
        old_doc = base.get(p)
        old = str(old_doc.frontmatter.get("state") or sm.initial) if old_doc else sm.initial
        new = str(c.doc.frontmatter.get("state") or sm.initial)
        if new == old:
            continue
        if not sm.allows(old, new):
            yield _err("LANE.state-transition", p, f"{c.spec.name} não vai de `{old}` para `{new}`")
            continue
        gate = next((t.via_gate for t in sm.transitions if old in t.from_states and t.to == new and t.via_gate), None)
        if gate is None:
            continue
        d = evaluate(inp.view, REGISTRY.gate(gate), c, now=inp.now)
        if isinstance(d, str):
            yield _err("LANE.state-transition", p, d)
            continue
        probs = [r.detail_pt for r in d.results if not r.passed] + list(d.approver_problems)
        if probs:
            yield _err("LANE.state-transition", p, f"gate {gate} não passa no head: " + "; ".join(probs))


RULES: tuple[Rule, ...] = (
    Rule("L0.frontmatter-parse", Level.L0, _parse),
    Rule("L0.type-nonempty", Level.L0, _type_nonempty),
    Rule("L0.index-frontmatter", Level.L0, _index_fm),
    Rule("L0.index-shape", Level.L0, _index_shape),
    Rule("L0.log-headings", Level.L0, _log_headings),
    Rule("L0.okf-version", Level.L0, _okf_version),
    Rule("L1.type-registered", Level.L1, _type_registered),
    Rule("L1.required-fields", Level.L1, _required),
    Rule("L1.field-kind", Level.L1, _field_kind),
    Rule("L1.uid-unique", Level.L1, _uid_unique),
    Rule("L1.path-matches-type", Level.L1, _path_matches),
    Rule("L1.id-segment", Level.L1, _id_segment),
    Rule("L1.index-description", Level.L1, _index_description),
    Rule("L1.profile-version", Level.L1, _profile_version),
    Rule("L1.no-gherkin", Level.L1, _no_gherkin),
    Rule("L1.product-repos-match-workspace", Level.L1, _repos_match),
    Rule("SCAN.secret", Level.L1, _secret),
    Rule("L2.relations-target-exists", Level.L2, _relations),
    Rule("L2.stale", Level.L2, _stale),
    Rule("L2.rotation-current", Level.L2, _rotation_current),
    Rule("L2.person-exists", Level.L2, _person_exists),
    Rule("L2.derived-drift", Level.L2, _drift),
    Rule("L2.anomaly", Level.L2, _anomaly),
    Rule("LANE.derived-untouched", Level.L1, _lane_derived, lane=True),
    Rule("LANE.records-add-only", Level.L1, _lane_records, lane=True),
    Rule("LANE.state-transition", Level.L1, _lane_state, lane=True),
)


def check(inp: CheckInput, level: Level) -> Report:
    """Rules with rule.level <= level; LANE rules only in PR mode. L1+ rules skip when L0 failed."""
    findings: list[Finding] = []
    for r in RULES:
        if r.level.value > level.value or (r.lane and inp.changed is None):
            continue
        findings += list(r.run(inp))
    return Report(tuple(findings))
