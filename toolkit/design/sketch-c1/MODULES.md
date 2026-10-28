# Module map (`src/t0/`)

Every module's internals are `_private`. `t0/__init__.py` exports only `KB`, `Plan`, `Source`, `CardFormat`, `Ref`, `GateId`, and the `Refusal`/`Report` result types. An import-linter contract in CI (`importlinter` config in pyproject) fails the build when a module outside the package, or a shell module (`cli`, `mcp_server`, `hooks`), imports anything but `t0.kb` and `t0.profile`.

| Module | Owns (knowledge, not stage) | Public surface | Pure? |
|---|---|---|---|
| `okf/document.py` | Reference parse semantics, `BundlePath`, `Actor`, `Instant` grammar | `parse`, `BundlePath`, `Actor`, `Instant` | yes |
| `profile/spec.py` | Shapes of the one table: `Field`, `TypeSpec`, `StateMachine`, `GateSpec`, `BetTypeSpec`, `Lane`, `CheckId`, `EventKind` | types only | yes |
| `profile/table.py` | The single table: `TYPES`, `GATES`, `BET_TYPES`, `PROFILE_VERSION`, `REGISTRY` | `REGISTRY` | yes (data) |
| `view.py` | Events, fold, derived keys, anomalies, `Concept` accessor | `View`, `Concept`, `fold`, `Event` | yes |
| `check.py` | Conformance L0/L1/L2 + lane rules + secret scan | `check(view, docs, level, lane, changed) -> Report` | yes |
| `gates.py` | Gate check implementations (one per `CheckId`) + approver rules | `evaluate(view, gate, target) -> GateDecision` | yes |
| `context.py` | Card/delta/subagent rendering with hard budgets | `render(view, ws, bet, fmt) -> Card \| None` | yes |
| `redact.py` | Deterministic scanner, `Redacted` type | `redact`, `scan`, `Redacted`, `RULESET_VERSION` | yes |
| `render.py` | Derived files (index.md, log.md, changeset.md) + materialized derived keys | `materialize(view) -> DerivedChange` | yes |
| `tracker/` | Jira port, REST flavors, file fake, sync planner | `Tracker`, `open_tracker`, `plan_sync`, `execute` | planner pure, adapters shell |
| `write.py` | `Plan`, ops, unique record names, spool, plumbing push, knowledge branch+PR | `Plan`, `apply` | shell (thin) |
| `_forge.py` | GitHub (GHE) via REST: draft PR, auto-merge for records PR only, reviews | private to `write` | shell |
| `ws.py` | Workspace manifest, bet detection chain, slice branches, `pr` trailers | `Workspace`, `detect_bet`, `slice_start`, `pr_open`, `pr_check` | mostly shell |
| `rituals.py` | Ritual open (agenda from concept inputs) and closers table | `open_agenda`, `close`, `CLOSERS` | yes (plans) |
| `reports.py` | digest, cycle, adoption, sweep, review-queue, budget, trace | `report(view, kind, sources) -> Plan \| str` | yes |
| `gen.py` | All generated per-tool files, profile.md, templates, eval mocks, skill header/footer | `TARGETS`, `generate`, `check_drift` | yes (renders to memory) |
| `kb.py` | Facade: opens a view source, routes every operation | `KB` | orchestrates |
| `hooks.py` | One entrypoint for every agent hook and git hook; git guard | `run_hook(name, stdin) -> HookReply` | thin |
| `mcp_server.py` | stdio server `t0-kb`, 6 tools, instructions ≤1500 chars | `serve(kb_dir)` | thin |
| `cli.py` | argparse command table; applies Plans; `--dry-run`, `--json` | `main` | thin |

## Trace: `t0 gate G2 BET-042` (3 files)

`cli.cmd_gate` → `KB.gate` (kb.py: `view = fold(...)`; `gates.evaluate(view, GATES['G2'], target)`) → on success returns `Plan(knowledge=KnowledgeChange(add gates/G2.md))` → `cli` calls `write.apply(plan)` → `_forge.open_pr` (always draft) with reviewers from `GateDecision.approvers`.

## Trace: merge of that PR → state

KB `push` to `main` → `t0 kb render --commit` → `KB.render()` → `fold` sees `gates/G2.md` on main + `gate-approved` record (approvers) → `render.materialize` sets `spec.md` derived `state: approved`, `status: stable`, `verified: [...]`, appends log line → one commit by the KB-writer App → `t0 jira sync --apply`.

## Trace: Copilot cloud agent asks for context

`kb_context("PAY-132")` (mcp_server) → `KB.open(kb_dir=.kb, source=MAIN)` → `KB.context(Ref("PAY-132"), AGENTS)` → `view.resolve` by derived `jira` key → `context.render` → `Card` (≤8000).
