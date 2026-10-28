---
type: Research
title: "Multi-agent compatibility: Claude Code, GitHub Copilot, Kiro"
description: What each of the three coding agents reads (instructions, skills, commands, agents, hooks, MCP, plugins, multi-repo), a capability matrix, and a recommended single-source architecture for the AIDLC toolkit and OKF knowledge base.
tags: [toolkit, portability, copilot, kiro, claude-code, research]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-27T00:00:00Z }
---

# Multi-agent compatibility: Claude Code, GitHub Copilot, Kiro

Scope: the AIDLC toolkit (skills forked from mattpocock/skills and pstack, KB access, Jira, rituals) has to work in **Claude Code**, **GitHub Copilot** (VS Code agent mode, Copilot CLI, Copilot cloud/coding agent) and **Kiro** (IDE and kiro-cli). Kiro is used **only as a coding-agent harness**: steering, hooks, MCP, skills, custom agents. Its `.kiro/specs` feature is out of scope. Our bet intent/spec/plan/tasks files in the OKF repo are the only spec system.

Every fact carries a URL, or is marked **(inferred)** when it is my reading or comes from a local test. Docs were checked on 2026-10-27.

---

## 1. Headline findings

1. **AGENTS.md is the one instruction file all three read natively.** Claude Code reads it when no CLAUDE.md exists (v2.1.277+) ([memory](https://code.claude.com/docs/en/memory.md#agents-md)). Copilot reads it in VS Code, the CLI and the cloud agent ([VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions), [CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions), [repo instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)). Kiro always includes it from the workspace root, subdirectories or `~/.kiro/steering/` ([steering](https://kiro.dev/docs/steering/)).
2. **All three support Agent Skills (`SKILL.md`), but each looks in different folders.** Copilot reads `.github/skills`, `.claude/skills` and `.agents/skills` ([GitHub](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)). Claude Code reads `.claude/skills` ([skills](https://code.claude.com/docs/en/skills.md)). Kiro reads only `.kiro/skills` and `~/.kiro/skills` ([Kiro skills](https://kiro.dev/docs/skills/)). So `.claude/skills/` covers Claude and Copilot, and Kiro needs a copy or a plugin.
3. **Plugins now have a cross-vendor core.** **Agent Plugins 1.0** ([agent-plugins.org](https://agent-plugins.org/)) was published on 2026-08-06 by Amazon, Cursor, Microsoft, OpenAI and Vercel, and Anthropic is not a maintainer. It standardises only `plugin.json` at the plugin root, `skills/` and `mcp.json` ([GitHub changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)). Copilot and Kiro powers support it ([Kiro create powers](https://kiro.dev/docs/powers/create/)). Claude Code still needs `.claude-plugin/plugin.json` ([plugins-reference](https://code.claude.com/docs/en/plugins-reference.md)). Copilot also loads Claude-format plugins and `.claude-plugin/marketplace.json` ([Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)). **One plugin directory can carry both manifests** **(inferred)**.
4. **MCP is the only runtime layer all three share** (the same `mcpServers` JSON shape), but each tool reads a different file path. That makes an **MCP server for the KB plus Jira** the right portable runtime for anything dynamic.
5. **Hooks do not port.** Each tool has its own event names and config files. Shell scripts that read event JSON on stdin and exit 2 to block work in all three, so keep the logic in scripts and generate only the thin registration files.
6. **Headless runs exist in all three** (`claude -p`, `copilot -p`, `kiro-cli chat --no-interactive`), so a cross-agent eval is feasible. However, `claude plugin eval` (graders, mocks) is Claude-only, and I found no off-the-shelf eval harness that covers Copilot CLI or kiro-cli.

---

## 2. Per-tool details

### 2.1 Instruction / context files

| | Claude Code | GitHub Copilot | Kiro |
|---|---|---|---|
| Root always-on file | `CLAUDE.md` or `.claude/CLAUDE.md`. `AGENTS.md` is read **instead** when there is no CLAUDE.md or CLAUDE.local.md at or above cwd. Setting `claude-md-and-agents-md` loads both ([memory](https://code.claude.com/docs/en/memory.md#agents-md)) | `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md` and `GEMINI.md` are all read by the CLI ([CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)). The cloud agent accepts AGENTS.md, or a single root CLAUDE.md or GEMINI.md ([repo instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)) | `.kiro/steering/*.md` with `inclusion: always` (the default), plus `AGENTS.md`, which is "always included" ([steering](https://kiro.dev/docs/steering/)) |
| Nested AGENTS.md | Loaded from cwd and its parents at start, and from a subdirectory when Claude reads a file there ([memory](https://code.claude.com/docs/en/memory.md#when-claude-code-reads-agentsmd)) | CLI: repo root, cwd, intermediate directories, and directories on the path of the file being worked on ([CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)). Cloud agent: "nearest AGENTS.md ... takes precedence" ([repo](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)). VS Code: nested files sit behind experimental `chat.useNestedAgentsMdFiles` (off by default) ([VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)) | Workspace root and subdirectories ([steering](https://kiro.dev/docs/steering/)) |
| Path-scoped rules | `.claude/rules/*.md` with `paths:` frontmatter ([VS Code doc on Claude harness](https://code.visualstudio.com/docs/copilot/customization/custom-instructions); [memory](https://code.claude.com/docs/en/memory.md)) | `.github/instructions/**/*.instructions.md` with `applyTo:` globs, optional `excludeAgent: code-review\|cloud-agent` ([repo](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)) | Steering `inclusion: fileMatch` with `fileMatchPattern` (string or array) ([steering](https://kiro.dev/docs/steering/)) |
| On-demand / description-matched | Skills | `.instructions.md` with `description` only, loaded on demand ([VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)) | `inclusion: auto` (needs `name` and `description`). `inclusion: manual` is invoked with `#name` or as a slash command ([steering](https://kiro.dev/docs/steering/)) |
| File includes | `@path` imports, also inside AGENTS.md ([memory](https://code.claude.com/docs/en/memory.md)) | Markdown links and `#file:` in prompt files ([prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)) | `#[[file:path]]`, `#[[file:path:10-20]]`, `#[[folder:path]]` ([steering](https://kiro.dev/docs/steering/)) |
| User-level | `~/.claude/CLAUDE.md`, `~/.claude/rules` | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/**`. Env `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` adds directories for AGENTS.md and `*.instructions.md` ([CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)) | `~/.kiro/steering/` ([steering](https://kiro.dev/docs/steering/)) |

**Traps:**
- If a repo has **both** AGENTS.md and CLAUDE.md, Copilot CLI reads both, so shared content would be injected twice. Claude Code reads only CLAUDE.md by default. **Recommendation: ship AGENTS.md only, with no CLAUDE.md** (inferred from the two docs above). Put Claude-only rules in `.claude/rules/`, which loads alongside AGENTS.md ([memory](https://code.claude.com/docs/en/memory.md#when-claude-code-reads-agentsmd)).
- `CLAUDE.local.md` counts as a CLAUDE.md, so it silently turns off AGENTS.md loading for that developer unless they set `claude-md-and-agents-md` ([memory](https://code.claude.com/docs/en/memory.md#when-claude-code-reads-agentsmd)).
- Kiro custom agents do **not** load steering or skills automatically. You must add `file://.kiro/steering/**/*.md` and `skill://.kiro/skills/*/SKILL.md` to `resources` ([steering](https://kiro.dev/docs/steering/), [skills](https://kiro.dev/docs/skills/)).

### 2.2 Agent Skills (SKILL.md)

| | Claude Code | Copilot | Kiro |
|---|---|---|---|
| Supports open standard | Yes, with extensions ([skills](https://code.claude.com/docs/en/skills.md)) | Yes ([GitHub](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)) | Yes ([Kiro skills](https://kiro.dev/docs/skills/)) |
| Project dirs | `.claude/skills/` in cwd and parents up to the repo root. Nested `<subdir>/.claude/skills` loads when a file there is touched. Dirs added with `--add-dir` load too ([skills](https://code.claude.com/docs/en/skills.md)) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)) | `.kiro/skills/` only ([Kiro skills](https://kiro.dev/docs/skills/)) |
| User dirs | `~/.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/`. VS Code also reads `~/.claude/skills/` ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)) | `~/.kiro/skills/` |
| Slash invocation | `/name`, or `/<plugin>:<skill>` for plugin skills | `/name` in VS Code ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)) | `/name`. `$ARGUMENTS` and `${N}` are substituted in the CLI only ([Kiro skills](https://kiro.dev/docs/skills/)) |
| Portable frontmatter | `name`, `description` (all three) | + `argument-hint`, `user-invocable`, `disable-model-invocation`, `context: fork` (VS Code) | + `license`, `compatibility`, `metadata` |
| Claude-only fields | `allowed-tools`, `model`, `effort`, `agent`, `hooks`, `paths`, `arguments`, `when_to_use` (see [plugin-eval-format.md](./plugin-eval-format.md)). Other tools ignore them **(inferred)** | | |

Name rules shared by Copilot and Kiro: lowercase, digits and hyphens, at most 64 chars, must match the folder name, and the description is at most 1024 chars ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Kiro](https://kiro.dev/docs/skills/)). Claude allows 1536 chars for the description ([plugin-eval-format.md](./plugin-eval-format.md)). **Write descriptions of 1024 chars or less.**

### 2.3 Prompt files / custom slash commands

- **Claude Code:** commands were merged into skills. `.claude/commands/x.md` still works ([skills](https://code.claude.com/docs/en/skills.md)).
- **Copilot (VS Code):** `.github/prompts/*.prompt.md` with frontmatter `name`, `description`, `argument-hint`, `agent`, `model` and `tools`, plus `${input:x}` variables. Prompt files run **only in the Local harness in the Chat view**, and VS Code recommends converting them to skills for other harnesses ([prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)). They are not documented for the CLI.
- **Kiro:** the IDE uses `inclusion: manual` steering, which becomes a `/<filename>` slash command. Manual hooks are legacy ([hook types](https://kiro.dev/docs/hooks/types.md)). Kiro CLI has `~/.kiro/prompts/` (reported by [rulesync README](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/README.md), not verified in Kiro docs).
- **Conclusion:** use **skills as the only slash-command format**. All three expose skills as `/name`.

### 2.4 Custom agents / subagents

| | Claude Code | Copilot | Kiro |
|---|---|---|---|
| Location / format | `.claude/agents/*.md` (frontmatter: name, description, tools, model, ...) | `.github/agents/*.agent.md`, with frontmatter `name`, `description` (required), `target: vscode\|github-copilot`, `tools`, `model`, `disable-model-invocation`, `user-invocable`, `mcp-servers` (ignored in IDEs). `handoffs` is ignored by the cloud agent ([custom agents ref](https://docs.github.com/en/copilot/reference/custom-agents-configuration)) | `.kiro/agents/*.json` (fields `name`, `description`, `prompt` (inline or `file://`), `tools`, `resources`, `hooks`, `mcpServers`, `includeMcpJson`, `model`), or `.md` with frontmatter and a body prompt in CLI V3 / IDE 1.0 ([Kiro agent config](https://kiro.dev/docs/custom-agents/configuration-reference/)) |
| Portability | Low: the tool names differ in each harness (Claude `Bash`/`Read`, Copilot `shell`/`view`, Kiro `shell`/`read`) **(inferred from the docs above and [hooks ref](https://docs.github.com/en/copilot/reference/hooks-configuration))** | | |

**Recommendation:** keep subagent definitions to a minimum and generate them per tool. Put the behaviour in skills.

### 2.5 Hooks

| | Claude Code | Copilot | Kiro |
|---|---|---|---|
| Config | `.claude/settings.json` `hooks`, plugin `hooks/hooks.json` | CLI: `.github/hooks/*.json`, `~/.copilot/hooks/*.json`, `.github/copilot/settings.json`, plugin `hooks.json`, **and `.claude/settings.json`** (PascalCase events with Claude-style matchers and tool names). The cloud agent reads only `.github/hooks/*.json` ([hooks ref](https://docs.github.com/en/copilot/reference/hooks-configuration)). VS Code runs Claude-format plugin hooks but **ignores matchers** ([search summary of VS Code plugin docs](https://code.visualstudio.com/docs/copilot/customization/agent-plugins), unverified) | `.kiro/hooks/<any>.json` `{version:"v1", hooks:[...]}`, global `~/.kiro/hooks/` in CLI V3, or inline in agent JSON ([hooks](https://kiro.dev/docs/hooks/)) |
| Events | PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart, ... | sessionStart/End, userPromptSubmitted, preToolUse, postToolUse, agentStop, subagentStop, preCompact, ... | Prompt Submit, Agent Stop, Session Start, Pre/Post Tool Use, File Create/Save/Delete (agent edits only), Pre/Post Task Execution ([hook types](https://kiro.dev/docs/hooks/types.md)) |
| Blocking | Exit 2 blocks | `preToolUse` exit 2 denies. Command hooks fail closed, timeouts fail open. Stop `decision:"block"` forces another turn ([hooks ref](https://docs.github.com/en/copilot/reference/hooks-configuration)) | PreToolUse can block (exit-code-2 semantics). CLI Prompt Submit cannot block. Stop `decision:"block"` continues the run ([hook types](https://kiro.dev/docs/hooks/types.md)) |
| Action types | command (+ prompt/agent types) | command, http, prompt (sessionStart only) | command, or agent (injects a prompt) ([hooks](https://kiro.dev/docs/hooks/)) |

Portable pattern **(inferred)**: one set of `scripts/hooks/*.sh` that read stdin JSON and handle both `tool_input.command` and the snake_case/camelCase variants, exiting 2 to block. Then generate three thin registration files. Copilot CLI picks up `.claude/settings.json`, so only Kiro and the Copilot cloud agent need extra files. Never rely on hooks for compliance-critical gates in VS Code, because matchers are ignored there. Enforce those in CI too.

### 2.6 MCP configuration

| | File(s) | Top-level key |
|---|---|---|
| Claude Code | `.mcp.json` (project), plugin `.mcp.json` or `mcpServers` in plugin.json ([plugins-reference](https://code.claude.com/docs/en/plugins-reference.md)) | `mcpServers` |
| Copilot VS Code | `.vscode/mcp.json` or the user profile `mcp.json` (key `servers`, labelled deprecated in the guided flow). Workspace-root `.mcp.json` sits behind experimental `chat.mcp.workspaceRootConfig.enabled`. User: `~/.copilot/mcp-config.json`. "Portable configurations don't support VS Code input variables" ([VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)) | `mcpServers` (portable) / `servers` (VS Code format) |
| Copilot CLI | `~/.copilot/mcp-config.json` ([VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)). Plugins use `.mcp.json`, `.github/mcp.json` or root `mcp.json` (Agent Plugins) ([plugin ref](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)) | `mcpServers` |
| Copilot cloud agent | Repo **Settings > Copilot > MCP servers** (JSON on github.com, not a file). Secrets must be prefixed `COPILOT_MCP_`. A `tools` allowlist is required ([cloud agent MCP](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp)) | `mcpServers` |
| Kiro | `.kiro/settings/mcp.json`, `~/.kiro/settings/mcp.json`, or agent `mcpServers`. Keys include `command/args/env/url/headers/disabled/autoApprove/disabledTools/oauth` ([Kiro MCP](https://kiro.dev/docs/mcp/configuration/)) | `mcpServers` |

The server entries are the same JSON shape, so a generator only has to copy one canonical `mcp.json` to `.mcp.json`, `.kiro/settings/mcp.json` and (optionally) `.vscode/mcp.json` with `servers` **(inferred)**.

### 2.7 Plugin / extension packaging

- **Claude Code plugins:** `.claude-plugin/plugin.json` (only `name` required), plus `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json` and a marketplace in `.claude-plugin/marketplace.json`. `$schema` in plugin.json is ignored at load ([plugins-reference](https://code.claude.com/docs/en/plugins-reference.md)). A skill folder that contains a `.claude-plugin/plugin.json` loads as a `<name>@skills-dir` plugin ([skills](https://code.claude.com/docs/en/skills.md)).
- **Copilot agent plugins (GA in VS Code, CLI and the app):**
  - The CLI checks manifests in this order: root `plugin.json` (Agent Plugins, takes precedence), `.plugin/plugin.json`, `.github/plugin/plugin.json`, then `.claude-plugin/plugin.json`.
  - It loads `agents/`, `skills/`, `commands`, `hooks.json` and MCP.
  - Marketplaces are found at `marketplace.json`, `.github/plugin/` or `.claude-plugin/marketplace.json`.
  - Install with `copilot plugin install OWNER/REPO[:PATH]`, a git URL or a local path ([CLI plugin ref](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)).
  - VS Code supports the "Copilot, Claude, and legacy OpenPlugin formats" and "Install Plugin From Source". Projects can recommend plugins through `extraKnownMarketplaces`/`enabledPlugins` in `.claude/settings.json` or `.github/copilot/settings.json` ([VS Code agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)).
  - In Agent Plugins 1.0, Copilot-specific agents, commands, rules and hooks go under `com.github.copilot/` ([changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)).
- **Kiro powers:** Agent Plugins format. Root `plugin.json` requires `$schema`, `name`, `version`, `description`, `author` and `keywords`, where keywords drive activation. Contents are `skills/` and root `mcp.json`. Legacy `POWER.md` still works. Install from the marketplace or GitHub URLs ([powers](https://kiro.dev/docs/powers/), [create](https://kiro.dev/docs/powers/create/)). Steering and hooks are not power components.
- **Org governance:** Copilot Business/Enterprise `managed-settings.json` supports `enabledPlugins`, `extraKnownMarketplaces` and `strictKnownMarketplaces` ([changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)). Claude Code has its own managed settings. This matters for a bank.

### 2.8 Multi-root / multi-repo (products span 5-6 repos)

- **Claude Code:**
  - `--add-dir` / `/add-dir` loads that directory's `.claude/skills`, `commands` and `agents` ([skills](https://code.claude.com/docs/en/skills.md#skills-from-additional-directories)).
  - CLAUDE.md from added directories loads only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`, and **AGENTS.md from added directories never loads** ([memory](https://code.claude.com/docs/en/memory.md#where-agentsmd-differs-from-claudemd)).
- **Copilot CLI:**
  - `/add-dir PATH` loads `.github/skills` and `.github/agents` from that path ([CLI command ref](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)).
  - `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` adds AGENTS.md and `.instructions.md` directories ([CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)).
- **Copilot VS Code:** multi-root discovery of instructions and skills is **not clearly documented**. Community reports conflict ([search](https://github.com/orgs/community/discussions/155450), [vscode#264837](https://github.com/microsoft/vscode/issues/264837)). `chat.useCustomizationsInParentRepositories` covers monorepos only ([VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)). Needs a local test **(inferred)**.
- **Copilot cloud agent:** single repo. The default GitHub MCP server is read-only to the current repo, and reaching other repos needs a PAT or GitHub App ([cloud agent MCP](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp)).
- **Kiro IDE (well documented):**
  - Reads `.kiro/` under **each** root, including steering, hooks and MCP.
  - `always` steering loads regardless of root. `fileMatch` steering loads only for files in its own root.
  - File hooks fire only for their own root.
  - On an MCP name clash, the last root wins, and all servers run with the first root as cwd ([multi-root](https://kiro.dev/docs/ide/editor/multi-root-workspaces.md)).

**Implication (inferred):** don't depend on each tool's per-folder discovery to reach the KB. Make the **KB reachable through MCP**, which works the same in every tool and every repo, and install the toolkit at **user or plugin level** rather than copying it into 6 repos. Each product repo keeps only a small AGENTS.md pointing to the KB and to the product's bet.

---

## 3. Capability matrix

Legend: Y = native, P = partial or with caveats, N = no.

| Capability | Claude Code | GitHub Copilot (VS Code / CLI / cloud agent) | Kiro (IDE / CLI) |
|---|---|---|---|
| Reads root `AGENTS.md` | Y (only if no CLAUDE.md) | Y / Y / Y | Y (always) |
| Nested `AGENTS.md` | Y | P (exp. setting) / Y / Y (nearest wins) | Y |
| Reads `CLAUDE.md` | Y | P (setting) / Y / Y (root only) | N |
| Path-scoped rules | `.claude/rules` `paths:` | `.github/instructions` `applyTo:` | steering `fileMatch` |
| Description-triggered rules | via skills | `.instructions.md` `description` | steering `auto` |
| Agent Skills SKILL.md | Y `.claude/skills` | Y `.github/.claude/.agents/skills` | Y `.kiro/skills` only |
| Skills as `/command` | Y | Y | Y |
| Prompt files | merged into skills | `.github/prompts` (VS Code Local only) | manual steering / CLI prompts |
| Custom agents | `.claude/agents/*.md` | `.github/agents/*.agent.md` | `.kiro/agents/*.json\|.md` |
| Hooks | Y (settings.json) | N? (VS Code via plugins, matcher ignored) / Y (reads `.claude/settings.json` too) / Y (`.github/hooks`) | Y (`.kiro/hooks/*.json`) |
| Blocking pre-tool hook | Y exit 2 | Y exit 2 (CLI, cloud) | Y |
| MCP project config | `.mcp.json` | `.vscode/mcp.json` or exp. `.mcp.json` / user `mcp-config.json` / repo settings UI | `.kiro/settings/mcp.json` |
| Plugin format | `.claude-plugin/plugin.json` | Agent Plugins 1.0 + Claude + Copilot formats | Agent Plugins 1.0 (powers) |
| Install plugin from git | Y (marketplace) | Y | Y (GitHub URL) |
| Org-managed plugin allowlist | Y (managed settings) | Y (`managed-settings.json`) | ? (not found) |
| Multi-repo context | `--add-dir` (no AGENTS.md) | P / `/add-dir` + env var / N | Y multi-root |
| Headless run | `claude -p --output-format json` | N / `copilot -p -s --output-format json` / async PR agent | `kiro-cli chat --no-interactive --output-format stream-json` (needs `KIRO_API_KEY`, paid tiers) |
| Built-in eval runner | Y `claude plugin eval` | N | N |

Sources: as cited in §2. Headless: [Claude headless](https://code.claude.com/docs/en/headless.md), [Copilot programmatic](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [Copilot CLI programmatic ref](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference), [kiro-cli headless](https://kiro.dev/docs/cli/headless/).

---

## 4. Kiro and our bet files (specs out of scope)

Per the scope decision, Kiro's `.kiro/specs` is **not used**. The bet intent/spec/plan/tasks files in the OKF repo are the single spec system. To give Kiro the same context the other tools get **(inferred)**:
- Each product repo carries a generated `.kiro/steering/aidlc.md` with `inclusion: always`. It is a few lines that point to AGENTS.md and to the active bet. Kiro already loads AGENTS.md, so this file can be omitted unless Kiro-specific wording is needed.
- To pull the current bet's files into context, use `#[[file:...]]` references in a `manual` or `auto` steering file ([steering](https://kiro.dev/docs/steering/)). If the KB is a separate repo, prefer the KB MCP server, because relative paths resolve from the workspace root.

---

## 5. Existing single-source generators

| Tool | What it does | Targets relevant here | Maturity (2026-10-27) |
|---|---|---|---|
| **rulesync** ([repo](https://github.com/dyoshikawa/rulesync), [README](https://raw.githubusercontent.com/dyoshikawa/rulesync/main/README.md)) | Generates rules, ignore, MCP, commands, subagents, skills, hooks and permissions from `.rulesync/`. Supports `import` from existing configs and `convert --from x --to y`. Has a `claudecode-plugin` packaging target | Claude Code, Copilot, Copilot CLI, Kiro CLI, Kiro IDE: all features except ignore for Copilot | 1,560 stars, v43.2.0 released 2026-10-27, very active (gh api). Fast churn (43 majors) means version pinning is required |
| **ruler** ([repo](https://github.com/intellectronica/ruler)) | `.ruler/AGENTS.md` + `ruler.toml` lead to per-agent rules, MCP propagation, skills and subagents | Copilot (AGENTS.md, `.mcp.json`, `.github/skills`, `.github/agents`), Claude (CLAUDE.md, `.claude/skills`, `.claude/agents`), Kiro (`.kiro/steering/ruler_kiro_instructions.md`, `.kiro/settings/mcp.json`, `.kiro/skills`, no subagents) | 2,952 stars, v0.3.46 released 2026-10-22, active, pre-1.0 |
| **Agent Plugins 1.0** ([spec](https://agent-plugins.org/)) | Packaging standard for skills + MCP | Copilot, Kiro. Claude needs an extra `.claude-plugin/plugin.json` | 1.0.0, Aug 2026. Anthropic is not a maintainer |

Neither generator handles hooks safely enough to trust blindly for a bank. Both are fine for rules, skills and MCP fan-out **(inferred)**.

---

## 6. Recommended architecture

```
okf-kb repo (OKF v0.2 bundle)          toolkit repo (aidlc-toolkit)
  methodology/ rituals/ bets/ adrs/       plugin/
                                            .claude-plugin/plugin.json   <- Claude manifest
                                            plugin.json  ($schema Agent Plugins 1.0, keywords) <- Copilot + Kiro
                                            skills/<name>/SKILL.md       <- single source, portable frontmatter
                                            mcp.json                     <- Agent Plugins; Claude manifest points mcpServers -> ./mcp.json
                                            hooks/hooks.json             <- Claude (Copilot reads Claude format)
                                            com.github.copilot/agents/*.agent.md  (generated)
                                            scripts/hooks/*.sh           <- one implementation, stdin JSON, exit 2
                                            evals/                       <- claude plugin eval suite
                                          .claude-plugin/marketplace.json <- Claude + Copilot read this path
                                          mcp-server/  (aidlc-mcp: KB search/read, bet context, Jira)
                                          cli/         (aidlc: deterministic ops)
                                          adapters/gen.ts  (or rulesync, pinned)
product repo x 5-6
  AGENTS.md            <- tiny: product, active bet id, "use aidlc MCP for KB", repo map
  .claude/rules/*      <- optional Claude-only
  .github/instructions/*.instructions.md, .kiro/steering/*.md  <- generated path-scoped rules
  .mcp.json, .kiro/settings/mcp.json  <- generated from one mcp.json
  .github/hooks/*.json, .kiro/hooks/aidlc.json  <- generated wrappers -> scripts
```

Layers, from most to least portable:
1. **MCP server (`aidlc-mcp`) is the shared runtime.** It gives KB search and read (OKF frontmatter-aware), "current bet context" (intent/spec/plan/tasks), ADR lookup, meeting records and Jira. All three tools and the Copilot cloud agent (configured through the repo settings UI with `COPILOT_MCP_` secrets) reach the same KB this way. It also solves the 5-6 repo problem without depending on each tool's multi-root behaviour. Expose prompts and resources too, but don't rely on them: tool calls are the lowest common denominator **(inferred)**.
2. **`aidlc` CLI for deterministic operations:** scaffold a bet, validate OKF frontmatter, move tasks, sync Jira, and run the adapter generator. Skills call it through the shell, so behaviour is identical across agents and testable in CI **(inferred)**.
3. **Agent Skills as the only workflow and slash-command format.** Use only portable frontmatter (`name`, `description` of 1024 chars or less, `argument-hint`, `user-invocable`, `disable-model-invocation`). Claude-only extras such as `allowed-tools`, `model`, `effort` and `context: fork` are acceptable where degradation is harmless. Don't use `$ARGUMENTS`, because Kiro substitutes it only in the CLI ([Kiro skills](https://kiro.dev/docs/skills/)). Avoid pstack-style dependence on Claude subagents: when a skill says "spawn a subagent", give a fallback "otherwise do it inline" **(inferred)**.
4. **Dual-manifest plugin as distribution.** It installs through the Claude marketplace, `copilot plugin install`, VS Code "Install Plugin From Source" and Kiro power-from-GitHub-URL. Pin by commit SHA ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)). Fallback for developers who block plugins: `aidlc install --user` copies skills to `~/.claude/skills`, `~/.copilot/skills` (or `~/.agents/skills`) and `~/.kiro/skills` **(inferred)**.
5. **AGENTS.md is the canonical instruction file, with thin generated adapters.** Don't commit CLAUDE.md, to avoid double-loading in Copilot. Generate `.github/instructions/*.instructions.md` (`applyTo`) and `.kiro/steering/*.md` (`fileMatch`) from one source of path-scoped rules (`aidlc/rules/*.md` with a `globs:` field). Use rulesync (pinned) or a 200-line in-house generator. I'd start in-house because there are only three targets and bank review favours small auditable code **(inferred)**.
6. **Hooks: shared scripts with generated registrations,** for Claude `.claude/settings.json` / plugin `hooks/hooks.json` (Copilot CLI reads it too), `.github/hooks/*.json` (cloud agent) and `.kiro/hooks/aidlc.json`. Real compliance gates (secrets, protected branches) also run in CI and pre-commit, because VS Code ignores matchers and timeouts fail open in Copilot ([hooks ref](https://docs.github.com/en/copilot/reference/hooks-configuration)).

Drift control: CI in each product repo runs `aidlc gen --check` and fails if the generated adapters differ from source **(inferred)**.

---

## 7. Eval portability

- **Claude:** `claude plugin eval` gives full graders (regex, tool_used, tool_order, file_exists, llm, baseline), MCP mocks and multiple runs ([plugin-eval-format.md](./plugin-eval-format.md)). It is the primary suite.
- **Copilot CLI:** `copilot -p "<prompt>" -s --no-ask-user --allow-tool=... --model X --output-format json` (JSONL) ([programmatic how-to](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [programmatic ref](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)). It needs `COPILOT_GITHUB_TOKEN`. VS Code agent mode has no headless runner (not found).
- **Kiro CLI:** `kiro-cli chat --no-interactive --trust-tools=... --agent X --model Y --output-format stream-json --require-mcp-startup`. It needs `KIRO_API_KEY`, which is limited to Pro and above and may need admin enablement ([kiro-cli headless](https://kiro.dev/docs/cli/headless/)). The Kiro IDE has no headless mode.
- **Off-the-shelf cross-agent harnesses:** `agent-skill-eval` (OpenCode, Claude, Codex), `caliper-eval` (claude-code, codex, pi, hermes) and `agent-eval-harness` (pluggable CLI schemas). None list Copilot or Kiro ([agent-skill-eval](https://pypi.org/project/agent-skill-eval/), [caliper-eval](https://pypi.org/project/caliper-eval/0.9.0/), [agent-eval-harness](https://skills.sh/youdotcom-oss/agent-skills/agent-eval-harness)).

**What's realistic (inferred):**
1. Keep the authoritative suite in `claude plugin eval` format.
2. Write a small cross-agent smoke runner (`aidlc eval --agent claude|copilot|kiro`). It reuses `evals/<case>/prompt.md` and the **deterministic** graders (regex over final text, file_exists, and tool_used where the JSONL exposes tool names, which differ per tool). It runs each case once in a scratch copy of a fixture repo and grades outcomes, not traces. LLM graders can run as a separate `claude -p` judge over the captured transcript.
3. Check trigger accuracy per tool: does `/skill` or a natural-language prompt load the skill? Descriptions trigger differently across harnesses, and this is where portability breaks.
4. Run the Claude suite on every PR, and the Copilot and Kiro smoke runs nightly or on release, because of cost and API-key constraints.
5. MCP mocks don't exist outside Claude's runner, so point the other agents at a stub `aidlc-mcp --fixture` mode.

---

## 8. Open questions / to verify locally

- VS Code multi-root: are `.github/skills` and `AGENTS.md` discovered from every workspace folder? (docs are silent and community reports conflict)
- Does Claude Code ignore a root `plugin.json` and `com.github.copilot/` dir cleanly inside a plugin? (expected yes, untested)
- Does Kiro load a power that also contains `.claude-plugin/` and `hooks/`? (expected to ignore them, untested)
- Kiro custom-agent `.md` frontmatter schema (only "frontmatter for config, body for prompt" is documented).
- Copilot cloud agent hook and skill support inside a bank's GHE setup (policy may disable it).
