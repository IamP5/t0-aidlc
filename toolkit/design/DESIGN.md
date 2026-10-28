# t0 toolkit: design contract (v2)

This is the contract every build stream implements. It wins over the sketch (`design/sketch-c1/`), the C2 grafts (`design/c2/`) and the v1 plans (`design/{skills,evals,layout,v0.1}.md`, kept as history).

Functional source: `methodology/v2-brief.md`, `methodology/methodology.md` (§11 is the step → command → artifact table) and `methodology/workspace-pattern.md`. Upstream analysis: `research/toolkit-inventory.md`. Decision trail: `.audit/aidlc-build.tsv`.

Approved by the user on 2026-10-28 (decisions D1 to D8, section 12).

## 1. Base

- **Candidate 1, "event-folded KB", narrowed.** It has the smaller public surface: a `KB` facade, `Plan | Refusal`, one `apply`. Invariants live in signatures (`RecordsPR`, always-draft forge, `Redacted`), the registry is one code table with self-tests, and there is one hook entrypoint.
- **Each state key has one owner, per type.**
  - Knowledge types (Idea after `new`, Bet, Spec, ADR, Policy, Rotation, Product `adoption_stage`): `state` and `verified` change only in the decision PR. `t0 gate aposta|spec` runs the checks in CI at PR head, and approving the PR is the decision.
  - Derived keys belong to `kb-render` only. That covers Slice `state` after `ready` (`building`, `in-review`, `done`, `blocked`), `pr`, `audit`, `jira` (write-once from `jira-linked` records), `markers_open` and `status`, plus `index.md`, `log.md` and `changeset.md`.
  - `view.fold` is the read-side index and anomaly detector. It does not own state.
  - Rapida track: the aposta PR writes Bet `active` and its one Slice `ready`. There is no Spec. The last merge runs `t0 bet ship`.
- **Ideas enter through the knowledge lane** as a small PR. `t0 new idea` reserves `IDEA-NNNN` by scanning `main` plus open branches. A collision fails L1 `uid-unique`.
- **The profile registry stays in code** (`t0/profile/table.py`). `profile.md` is generated into the KB and drift-checked by `t0 gen --check --scope kb`, because a KB PR must never break every dev's CLI. The team edits Policy (thresholds, models, WIP, records mode, retention) and Template (pt-BR skeletons) without a release.

## 2. Methodology mapping (v2)

- **Human decisions.** Three: `aposta`, `spec`, `degrau`. G0 to G8 are gone. Build, review and merge belong to CI and normal PR review.
- **Tracks.** `rapida` is one slice, no spec, and the slice body carries "atual / esperado / não muda" plus a test. `bet` is prototype, spec, slices. Public surfaces are Tier 2. There are no bet types.
- **Idea prototype fields.** `verdict: segue|ajusta|mata`, `prototype_ref`, `decided_at`.
- **Rituals.** `daily-time`, `daily-pod`, `harness-health` (weekly), `demo` (every 2 weeks), `retro` (monthly), plus external `pi`. The engine is generic. Specific closers:
  - opening `daily-time` prints the digest: merges, reviews stale for more than 24h, blockers;
  - closing `harness-health` refuses without a PR per accepted Harness Item;
  - closing `demo` records the rotation.
- **Roles.** Lead/AIVA, Bet Owner, Builder, Harness Keeper (rotation), Flow Steward (rotation).
- **Pods.** `dev-tooling`, `paco`, `portal-metricas`, used as product slugs.
- **WIP.** At most 2 slices building per person (Policy `wip`). `t0 slice dor` enforces it.

## 3. KB types (profile `t0-team`)

There are 20 types: Idea, Bet, Spec, Slice, ADR, Ritual, Ritual Record, Transcript, Harness Item, Product, Workspace, Eval Suite, Adoption Report, Policy, Template, Person, Role, Rotation, Glossary Term and Step. OKF's own Log and Reference also apply.

- **Spec sections.** Spec has optional Plano and Design sections. Product carries the live spec, and the contract is a section of it.
- **Ritual.** This is the definition concept. The engine reads its `inputs`.
- **Removed.** Plan, Assessment, Bugfix, Cycle Record, Accountability, PI Outcome and Contract.
- **Deferred.** Metric Snapshot waits for the metrics work.

Prototypes and arena candidates never enter the KB. Only the verdict, the chosen design and the audit trail do.

## 4. OKF template (`okf-template/`, also the positive test fixture)

```
t0-kb/
  index.md  profile.md  log.md        [gen]
  .t0/toolkit.lock  .t0/schemas/      [gen]
  .github/CODEOWNERS                  knowledge lane owners; none on steps/ and ideas/
  .github/workflows/kb.yml            [gen] check on PR; render + jira sync on main
  methodology/
    methodology.md  workspace-pattern.md        Reference
    pack.md                                     [gen] skills and t0 commands
    practices/  review-tiers.md  harness-ladder.md  dor-dod.md
    policies/   adoption-floors.md  eval-gate.md  transcript-retention.md  models.md  records-lane.md  wip.md
    adr/
  templates/   idea bet spec slice adr harness-item ritual-record (.md)
  team/        people/  roles/ (5)  rotations/ (harness-keeper, flow-steward)
  ideas/       IDEA-NNNN.md
  rituals/     <slug>/ritual.md + <slug>/YYYY-MM-DD.md
               daily-time daily-pod harness-health demo retro pi
  transcripts/ YYYY-MM-DD-<ritual>.md (redacted only)
  steps/       records outside a bet
  glossary/
  harness/     HI-NNNN.md  budget.md
  products/<pod>/                     dev-tooling  paco  portal-metricas  exemplo (fixture)
    product.md  workspace.md  evals.md
    adr/  adoption/
    bets/BET-NNN/ bet.md  spec.md  slices/NN-slug.md  steps/
```

`products/exemplo/` exercises every type, both tracks and every lane. `toolkit/tests/fixtures/kb-positive` points at `okf-template/`.

## 5. Write lanes

The lanes are records, knowledge and derived, as in workspace-pattern §4.

**Records mode** comes from Policy `records-lane`:
- the default is `batch`, one PR a day before the daily do time, approved by the Flow Steward;
- `auto` (auto-merge without approval) turns on only after security confirms the bank's branch protection allows it.

Raw transcripts live only in `~/.t0/inbox/`. The PreToolUse read guard blocks agents from reading there. Transcript persistence stays dry-run until the LGPD sign-off.

## 6. Skills

There are 15 skills, flat at `plugin/skills/<name>/SKILL.md`, with descriptions up to 300 chars. "Compose" means upstream text with patches applied at build time (section 7). "Own" means t0 text only.

| Skill | Kind | Base (MP = mattpocock-skills, PS = pstack) | Behavior |
|---|---|---|---|
| `t0` | own, PS `poteto-mode` on watch | | Entry and orchestrator in poteto-mode's shape. It holds the non-negotiables (draft-only, three human decisions, KB writes only through `t0`, pt-BR output), the principles index and the playbook router. It also holds the subagent rules, with `t0-agent` |
| `idea-capture` | own | | `t0 new idea` with dedup |
| `grill` | compose | MP `grilling` + `domain-modeling` | glossary to KB `glossary/` (bilingual), ADR through `t0 new adr` |
| `prototype` | compose | MP `prototype` | works off main; ends with `t0 idea prototype --verdict` |
| `bet-new` | own | | `t0 new bet --track rapida\|bet` opens the aposta PR. On rapida it also writes the slice |
| `bet-spec` | compose | MP `to-spec` | drop setup pointer and tracker publish; keep the seams check; Template spec with Critérios de aceite (bullets), Como verificar, Tier, optional Design |
| `bet-slice` | compose | MP `to-tickets` | drop tracker and `.scratch/`; keep the approval loop; one file per slice on the spec branch, so one PR carries the gate spec; Jira mirror in CI after merge |
| `architect` | compose | PS `architect` | grounding through KB MCP and repo reads; runners from Policy `models`; checkpoint mandatory; Phases D and E dropped; output to the spec Design section and an ADR |
| `arena` | compose | PS `arena` | models from Policy; poteto-mode subagent pointer replaced; worktree candidates never pushed; `same-family` label |
| `swarm` | compose | PS `swarm` | same model patch; cloud becomes a worktree |
| `slice-build` | compose | MP `implement` + `tdd` + `pr`, PS `show-me-your-work` + `in-your-own-words` | `t0 slice dor`/`start`, branch `<KEY>-slug`, draft PR with `Jira`, `Tier`, `Trilha` and "Em minhas palavras"; `.audit/<KEY>.tsv` committed |
| `slice-verify` | compose | MP `code-review`, PS `blast-radius` + `swarm`, project `verify-<app>` | review against the KB spec; Tier 2 runs the blast-radius proof ladder without its arena step; app evidence through `verify-<app>`; a repeated error becomes a Harness Item |
| `verify-setup` | compose | PS `create-` + `maintain-verification-skill` | writes `.t0/skills/verify-<app>/` in the product repo, and `t0 setup` links it per tool; the maintain half feeds Harness Health with one draft PR |
| `ritual` | own (C2 engine) | | `ritual <slug> open\|close [--transcript F]`, transcript redacted first |
| `harness-fix` | compose | PS `correct` + MP `retro` | highest rung of the harness ladder; workspace-scoped logs; one draft PR per item |

**`/t0` playbooks** are t0's own: `ideia`, `rapida`, `bet`, `slice`, `harness`, `ritual`.

**Composed from pstack playbooks:** `investigation`, `bug-fix`, `feature`, `refactoring`, `prototype`, `perf-issue`.

**Not shipped.** These ship, merge, open ready PRs or read raw transcripts: `opening-a-pr`, `babysit`, `shipping`, `autopilot-*`, `orchestrate`, `multi-phase-plan`, `session-pickup`.

**Principles vendored (19):**
- laziness-protocol, foundational-thinking, subtract-before-you-add, minimize-reader-load, build-the-lever;
- model-the-domain, boundary-discipline, type-system-discipline, make-operations-idempotent, separate-before-serializing-shared-state;
- prove-it-works, fix-root-causes, sequence-verifiable-units, test-behavior-not-implementation;
- exhaust-the-design-space, outcome-oriented-execution, redesign-from-first-principles, encode-lessons-in-structure;
- never-block-on-the-human, which `/t0` limits to reversible work inside a slice.

**Subagents** (`plugin/agents/`, generated per tool): `t0-agent`, `spec-reviewer`, `standards-reviewer`, `verifier`.

## 7. Upstream sync

Upstream text is vendored byte-identical. Each skill is composed at build time from a recipe. The shipped `SKILL.md` is one self-contained file.

- **Vendor.** `vendor/<stream>/...` keeps upstream's tree shape and its `LICENSE`, plus `pr/CREDITS.md`. It is pinned by sha256 in `upstream/upstream.lock`, with the commit recorded as advisory. It is never edited and never shipped as-is.
- **Recipe.** Each skill has `skills-src/<name>/skill.toml`, with frontmatter, `[[part]]` entries (`from = "<stream>:<path>"` or `own = "<file>.md"`) and patches. The patch kinds are:
  - `drop_section` and `replace_section`, by heading;
  - `drop_line` and `replace_line`, by a literal substring that must match exactly once;
  - `append`.

  A global rewrite turns `Call the Skill tool with "<x>"` into a pointer to the composed section `<x>`. It fails the build when `<x>` isn't composed in.
- **Streams.** `upstream/streams.toml` holds, per stream, `repo`, `subdir`, `ref`, `paths`, `renamed` and `watch`. It also holds `local`, the dev's plugin cache, which is the fallback when GitHub is blocked.
  - mattpocock: `github.com/mattpocock/skills` at `v1.3.1`.
  - pstack: `github.com/cursor/plugins` subdir `pstack`, pinned by commit. The pstack tag scheme is not verified.
  - `watch` lists files reported on every bump for a manual port. Today that is only `poteto-mode/SKILL.md`.

**Commands:**
- **`t0 upstream status`.** Shows changed, added and removed files per stream, which skills compose each one, and untracked new upstream skills. It exits non-zero when a tracked path vanished without a `renamed` entry.
- **`t0 upstream pull <stream> [--ref R]`.** Refreshes `vendor/`, rewrites the lock, runs `t0 gen` and writes `upstream/reports/<stream>-<from>-<to>.md`. The Harness Keeper commits it and opens a draft PR. Pulling at the same ref is a no-op.
- **`t0 gen --check`** (CI). Vendor files match the lock, every patch anchor matches once, every `Skill` call or `../<name>` reference resolves, and the shipped files equal a fresh compose.

**Loop.** Weekly, `status` feeds Harness Health. When something has moved, the Harness Keeper runs `pull` and fixes the patches that a broken anchor points to. Someone skims the clean changes for behavior worth adopting, which becomes a Harness Item. Evals prove the removed behaviors stay gone, and then the PR merges and the version bumps.

## 8. Enforcement

The `pre-tool` hook blocks these on the Bash surface and on GitHub MCP tools alike:
- force push and `reset --hard`;
- `gh pr create` without `--draft`, and non-draft `create_pull_request`;
- `gh pr ready`, `gh pr merge` and `merge_pull_request`;
- edits of derived keys;
- reads under `~/.t0/inbox/`.

The forge adapter's `open_pr` has no `draft` parameter, and auto-merge is accepted only for `RecordsPR`.

## 9. Layout

**Toolkit repo:**

```
toolkit/                 python package `t0` (pyproject, src/t0, tests)
  design/                this file, STREAMS.md, history
vendor/                  [vendor] mattpocock/, pstack/
skills-src/<name>/       [src] skill.toml + t0-owned .md
upstream/                streams.toml [src], upstream.lock [gen], reports/ [gen]
okf-template/            the KB starter, shipped as package data
plugin/                  [gen] everything below
methodology/  research/
```

**Plugin (all generated by `t0 gen`):**

```
plugin/
  .claude-plugin/plugin.json  .claude-plugin/marketplace.json  plugin.json   explicit skills list; Agent Plugins 1.0
  .mcp.json  mcp.json         t0-kb -> `t0 mcp`
  hooks/hooks.json            -> `t0 hook <event> --tool <t>`
  agents/                     t0-agent, spec-reviewer, standards-reviewer, verifier
  skills/<15>/SKILL.md        (+ references/ copied from upstream)
  evals/                      `claude plugin eval` cases
  THIRD_PARTY_NOTICES.md      from vendor/*/LICENSE + streams.toml
```

The plugin directory has no Python. Hooks and MCP call `t0` on PATH, and the plugin version equals the package version.

## 10. CLI surface v0.1

```
t0 setup                       product repo: AGENTS.md, pointers, hooks, verify-skill links
t0 kb check [--level L0|L1|L2] [--format text|github|json] [--changed-from REF]
t0 kb find|get|render|push|init
t0 new idea|bet|spec|slice|adr|harness [--dry-run]
t0 idea prototype <IDEA> --verdict segue|ajusta|mata [--ref R]
t0 log progress|decision|blocker|kill "<texto>" [--bet B] [--story K]
t0 gate aposta|spec <ref> [--dry-run] [--ci]
t0 ritual <slug> open|close [--transcript F]
t0 transcript redact <file> [--dry-run]
t0 slice dor|start <KEY>       t0 bet detect|use|ship      t0 ci <KEY>
t0 jira sync [--apply] [--tracker file:<dir>]
t0 context [ref] [--format agents|delta|subagent]
t0 upstream status|pull
t0 gen [--check] [--scope plugin|kb] [--src S] [--out O]
t0 hook <event> [--tool claude|copilot|kiro]     (stdin JSON, exit 2 blocks)
t0 mcp [--kb DIR] [--read-only]
t0 doctor
```

Every mutating command returns a `Plan`, prints it and supports `--dry-run`. Effects are limited to the records spool, a draft knowledge PR (or a local branch and commit when no forge is configured), or nothing. `Report.format(text|github|json)` is shared.

Context budgets: the card is 8,000 chars, the delta is 3,000, and the subagent card and MCP instructions are 1,500 each.

## 11. Evals and tests

**Plugin evals** live in `plugin/evals/` and follow `research/plugin-eval-format.md`:
- scaffolds only through `case.yaml` `context.scaffold_script`;
- mocks only for servers the plugin declares;
- no `tool_order` with one tool;
- `file_exists` only for files Claude creates;
- no `baseline` grader without `baseline_file`;
- denial is asserted with `regex` on `trace`/`last_message`.

**Cases:**
- `slice-build-draft-only`;
- `kb-record-secret-refused`;
- `ritual-transcript-redacted`;
- `hook-blocks-derived-edit`;
- `portable-skill-trigger`;
- `bet-spec-no-tracker-publish`;
- `architect-stops-at-design`;
- `slice-build-commits-audit-log`;
- `arena-labels-same-family`.

There is one eval for each patch that removes a behavior.

**Deterministic tests (pytest):**
- one negative fixture per checker rule;
- one test per patch kind;
- "a broken anchor fails gen";
- "a vanished path fails upstream status";
- the redaction corpus.

The cross-agent runner (Copilot CLI, kiro-cli) is deferred.

## 12. Approved decisions (2026-10-28)

| # | Decision |
|---|---|
| D1 | poteto-mode (as `/t0`), arena and swarm enter the toolkit; §11 updated |
| D2 | Build-time composition (vendor + recipe + patches) instead of runtime overlays or forks |
| D3 | `/t0` is t0-owned text, poteto-mode on `watch` |
| D4 | Records lane `batch` daily by default, `auto` after security confirms |
| D5 | `verify-<app>` lives at `.t0/skills/verify-<app>/` in product repos, linked per tool by `t0 setup` (unverified on Copilot and Kiro) |
| D6 | Subagent card budget is 1,500 chars |
| D7 | `degrau` deferred to v0.2 |
| D8 | arena and swarm stay user-invocable |

## 13. Deferred

| Item | Why | Needs |
|---|---|---|
| `t0 gate degrau`, `t0 adoption`, `t0 eval run` | no product at the squads rung yet | v0.2 |
| `JiraRest` Cloud/DC wiring | flavor unknown | answer to "Jira Cloud ou DC?" |
| `t0 ws init/sync` cloning, `t0 pr check` merge order | GHE details unknown | GHE version, App approval |
| Records `auto` mode | bank branch protection unverified | security review |
| Metrics (idea → prototype, idea → production), Metric Snapshot | telemetry sources | pod Portal e Métricas |
| Cross-agent eval runner | Kiro headless needs a paid key | key + Copilot CLI policy |
| `rules build`, `review-queue`, `trace` | not used by the v2 flow | demand |
