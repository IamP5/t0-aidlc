"""`t0` command surface. argparse (stdlib). Every mutating command returns Plan | Refusal from KB; this
dispatcher alone prints the plan, honours --dry-run/--json, and calls KB.apply. Exit codes:
0 ok / no-op, 1 refusal or check failure, 2 usage, 3 KB unavailable (skills stop on 3).

Surface: 12 nouns. Methodology §10 / workspace §6 commands map onto them (left = their names).

  KB (records, knowledge, derived, conformance)
    t0 kb check [--level L0|L1|L2] [--changed-from REV] [--lane records|knowledge|auto]   kb-check, t0 kb check
    t0 kb find [--type T] [--text S] [--state S] [--product P] [--json]                  t0 kb find, kb-search
    t0 kb get <ref> [--json]
    t0 kb propose "<título>"          the ONE way to open/update a knowledge PR from the kb work tree
    t0 kb push [--if-due] | t0 kb status [--wait]                                          kb push/status
    t0 kb render [--commit]           kb-render workflow only
    t0 new <type> [--field k=v ...] [--from IDEA-NNNN] [--bugfix ...]  idea new, bet new, adr new, rotate (rotation),
                                                                        harness record (Harness Item occurrence)
    t0 log <kind> "<texto>" [--story KEY] [--bet BET] [--ref R]      t0 log, kb record, kb_record (MCP)
    t0 gate <G0..G8> <ref> [--to shipped|killed|extended] [--ci]     t0 gate
  Context + workspace
    t0 context [ref] [--format agents|delta|hook|subagent|json] [--write] [--kb DIR]
    t0 ws init <product> [--group G] | ws sync [--quick] | ws status
    t0 bet start <BET> [--isolate] [--repos a,b] | bet use <BET|KEY> | bet detect | bet close
    t0 slice start <KEY>
    t0 pr [--verify] | t0 pr check                                    (product repo CI)
  Mirrors + meetings + reports
    t0 jira sync [--apply] [--reconcile] [--bet BET]   local default = plan only (token lives in KB CI)
    t0 ritual <slug> open | close --decisions FILE [--transcript REDACTED_FILE]
    t0 transcript redact <raw> --ritual <slug> [--out FILE] [--scan-only]   raw must be under ~/.t0/inbox/
    t0 report digest|cycle|adoption|sweep|review-queue|budget|trace [--commit]   digest, metrics cycle,
                                                                                  adoption, sweep, review-queue, trace
  Toolkit plumbing
    t0 gen [--check] [--scope toolkit|repo|workspace|kb] [--upstream-diff SKILL]   adapters + drift check (t0 rules build)
    t0 setup [--kb] [--check]                                   pack-setup in a product repo / the KB repo
    t0 install --user | t0 doctor [--repo] [--jira]
    t0 mcp [--kb DIR] [--read-only]
    t0 hook <session-start|subagent-start|prompt-submit|pre-tool-edit|pre-tool-shell|pre-tool-read|stop|pre-push>
    t0 eval smoke --agent claude|copilot|kiro [--case NAME]     cross-agent smoke runner (design: evals.md)

Deliberately absent (one way per task): `t0 edit` (edit files + `kb propose`), `t0 kb record`
(= `t0 log`), `t0 rotate` (= the betting closer edits Rotation assignments; ad hoc swaps = edit + `kb propose`), `t0 rules build`
(= `t0 gen --scope repo`), `t0 metrics` / `t0 adoption` / `t0 sweep` / `t0 review-queue` / `t0 trace`
(= `t0 report <kind>`), `t0 harness record` (= `t0 new harness` occurrence record).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class Command:
    path: tuple[str, ...]                 # ('kb', 'check')
    run: Callable[..., object]            # (kb, args) -> Plan | Refusal | Report | str | Card | None
    mutates: bool                         # dispatcher applies Plans only for mutating commands
    ships: str                            # 'v0.1' | 'v0.2' | 'v0.3' (help text marks unshipped as 'em breve')


COMMANDS: tuple[Command, ...] = ()        # single table -> argparse tree, docs/cli.md (gen), skill lint
                                          # (a SKILL.md mentioning `t0 <x>` not in COMMANDS fails `t0 gen --check`)


def main(argv: Sequence[str] | None = None) -> int:
    raise NotImplementedError
