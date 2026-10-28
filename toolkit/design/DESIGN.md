# t0 toolkit: design contract (v2)

This is the contract every build stream implements. It wins over the sketch (`design/sketch-c1/`), the C2 grafts (`design/c2/`) and the v1 plans (`design/{skills,evals,layout,v0.1}.md`, kept as history).

Functional source: `methodology/v2-brief.md`, `methodology/methodology.md` (§11 is the step → command → artifact table) and `methodology/workspace-pattern.md`. Upstream analysis: `research/toolkit-inventory.md`. Decision trail: `.audit/aidlc-build.tsv`.

Approved by the user on 2026-10-28 (decisions D1 to D8, section 12; D2 revised the same day).

## 1. Base

- **Candidate 1, "event-folded KB", narrowed.** It has the smaller public surface: a `KB` facade, `Plan | Refusal`, one `apply`. Invariants live in signatures (`RecordsPR`, always-draft forge, `Redacted`), the registry is one code table with self-tests, and there is one hook entrypoint.
- **Each state key has one owner, per type.**
  - Knowledge types (Idea after `new`, Bet, Spec, ADR, Policy, Rotation, Product `adoption_stage`): `state` changes only in the decision PR. `t0 gate aposta|spec` runs the checks in CI at PR head, and approving the PR is the decision. Nobody writes `verified` by hand or in the decision PR: on merge, `t0 ci <ref> --state merged` records the approvals in a `pr-merged` record and `kb-render` derives `verified` from it.
  - Derived keys belong to `kb-render` only. That covers Slice `state` after `ready` (`building`, `in-review`, `done`, `blocked`), `verified` on every stateful type (from `pr-merged` approvals), `pr`, `audit`, `jira` (write-once from `jira-linked` records), `markers_open` and `status`, plus `index.md`, `log.md` and `changeset.md`.
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

**Branches.** KB knowledge-lane work goes on `bet/BET-NNN/<handle>` (spec, slices, glossary, Design section). Product code goes on `<KEY>-<slug>` in the slice's repo, created by `t0 slice start <KEY>`.

**Policy `models` role keys.** `architect-runner`, `arena-runner`, `judge`, `reviewer`, `swarm-worker`, `verifier`, each mapping a tool to a model, plus `families_approved`.

## 3. KB types (profile `t0-team`)

There are 20 types: Idea, Bet, Spec, Slice, ADR, Ritual, Ritual Record, Transcript, Harness Item, Product, Workspace, Eval Suite, Adoption Report, Policy, Template, Person, Role, Rotation, Glossary Term and Step. OKF's own Log and Reference also apply.

- **Spec sections.** Spec has optional Plano and Design sections. Person has `junior: true|false`, which drives the "Em minhas palavras" rule. Product carries the live spec, and the contract is a section of it.
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

There are 15 skills, hand-written in pt-BR at `plugin/skills/<name>/SKILL.md`, with descriptions up to 300 chars. Each one is based on its reference skill (MP = mattpocock-skills 1.3.1, PS = pstack 0.15.25, read from the local plugin caches), keeping what works in the reference and writing the t0 behavior in directly. There is no vendoring. `metadata.credits` names the reference and its version. "Own" means there is no reference.

| Skill | Kind | Reference (MP = mattpocock-skills, PS = pstack) | Behavior |
|---|---|---|---|
| `t0` | based on | PS `poteto-mode` | Entry and orchestrator in poteto-mode's shape. It holds the non-negotiables (draft-only, three human decisions, KB writes only through `t0`, pt-BR output), the principles index and the playbook router. It also holds the subagent rules, with `t0-agent` |
| `idea-capture` | own | | `t0 new idea` with dedup |
| `grill` | based on | MP `grilling` + `domain-modeling` | glossary to KB `glossary/` (bilingual), ADR through `t0 new adr` |
| `prototype` | based on | MP `prototype` | works off main; ends with `t0 idea prototype --verdict` |
| `bet-new` | own | | `t0 new bet --track rapida\|bet` opens the aposta PR. On rapida it also writes the slice |
| `bet-spec` | based on | MP `to-spec` | drop setup pointer and tracker publish; keep the seams check; Template spec with Critérios de aceite (bullets), Como verificar, Tier, optional Design |
| `bet-slice` | based on | MP `to-tickets` | drop tracker and `.scratch/`; keep the approval loop; one file per slice on the spec branch, so one PR carries the gate spec; Jira mirror in CI after merge |
| `architect` | based on | PS `architect` | grounding through KB MCP and repo reads; runners from Policy `models`; checkpoint mandatory; Phases D and E dropped; output to the spec Design section and an ADR |
| `arena` | based on | PS `arena` | models from Policy; poteto-mode subagent pointer replaced; worktree candidates never pushed; `same-family` label |
| `swarm` | based on | PS `swarm` | models from Policy `models`; cloud becomes a worktree; `same-family` label |
| `slice-build` | based on | MP `implement` + `tdd` + `pr`, PS `show-me-your-work` + `in-your-own-words` | `t0 slice dor`/`start`, branch `<KEY>-slug`, draft PR with `Jira`, `Tier`, `Trilha` and "Em minhas palavras"; `.audit/<KEY>.tsv` committed |
| `slice-verify` | based on | MP `code-review`, PS `blast-radius` + `swarm`, project `verify-<app>` | review against the KB spec; Tier 2 runs the blast-radius proof ladder without its arena step; app evidence through `verify-<app>`; a repeated error becomes a Harness Item |
| `verify-setup` | based on | PS `create-` + `maintain-verification-skill` | writes `.t0/skills/verify-<app>/` in the product repo, and `t0 setup` links it per tool; the maintain half feeds Harness Health with one draft PR |
| `ritual` | own (C2 engine) | | `ritual <slug> open\|close [--transcript F]`, transcript redacted first |
| `harness-fix` | based on | PS `correct` + MP `retro` | highest rung of the harness ladder; workspace-scoped logs; one draft PR per item |

**`/t0` playbooks** are t0's own: `ideia`, `rapida`, `bet`, `slice`, `harness`, `ritual`.

**General playbooks**, written in pt-BR from the pstack ones: `investigation`, `bug-fix`, `feature`, `refactoring`, `prototype`, `perf-issue`.

**Not carried over.** These ship, merge, open ready PRs or read raw transcripts: `opening-a-pr`, `babysit`, `shipping`, `autopilot-*`, `orchestrate`, `multi-phase-plan`, `session-pickup`.

**Principles** (19), in pt-BR in `t0/references/principios.md`, one short paragraph each, from the pstack `principle-*` skills:
- laziness-protocol, foundational-thinking, subtract-before-you-add, minimize-reader-load, build-the-lever;
- model-the-domain, boundary-discipline, type-system-discipline, make-operations-idempotent, separate-before-serializing-shared-state;
- prove-it-works, fix-root-causes, sequence-verifiable-units, test-behavior-not-implementation;
- exhaust-the-design-space, outcome-oriented-execution, redesign-from-first-principles, encode-lessons-in-structure;
- never-block-on-the-human, which `/t0` limits to reversible work inside a slice.

**Subagents** (`plugin/agents/`, generated per tool): `t0-agent`, `spec-reviewer`, `standards-reviewer`, `verifier`.

## 7. References and credits

The skills are t0's own pt-BR text. The upstream skills are reference material only.

- `THIRD_PARTY_NOTICES.md` carries the MIT notices of mattpocock-skills and pstack (plus the Humanlayer credit carried by MP `pr`). Each SKILL.md lists its reference in `metadata.credits`.
- Nothing is generated from upstream. The one copied file is PS `show-me-your-work/scripts/log.sh` (as `slice-build/scripts/log.sh`, MIT header kept), for its CSV-injection guard.
- Following upstream changes is manual. When the Harness Keeper sees a new version of either plugin, they read its CHANGELOG in Harness Health and open a Harness Item for anything worth porting.

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
okf-template/            the KB starter, shipped as package data
plugin/                  skills/ and .mcp.json are [src]; the rest is [gen]
methodology/  research/
```

**Plugin:**

```
plugin/
  .claude-plugin/plugin.json  .claude-plugin/marketplace.json  plugin.json   explicit skills list; Agent Plugins 1.0
  .mcp.json  mcp.json         t0-kb -> `t0 mcp`
  hooks/hooks.json            -> `t0 hook <event> --tool <t>`
  agents/                     t0-agent, spec-reviewer, standards-reviewer, verifier
  skills/<15>/SKILL.md        [src] pt-BR, + references/ per skill
  evals/                      [src] `claude plugin eval` cases
  THIRD_PARTY_NOTICES.md      [src] MIT notices of the references
```

The plugin directory has no Python. Hooks and MCP call `t0` on PATH, and the plugin version equals the package version.

## 10. CLI surface v0.1

```
t0 setup                       product repo: AGENTS.md, pointers, hooks, verify-skill links
t0 kb check [--level L0|L1|L2] [--format text|github|json] [--changed-from REF]
t0 kb find|get|render|push|init
t0 kb propose -m MSG [--dry-run]   draft knowledge PR for the current branch (local branch + commit with no forge)
t0 new idea|bet|spec|slice|adr|harness [--dry-run]
t0 idea prototype <IDEA> --verdict segue|ajusta|mata [--ref R]
t0 log progress|decision|blocker|kill "<texto>" [--bet B] [--story K]
t0 gate aposta|spec <ref> [--dry-run] [--ci]   state + status in the decision PR; never `verified`
t0 adr accept <ADR> [--dry-run]  knowledge-lane edit to `state: accepted`, draft PR to the deciders (as `kb propose`)
t0 ritual <slug> open|close [--decisions FILE] [--transcript F]
t0 transcript redact <file> [--dry-run]
t0 slice dor|start <KEY>       t0 bet detect|use|ship
t0 ci <KEY|ref> --pr P --state draft|ready|merged [--approval A]   records for kb-render; on a merged decision PR, the approvals behind `verified`
t0 jira sync [--apply] [--tracker file:<dir>]
t0 context [ref] [--format agents|delta|subagent]
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

There is one eval for each behavior where t0 departs from its reference skill.

**Deterministic tests (pytest):**
- one negative fixture per checker rule;
- the redaction corpus.

The cross-agent runner (Copilot CLI, kiro-cli) is deferred.

## 12. Approved decisions (2026-10-28)

| # | Decision |
|---|---|
| D1 | poteto-mode (as `/t0`), arena and swarm enter the toolkit; §11 updated |
| D2 | Skills hand-written in pt-BR from the reference skills; no vendoring, composition or upstream sync tooling (revised 2026-10-28, replacing build-time composition) |
| D3 | `/t0` is t0's own pt-BR text in poteto-mode's shape |
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
