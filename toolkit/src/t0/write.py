"""Plans and the single side-effect point.

Lanes are encoded in types:
  AddRecord        - only a NEW, uniquely named file of a RECORDS-lane type. Constructor is private:
                     build via `new_record(...)`, which assigns '<utc-ts>-<handle>-<repo|kb>-<rand4>.md'
                     (or seq id for Ideas, retried on collision) and runs the secret/PII scan.
  KnowledgeChange  - files on a branch of the kb clone -> one DRAFT PR. May add or modify authored keys/body.
                     Never touches derived keys (stripped + verified before commit).
  DerivedChange    - only render.materialize can build it (module-private token). Applied only when
                     T0_ROLE=kb-render AND running as the KB-writer App (checked by apply()).

Idempotency:
  - Records carry `dedup`; apply() skips records whose dedup already exists on main or in the spool.
  - Knowledge puts whose bytes equal main are dropped; an empty KnowledgeChange is not opened.
  - Gate files: path is the key; an existing file -> AlreadyDone, an open PR with that path -> Pending.
  - Crash between spool write and push: spool is the source; `t0 kb push` is safe to re-run (re-bases the
    single commit, 3 attempts); a records PR already open for the spool batch is reused (branch name from
    batch hash).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping

from .okf.document import Actor, BundlePath
from .profile.spec import EventKind


@dataclass(frozen=True)
class RenderedDoc:
    path: BundlePath
    text: str                      # output of okf.document.dump; already validated L0+L1 by the planner


class _RecordToken: ...            # module-private; prevents AddRecord(...) outside this module
class _DerivedToken: ...           # handed only to render.py via a friend import


@dataclass(frozen=True)
class AddRecord:
    doc: RenderedDoc
    dedup: str
    _token: _RecordToken = field(repr=False, compare=False, default=None)  # type: ignore[assignment]


@dataclass(frozen=True)
class KnowledgeChange:
    branch: str                    # 'bet/BET-042/ana' | 'kb/ana/<topic>' | 'gate/G2/BET-042'
    title_pt: str                  # PR title
    body_pt: str                   # PR body: what, why, checks evidence, link to card
    puts: tuple[RenderedDoc, ...]
    reviewers: tuple[Actor, ...]   # requested reviewers (CODEOWNERS still decides approval)


@dataclass(frozen=True)
class DerivedChange:
    puts: tuple[RenderedDoc, ...]
    _token: _DerivedToken = field(repr=False, compare=False, default=None)  # type: ignore[assignment]


@dataclass(frozen=True)
class Plan:
    """Pure output of every mutating command. Empty plan == already done (idempotent)."""
    records: tuple[AddRecord, ...] = ()
    knowledge: KnowledgeChange | None = None
    derived: DerivedChange | None = None
    messages_pt: tuple[str, ...] = ()

    @property
    def empty(self) -> bool:
        return not self.records and self.knowledge is None and self.derived is None


@dataclass(frozen=True)
class Refusal:
    """A command that refused to plan (failed gate checks, DoR missing, no active bet...)."""
    reasons_pt: tuple[str, ...]


def new_record(kind: EventKind, *, type_name: str, fields: Mapping[str, object], body: str,
               actor: Actor, handle: str, where: Mapping[str, str], dedup: str | None = None) -> AddRecord:
    """The only constructor of AddRecord. Validates type is a RECORDS-lane type; names the file uniquely;
    runs redact.scan on body+fields and raises SecretFound (never writes a record with a secret)."""
    raise NotImplementedError


# Named scaffolds referenced by TypeSpec.on_create (table stays pure data).
SCAFFOLDS: Mapping[str, Callable[..., Plan]] = {}
#   'bugfix_single_slice': Bet + Bugfix + slices/01-fix.md (state proposed, repo from --repo) in one KnowledgeChange


@dataclass(frozen=True)
class Applied:
    spooled: tuple[Path, ...]
    pr_url: str | None
    commit: str | None
    skipped: tuple[str, ...]        # dedup hits / no-op puts


class ApplyMode(Enum):
    LOCAL = "local"                 # dev: records -> spool; knowledge -> branch + draft PR via forge
    CI_RECORDS = "ci-records"       # CI with KB-writer App: records -> rec/bot/... PR (auto-merge)
    KB_RENDER = "kb-render"         # only mode that accepts DerivedChange; commits to main as the App


def apply(plan: Plan, *, mode: ApplyMode, kb_dir: Path, spool_dir: Path) -> Applied:
    """The one side-effect point. Refuses DerivedChange outside KB_RENDER; refuses knowledge in CI_RECORDS."""
    raise NotImplementedError


def push_spool(*, kb_dir: Path, spool_dir: Path, if_due: bool = False) -> Applied:
    """`t0 kb push`: one commit per session built with a temporary index on origin/main (plumbing; never
    touches the work tree), push to rec/<handle>/<utc-ts>, open a records PR via _forge.open_records_pr and
    enable auto-merge. Records PRs are the ONLY non-draft, auto-merged PRs in the system (add-only, checked by
    LANE.records-add-only + SCAN). Fallback mode (bank policy forbids 0-approval auto-merge): push the branch
    only; the KB `kb-batch` workflow folds rec/* branches into one hourly PR for the Flow Steward.
    `if_due`: push only when spool age > 10 min or session ends (Stop hooks)."""
    raise NotImplementedError
