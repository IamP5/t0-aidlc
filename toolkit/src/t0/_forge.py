"""Forge adapter, private to write.py. Chosen by T0_FORGE (or `forge:` in ~/.t0/config.yaml):
  unset          no forge: knowledge writes stay a local branch + commit (eval sandbox, offline)
  file:<dir>     PRs as JSON in <dir>/prs.json (tests, evals, offline demos)
  github:<o/r>   GHE/GitHub REST via urllib; token from GITHUB_TOKEN or GH_TOKEN; API from T0_GITHUB_API

Invariants in signatures: open_pr() has no draft parameter (every knowledge PR is draft); there is no
ready() and no merge(); enable_auto_merge() accepts only RecordsPR, which only open_records_pr() returns.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .okf.document import Actor


@dataclass(frozen=True)
class Forge:
    kind: str          # file | github
    target: str        # dir | owner/repo


@dataclass(frozen=True)
class PR:
    repo: str
    number: int
    url: str
    node_id: str = ""


@dataclass(frozen=True)
class RecordsPR(PR):
    """Only for rec/* branches on the KB. Constructed only by open_records_pr."""


class ForgeError(Exception): ...


def configured() -> Forge | None:
    raw = os.environ.get("T0_FORGE")
    if raw is None:
        cfg = Path.home() / ".t0" / "config.yaml"
        if cfg.is_file():
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            raw = data.get("forge") if isinstance(data, dict) else None
    if not raw:
        return None
    kind, _, target = str(raw).partition(":")
    if kind not in ("file", "github") or not target:
        raise ForgeError(f"T0_FORGE inválido: {raw!r} (use file:<dir> ou github:<dono>/<repo>)")
    return Forge(kind, target)


# ------------------------------------------------------------------ file backend


def _file_open(f: Forge, head: str, base: str, title: str, body: str, reviewers: tuple[Actor, ...],
               draft: bool) -> dict[str, Any]:
    path = Path(f.target) / "prs.json"
    prs: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []
    hit = next((p for p in prs if p["head"] == head and p["state"] == "open"), None)
    if hit is None:
        hit = {"number": len(prs) + 1, "head": head, "base": base, "state": "open", "auto_merge": False}
        prs.append(hit)
    hit.update(title=title, body=body, draft=draft, reviewers=list(reviewers))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return hit


# ------------------------------------------------------------------ github backend


def _gh(f: Forge, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise ForgeError("sem GITHUB_TOKEN/GH_TOKEN para falar com o forge")
    api = os.environ.get("T0_GITHUB_API", "https://api.github.com").rstrip("/")
    req = urllib.request.Request(url if url.startswith("http") else api + url, method=method,
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            return {"_exists": True}
        raise ForgeError(f"forge respondeu {e.code} em {url}") from e


def _gh_open(f: Forge, head: str, base: str, title: str, body: str, draft: bool) -> dict[str, Any]:
    r = _gh(f, "POST", f"/repos/{f.target}/pulls", {"title": title, "head": head, "base": base, "body": body, "draft": draft})
    if r.get("_exists"):
        owner = f.target.split("/")[0]
        found = _gh(f, "GET", f"/repos/{f.target}/pulls?state=open&head={owner}:{head}")
        if not found:
            raise ForgeError(f"PR de {head} não abriu e não existe")
        r = found[0]
    return r


# ------------------------------------------------------------------ the three operations


def open_pr(f: Forge, *, head: str, base: str, title: str, body: str, reviewers: tuple[Actor, ...]) -> PR:
    """Always draft. Reuses the open PR with the same head (idempotent)."""
    if f.kind == "file":
        p = _file_open(f, head, base, title, body, reviewers, True)
        return PR(f.target, p["number"], f"file://{Path(f.target) / 'prs.json'}#{p['number']}")
    r = _gh_open(f, head, base, title, body, True)
    handles = [a.split(":", 1)[1] for a in reviewers if a.startswith("human:")]
    if handles:
        _gh(f, "POST", f"/repos/{f.target}/pulls/{r['number']}/requested_reviewers", {"reviewers": handles})
    return PR(f.target, r["number"], r["html_url"], r.get("node_id", ""))


def open_records_pr(f: Forge, *, head: str, base: str, title: str, body: str) -> RecordsPR:
    if not head.startswith("rec/"):
        raise ForgeError("PR de registros só sai de branch rec/*")
    if f.kind == "file":
        p = _file_open(f, head, base, title, body, (), False)
        return RecordsPR(f.target, p["number"], f"file://{Path(f.target) / 'prs.json'}#{p['number']}")
    r = _gh_open(f, head, base, title, body, False)
    return RecordsPR(f.target, r["number"], r["html_url"], r.get("node_id", ""))


def enable_auto_merge(f: Forge, pr: RecordsPR) -> None:
    if not isinstance(pr, RecordsPR):
        raise ForgeError("auto-merge só para PR de registros")
    if f.kind == "file":
        path = Path(f.target) / "prs.json"
        prs = json.loads(path.read_text(encoding="utf-8"))
        for p in prs:
            if p["number"] == pr.number:
                p["auto_merge"] = True
        path.write_text(json.dumps(prs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    q = ("mutation($id:ID!){enablePullRequestAutoMerge(input:{pullRequestId:$id,mergeMethod:SQUASH})"
         "{clientMutationId}}")
    _gh(f, "POST", "/graphql", {"query": q, "variables": {"id": pr.node_id}})
