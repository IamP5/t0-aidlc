# Request from edges to core: CLI wiring and three contract points

The edge modules are implemented and tested. `cli.py`, `kb.py`, `write.py` and `pyproject.toml` are not mine, so these are the calls I need from them.

## 1. CLI commands to wire (`cli.py`)

| Command | Call |
|---|---|
| `t0 hook <name> [--tool claude\|copilot\|kiro]` | `code, out, err = hooks.run_hook(name, sys.stdin.buffer.read(), tool=tool)`, then write out/err and exit with `code`. `gen` registers Copilot and Kiro hooks with `--tool copilot` / `--tool kiro`, so the flag must be accepted. Names: `session-start`, `subagent-start`, `prompt-submit`, `pre-tool`, `stop` (aliases `pre-tool-edit|shell|read` also work). |
| `t0 mcp [--kb DIR] [--read-only]` | `mcp_server.serve(kb_dir, read_only=...)` |
| `t0 gen [--check] [--scope plugin\|kb] [--src DIR] [--out DIR]` | `gen.run(scope=..., out=..., src=..., check=...)` returns the exit code. `--src`/`--out` are additions to the frozen surface (needed to render to a scratch dir). |
| `t0 bet detect [--json]` | `ws.detect(Path.cwd())` returns `Detection(bet, story, rule, product)` and needs no KB. |
| `t0 bet use <BET\|KEY>` | `ws.bet_use(kb, ws.locate(cwd), ref)` returns `Plan` or `Refusal` and writes `.t0/bet.json`. Then re-render `AGENTS.md` via `KB.context`. |
| `t0 slice start <KEY>` | `ws.slice_start(kb, ws.locate(cwd), key)` returns `Plan` or `Refusal`. |
| `t0 jira sync [--apply] [--tracker file:<dir>]` | `t = tracker.open_tracker(TrackerConfig(kind="file", file_dir=dir))`, `p = sync.plan_sync(view, sync.snapshot(t, view))`; with `--apply`, `plan = sync.execute(p, t)` and then `KB.apply(plan)`. |
| `t0 transcript redact <file>` | `text, report = redact.redact(raw)`. Only `redact()` can build `Redacted`. |

## 2. What the edges expect from `KB` / `write`

- `KB.open(kb_dir=None)` raises `KBUnavailable` with the pt-BR stop message. The MCP server turns it into a tool error, and the hooks inject it as text.
- `KB.context(ref | None, CardFormat)` should build `context.WorkspaceFacts` from `ws.locate(cwd).facts()`, resolve the bet with `ws.detect_bet(kb, cwd)`, and call `context.render(view, ws_facts, resolved, fmt, changed=..., now=...)`. Session-start calls `KB.open().context(None, CardFormat.DELTA)`, and subagent-start uses `CardFormat.SUBAGENT`.
- `KB.push(if_due=True)` is called by the stop hook. Errors are swallowed there.
- `KB.get(Ref)` must resolve a Jira key to the Slice concept, and a `BET-NNN` id to the bet's `bet.md`. `ws.bet_use` and `ws.slice_start` depend on that.
- `write.new_record(EventKind.JIRA_LINKED, type_name="Step", fields={kind, target, payload: {key}}, body, actor="process:t0-sync", handle="t0-sync", where={"repo": "kb"}, dedup="jira-linked:<uid>:<key>")` is how sync emits records. While it raises `NotImplementedError`, `sync.execute` returns the links as `Plan.messages_pt` lines `jira-linked <uid> <KEY>`.
- `Report.format("json")` is used by the MCP tool `kb_check`.

## 3. Contract points to settle

- **`mcp` version.** `pyproject.toml` says `mcp>=1.2`, but the venv has 2.3.0, and 2.x renamed FastMCP to `MCPServer`. `mcp_server.py` targets 2.x. Please pin `mcp>=2.3,<3`.
- **Subagent card budget.** The edges brief says 1500. workspace-pattern §2.4/§2.6 and the sketch say 3000. `context.SUBAGENT_BUDGET = 1500` follows the brief. The coordinator should pick one.
- **Derived keys.** `hooks.derived_keys(type_name)` reads `profile.table.TYPES` + `STATEFUL_DERIVED` directly because `Registry.derived_keys` raises `NotImplementedError`. Once it exists, the hook can call it with the same result.
- **`profile.md`.** `render.py`'s docstring lists `/profile.md`. `gen.profile_md(Sources)` renders it from the table, and `t0 gen --check --scope kb` drift-checks it. If `render.materialize` should own it, it can call `gen.generate(GenContext(kb_root, Scope.KB))`.
