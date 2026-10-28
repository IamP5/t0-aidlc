---
type: Research
title: "Agent-side mechanics: keeping an OKF KB in Claude Code context across many repos"
description: How Claude Code (v2.1.311) can load a separate OKF knowledge-base repo into every session, ritual work and code work in 5-6 product repos alike. Covers --add-dir, additionalDirectories, CLAUDE.md imports, plugin hooks and userConfig, MCP, worktrees and parent-folder launches, plus context-budget numbers and how other tools handle multi-repo context. Ends with mechanisms ranked by friction and reliability.
tags: [claude-code, multi-repo, agent-context, okf, plugin, hooks, mcp, research]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-27T00:00:00Z }
sources:
  - id: cc-memory
    resource: https://code.claude.com/docs/en/memory
    title: Claude Code docs, How Claude remembers your project (CLAUDE.md, imports, rules, AGENTS.md)
  - id: cc-permissions
    resource: https://code.claude.com/docs/en/permissions
    title: Claude Code docs, Permissions (working directories, additional directories)
  - id: cc-large
    resource: https://code.claude.com/docs/en/large-codebases
    title: Claude Code docs, Set up Claude Code in a monorepo or large codebase
  - id: cc-skills
    resource: https://code.claude.com/docs/en/skills
    title: Claude Code docs, Skills
  - id: cc-hooks
    resource: https://code.claude.com/docs/en/hooks
    title: Claude Code docs, Hooks reference
  - id: cc-plugin-ref
    resource: https://code.claude.com/docs/en/plugins-reference
    title: Claude Code docs, Plugin manifest reference (userConfig)
  - id: cc-settings-ref
    resource: https://code.claude.com/docs/en/settings-reference
    title: Claude Code docs, Settings reference (pluginConfigs)
  - id: cc-mcp
    resource: https://code.claude.com/docs/en/mcp
    title: Claude Code docs, MCP (resources, tool search, roots)
  - id: cc-context
    resource: https://code.claude.com/docs/en/context-window
    title: Claude Code docs, Context window (what survives compaction)
  - id: cc-worktrees
    resource: https://code.claude.com/docs/en/worktrees
    title: Claude Code docs, Worktrees
  - id: cc-subagents
    resource: https://code.claude.com/docs/en/sub-agents
    title: Claude Code docs, Subagents (what loads at startup)
  - id: cc-env
    resource: https://code.claude.com/docs/en/env-vars
    title: Claude Code docs, Environment variables
  - id: cc-cli
    resource: https://code.claude.com/docs/en/cli-reference
    title: Claude Code docs, CLI reference
  - id: anthropic-ctx
    resource: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    title: Anthropic Engineering, Effective context engineering for AI agents
  - id: codex-agents
    resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: OpenAI Codex, Custom instructions with AGENTS.md
  - id: vscode-instr
    resource: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
    title: VS Code, Copilot custom instructions
  - id: augment-ws
    resource: https://docs.augmentcode.com/setup-augment/workspace-context-vscode
    title: Augment Code, Workspace context
  - id: augment-mcp
    resource: https://www.augmentcode.com/blog/context-engine-mcp-now-live
    title: Augment, Context Engine MCP launch post
  - id: sourcegraph-mcp
    resource: https://sourcegraph.com/mcp
    title: Sourcegraph MCP
---

# Agent-side mechanics: the KB in every Claude Code session

**Scope.** This is slice 1 of 2: the agent side, meaning how Claude Code and similar tools pull a separate KB repo into context. Repo topology (submodules, manifests, monorepo) is covered in `workspace-topology.md`.

**Provenance tags.**
- **(docs: id)**: from a source listed in the frontmatter. The Claude Code docs were fetched as raw `.md` on 2026-10-27.
- **(local CLI check)**: verified on this machine with Claude Code **2.1.311**, using `claude -p --model haiku` against throwaway fixtures in the scratchpad. The fixtures were a `ws/` parent folder holding `kb/` and a git repo `repoA/`, each file carrying a unique codeword, and the model was asked which codewords it had in context.
- **(inferred)**: my reading or recommendation.

---

## 0. TL;DR

1. **`--add-dir` and `additionalDirectories` are not the same thing.** The `permissions.additionalDirectories` setting grants **file access only**. It never loads CLAUDE.md, rules or skills. (docs: cc-permissions, cc-large; local CLI check) The `--add-dir` flag and the `/add-dir` command load the added dir's **skills, commands and agents**, but its **CLAUDE.md and rules load only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`**. (docs: cc-memory, cc-permissions; local CLI check)
2. **External `@imports` in a product repo's CLAUDE.md need a one-time interactive approval per project.** In `-p` (CI or headless) runs they are **silently skipped** until someone approves them. (docs: cc-memory; local CLI check) Imports in `~/.claude/CLAUDE.md` load with no dialog. (docs: cc-memory)
3. **The most reliable "always in context" channel is a plugin `SessionStart` hook** that reads a `userConfig` option of `type: "directory"` (the KB path) and returns `additionalContext`. It works in any repo and any launch mode, re-runs on `compact`, and is capped at 10,000 chars per value. (docs: cc-hooks, cc-plugin-ref; local CLI check)
4. **Progressive disclosure fits the budget.** Inject the KB root `index.md` plus the active bet's `index.md` (a few KB) at session start, and let skills or Read pull everything else on demand. Do not inline the bundle, and do not chain `@imports` (imports don't save tokens). (docs: cc-memory, anthropic-ctx)

---

## 1. Claude Code multi-directory mechanics

### 1.1 Three ways to add a directory, and what each loads

| Mechanism | File access | Skills / commands / agents | CLAUDE.md + `.claude/rules` | Settings from that dir |
|---|---|---|---|---|
| `--add-dir <path>` (launch) | yes | **yes** (skills live-reload; commands and agents need a restart) | **only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`** | only `enabledPlugins` and `extraKnownMarketplaces` |
| `/add-dir <path>` (mid-session) | yes | yes | same env-var rule | same |
| `permissions.additionalDirectories` in settings.json | yes | **never** | **never** | none |

Sources: (docs: cc-permissions §"Additional directories grant file access, not configuration"; cc-large §"Grant access across packages or repositories"; cc-skills §"Skills from additional directories")

Local CLI checks (fixtures: KB `CLAUDE.md` = `PELICAN-KB-CLAUDEMD`, KB skill description = `HERON-SKILL`):
- `claude -p … --add-dir ../kb` gave `CRANE-PARENT, FINCH-REPO, HERON-SKILL`. The KB **skill loaded and the KB CLAUDE.md did not**. (local CLI check)
- With `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` added, the output also included `PELICAN-KB-CLAUDEMD`. (local CLI check)
- `.claude/settings.json` with `permissions.additionalDirectories: ["../kb"]` plus the env var: in `-p` mode on a never-trusted folder the CLI printed *"Ignoring 1 permissions.additionalDirectories entry … this workspace has not been trusted"*. Neither the KB CLAUDE.md nor the skill loaded. **Project-scope `additionalDirectories` waits for workspace trust.** (local CLI check; consistent with docs: cc-settings "The key waits for trust")
- **Gotcha:** `--add-dir` is variadic. `claude -p --add-dir ../kb "prompt"` swallows the prompt as a second directory and fails with *"Input must be provided…"*. Put the prompt first, or end the list with `--`. (local CLI check)

Other facts:
- The env var can be made permanent in the `env` block of `~/.claude/settings.json`. (docs: cc-memory)
- With the env var, Claude loads `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` and `CLAUDE.local.md` from the added dir. An `AGENTS.md` in an added dir does **not** load, even with the env var. (docs: cc-memory, "Where AGENTS.md differs")
- Skills from `--add-dir` directories still load under `--bare` / `CLAUDE_CODE_SIMPLE`, which skips nearly everything else. (docs: cc-cli, cc-env) This is useful for lean CI or headless runs. (inferred)
- If a skill name in an added dir clashes with a project or user skill, it gets a prefix such as `/kb:verify`. (docs: cc-skills)
- `DirectoryAdded` hook: fires after `/add-dir` (not after `--add-dir`, which `SessionStart` covers). (docs: cc-hooks)
- `/cd <path>` moves the session's primary directory. It loads the new dir's CLAUDE.md, settings, hooks, `.mcp.json` and skills, and **keeps** `--add-dir` / `/add-dir` directories. (docs: cc-permissions) For a cross-repo session, this means the KB stays attached when you hop between product repos. (inferred)
- Agent SDK: TypeScript `additionalDirectories` / Python `add_dirs` behave like `--add-dir`, not like the settings key of the same name. (docs: cc-permissions)
- The MCP `roots/list` reply covers the launch dir plus every additional working dir. (docs: cc-mcp)

### 1.2 CLAUDE.md loading and `@path` imports

- **Ancestors load at launch, and nested files load on demand.** CLAUDE.md and CLAUDE.local.md from cwd **and every parent** load at launch, concatenated root-first. Subdirectory CLAUDE.md files load the first time Claude reads or edits a file there. (docs: cc-memory) Local check: launching in `ws/repoA` loaded `ws/CLAUDE.md` (`CRANE-PARENT`) and `repoA/CLAUDE.md`. Launching in `ws/` loaded only `CRANE-PARENT`, because child repo files load lazily. (local CLI check)
- **Import syntax.** `@path` takes relative paths (resolved from the importing file) or absolute paths. `@~/…` works (the docs example is `@~/.claude/my-project-instructions.md`). Imports can recurse up to **4 hops**. Paths with spaces need backslash escapes, and imports inside code spans or fences are ignored. (docs: cc-memory)
- **Imports don't reduce cost.** *"Imports … don't reduce its context cost, because imported files load together with the CLAUDE.md that imports them."* Keep each CLAUDE.md under about 200 lines. (docs: cc-memory)
- **External imports need approval.** An import that resolves outside the working dir is "external". The first interactive session shows an approval dialog. If the user declines, the imports stay disabled and the dialog does not come back. (docs: cc-memory) Local checks:
  - `@../kb/index.md` and `@/abs/…/kb/index.md` in `repoA/CLAUDE.md` were **silently not loaded under `claude -p`**, with no warning. The result was the same even with `--add-dir ../kb`. (local CLI check)
  - `~/.claude.json` stores per-project `hasClaudeMdExternalIncludesApproved` and `hasClaudeMdExternalIncludesWarningShown` flags (124 project entries on this machine). (local CLI check)
  - **Consequence:** an `@../team-kb/index.md` line committed to each product repo works for a dev only after they approve it once per repo per machine. In fresh CI runners and cloud sessions it fails silently. (inferred)
- **User-scope imports skip the dialog.** `~/.claude/CLAUDE.md` and `~/.claude/rules/` are trusted, so their imports load with no dialog. The exception is Cowork desktop sessions, which skip user-scope imports outside the working dir. (docs: cc-memory) A per-dev `@~/kb/index.md` line in `~/.claude/CLAUDE.md` is therefore zero-dialog, but it depends on every dev cloning the KB to the same path. (inferred)
- **Rules via symlink.** A `.claude/rules/` symlink can point at a shared folder. Targets outside the working dir count as external imports (same approval), and once approved only the rules **without** `paths:` load. (docs: cc-memory)
- **Rules scoped by path.** `.claude/rules/*.md` with `paths:` frontmatter load only when a matching file is read or edited. They are summarized away on compaction. (docs: cc-memory, cc-context)
- **Managed CLAUDE.md.** A managed file (`/Library/Application Support/ClaudeCode/CLAUDE.md`) or the `claudeMd` key in managed settings applies to every user and cannot be excluded. (docs: cc-memory) This is a candidate for a 5-line org-wide pointer such as "the KB lives at …; read its index first". (inferred)
- **AGENTS.md.** Claude Code ≥2.1.277 reads `AGENTS.md` when no CLAUDE.md exists in cwd or its ancestors. The `instructionFiles` option `claude-md-and-agents-md` reads both. (docs: cc-memory) Product repos that also serve Codex and Copilot can keep `AGENTS.md` as the single file. (inferred)

### 1.3 Project memory vs user memory

| Layer | Location | Shared via | KB role (inferred) |
|---|---|---|---|
| Managed | `/Library/Application Support/ClaudeCode/CLAUDE.md` or `claudeMd` in managed settings | MDM / IT | Org-wide pointer to the KB, cannot be disabled |
| User | `~/.claude/CLAUDE.md`, `~/.claude/rules/` | per dev | `@~/kb/index.md` with no dialog, but path discipline is needed |
| Project | `./CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/` | git | Product-repo rules plus which bet or product this repo belongs to |
| Local | `./CLAUDE.local.md` | gitignored | Personal |
| Auto memory | per repo, shared across worktrees; first 200 lines / 25 KB loaded | machine-local | Not a team KB channel |

Sources: (docs: cc-memory)

### 1.4 Plugins: SessionStart `additionalContext` and `userConfig`

- **`SessionStart` hook.** Matchers are `startup`, `resume`, `clear`, `compact` and `fork`. Hooks return `hookSpecificOutput.additionalContext`, and plain stdout is also added as context. The text arrives as a system reminder before the first prompt, and Claude's first response waits for the hooks. (docs: cc-hooks)
- **Size cap: 10,000 characters per value.** Anything longer is written to a file, and Claude gets the path plus a 2,000-char preview, with no instruction to read it. There is no setting to raise the cap. (docs: cc-hooks)
- **Compaction.** Hook context added earlier is summarized away on compaction, but a `SessionStart` hook matching `compact` re-runs and re-injects. (docs: cc-context) **Use `startup|resume|clear|compact`.** (inferred)
- **Subagents.** `SubagentStart` can also return `additionalContext`. (docs: cc-hooks) Built-in Explore and Plan start **without** CLAUDE.md, and custom subagents load it unless `omitClaudeMd: true`. (docs: cc-subagents) A `SubagentStart` hook is the way to give KB context to Explore and Plan. (inferred)
- **Mid-session injection.** `UserPromptSubmit` can add `additionalContext` per prompt. (docs: cc-hooks) It could carry a "current bet" pointer when the prompt mentions a Jira key. (inferred)
- **No MCP from SessionStart at launch.** `SessionStart` at launch fires before MCP servers connect, so `mcp_tool` hooks are skipped there. Use `command` hooks. (docs: cc-hooks)
- **`userConfig` types: `string`, `number`, `boolean`, `directory`, `file`.** `directory` is the right type for "path to your KB clone". The user is prompted when the plugin is enabled, and the value is also editable in `/config`. Non-sensitive values are stored in `pluginConfigs` in user settings. (docs: cc-plugin-ref, cc-settings-ref)
- **How the value reaches each component.** It is exported to hooks as `CLAUDE_PLUGIN_OPTION_<KEY>` and substituted as `${user_config.KEY}` in MCP config, LSP config, exec-form hook `args`, and skill and agent content. Shell-form hooks must read the env var instead, because `${user_config.*}` is rejected in shell-form commands. (docs: cc-plugin-ref)
- **Local check (plugin loaded via `--plugin-dir`).** The plugin declared `userConfig.kb_path` (`type: directory`) and a SessionStart hook that prints `$CLAUDE_PLUGIN_OPTION_KB_PATH` and the first 2,000 chars of `$KB/index.md`:
  - **With nothing saved, the hook saw `unset`.** The `default` in the manifest was **not** applied under `-p`. (local CLI check) The plugin must handle a missing value (fallback paths, or a message telling the user to run `/config`). (inferred)
  - **With the value saved, injection worked.** After `--settings '{"pluginConfigs":{"kbplug@inline":{"options":{"kb_path":"…"}}}}'` (plain `"kbplug"` also worked), the hook got the path and the KB `index.md` codeword reached context. (local CLI check)
  - `${user_config.kb_path}` in a **skill `description`** was **not** substituted. The listing showed the literal placeholder. Body substitution at invocation (per docs) was not verified. (local CLI check) Don't rely on user_config inside descriptions. (inferred)
- **Org rollout.** Plugins can be pre-installed and required for everyone through managed settings. (docs: cc-large → plugins/org) `enabledPlugins` and `extraKnownMarketplaces` are the two settings keys honored even from `--add-dir` dirs. (docs: cc-permissions)

### 1.5 MCP server exposing the KB

- **Resources.** Resources appear in `@` autocomplete as `@server:protocol://path`, are fetched as attachments when referenced, and Claude Code auto-provides list and read tools for them. (docs: cc-mcp)
- **Tool search is on by default.** Only tool names and **server instructions** load at start, and tool definitions are deferred. Server instructions and the descriptions of upfront tools are cut at **4,096 chars**. (docs: cc-mcp)
- **Server instructions as the context channel.** A "kb" MCP server can put a short "read kb_index first; bets live under …" text in its instructions, so it is present every session at near-zero cost. (inferred)
- **What MCP adds beyond files.** Search (grep or embedding), `get_bet(jira_key)`, write-backs (append to `log.md`, create an ADR) with schema validation, and access from Claude.ai, Desktop, the web and CI where no local clone exists. (inferred) Anthropic's own large-codebase guide recommends exposing an existing code-search or RAG index as MCP. (docs: cc-large)
- **Packaging.** A plugin can ship the MCP server and pass the KB path in through `${user_config.kb_path}`. (docs: cc-plugin-ref)
- **Off-the-shelf option.** The generic filesystem MCP works, but it duplicates Read/Grep and adds nothing over `--add-dir` locally. (inferred)

### 1.6 Worktrees and parent-folder launches

- **Worktrees are per repo.** `claude -w <name>` creates `.claude/worktrees/<name>/` in **one** git repo, branched from the default branch unless `worktree.baseRef: "head"`. (docs: cc-worktrees) Launched from a non-git parent folder it fails with *"Can only use --worktree in a git repository … Configure a WorktreeCreate hook to use --worktree with other VCS systems."* (local CLI check) A multi-repo "bet worktree" therefore needs either a `WorktreeCreate` hook that runs `git worktree add` in each product repo, or a manifest tool. (inferred)
- **Worktrees and `--add-dir`.** Inside a worktree the working dir is the worktree root, so a per-area `additionalDirectories` from the parent settings no longer applies. (docs: cc-large) `--add-dir` directories survive `/cd` and EnterWorktree moves. (docs: cc-permissions) Project-scope plugins installed from the main checkout also load in its worktrees. (docs: cc-worktrees)
- **Path-scoped skills don't follow added worktrees.** Skills with `paths:` do not activate for files in a sibling worktree added with `/add-dir`. (docs: cc-skills)
- **Parent folder with several clones** (`~/work/<product>/{kb, svc-a, svc-b, …}`):
  - It works for **CLAUDE.md**: a parent `CLAUDE.md` loads as an ancestor in every child session, and imports from the parent into `kb/` are "inside the working dir" only when launched from the parent. (docs: cc-memory; local CLI check for ancestor loading)
  - **`.claude/settings.json` has no parent fallback.** Hooks and settings load only from the cwd's `.claude/`. A session launched in the parent misses each repo's settings and hooks, and one launched in a child misses the parent's. (docs: cc-permissions, cc-large)
  - Launched from the parent: child CLAUDE.md files load lazily, `-w` fails (not a git repo), and the git status snapshot is missing. (local CLI check; inferred)

---

## 2. Context budget: "always in context" without loading the whole bundle

### 2.1 Numbers (docs unless tagged)

| Item | Budget / cap |
|---|---|
| CLAUDE.md guidance | under ~200 lines per file; imports add their full size (cc-memory) |
| Auto memory | first 200 lines or 25 KB (cc-memory) |
| Hook `additionalContext` / stdout | 10,000 chars per value, then spilled to a file with a 2,000-char preview (cc-hooks) |
| Skill listing | about **1% of the context window** in total; each `description` + `when_to_use` truncated at 1,536 chars; descriptions get dropped when over budget (cc-skills) |
| Invoked skill bodies after compaction | 5,000 tokens per skill, 25,000 total, oldest dropped (cc-context, cc-skills) |
| Files re-read after compaction | up to 5 most recent; a file over 5,000 tokens becomes a path reference only (cc-context) |
| MCP server instructions / upfront tool description | 4,096 chars (cc-mcp) |
| Codex AGENTS.md chain | 32 KiB `project_doc_max_bytes` (codex-agents) |
| Rough conversion | ~4 chars per token for English markdown, so 10,000 chars ≈ 2.5k tokens (inferred) |

Context-quality rationale: Anthropic describes an "attention budget" and recommends lightweight identifiers (paths) loaded just in time. In their words, CLAUDE.md is "dropped into context up front" while glob and grep fetch the rest on demand. (docs: anthropic-ctx)

### 2.2 Recommended layering for the OKF bundle (inferred, using the facts above)

1. **Always (around 1-3k tokens).** The SessionStart hook injects:
   - a fixed preamble saying what the KB is and how to use it;
   - the KB root `index.md`, trimmed to a section list with one-line descriptions;
   - the **active bet's** `index.md` (intent, spec, plan and task links), resolved from (a) the branch name or Jira key, (b) a `.kb-bet` or `kb:` field in the product repo's CLAUDE.md, or (c) the most recent `log.md` entry;
   - the glossary headwords only.

   Keep the total under 10,000 chars. Re-run on `compact`.
2. **On demand via skills.** `kb-read`, `kb-write`, `ritual-<name>`, `spec`, `adr` and similar. Skill descriptions are always listed (within the 1% budget) and bodies load only when invoked. Skills instruct "read `index.md` first, then follow links", the OKF progressive-disclosure path.
3. **On demand via Read/Grep.** This needs file access to the KB: `--add-dir`, user-scope `additionalDirectories`, or `Read(...)` allow rules. Reads outside working and additional dirs prompt. (docs: cc-permissions table "Read-only … No [prompt], within the working directory and additional directories")
4. **Path-scoped rules in product repos** for code conventions only. The KB is not a code-path concern.
5. **Never** `@import` the whole bundle, and never inline more than the index in CLAUDE.md.

---

## 3. How other tools and teams handle multi-repo AI context

| Tool | Multi-repo mechanism | Instruction files across roots | Source |
|---|---|---|---|
| **Cursor** | Multi-root workspaces (`.code-workspace`) | Mixed. Forum reports say early versions read only the first root's rules, later ones read each root's `.cursor/rules`, `alwaysApply` rules are duplicated across roots and worktrees, and path rules are unreliable. A third-party guide advises putting must-apply rules at user or workspace scope. | forum.cursor.com threads [158433](https://forum.cursor.com/t/cursor-folders-in-multi-root-workspaces/158433/4), [151165](https://forum.cursor.com/t/bug-report-always-applied-rules-duplicated-across-workspace-roots-in-multi-root-workspaces/151165), [168224](https://forum.cursor.com/t/apply-to-specific-files-rules-are-not-reliably-included-for-matching-files-in-multi-root-workspaces/168224); [agentpatterns.ai](https://www.agentpatterns.ai/tools/cursor/multi-root-workspaces/) (community; not confirmed in official docs) |
| **VS Code + Copilot** | Multi-root `.code-workspace` | Reads `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (`applyTo`), root `AGENTS.md` (`chat.useAgentsMdFile`, on by default), nested AGENTS.md (experimental, off), `CLAUDE.md` (`chat.useClaudeMdFile`), user `~/.copilot/instructions`, org-level instructions, and `chat.instructionsFilesLocations` for extra folders. The docs say nothing explicit about multi-root, and a community thread reports gaps. | (docs: vscode-instr); [GitHub discussion 155450](https://github.com/orgs/community/discussions/155450) |
| **Codex** | `--cd`, `--add-dir` (local CLI check: `codex --help` lists both) | Global `~/.codex/AGENTS.md`, then git root → cwd, one file per dir (`AGENTS.override.md` > `AGENTS.md` > fallbacks), capped at 32 KiB. The docs don't say anything about loading AGENTS.md from added dirs. | (docs: codex-agents) |
| **Augment** | "Workspace context": add other repos as source folders, which are indexed semantically. The Context Engine is also exposed as an MCP (claimed usable from Claude Code). | n/a (index-based) | (docs: augment-ws, augment-mcp), vendor claims unverified |
| **Sourcegraph / Amp** | Cross-repo code search through Sourcegraph MCP. Amp reportedly reads AGENTS.md up to `$HOME` with `@`-mentions, and its "Librarian" subagent searches across repos. | AGENTS.md hierarchy | (docs: sourcegraph-mcp); third-party [blog](https://codex.danielvaughan.com/2026/04/07/sourcegraph-amp-multi-repo-orchestrator/) (unverified) |
| **"Meta-repo" pattern** | A hub repo with an AGENTS.md entry point plus a repo registry, with agents launched from the hub | hub AGENTS.md | [seylox blog](https://seylox.github.io/2026/03/05/blog-agents-meta-repo-pattern.html) (community) |
| **Anthropic guidance** | Monorepo: start at the root for cross-package tasks and layer CLAUDE.md. Polyrepo or siblings: `--add-dir` or `additionalDirectories`. When layering stops scaling, move conventions into skills, centrally owned plugins (managed install) and MCP. Use a SessionStart hook to point people at the right plugin. Plan cross-package changes in plan mode, because the plan file is re-injected after compaction. | CLAUDE.md layering | (docs: cc-large) |

The common lesson (inferred) is that every tool's per-root instruction discovery is fragile in multi-root setups. Teams that need "always" context put it in a **user/org/plugin-scoped** channel or a **hub** launch point, not in per-root files.

---

## 4. Mechanisms ranked

Friction means setup plus daily effort for about 10 devs. Reliability means the KB actually reaches context in every mode: interactive, `-p`/CI, IDE, Desktop, subagents, after compaction, and inside worktrees. All rankings are inferred from the facts above.

| # | Mechanism | Friction | Reliability | Notes |
|---|---|---|---|---|
| 1 | **Internal plugin: SessionStart (`startup\|resume\|clear\|compact`) + SubagentStart hooks inject root index + active-bet index from `userConfig.kb_path` (type `directory`)** | Low: one managed or marketplace install, one path prompt | **High**: works in any repo, cwd, launch mode and worktree; survives compaction; 10k-char cap | Must handle a missing value (default not applied in `-p`, per local check). Pair with #2 for the read path. Can `git -C $KB pull --ff-only` with a timeout for freshness. |
| 2 | **Plugin skills for KB read, write and rituals** (bodies read the KB on demand) | Low (same plugin) | High for discovery (listing always present); invocation is model-driven or `/`-driven | Don't put `${user_config}` in descriptions (local check). Reads still need file access, see #3. |
| 3 | **KB file access**: user-scope `permissions.additionalDirectories` or `Read(<kb>/**)` allow rule | Low (one user-settings line, writable by plugin setup docs or managed settings) | High for access; loads nothing by itself | Project-scope entries wait for workspace trust (local check). |
| 4 | **`claude --add-dir $KB` launcher alias + `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`** in user `env` | Medium: depends on launcher discipline; IDE, Desktop or web launches may skip it | Medium-high when used: KB CLAUDE.md, rules **and** skills load and survive `/cd` | A good fit if the KB repo ships its own `.claude/skills/` (KB-owned skills, no plugin release cycle). Watch the variadic-flag gotcha. |
| 5 | **Org pointer in managed CLAUDE.md / `claudeMd`** ("KB at …; use /kb skills") | Medium (IT/MDM) | High for presence, low for content (static text, no bet awareness) | Cheap safety net under #1. |
| 6 | **"kb" MCP server** (resources + `search`/`get_bet`/`append_log` tools + server instructions) | Medium-high (build and run) | High, including no-clone surfaces (Claude.ai, Desktop, cloud, CI) and Jira-joined queries | The only option that serves non-local agents. Server instructions are ≤4,096 chars and always loaded. |
| 7 | **User `~/.claude/CLAUDE.md` with `@~/kb/index.md`** | Low-medium (per-dev, path convention) | Medium: no dialog, but static, root index only, Cowork skips it | Fallback for devs not on the plugin. |
| 8 | **Parent "product workspace" folder** with `CLAUDE.md` importing `kb/` | Medium | Medium-low: per-repo settings/hooks don't apply from the parent; `-w` fails; child CLAUDE.md files load lazily | Good for ritual and spec sessions that aren't code sessions. |
| 9 | **`@../kb/...` imports committed in each product repo** | Medium (per-repo and per-machine approval) | **Low**: silently skipped in `-p`/CI and fresh machines until approved; assumes a sibling layout | Avoid as the primary channel. |

**Suggested stack (inferred):** #1 + #2 + #3 shipped in the internal plugin (pre-installed via managed settings), #5 as the safety net, #4 optional for power users, and #6 when the team needs KB access outside local Claude Code or validated write-backs.

## 5. Open questions / not verified

- Whether `userConfig` `default` applies in interactive sessions when the user dismisses the dialog. Only `-p` was tested, and it was not applied there.
- Whether `~` expansion works in `permissions.additionalDirectories` entries.
- Whether `${user_config.*}` substitution happens in skill **bodies** at invocation. The docs say yes, but only the description was checked locally, and it was not substituted.
- How Claude Code Desktop and IDE-extension launches pass `--add-dir`. The docs suggest the settings and env routes. This needs a check per surface.
- Cursor and Copilot multi-root behavior is based on forum and community sources only.
