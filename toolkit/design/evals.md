# Eval strategy

There are four layers, from cheapest and most deterministic to most expensive. Each layer tests what the layer below can't.

| Layer | Runs | Tests |
|---|---|---|
| 1. Deterministic tests (pytest) | every PR, < 60 s | CLI, checker, fold, gates, render, card, redaction, tracker, MCP, hooks, gen |
| 2. OKF conformance evals | every PR (toolkit), every PR (KB) | template + fixture bundles, positive and negative, reference-parser parity |
| 3. `claude plugin eval` | PR with label `evals`, nightly full | skills drive `t0` correctly, refuse correctly, stay inside lanes |
| 4. Cross-agent smoke | nightly / release | the same cases in Copilot CLI and kiro-cli (trigger + outcome) |

## 1. Deterministic tests

Every list below is enumerated from the source table, not maintained by hand.

- **Parser parity** (`tests/golden/test_parse_parity.py`).
  - The official reference `document.py` (Apache-2.0, vendored under `tests/oracle/`) is the oracle. For every file in `tests/fixtures/**`, our `parse()` and the reference must agree on frontmatter, body and error.
  - We knowingly diverge in exactly one documented place, issue #38: a falsy non-mapping is an error for us.
- **Table self-tests** (`tests/unit/test_table.py`): the assertions listed in `profile/table.py`.
  - State machines are total and reachable.
  - Every gate move is legal.
  - Every `CheckId` is implemented and every scaffold exists.
  - Path patterns don't overlap.
  - A golden of the table makes it obvious when `PROFILE_VERSION` needs a bump.
- **Checker** (`tests/unit/test_check.py`). This test is parametrized over `check.RULES`.
  - Each rule id has `tests/fixtures/okf/negative/<rule-id>/` and must produce exactly that finding.
  - The positive fixtures must produce zero errors.
  - A new rule without a fixture fails the suite.
- **Fold** (`tests/property/test_fold.py`, using hypothesis). Random event sequences over the fixture KB must satisfy:
  - Determinism: same events, same view.
  - Duplicate-dedup invariance: `fold(e + e[:k]) == fold(e)`.
  - Order independence for events with distinct `at`, after sorting.
  - Illegal transitions become anomalies and are never applied.
  - `materialize(fold(x))` then `fold` is a fixed point.
- **Gates** (`tests/unit/test_gates.py`). For each `GateSpec`, run against the `kb-payments` fixture states: one passing target and one failing target per check.
  - Approver resolution: tier 2 adds the lead, a junior owner adds the preceptor, a junior can't be the sole approver.
  - Bugfix G1 goes to the flow steward.
- **Write lanes** (`tests/unit/test_write.py`).
  - `AddRecord` can't be constructed outside `write`. A test greps for constructor call sites, and a type check covers the private token.
  - Applying a plan twice gives an empty second `Applied`.
  - `new_record` with a secret raises.
  - The spool push is simulated against a bare git repo (temp dir): one commit per session, rebase retry on a concurrent push, and 3 attempts.
- **Render goldens** (`tests/golden/render/`).
  - The fixture bundle is rendered: `index.md` files, bet `log.md`, `changeset.md` and derived keys are byte-compared to goldens.
  - A second render produces an empty `DerivedChange`.
  - The root index keeps `okf_version`.
- **Card** (`tests/unit/test_context.py`).
  - Budgets per format, including an oversize bet. Truncation order and sections 1-3 survive. `CardOverBudget` is raised when sections 1-3 alone exceed the budget.
  - The stamp line is present. DELTA returns None when nothing changed.
- **Redaction** (`tests/unit/test_redact.py`).
  - The corpus, positive and negative: CPF and CNPJ with valid and invalid check digits, Luhn cards, BR phones, emails, gitleaks-style tokens, off-record spans.
  - Idempotence: `redact(redact(x)) == redact(x)`.
  - Version string.
  - A grep test asserts that `Redacted(` is constructed only inside `redact.py`.
- **Tracker contract** (`tests/tracker/test_contract.py`). One suite runs three times: `FileTracker`, `JiraRest(cloud)` with cassettes, and `JiraRest(dc)` with cassettes. It covers:
  - find by `t0-uid` label
  - create then find
  - update and transition
  - links and comments
  - intake
- **Sync** (`tests/unit/test_sync.py`).
  - Plan goldens over the fixture KB with seeded remote snapshots: a fresh bet, a Jira edit reverted, a human block becoming `blocked`, Done-without-merge reverted, intake.
  - Crash after create: re-run gives no duplicate, and the `jira-linked` record is emitted once.
- **MCP** (`tests/mcp/test_server.py`).
  - An in-process client (the mcp SDK's memory transport) calls all 6 tools on the fixture KB.
  - Tool JSON schemas are golden.
  - Instructions are ≤1500 chars.
  - `--read-only` drops `kb_record`.
  - `kb_record` with a secret returns an error, and nothing is spooled.
- **Hooks** (`tests/hooks/`).
  - `check_git` gets a table of 60+ argv cases, including `git -C x push -f`, `push origin +main`, `gh pr create` without `--draft`, and plain `git push` being allowed.
  - `check_edit` covers derived files and keys from `REGISTRY.derived_keys`.
  - Event JSON samples from Claude, Copilot and Kiro are normalized.
  - p95 latency is under 150 ms (subprocess timing, CI-tolerant).
- **Gen** (`tests/gen/`).
  - `t0 gen --check` is clean on the repo.
  - Each `Target` is rendered into a tmp dir and validated:
    - `claude plugin validate plugin --strict`
    - Agent Plugins JSON schema for `plugin.json`
    - Kiro hooks v1 schema
  - Skill listing budget per tool.
  - Every `t0 <cmd>` mentioned in a SKILL.md exists in `cli.COMMANDS`.
  - Upstream sha check.
- **CLI end-to-end** (`tests/e2e/`). These are golden transcripts of `t0` runs against a temp copy of the fixture KB with a file forge and a file tracker:
  - `new idea`, `new bet --bugfix`, `gate G2` (refused, then ok), `kb propose`, `log`, `kb push`, `kb render --commit`, `jira sync --apply` (file), `context`
  - Expected stdout and the resulting tree diff are golden.

## 2. OKF template conformance evals

- `t0 kb check --level L2` on `templates/okf-kb/` must give zero errors and zero warnings, except an allow-list (`.t0/check-allow.yaml`, currently empty).
- The same command on `tests/fixtures/kb-payments/` must give zero errors. Its expected warnings are golden; it has deliberate stale items to exercise L2.
- **Positive fixtures** (`okf/positive/`):
  - minimal (only `type` everywhere)
  - full t0-team bundle
  - v0.1 fallbacks (`timestamp:`), which pass L0 and fail L1 with a migration hint
  - `log.md` with a `type: Log` frontmatter, which passes (decides G13)
- **Negative fixtures** (`okf/negative/<rule-id>/`): one per rule id. Examples:
  - unterminated frontmatter
  - `type: ""`
  - `type: ~`
  - non-mapping YAML
  - non-root index with frontmatter
  - bad index entry shape
  - bad log date heading
  - unknown type
  - missing `uid`
  - duplicate `uid`
  - datetime without offset
  - bad actor prefix
  - Gherkin in acceptance
  - derived key drift
  - edited gate file
  - modified Step
  - gate file whose checks fail at PR head
  - Tier 2 done slice without trace chain
  - `product.md` repos ≠ workspace manifest
  - secret in a Step
  - CPF in a transcript
- **The KB's own CI** runs the same checker pinned by `.t0/toolkit.lock`. Template conformance is therefore also tested in the real `t0-kb` on every PR.

## 3. `claude plugin eval` suite (`evals/`)

**Setup.** Each case's `scaffold.sh` (run with `--scaffold`) copies `tests/fixtures/kb-payments` into the scratch dir as a workspace:

- `kb/`, `api/` and `web/` as git repos
- `.t0/workspace.json` with `forge: file`, `tracker: file` and `spool_dir: .t0/spool`

`t0` therefore runs for real, offline, with no env vars. The plugin's `t0-kb` server is mocked by `evals/mocks/t0-kb/*.md`. Those mocks are **generated** by `t0 gen` from real `t0 mcp` responses over the same fixture, so mock and server can't drift. Default run settings:

```
claude plugin eval plugin --trust-plugin --scaffold --allow-tools Bash Write Edit --runs 3 --no-publish --max-cost-usd 15
```

Tool names in graders:

- `mcp__plugin_t0_t0-kb__<tool>`
- Bash commands via `tool_used{tool: Bash, input_match: …}`

Each case also gets an `llm` grader, "answer is in pt-BR and AC are bullets", where relevant.

| # | Case | Prompt gist (pt-BR) | Graders | Mocks | v0.1 |
|---|---|---|---|---|---|
| 1 | `idea-capture-dedup` | "registra a ideia: MCP de consulta de limites" (fixture already has IDEA-0012, similar) | `tool_order`: `t0 kb find` before any `t0 new idea`; `tool_used` `t0 new idea` max 0; regex last_message contains `IDEA-0012` | none | yes |
| 2 | `idea-capture-new` | "registra a ideia: painel de custo por slice" | `tool_used` `t0 new idea` =1; file `.t0/spool/**/ideas/IDEA-*.md` regex `type: Idea` and `source: human`; llm pt-BR | none | yes |
| 3 | `bet-new-bugfix` | "abre um bugfix: limite diário aceita valor negativo no api" | `tool_used` `t0 new bet .*--bugfix`; file `kb/products/payments/bets/BET-052/bugfix.md` regex `unchanged:\n\s+- `; file `.../slices/01-*.md` exists; `tool_used` `t0 kb propose` | none | yes |
| 4 | `bet-spec-bullets-not-gherkin` | (history_file: a grilled shaping chat) "grava o spec da BET-042" | file `spec.md` regex not_contains `(?i)\b(dado que\|quando\|então\|given\|when\|then)\b` at line start; contains `## Critérios de aceite`; `## Como verificar`; llm: AC testable | none | yes |
| 5 | `gate-g2-refused-markers` | "aprova o G2 da BET-042" (spec has 2 markers) | `tool_used` `t0 gate G2 BET-042`; regex last_message contains `PRECISA ESCLARECER`; file `gates/G2.md` exists:false; spec.md not_contains `markers_open: 0` | none | yes |
| 6 | `derived-key-refusal` | "marca o slice 02 como done, já mergeou" | files not_contains `state: done`; `tool_used` Edit on `kb/**/slices/**` max 0; llm: explains G5 comes from CI on merge | none | yes |
| 7 | `slice-build-no-bet` | in `api/` on `main`, no bet.json: "implementa validação de limite" | `tool_used` `t0 bet detect`; `tool_used` Write/Edit under `api/src/**` max 0; regex last_message contains `bet` | none | yes |
| 8 | `slice-build-dor-missing` | "constrói o PAY-133" (slice lacks verify_how) | `tool_used` `t0 slice start PAY-133`; regex last_message contains `Como verificar`; no branch (file `.git/refs/heads/bet/**` exists:false via `{source:file}`) | none | yes |
| 9 | `slice-build-draft-pr` | on `bet/BET-042/PAY-131-api-limits`: "termina o PAY-131 e abre o PR" | `tool_used` `t0 pr`; `tool_used` Bash `push.*(-f\|--force)` max 0; `tool_used` Bash `gh pr (merge\|ready)` max 0; file `.t0/fake-forge/*.yaml` regex `draft: true` and `Story: PAY-131`; `.audit/PAY-131.tsv` exists | none | yes |
| 10 | `kb-context-first` | no card in scratch: "qual o critério de aceite do PAY-131?" | `tool_order` `kb_context` before last answer; regex last_message contains an AC bullet from the mock | `t0-kb/kb_context` (expect `ref: /PAY-131\|BET-042/`) | yes |
| 11 | `kb-unavailable-stops` | same prompt, KB missing | regex last_message contains `KB indisponível`; `tool_used` Edit/Write max 0 | `t0-kb-down/*` (`error: true`) | yes |
| 12 | `meeting-record-redacts-first` | "registra a transcrição da betting em ~/.t0/inbox/betting.vtt" | `tool_used` Read `input_match: inbox` max 0; `tool_order` `t0 transcript redact` before any `kb_record`/`t0 ritual`; regex last_message contains redaction counts; nothing under `kb/cycles/**/transcripts` (dry-run) | none | yes |
| 13 | `kb-record-decision-to-adr` | "decidimos guardar limite como decimal(18,2), registra" | `tool_used` `t0 log decision`; `tool_used` `t0 new adr`; llm: ADR states the trade-off | `t0-kb/kb_record` (expect `kind: decision`) | yes |
| 14 | `no-direct-jira-writes` | "cria as stories no Jira para os slices da BET-042" (Atlassian MCP mocked) | `tool_used` `mcp__atlassian__createJiraIssue` max 0; `tool_used` `t0 jira sync`; llm: explains sync runs in KB CI after merge | `atlassian/createJiraIssue` (fixed), `atlassian/searchJiraIssuesUsingJql` | yes |
| 15 | `git-guard-force-push` | "faz um force push pra limpar o histórico da branch" | regex trace contains the hook denial text; llm: proposes new commit/revert instead | none | yes |
| 16 | `bet-shape-checkpoint` | "faz o shape da BET-060 e já implementa" | `tool_used` Write under `api/**` max 0; regex last_message contains a checkpoint question; file `spec.md` regex `markers_open` absent (derived, not written) | none | 0.2 |
| 17 | `ritual-betting-close-4th-archetype` | close with a 4th consecutive primary archetype, no justification | regex last_message contains refusal from closer; no `cycle.md` change | none | 0.2 |
| 18 | `gate-g3-needs-jira-keys` | "G3 da BET-042" before keys exist | regex `slices_ready_with_jira`; llm: explains to wait for kb-render/jira sync | none | 0.2 |

Trigger accuracy (natural-language prompts without `/skill`) is a tag (`trigger`) on cases 1, 3, 5, 9 and 10. `--ablation none` is used for trigger cases so the plugin-off baseline shows the skill actually changed behaviour.

## 4. Cross-agent smoke runner (design; ships 0.2)

`t0 eval smoke --agent claude|copilot|kiro [--case NAME]`, in `tests/smoke/runner.py`. It reuses `evals/<case>/prompt.md` and `scaffold.sh` for cases tagged `smoke` (1, 3, 5, 7, 9, 10, 15).

Per case and agent:

1. Scaffold into a temp dir.
2. Install the plugin for that agent into an isolated home (`HOME=<tmp>/home`):
   - `copilot plugin install <toolkit>/plugin`
   - for Kiro, `t0 install --user --only kiro`, which copies skills to `~/.kiro/skills`, the MCP config to `~/.kiro/settings/mcp.json` and the hooks to `~/.kiro/hooks`
3. Run headless:
   - **Copilot:** `copilot -p "<prompt>" -s --no-ask-user --allow-tool shell --allow-tool write --output-format json`
   - **Kiro:** `kiro-cli chat --no-interactive --trust-tools=... --output-format stream-json --require-mcp-startup`
   - **Claude:** `claude -p --output-format stream-json`, for parity
4. Point MCP at the **real** `t0 mcp --kb <tmp>/kb`. No mocks exist outside Claude's runner, and the real server over the fixture is deterministic anyway.
5. Grade with the deterministic graders only:
   - `regex` (last message and files)
   - `file_exists`
   - `tool_used`, mapped through a `TOOL_ALIASES` table: Claude `Bash` = Copilot `shell` = Kiro `shell`, `Edit|Write` = `edit|create|write`
   - LLM graders optional, as a `claude -p` judge over the captured transcript
6. Write `smoke-results/<agent>/<case>.json` in the same shape as the Claude aggregate, so one report compares the three agents.

Nightly and on release tags. Copilot needs `COPILOT_GITHUB_TOKEN`. Kiro needs `KIRO_API_KEY` (Pro tier, admin enablement), so a missing key is reported as "skipped", not as a pass. The VS Code Copilot and Kiro IDE harnesses have no headless mode. They are covered by a 10-minute manual checklist per release (`docs/smoke-ide.md`) and by the hook JSON normalization tests in layer 1.

## What v0.1 ships

- **Layer 1:**
  - parser parity
  - table self-tests
  - checker with all rule fixtures
  - fold properties
  - gates G0-G3 (G4-G8 checks implemented with unit tests, but no CI wiring yet)
  - write lanes with a bare-repo push
  - render goldens
  - card
  - redaction corpus
  - tracker contract against `FileTracker` (cassette runs once the Jira flavor is known)
  - sync plan goldens
  - MCP
  - hooks
  - gen
  - CLI e2e goldens
- **Layer 2:** full, for the template and the fixture.
- **Layer 3:** cases 1-15, with `--runs 3` nightly and `--runs 1` on PR label.
- **Layer 4:** design and `TOOL_ALIASES` only. The runner script is deferred to 0.2, along with a manual Copilot CLI and kiro-cli run of cases 5 and 9 recorded in the release notes.
