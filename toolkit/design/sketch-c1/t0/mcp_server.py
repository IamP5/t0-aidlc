"""stdio MCP server `t0-kb` (official `mcp` Python SDK, FastMCP). Local process, no port, no service.

Six tools. Inputs are parsed into domain types here; outputs are plain text/markdown or small JSON
objects defined below (no View/Concept objects cross the wire). Every tool is a one-liner over KB.

Write surface is exactly one tool, kb_record (records lane -> spool). Knowledge-lane writes and gates
go through skills + CLI so they always land as a reviewed PR.

Instructions (asserted <= 1500 chars by test; pt-BR because they shape agent output):
  "KB = t0-kb (OKF). Sem card t0 no contexto, chame kb_context primeiro. Nunca edite index.md, log.md,
   changeset.md nem chaves derivadas (state, status, verified, jira, pr). Para registrar passo ou
   decisão use kb_record. Mudança de estado é gate: rode a skill `gate`. ..."
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocOut:
    path: str
    uid: str
    type: str
    state: str | None
    trust: str                # unverified | machine-confirmed | human-reviewed
    stale: bool
    frontmatter_yaml: str     # derived keys included, marked with '# derivado'
    body: str


@dataclass(frozen=True)
class BetOut:
    bet: DocOut
    gates: list[dict]         # [{gate, state: done|pending|refused|n/a, checks: [...]}] from KB.decide
    slices: list[dict]        # [{uid, title, repo, state, jira, pr, depends_on}]
    links: dict[str, str]     # spec, plan, assessment, bugfix, changeset, log


# Tools (signatures as exposed to agents)
def kb_context(ref: str | None = None) -> str:
    """Card (AGENTS format, <=8000 chars) for a bet/Jira key/slice, or the active bet."""
    raise NotImplementedError


def kb_search(query: str, type: str | None = None, product: str | None = None,
              state: str | None = None, limit: int = 10) -> list[dict]:
    """Frontmatter-aware search (type enum derived from REGISTRY in the JSON schema)."""
    raise NotImplementedError


def kb_get(ref: str) -> DocOut:
    """uid | path | Jira key | KB id. Transcripts return only redacted text (they are stored redacted)."""
    raise NotImplementedError


def bet_get(ref: str) -> BetOut:
    raise NotImplementedError


def changeset_get(bet: str) -> dict:
    raise NotImplementedError


def kb_record(kind: str, text: str, bet: str | None = None, story: str | None = None,
              refs: list[str] | None = None) -> dict:
    """kind in {progress, decision, blocker, handoff, session}. Returns {spooled: path, push: 'pending'}.
    Secret/PII in text -> error with the finding kinds (nothing written)."""
    raise NotImplementedError


def serve(kb_dir: Path | None, *, read_only: bool = False) -> None:
    """`t0 mcp [--kb DIR] [--read-only]`. --read-only (cloud agent, CI) drops kb_record from the tool list."""
    raise NotImplementedError
