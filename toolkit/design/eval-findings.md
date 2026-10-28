# Eval loop findings

One line per issue found by running the skills against the eval KB (`plugin/evals/`, seed built by `plugin/evals/_lib/build-seed.sh` from okf-template plus IamP5 repos). Status: open, fixed (with where), wontfix (with why).

## Round 1 (2026-10-28)

| # | Found by | Issue | Status |
|---|---|---|---|
| 1 | build-seed | `gen.load_sources` read `pyproject.toml` beside the source; an installed t0 crashed on `kb init` | fixed: falls back to package metadata |
| 2 | seed card | AGENTS.md card listed v1 skills (`/bet-use`, `/kb-record`, `/kb-search`) | fixed: card skills derived from state, tested against plugin/skills |
| 3 | kb check | template transcript lacks a known `redaction` block, plus 6 derived-drift warnings | fixed: template checks clean at L2 |
| 4 | scaffold | `t0 gate aposta` needs `hypothesis` and `kill_criteria`; appetite over P1W needs Lead, and the template Lead has no `holders` | fixed: Lead holders in template; bet-new behavior checked by eval bet-new-aposta |
| 5 | scaffold | `jira` is derived, so a slice gets its key only via `t0 jira sync`; the dev-tooling manifest needs `jira_project` | fixed in seed (SBP) |
| 6 | scaffold | `t0 gate spec` reads `acceptance`/`verify_how` from frontmatter, while the skills and templates write `## Critérios de aceite` / `## Como verificar` sections | fixed: `okf/document.section()` reads the body; frontmatter keys and L2.acceptance-body removed |
| 7 | review | the bet-new, bet-spec and bet-slice templates also duplicated `acceptance`, `verify_how`, `current`, `expected` and `unchanged` in frontmatter | fixed: removed from the skill templates; sections only |
| 8 | scaffold | records (jira-linked) only land after `kb push`, merging the `rec/` batch branch, and `kb render`; the bet takes SBP-1, the slice SBP-2 | fixed in scaffold (approve_records) |
| 9 | round 1 | in the eval sandbox `t0` (not on PATH) and git (`/usr/bin/git` is the Xcode shim, Xcode unreadable) never ran, so 11 of 17 cases failed on environment, not skills | fixed: plugin hooks go through `hooks/t0-hook.sh`, which finds a workspace-pinned `.t0/bin/t0` and exports it via `CLAUDE_ENV_FILE`; eval workspaces ship a relocated git in `.t0/git` |
| 10 | round 1 | the scaffold ran `git config --global` as the real user and overwrote the global identity | fixed: identity restored (Tuba, hotmail); scaffold sets identity per repo only |
| 11 | round 1b | `t0 slice start` writes upstream config into `.git/config` (sandbox forbids; also needless) | fixed |
| 12 | round 1b | redactor keeps a "fora do registro" utterance; the agent rightly stopped | fixed |
| 13 | round 1b | `t0` loses the KB when the agent cds outside the workspace | fixed: hook exports T0_KB; KB.workspace() finds the workspace from anywhere |
| 14 | round 1b | idea-capture and the rapida route block on 3 questions the request already answers | fixed: idea-capture infers fields, asks at most 1; rapida goes straight to `t0 new bet --track rapida "texto"` |
| 15 | round 1b | slice-build chains slice-verify + an audit reviewer ($2.96 per build) | fixed: slice-build ends at the draft PR; audit reviewer only on Tier 2 |
| 16 | round 1b | no rule for "draft PR" on product repos without a forge; harness-fix gave up | fixed: one no-forge rule in t0 non-negotiables, referenced by slice-build, harness-fix, verify-setup |
| 17 | round 1b | dev-tooling pod had no Bet Owner, so bet-new rightly asked who approves | fixed in seed |
| 18 | round 1b | graders: bet-slice single-turn could not pass an approval loop; no-raw-cat regex hit a head on another file; slice-build/grill judges stricter than the method | fixed in cases |

## Round 2 (12/17 pass, $9.15)

| # | Found by | Issue | Status |
|---|---|---|---|
| 19 | bet-new-aposta | bet-new asked 7 confirmations, `decision_by` included, though `t0 gate aposta` derives approvers and the PR approval is the decision | fixed: proposes and writes fields; `t0 new bet` fills `decision_by` from the pod Bet Owner |
| 20 | architect-checkpoint | architect refused with no spec, and asked before the reversible `t0 bet use` | fixed |
| 21 | several | agents call `t0 kb find "texto"` positionally | fixed |
| 22 | ritual-daily-time | the digest printed raw source specs (`forge:merged since=…`) | fixed |
| 23 | harness-fix | the past mistake only existed as a GitHub link, so the check could not be proved | fixed in scaffold: real bad commit in history, linked as occurrence |
| 24 | graders | not-on-main matched `git merge-base`; Read on plugin references was not granted | fixed: tighter regex; `--allow-tools` adds Read |

## Round 3 (2 runs per case; 7/17 pass both, $25.23)

| # | Found by | Issue | Status |
|---|---|---|---|
| 25 | judge | default haiku judge failed several correct runs (route-no-slice, slice-verify caught the planted defect, harness-health refusal) | fixed: `--judge-model opus` (user rule: no sonnet for judges) |
| 26 | architect-checkpoint | arena runners wrote full prototypes for a small decision: about $3 per run | fixed: 2 design-only candidates by default; worktrees only for code depth |
| 27 | ritual-transcript | close asked 3 confirmations; the method says extracted items enter unverified | fixed |
| 28 | prototype-verdict | agent tried `git push` on the proto branch | fixed |
| 29 | graders | draft-only matched text inside a heredoc; not-on-main forbade any push; bet-slice judged only the final message; used-t0 depends on slash routing in -p mode | fixed in cases |

## Round 4 (2 runs, Opus judge; 15/17 pass both, $24.55)

| # | Found by | Issue | Status |
|---|---|---|---|
| 30 | ritual-transcript | `ritual close` refuses an unowned blocker, so a transcript close stops to ask | fixed: unowned blockers stored as unassigned and listed in the daily-time digest |
| 31 | slice-build | one run still tried `git push` with no forge | fixed: forge check (gh repo view + push URL) before any push in slice-build, harness-fix, verify-setup |
| 32 | ritual-transcript | no-raw-cat matched `cat > file <<EOF` heredocs | fixed in case |
| 33 | cost | architect (arena, 2 design runners) about $2.50 to $3 per run; verify-setup about $2 to $3 (one-off per repo) | wontfix for now: architect only on Tier 2 or cross-boundary |

## Round 5 (21 cases incl. demo, retro, kill, swarm; 17/21 pass both, $22.30)

| # | Found by | Issue | Status |
|---|---|---|---|
| 34 | architect-checkpoint | stopped as "KB indisponível" when the t0-kb MCP was not loaded, though `t0 kb` and `kb/` had the same facts | fixed: MCP, then `t0 kb`, then `kb/` files; stop only when all three fail |
| 35 | swarm-coverage | the verifier refused to run code without a `verify-<app>` skill, so every cell came back BLOCKED | fixed |
| 36 | ritual-retro | close blocked asking who owns a decision that clearly belongs to a role | fixed |
| 37 | bet-kill | the grader expected an immediate kill; the kill rightly waits as a KB branch for the Bet Owner | fixed in case |

## Round 6 (21 cases, 2 runs each, Opus judge): 21/21 pass both runs, $28.86. Loop stopped.

## Round 7 (21 cases, 1 run, kept workspaces; 21/21 pass, $14.58)

| # | Found by | Issue | Status |
|---|---|---|---|
| 38 | unified KB (`kb check` over all cases) | slice-verify passed `--set generated=...` with a space-separated date; `t0 new` wrote it, and `t0 new --help` listed `generated` as obrigatória | fixed: `--set` refuses t0-owned keys (`T0_KEYS`, incl. `generated`) and checks each value's kind; help marks them "o t0 escreve". Graders still do not run `kb check` on agent branches |
