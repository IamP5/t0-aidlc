"""Plans and the single side-effect point.

Lanes are encoded in types:
  AddRecord        a NEW, uniquely named Step. Built only by `new_record`, which runs the secret/PII scan.
  KnowledgeChange  files on a KB branch -> one commit -> one DRAFT PR (or only the local branch with no forge).
                   Each knowledge branch lives in its own git worktree (`checkout`); t0 never moves the main
                   clone's HEAD, so sessions sharing one KB clone never write on each other's branch.
  DerivedChange    only render.materialize builds it; applied only on the KB's main branch.

Idempotency:
  - records carry `dedup`; apply skips a record whose dedup already exists in the view (main + spool);
  - knowledge puts whose bytes equal the work tree are dropped; an empty change makes no commit;
  - push adds to the day's `rec/<handle>/<date>` branch only the records it does not have yet.
"""
from __future__ import annotations

import fcntl
import hashlib
import os
import re
import secrets
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Mapping

from . import _forge
from .okf.document import Actor, dump
from .profile.spec import EventKind
from .redact import scan

MAIN = "main"


@dataclass(frozen=True)
class RenderedDoc:
    path: str                      # bundle-absolute
    text: str


class _RecordToken: ...
class _DerivedToken: ...


_RT, _DT = _RecordToken(), _DerivedToken()


@dataclass(frozen=True)
class AddRecord:
    doc: RenderedDoc
    dedup: str
    _token: object = field(repr=False, compare=False, default=None)

    def __post_init__(self) -> None:
        if self._token is not _RT:
            raise TypeError("AddRecord só sai de write.new_record")


@dataclass(frozen=True)
class KnowledgeChange:
    branch: str                    # 'bet/BET-042/ana' | 'kb/ana/<topic>'
    title_pt: str
    body_pt: str
    puts: tuple[RenderedDoc, ...]
    reviewers: tuple[Actor, ...] = ()
    commit_all: bool = False       # `t0 kb propose`: commit every change in the KB work tree
    include: tuple[str, ...] = ()  # extra work-tree paths committed with the puts (a bet folder's hand edits)


@dataclass(frozen=True)
class DerivedChange:
    puts: tuple[RenderedDoc, ...]
    _token: object = field(repr=False, compare=False, default=None)

    def __post_init__(self) -> None:
        if self._token is not _DT:
            raise TypeError("DerivedChange só sai de render.materialize")


def derived_change(puts: tuple[RenderedDoc, ...]) -> DerivedChange:
    """The friend constructor render.py uses."""
    return DerivedChange(puts, _DT)


@dataclass(frozen=True)
class Plan:
    """Pure output of every mutating command. An empty plan means already done."""
    records: tuple[AddRecord, ...] = ()
    knowledge: KnowledgeChange | None = None
    derived: DerivedChange | None = None
    messages_pt: tuple[str, ...] = ()

    @property
    def empty(self) -> bool:
        return not self.records and self.knowledge is None and self.derived is None


@dataclass(frozen=True)
class Refusal:
    reasons_pt: tuple[str, ...]


class SecretFound(Exception):
    def __init__(self, kinds: list[str]) -> None:
        super().__init__(f"texto contém {', '.join(kinds)}; remova e tente de novo")
        self.kinds = kinds


@dataclass(frozen=True)
class Applied:
    spooled: tuple[Path, ...] = ()
    pr_url: str | None = None
    commit: str | None = None
    skipped: tuple[str, ...] = ()
    branch: str | None = None
    tree: Path | None = None       # the knowledge branch's worktree


class ApplyMode(Enum):
    LOCAL = "local"
    KB_RENDER = "kb-render"


class ApplyError(Exception): ...


# ------------------------------------------------------------------ records


def now_instant() -> str:
    raw = os.environ.get("T0_NOW")
    return raw or datetime.now().astimezone().replace(microsecond=0).isoformat()


def _first_line(text: str, n: int) -> str:
    line = next((l.strip() for l in text.splitlines() if l.strip()), "")
    return line if len(line) <= n else line[: n - 1] + "…"


def new_record(kind: EventKind, *, type_name: str, fields: Mapping[str, object], body: str,
               actor: Actor, handle: str, where: Mapping[str, str], dedup: str | None = None) -> AddRecord:
    """The only constructor of AddRecord. Names the file uniquely and refuses secrets and personal data."""
    if type_name != "Step":
        raise ValueError("a raia de registros só aceita Step")
    found = scan(body + "\n" + "\n".join(str(v) for v in fields.values()))
    if found:
        raise SecretFound(sorted({f.kind.value for f in found}))
    at = now_instant()
    ts = datetime.fromisoformat(at).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rand = secrets.token_hex(2)
    repo = where.get("repo")
    name = "-".join(x for x in (ts, handle, repo, rand) if x)
    folder = where.get("bet_folder") or ""
    path = f"{folder}/steps/{name}.md"
    title = _first_line(body, 72) or kind.value
    fm: dict[str, object] = {
        "type": "Step", "title": title, "description": _first_line(body, 200) or kind.value,
        "uid": f"step-{name}", "owner": actor, "generated": {"by": actor, "at": at}, "kind": kind.value}
    fm.update({k: v for k, v in fields.items() if v not in (None, "", [], {}) and k != "kind"})
    key = dedup or path
    if dedup:
        fm["dedup"] = dedup
    return AddRecord(RenderedDoc(path, dump(fm, body.rstrip("\n") + "\n")), key, _RT)


# ------------------------------------------------------------------ git


def git(kb: Path, *args: str, env: Mapping[str, str] | None = None, check: bool = True) -> str:
    base = ["git", "-C", str(kb), "-c", "user.name=" + (_git_cfg(kb, "user.name") or "t0"),
            "-c", "user.email=" + (_git_cfg(kb, "user.email") or "t0@localhost")]
    p = subprocess.run([*base, *args], capture_output=True, text=True, env={**os.environ, **(env or {})}, timeout=60)
    if check and p.returncode != 0:
        raise ApplyError(f"git {' '.join(args)}: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def _git_cfg(kb: Path, key: str) -> str:
    p = subprocess.run(["git", "-C", str(kb), "config", key], capture_output=True, text=True)
    return p.stdout.strip()


def is_git(kb: Path) -> bool:
    return (kb / ".git").exists()


def current_branch(kb: Path) -> str | None:
    if not is_git(kb):
        return None
    out = git(kb, "symbolic-ref", "--short", "-q", "HEAD", check=False)
    return out or None


def ref_exists(kb: Path, ref: str) -> bool:
    return subprocess.run(["git", "-C", str(kb), "rev-parse", "--verify", "--quiet", ref],
                          capture_output=True).returncode == 0


def dirty(kb: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(kb), "status", "--porcelain", "-z", "--untracked-files=all"],
                         capture_output=True, text=True).stdout
    return [e[3:] for e in out.split("\0") if len(e) > 3 and e[2] == " "]


def base_ref(kb: Path) -> str:
    return next((r for r in (MAIN, f"origin/{MAIN}") if ref_exists(kb, r)), "HEAD")


@dataclass(frozen=True)
class Checkout:
    """A knowledge branch and the git worktree that holds it."""
    branch: str
    path: Path


def worktree_root(kb: Path) -> Path:
    """`<kb>.wt`, beside the main clone: one worktree per knowledge branch, at `<kb>.wt/<branch>`."""
    kb = kb.resolve()
    return kb.with_name(kb.name + ".wt")


def _worktrees(kb: Path) -> list[tuple[Path, str | None]]:
    rows = []
    for block in git(kb, "worktree", "list", "--porcelain").split("\n\n"):
        f = dict(l.split(" ", 1) for l in block.splitlines() if " " in l)
        if "worktree" in f:
            rows.append((Path(f["worktree"]).resolve(), f.get("branch", "").removeprefix("refs/heads/") or None))
    return rows


def main_clone(kb: Path) -> Path:
    """The main work tree of the KB repo; a linked worktree has a `.git` file instead of a folder."""
    return _worktrees(kb)[0][0] if (kb / ".git").is_file() else kb


def checkouts(kb: Path) -> tuple[Checkout, ...]:
    return tuple(Checkout(b, p) for p, b in _worktrees(kb)[1:] if b and b.startswith(("bet/", "kb/")))


def open_checkouts(kb: Path) -> tuple[Checkout, ...]:
    """Knowledge worktrees with work main does not have yet: uncommitted edits or commits not merged."""
    base = base_ref(kb)
    return tuple(co for co in checkouts(kb) if dirty(co.path) or subprocess.run(
        ["git", "-C", str(kb), "merge-base", "--is-ancestor", co.branch, base]).returncode != 0)


def checkout(kb: Path, branch: str) -> Checkout:
    """The worktree of `branch`, from the main clone `kb`. Reused when it exists; a new branch starts from main;
    a branch already merged into main restarts from main, carrying uncommitted edits git can carry."""
    base = base_ref(kb)
    if not ref_exists(kb, base):
        raise ApplyError("KB sem commit no main; faça o primeiro commit")
    git(kb, "worktree", "prune")
    path = next((p for p, b in _worktrees(kb) if b == branch), None)
    if path == kb.resolve():
        raise ApplyError(f"o clone principal do KB está em {branch}; volte com `git -C {kb} switch main`")
    exists = ref_exists(kb, f"refs/heads/{branch}")
    stale = exists and git(kb, "rev-parse", branch) != git(kb, "rev-parse", base) and subprocess.run(
        ["git", "-C", str(kb), "merge-base", "--is-ancestor", branch, base]).returncode == 0
    if path is None:
        path = worktree_root(kb) / branch
        if path.exists():
            raise ApplyError(f"{path} existe e não é worktree do KB; apague a pasta e rode de novo")
        if exists and not stale:
            git(kb, "worktree", "add", "-q", str(path), branch)
        else:
            git(kb, "worktree", "add", "-q", "--no-track", "-B", branch, str(path), base)
    elif stale:
        try:
            git(path, "switch", "-q", "--no-track", "-C", branch, base)
        except ApplyError:
            raise ApplyError(f"{branch} já entrou no main e o worktree {path} tem mudanças que conflitam com o main; "
                             "faça commit ou descarte") from None
    return Checkout(branch, path)


# ------------------------------------------------------------------ spool


def spool_dir(kb: Path) -> Path:
    key = hashlib.sha1(str(kb.resolve()).encode()).hexdigest()[:12]
    return Path.home() / ".t0" / "spool" / key


def _write(path: Path, text: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".t0tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


# ------------------------------------------------------------------ apply


def apply(plan: Plan, *, mode: ApplyMode, kb_dir: Path, known_dedup: frozenset[str] = frozenset()) -> Applied:
    """The one side-effect point."""
    if plan.derived is not None and mode is not ApplyMode.KB_RENDER:
        raise ApplyError("mudança derivada só pelo kb-render")
    spooled: list[Path] = []
    skipped: list[str] = []
    sp = spool_dir(kb_dir)
    for r in plan.records:
        if r.dedup in known_dedup:
            skipped.append(r.dedup)
            continue
        p = sp / r.doc.path.lstrip("/")
        _write(p, r.doc.text)
        spooled.append(p)
    commit = pr_url = branch = tree = None
    if plan.knowledge is not None:
        commit, pr_url, branch, tree = _apply_knowledge(plan.knowledge, kb_dir)
    if plan.derived is not None:
        commit, branch = _apply_derived(plan.derived, kb_dir), MAIN
    return Applied(tuple(spooled), pr_url, commit, tuple(skipped), branch, tree)


def _commit(kb: Path, paths: list[str] | None, msg: str) -> str | None:
    git(kb, "add", "-A", *(["--", *paths] if paths else []))
    if subprocess.run(["git", "-C", str(kb), "diff", "--cached", "--quiet"]).returncode == 0:
        return None
    git(kb, "commit", "-q", "-m", msg)
    return git(kb, "rev-parse", "--short", "HEAD")


def _apply_knowledge(k: KnowledgeChange, kb: Path) -> tuple[str | None, str | None, str | None, Path | None]:
    if not is_git(kb):
        for d in k.puts:
            _write(kb / d.path.lstrip("/"), d.text)
        return None, None, None, None
    tree = checkout(kb, k.branch).path
    for d in k.puts:
        _write(tree / d.path.lstrip("/"), d.text)
    paths = None if k.commit_all else [d.path.lstrip("/") for d in k.puts] + [p.lstrip("/") for p in k.include]
    commit = _commit(tree, paths, k.title_pt + ("\n\n" + k.body_pt if k.body_pt else ""))
    forge = _forge.configured()
    if forge is None:
        return commit, None, k.branch, tree
    if forge.kind == "github":
        git(tree, "push", "origin", f"{k.branch}:{k.branch}")
    pr = _forge.open_pr(forge, head=k.branch, base=MAIN, title=k.title_pt, body=k.body_pt, reviewers=k.reviewers)
    return commit, pr.url, k.branch, tree


def _apply_derived(d: DerivedChange, kb: Path) -> str | None:
    if is_git(kb) and current_branch(kb) not in (MAIN, None):
        raise ApplyError(f"kb-render escreve só no {MAIN}; o KB está em {current_branch(kb)}")
    for doc in d.puts:
        _write(kb / doc.path.lstrip("/"), doc.text)
    if not is_git(kb):
        return None
    return _commit(kb, [doc.path.lstrip("/") for doc in d.puts], "kb-render: derivados")


def push_spool(*, kb_dir: Path, handle: str, mode: str, landed: frozenset[str]) -> tuple[Applied, list[str]]:
    """`t0 kb push`: commit the spooled records onto `rec/<handle>/<date>` from main with a temporary
    index (plumbing; the work tree is untouched), then open the records PR when a forge exists
    (auto-merge only in mode `auto`). Spool files already on main are removed first. One push at a time per
    spool: a second session's push skips while the first holds the lock."""
    sp = spool_dir(kb_dir)
    if not sp.is_dir():
        return Applied(), ["nada no spool para empurrar"]
    with open(sp / ".push.lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return Applied(), ["push em andamento em outra sessão"]
        return _push(sp, kb_dir=kb_dir, handle=handle, mode=mode, landed=landed)


def _push(sp: Path, *, kb_dir: Path, handle: str, mode: str, landed: frozenset[str]) -> tuple[Applied, list[str]]:
    files = sorted(sp.rglob("*.md"))
    msgs: list[str] = []
    pending: list[tuple[str, Path]] = []
    for p in files:
        rel = "/" + str(p.relative_to(sp))
        if rel in landed:
            p.unlink()
        else:
            pending.append((rel, p))
    if not pending:
        return Applied(), ["nada no spool para empurrar"]
    if not is_git(kb_dir):
        for rel, p in pending:
            _write(kb_dir / rel.lstrip("/"), p.read_text(encoding="utf-8"))
            p.unlink()
        return Applied(skipped=tuple(rel for rel, _ in pending)), [f"{len(pending)} registro(s) gravados no KB (sem git)"]
    branch = f"rec/{handle}/{now_instant()[:10]}"
    parent = f"refs/heads/{branch}" if ref_exists(kb_dir, f"refs/heads/{branch}") else base_ref(kb_dir)
    with tempfile.TemporaryDirectory() as td:
        env = {"GIT_INDEX_FILE": str(Path(td) / "index")}
        git(kb_dir, "read-tree", parent, env=env)
        have = set(git(kb_dir, "ls-files", env=env).splitlines())
        added = 0
        for rel, p in pending:
            if rel.lstrip("/") in have:
                continue
            blob = git(kb_dir, "hash-object", "-w", str(p))
            git(kb_dir, "update-index", "--add", "--cacheinfo", f"100644,{blob},{rel.lstrip('/')}", env=env)
            added += 1
        commit = None
        if added:
            tree = git(kb_dir, "write-tree", env=env)
            commit = git(kb_dir, "commit-tree", tree, "-p", parent, "-m", f"registros: {added} de {handle}")
            git(kb_dir, "update-ref", f"refs/heads/{branch}", commit)
    msgs.append(f"{added} registro(s) novos em {branch}" if added else f"{branch} já tinha os registros")
    forge = _forge.configured()
    pr_url = None
    if forge is not None:
        if forge.kind == "github":
            git(kb_dir, "push", "origin", f"{branch}:{branch}")
        pr = _forge.open_records_pr(forge, head=branch, base=MAIN, title=f"Registros de {handle}",
                                    body=f"{len(pending)} registro(s) da raia de registros. Só adições.")
        pr_url = pr.url
        if mode == "auto":
            _forge.enable_auto_merge(forge, pr)
            msgs.append("auto-merge ligado (Policy records-lane: auto)")
        else:
            msgs.append("lote para o Flow Steward aprovar (Policy records-lane: batch)")
    else:
        msgs.append(f"sem forge: o lote fica no branch local {branch}; o merge no main é a aprovação")
    return Applied(commit=commit[:7] if commit else None, pr_url=pr_url, branch=branch), msgs


def slug(text: str, n: int = 40) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-") or "x"
