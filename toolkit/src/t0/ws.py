"""Workspace + bet resolution + slice branches (workspace-pattern §2-3).

v0.1 scope: locate an existing workspace, read the manifest (`workspace:` block of
/products/<p>/workspace.md), the bet detection chain, `bet use` (writes .t0/bet.json) and
`slice start` (creates the slice branch in its repo). `ws init` (the cloning converge) lives in install.py;
`ws sync|status` are deferred.
Writes only local generated files and git branches in product clones; never the KB.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .context import ResolvedBet, WorkspaceFacts
from .okf.document import section
from .profile.table import ACCEPTANCE
from .view import Ref
from .write import Plan, Refusal

BRANCH_RE = re.compile(r"^([A-Z][A-Z0-9]+-\d+)-")
BET_ID_RE = re.compile(r"^BET-\d+$")
JIRA_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+)-(\d+)\b")
WORKSPACE_JSON = Path(".t0/workspace.json")
BET_JSON = Path(".t0/bet.json")


@dataclass(frozen=True)
class RepoSpec:
    name: str
    url: str
    role: str
    kind: str
    optional: bool
    tier: int
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class Manifest:
    product: str
    jira_project: str | None
    forge: str
    default_branch: str
    repos: tuple[RepoSpec, ...]
    groups: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Workspace:
    root: Path
    product: str
    repos: tuple[RepoSpec, ...]
    absent: frozenset[str]
    isolated_bet: str | None
    default_branch: str = "main"

    @property
    def kb_dir(self) -> Path:
        return self.root / "kb"

    def facts(self) -> WorkspaceFacts:
        rows = tuple((r.name, r.role, current_branch(self.root / r.name) or "-", r.name in self.absent)
                     for r in self.repos)
        return WorkspaceFacts(self.product, rows, "./kb")


@dataclass(frozen=True)
class Detection:
    bet: str | None
    story: str | None
    rule: str                  # env | branch | bet.json | none
    product: str | None = None


class ManifestError(Exception): ...


# ------------------------------------------------------------------ manifest + workspace


def _frontmatter(text: str) -> Mapping[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ManifestError("workspace.md sem frontmatter")
    try:
        end = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
    except StopIteration:
        raise ManifestError("frontmatter de workspace.md não fecha") from None
    data = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ManifestError("frontmatter de workspace.md não é um mapa")
    return data


def _repo(raw: Mapping[str, Any]) -> RepoSpec:
    name = str(raw.get("name", ""))
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ManifestError(f"nome de repo inválido: {name!r}")
    return RepoSpec(name, str(raw.get("url", "")), str(raw.get("role", "")), str(raw.get("kind", "service")),
                    bool(raw.get("optional", False)), int(raw.get("tier", 2)),
                    tuple(str(d) for d in raw.get("depends_on") or ()))


def read_manifest(kb_dir: Path, product: str) -> Manifest:
    """Parse /products/<p>/workspace.md (boundary: validates and returns domain types)."""
    path = kb_dir / "products" / product / "workspace.md"
    if not path.is_file():
        raise ManifestError(f"manifesto ausente: {path}")
    ws = _frontmatter(path.read_text(encoding="utf-8")).get("workspace")
    if not isinstance(ws, dict):
        raise ManifestError("workspace.md sem bloco `workspace:`")
    if ws.get("product") != product:
        raise ManifestError(f"workspace.product={ws.get('product')!r} difere da pasta {product!r}")
    repos = tuple(_repo(r) for r in ws.get("repos") or ())
    names = [r.name for r in repos]
    if len(set(names)) != len(names):
        raise ManifestError("nomes de repo repetidos no manifesto")
    groups = {str(k): tuple(v) for k, v in (ws.get("groups") or {}).items()}
    return Manifest(product, ws.get("jira_project"), str(ws.get("forge", "github")),
                    str(ws.get("default_branch", "main")), repos, groups)


def locate(cwd: Path) -> Workspace | None:
    """Walk up to .t0/workspace.json; the repo list comes from the KB manifest when the kb is present."""
    for d in (cwd, *cwd.parents):
        f = d / WORKSPACE_JSON
        if f.is_file():
            data = json.loads(f.read_text(encoding="utf-8"))
            product = str(data["product"])
            try:
                m = read_manifest(d / "kb", product)
                repos, branch = m.repos, m.default_branch
            except ManifestError:
                repos, branch = tuple(_repo(r) for r in data.get("repos") or ()), "main"
            return Workspace(d, product, repos, frozenset(data.get("absent") or ()), data.get("isolated_bet"), branch)
    return None


# ------------------------------------------------------------------ git


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=10)


def current_branch(repo: Path) -> str | None:
    if not repo.is_dir():
        return None
    p = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return p.stdout.strip() if p.returncode == 0 else None


# ------------------------------------------------------------------ detection chain


def read_bet_marker(cwd: Path) -> tuple[Path, Mapping[str, Any]] | None:
    for d in (cwd, *cwd.parents):
        f = d / BET_JSON
        if f.is_file():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
            return (f, data) if isinstance(data, dict) else None
    return None


def detect(cwd: Path, env: Mapping[str, str] | None = None) -> Detection:
    """T0_BET env -> branch regex -> .t0/bet.json (walking up) -> none. Needs no KB."""
    env = os.environ if env is None else env
    marker = read_bet_marker(cwd)
    product = marker[1].get("product") if marker else None
    if env.get("T0_BET"):
        return Detection(env["T0_BET"], env.get("T0_STORY") or None, "env", product)
    m = BRANCH_RE.match(current_branch(cwd) or "")
    if m:
        story = m.group(1)
        return Detection(_marker_bet_for(marker, story), story, "branch", product)
    if marker:
        data = marker[1]
        return Detection(data.get("bet"), data.get("active_story"), "bet.json", product)
    return Detection(None, None, "none", product)


def _marker_bet_for(marker: tuple[Path, Mapping[str, Any]] | None, story: str) -> str | None:
    """The card's bet, only when the card lists this story; otherwise the KB resolves it from the Slice."""
    if not marker:
        return None
    data = marker[1]
    return data.get("bet") if story in (*(data.get("stories") or ()), data.get("active_story")) else None


def divergence(cwd: Path, env: Mapping[str, str] | None = None) -> str | None:
    """Session-start warning when the branch's story is not on the .t0/bet.json card (§2.5)."""
    d = detect(cwd, env)
    marker = read_bet_marker(cwd)
    if d.rule == "branch" and d.bet is None and marker and marker[1].get("bet"):
        return f"branch é {d.story}, card é {marker[1]['bet']}: rode `t0 bet use {d.story}`"
    return None


def detect_bet(kb: Any, cwd: Path, *, task_text: str | None = None) -> ResolvedBet | None:
    """Detection chain, then the bet concept from the KB view. task_text (Jira lookup) is v0.2."""
    d = detect(cwd)
    if d.bet is not None:
        concept = kb.get(Ref(d.bet))
    elif d.story is not None:
        story = kb.get(Ref(d.story))
        concept = kb.view().bet_of(story) if story is not None else None
    else:
        return None
    return ResolvedBet(concept, d.story, d.rule) if concept is not None else None


# ------------------------------------------------------------------ bet use / slice start


def _fm(c: Any) -> Mapping[str, Any]:
    return {**dict(c.doc.frontmatter), **dict(c.derived)}


def _bet_folder(c: Any) -> str:
    path = c.doc.path.value
    m = re.match(r"^(/products/[^/]+/bets/BET-\d+)/", path)
    if not m:
        raise ValueError(path)
    return m.group(1)


def write_if_changed(path: Path, text: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def bet_use(kb: Any, ws: Workspace, ref: str) -> Plan | Refusal:
    """`t0 bet use BET-042|PAY-123`: resolve via the KB, write .t0/bet.json. Re-running is a no-op.
    A bet of another product is refused: its card would mix that bet with this workspace's repos."""
    concept = kb.get(Ref(ref))
    if concept is None:
        return Refusal((f"{ref} não encontrado no KB",))
    try:
        folder = _bet_folder(concept)
    except ValueError:
        return Refusal((f"{ref} não é uma bet nem um slice de bet",))
    bet_id = folder.rsplit("/", 1)[1]
    product = folder.split("/")[2]
    if product != ws.product:
        return Refusal((f"{bet_id} é do produto {product}, e este workspace é de {ws.product}; "
                        f"abra {ws.root.parent / product} (ou rode `t0 bet use {ref}` lá)",))
    slices = sorted((c for c in kb.view().concepts.values()
                     if _fm(c).get("type") == "Slice" and c.doc.path.value.startswith(folder + "/slices/")),
                    key=lambda c: c.doc.path.value)
    bet_c = next((c for c in kb.view().concepts.values() if c.doc.path.value == folder + "/bet.md"), None)
    story = ref if JIRA_KEY_RE.fullmatch(ref) and not BET_ID_RE.match(ref) and _fm(concept).get("type") == "Slice" else None
    data = {
        "schema": 1, "product": product, "bet": bet_id,
        "jira": _fm(bet_c).get("jira") if bet_c else None, "kb_path": folder,
        "repos": sorted({str(_fm(c).get("repo")) for c in slices if _fm(c).get("repo")}),
        "stories": [k for k in (_fm(c).get("jira") for c in slices) if k],
        "active_story": story,
    }
    changed = write_if_changed(ws.root / BET_JSON, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    msg = f"bet ativa: {bet_id}" + (f", story {story}" if story else "") + ("" if changed else " (já estava)")
    return Plan(messages_pt=(msg,))


def _slug(name: str) -> str:
    return re.sub(r"^\d+-", "", name)


def slice_start(kb: Any, ws: Workspace, story: str) -> Plan | Refusal:
    """DoR from the slice concept; refuses dirty tree or absent repo; creates or switches to
    <KEY>-<slug> (DESIGN §2 Branches) from the default branch. Writes no KB record (PR_OPENED moves the state)."""
    if not JIRA_KEY_RE.fullmatch(story):
        return Refusal((f"chave Jira inválida: {story}",))
    c = kb.get(Ref(story))
    if c is None or _fm(c).get("type") != "Slice":
        return Refusal((f"nenhum slice com jira {story} no KB",))
    fm = _fm(c)
    missing = [] if fm.get("repo") else ["repo"]
    missing += [] if section(c.doc.body, ACCEPTANCE).bullets else ["a seção '## Critérios de aceite'"]
    if fm.get("state") not in ("ready", "building"):
        missing.append(f"state `ready` (está `{fm.get('state', 'proposed')}`; falta o gate)")
    if missing:
        return Refusal(tuple(f"DoR: falta {m}" for m in missing))
    repo = str(fm["repo"])
    repo_dir = ws.root / repo
    if repo in ws.absent or not (repo_dir / ".git").exists():
        return Refusal((f"repo `{repo}` ausente no workspace",))
    if _git(repo_dir, "status", "--porcelain").stdout.strip():
        return Refusal((f"árvore suja em `{repo}`: faça commit ou stash antes",))
    name = c.doc.path.value.rsplit("/", 1)[1].removesuffix(".md")
    branch = f"{story}-{_slug(name)}"
    if current_branch(repo_dir) == branch:
        return Plan(messages_pt=(f"já em {branch} ({repo})",))
    if _git(repo_dir, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0:
        p = _git(repo_dir, "switch", branch)
    else:
        base = next((b for b in (f"origin/{ws.default_branch}", ws.default_branch)
                     if _git(repo_dir, "rev-parse", "--verify", "--quiet", b).returncode == 0), "HEAD")
        p = _git(repo_dir, "switch", "--no-track", "-c", branch, base)
    if p.returncode != 0:
        return Refusal((f"git falhou em `{repo}`: {p.stderr.strip()}",))
    return Plan(messages_pt=(f"{repo}: branch {branch}",))
