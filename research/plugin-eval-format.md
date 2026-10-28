# Claude Code plugin + `claude plugin eval` format (CLI 2.1.311)

Source: research worker, from https://code.claude.com/docs/en/plugin-evals.md, plugins/manifest-reference.md, plugins/components.md, skills.md, sub-agents.md, hooks-guide.md, and local CLI runs.

## Plugin layout

```
plugin/
  .claude-plugin/plugin.json   # only file here
  skills/<name>/SKILL.md
  agents/<name>.md
  hooks/hooks.json             # top-level "hooks" key
  scripts/
  .mcp.json                    # plugin root
  evals/                       # default eval dir
```

plugin.json: only `name` required. Fields: version, description, author{name,email,url}, homepage, repository, license, keywords, skills (adds), commands/agents (replace default scan), hooks/mcpServers (merge), userConfig{key:{type: string|number|boolean|directory|file, title, description, required, default, sensitive}}, `experimental.evals` (relative dir). Paths start with `./`.

SKILL.md frontmatter: name, description (+when_to_use, 1536 char cap), argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context: fork, agent, paths, hooks. Command is `/<plugin>:<skill>`.

Agents: name, description required; tools, disallowedTools, model, effort, maxTurns, skills, isolation. permissionMode/hooks/mcpServers ignored for plugin agents.

Hooks: `{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"\"${CLAUDE_PLUGIN_ROOT}/scripts/x.sh\""}]}]}}`. Script reads event JSON on stdin (`.tool_input.command`), exit 2 blocks with stderr as reason. Known regex gaps: `git -C dir push -f`, `git push origin +main`.

MCP tools from plugin server: `mcp__plugin_<plugin>_<server>__<tool>`.

Marketplace: `.claude-plugin/marketplace.json` {name, owner{name}, plugins:[{name, source:"./plugins/x", description}]}.

## Eval suite

```
evals/<case>/prompt.md          # frontmatter + body prompt
evals/<case>/case.yaml          # optional alternative
evals/<case>/graders/<name>.md  # frontmatter type+options, body = llm criteria
evals/mocks/<server>/<tool>.md  # MCP mocks
evals/results/                  # gitignore
```

prompt.md frontmatter: name, description, expected_outcome, tags, plugins, runs (default 3), model, max_turns (10), timeout_seconds (300), allowed_tools (read-only granted; others need --allow-tools), append_system_prompt, env (EVAL_*). Unknown keys are errors.

case.yaml: schema_version "1.1", name, description, tags, runs, execution{model,max_turns,timeout_seconds,allowed_tools,append_system_prompt,env,prompt}, context{scaffold_script (needs --scaffold), history_file, add_dirs}, graders: [ {name, type, ...} ].

Graders (6 types): regex{pattern, flags, match: contains|not_contains|count:N, target}, tool_used{tool, input_match, min, max}, tool_order{before, after}, file_exists{path glob, exists} (only files Claude created), llm{criteria/body, focus}, baseline{baseline_file, criteria}. Common: weight, arm: with-only|both. Targets: last_message, trace, files, {source: file, path}, mock_calls. JS regex.

Mocks: frontmatter type fixed|agent, expect{dotted.path: string|number|/regex/|literal|[list]} (violation aborts run with score 0), error: true. Body = result, `{{input.field}}`.

Running: `claude plugin eval <dir> --trust-plugin --allow-tools Write Edit Bash --runs 1 --ablation none --no-publish --max-cost-usd N`. Results in evals/results/<ts>/aggregate-result.json. Free checks: `claude plugin validate <dir> [--strict]`, `claude --plugin-dir <dir> plugin details <name>`.

Unconfirmed: exact mock tool name; mock_calls text format.
