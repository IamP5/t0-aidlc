# t0 toolkit: synthesized design (architect arena)

This is the contract every build stream implements. Where it differs from the sketch, this file wins.

## Synthesis decision

- **Base: candidate 1 ("event-folded KB")**, sketch in `design/sketch-c1/`. Cross-judge (Fable) scored C1 23 and C2 19. C1 has the smaller public surface (`KB` facade, `Plan | Refusal`, one `apply`), invariants in signatures (`RecordsPR`, always-draft forge, `Redacted`), the registry as one code table with self-tests, and a single hook entrypoint.
- **Narrowed central bet.** C1 derived every `state`/`verified` from events, which contradicts methodology §2.2 and workspace §4, needs an App to read PR reviews, and adds a 1–2 min lag. Synthesis: each key has exactly one owner, per type.
  - Knowledge-lane types (Idea after `new`, Bet, Spec, Plan, Contract, ADR, Policy, Assessment, Bugfix, Rotation, Cycle Record): `state` and `verified` change **only** in the gate PR (`t0 gate`), which also adds the evidence file `gates/<G>.md`. Approval of that PR is the gate approval. `t0 kb check` re-runs the gate checks at PR head (`L1.gate-checks-hold`).
  - Derived keys owned by `kb-render` only: Slice `state` after `ready` (`building`, `in-review`, `done`, `blocked`), `pr`, `audit`, `jira` (write-once from `jira-linked` records), `markers_open`, `status` (from `state` via the table's `status_map`), plus `index.md`, `log.md`, `changeset.md`.
  - `view.fold` stays as the read-side index and anomaly detector (illegal transitions, materialized drift), not the owner of state.
- **Ideas are created through the knowledge lane** (a small PR, auto-reviewable by the Flow Steward), not the records lane, so sequential ids never collide. `t0 new idea` reserves `IDEA-NNNN` by scanning `main` plus open branches; collisions fail L1 `uid-unique` at PR time.
- **Profile registry stays in code** (`t0/profile/table.py`), and `profile.md` is generated into the KB and drift-checked (`t0 gen --check --scope kb`). Judge's reasons: check predicates are code anyway; a KB PR must never break every dev's CLI without a failing test. What the team edits without a release lives in KB concepts read at runtime: `Policy` (thresholds, floors, retention) and `Template` (pt-BR body skeletons, graft from C2).

## Grafts from candidate 2

1. Generic `ritual` engine and skill in v0.1 (`design/c2/gate_ritual.py`): `t0 ritual <slug> open|close`, agenda from the Ritual concept's `inputs`, close writes Ritual Record (+ redacted Transcript), preceptoria refuses a transcript.
2. The KB template **is** the positive test fixture (`toolkit/tests/fixtures/kb-positive` points at `okf-template/`), with `products/exemplo/` exercising every type and lane.
3. Template bodies as KB `Template` concepts (`methodology/templates/<type>.md`); `t0 new <type>` instantiates them.
4. `Report.format(text|github|json)`; `t0 kb check --format github`; `t0 slice dor <KEY>`; `t0 doctor` (subset).
5. Eval cases: `slice-build-draft-only`, `kb-record-secret-refused`, `ritual-preceptoria-no-transcript`, `hook-blocks-derived-edit`, `portable-skill-trigger`.

## Fixes from the judge (both)

- Plugin eval format (see `research/plugin-eval-format.md`): evals live in `plugin/evals/` (default dir); scaffolds only via `case.yaml` `context.scaffold_script` (run with `--scaffold`); no `tool_order` with one tool; mocks only for servers the plugin declares; `file_exists` only for files Claude creates; no `baseline` grader without `baseline_file`; `tool_used` cannot assert denial (use `regex` on `trace`/`last_message`).
- Skills live flat at `plugin/skills/<name>/SKILL.md` (Copilot/Kiro scan one level). Descriptions ≤300 chars.
- Draft-only in the type: the forge adapter's `open_pr` has no `draft` parameter; auto-merge accepted only for `RecordsPR`.
- Transcript L1 checks `redaction.ruleset` is a known ruleset (any released version), not equality with the current one.
- Raw transcripts live only in `~/.t0/inbox/`; the PreToolUse read guard blocks agents from reading there.
- Bundle reads from git use `git cat-file --batch`, not per-file `git show`.

## Repository layout (this repo)

```
toolkit/                 python package `t0` (pyproject, src/t0, tests)
  design/                arena outputs and this file
okf-template/            the OKF bundle template (t0-kb starter), shipped as package data
plugin/                  portable plugin: .claude-plugin/plugin.json + plugin.json (Agent Plugins), skills/, hooks/, .mcp.json, evals/
methodology/             methodology docs (also copied into okf-template/methodology/)
research/                research reports
```

## v0.1 command surface (frozen)

```
t0 kb check [--level L0|L1|L2] [--format text|github|json] [--changed-from REF]
t0 kb find [--type T] [--text S] [--json]      t0 kb get <ref> [--json]
t0 kb render [--check|--write]                  t0 kb propose -m MSG [--dry-run]
t0 kb push [--dry-run]                          t0 kb init <dir>   (copies okf-template)
t0 new idea|bet|spec|plan|slice|adr|assessment|bugfix|harness [args] [--dry-run]
t0 log progress|decision|blocker "<texto>" [--bet B] [--story K]
t0 gate G0..G8 <ref> [--dry-run] [--ci]
t0 ritual <slug> open|close [--decisions FILE] [--transcript FILE]
t0 slice dor <KEY>    t0 slice start <KEY>
t0 bet detect [--json]   t0 bet use <BET>
t0 context [ref] [--format agents|delta|subagent]
t0 transcript redact <file> [--dry-run]
t0 jira sync [--apply] [--tracker file:<dir>]
t0 gen [--check] [--scope plugin|kb]
t0 hook <session-start|prompt-submit|pre-tool|stop>   (stdin JSON, exit 2 blocks)
t0 mcp [--kb DIR] [--read-only]
t0 doctor
```

Every mutating command returns a `Plan`, prints it, and supports `--dry-run`. Effects are only: records spool, a draft knowledge PR (or a local branch + commit when no forge is configured), or nothing.

## Deferred (with reason)

| Item | Why deferred | Needs |
|---|---|---|
| `JiraRest` Cloud/DC wiring | flavor unknown | answer to "Jira Cloud ou DC?" |
| `t0 ws init/sync` cloning, `t0 pr check` merge order | forge (GHE) details unknown | GHE version, App approval |
| Records auto-merge | bank branch protection unverified | security review; fallback = hourly batch PR |
| Digest/metrics/adoption reports | need telemetry sources | painel do pod Insights |
| Cross-agent eval runner (Copilot CLI, kiro-cli) | Kiro headless needs paid key | key + Copilot CLI policy |
