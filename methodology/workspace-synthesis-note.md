# Workspace pattern: synthesis note

Arena B (multi-repo workspace + KB as context). Output: `methodology/workspace-pattern.md` and `methodology/workspace-summary.md`.

**Base.** Candidate 1. Its floor is a generated root `AGENTS.md` that all three tools read natively. Write-back uses three lanes: add-only uniquely named records, reviewed knowledge PRs with CODEOWNERS, and derived files with one serialized writer. No hosted service on day one.

**Judge verdict.** Cross-judge totals: C1 28, C2 21. C1 won on write-back safety with 10 concurrent writers (W4) and least machinery (W5); C2 won on workspace ergonomics and the manifest-as-concept idea.

## Grafts from candidate 2

1. Default is one long-lived product workspace `~/ws/<product>/{kb,<repo>...}` with normal clones. C1's per-bet worktree folders became opt-in (`t0 bet start <BET> --isolate`). Isolated workspaces sit beside the main one (`~/ws/<p>@<BET>/`), not inside it, so the main `AGENTS.md` never loads as an ancestor (that would mean two cards).
2. Manifest as an OKF concept, `/products/<p>/workspace.md`, `type: Workspace`, data under `workspace:` (schema, product, jira_project, forge, default_branch, repos[{name,url,role,kind,optional,tier,depends_on}], groups). Reviewed in the knowledge lane.
3. Bet directory named by id only. Per the coordinator's correction, the id is the KB-native `BET-NNN`, not the Jira key.
4. Launch ergonomics. `.t0/env.sh` sets `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` for Copilot CLI. Kiro `.kiro/steering/t0.md` uses `inclusion: always` with `#[[file:.t0/context.md]]`. **Adjusted:** `.t0/context.md` holds the freshness delta (one line when current, ≤3,000 chars when stale), not a second copy of the card. Kiro already always-includes root `AGENTS.md`, so including the full card would load it twice.
5. Guardrails. Code-generation skills refuse to write code without a resolved bet (ritual skills exempt). A Claude `UserPromptSubmit` hook warns when the prompt names another bet's Jira key.
6. `changeset.md` shape `changes: [{repo, story, pr, order, state, sha}]` + `tested_together`. It is derived by `kb-render` from records, never hand-edited.

## Fixes applied

- Cross-repo credential. `t0 pr check` reads change-set state only from the KB (`main` plus pending bot records in `rec/bot/*`) with a read-scoped token. It never calls other product repos' APIs. `repository_dispatch` was dropped. Re-runs come from a 15-minute scheduled workflow and `workflow_dispatch` in the repo itself. The KB-writer App, installed only on `t0-kb`, is the one cross-repo credential. It mints downscoped tokens (verify).
- Stale card double load. Only `t0 ws sync`, `t0 bet start|use` and ritual commands rewrite `AGENTS.md`. Session-start hooks inject a ≤3,000-char delta only when a KB commit touching the bet or the manifest is newer than the card stamp. The budget table sums to 24,800 chars worst case, and every hook value stays under the 10,000-char cap.
- Marked (verificar): cloud-agent stdio MCP after setup steps, Copilot CLI and Kiro hook stdout as context, auto-merge of record PRs. The fallback is an hourly batch PR approved by the Flow Steward rotation.
- Absolute paths only in `permissions.additionalDirectories`.
- VS Code: single-root workspace folder by default. The committed per-repo `AGENTS.md` block is the fallback.

## Aligned to methodology.md (coordinator correction)

- Layout: `/products/<p>/bets/BET-NNN/{bet.md,spec.md,plan.md,slices/NN-slug.md,log.md}`. Jira keys live in `jira:` on `bet.md` and the slices. Branch `bet/BET-NNN/<STORY>-<slug>`. Trailers `Bet:`, `Story:`, `Jira-Feature:`.
- One slice = one repo = one PR, matching the Slice type's single `repo`. The change set is the bet's slice PRs.
- `t0 log` emits a `Step` record and `log.md` is rendered from them. Slice `state`/`pr`/`audit` and the write-once `jira:` keys are derived keys owned by `kb-render`. This keeps every concurrent lane free of shared hand-edited files.
- `t0 setup` keeps its methodology meaning (product repo setup). Machine bootstrap is `t0 install --user`.
- **Open item for methodology.md (not edited):** §10 `slice-build` says branch `<KEY>-slug`. It should read `bet/BET-NNN/<KEY>-slug`. §5.4 says `t0 log` and the CI gates write `log.md` and slice keys directly. Under this pattern they emit records and `kb-render` applies them.

## Rejected

- C2 lane 1 (direct push to `main` with `merge=union`, the hidden `kb/.journal` worktree, `tasks.md` checkbox state). It puts shared hand-edited files on the concurrent path and has no check before landing.
- C2 hosted HTTP `t0-kb` server with `COPILOT_MCP_KB_TOKEN`. It is a service needing security review on day one. A local stdio server plus a read-only `.kb/` checkout covers cloud and CI.
- C2 multi-root `.code-workspace` as the default (undocumented Copilot discovery). C2 per-repo committed adapter files (`.mcp.json`, `.github/hooks`, `.kiro/settings`) in every repo.
- C2's `log.md` "most recent entry" bet guess. Resolving the wrong bet does more harm than resolving none.
- C1 read-only base clones under `repos/` with per-bet folders as the default. C1 `repository_dispatch` re-runs. C1 `Read(~/t0/**)` with a tilde path. C1 rewriting `AGENTS.md` at session start.
- C1 `prepare-commit-msg` template per worktree. Skills add commit trailers instead.
