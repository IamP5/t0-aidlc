# Build streams for v0.1 (v2 contract)

Contract: `toolkit/design/DESIGN.md`, which wins over the sketch signatures in `toolkit/src/t0/`. Functional spec: `methodology/methodology.md` §2, §5, §6, §10, §11 and `methodology/workspace-pattern.md`.

Environment: `cd toolkit && .venv/bin/python`, tests with `.venv/bin/pytest`. Never `git commit`, `git push`, or touch files outside your stream's ownership. If you need a signature that another stream owns, write the request in `toolkit/design/requests/<stream>-<topic>.md` and work around it with the frozen signature.

Already done:
- **edges** (149 tests): `redact`, `context`, `ws`, `hooks`, `mcp_server`, `tracker/`, `gen` (adapters, `profile.md`). Requests still open are in `requests/edges-cli-wiring.md`. Its mcp pin and card budget points are settled: `mcp>=2.3,<3`, subagent card 1,500.
- **skills**: the 15 pt-BR skills in `plugin/skills/`, plus the `bet-spec-no-tracker-publish` eval.

| Stream | Owns (only these paths) | Done when |
|---|---|---|
| **core** | `toolkit/src/t0/{__init__,okf/*,profile/*,check,view,render,gates,write,_forge,kb,cli,rituals,reports}.py`, matching `toolkit/tests/test_*.py`, `toolkit/tests/fixtures/kb-negative/**` | see below |
| **edges** | `toolkit/src/t0/{redact,context,hooks,mcp_server,ws,gen}.py`, `toolkit/src/t0/tracker/**`, matching tests | see below |
| **template** | `okf-template/**` | see below |
| **evals** | `plugin/evals/**` | see below |

**core** is done when:
- the profile table has the 20 v2 types;
- `t0 gate aposta|spec` works;
- `t0 slice dor` enforces WIP from Policy;
- `t0 ritual` has the daily-time digest and the harness-health and demo closers;
- every command in DESIGN §10 runs;
- `t0 kb check --level L2` is clean on `okf-template/`;
- each rule has a negative fixture that fails;
- pytest is green.

**edges** is done when:
- the pre-tool guard also blocks GitHub MCP tools (non-draft `create_pull_request`, `merge_pull_request`) and `gh pr ready`;
- `gen` emits `agents/` per tool;
- `t0 setup` links `.t0/skills/verify-*` per tool.

**template** is done when:
- it has the DESIGN §4 tree in pt-BR;
- `products/exemplo/` covers every type, both tracks and every lane;
- it has the Policies `models`, `records-lane` (batch) and `wip`;
- it passes `t0 kb check --level L2` once core lands.

**evals** is done when:
- every behavior listed in DESIGN §11 has a case;
- the full suite passes in Claude Code;
- the plugin loads in Copilot CLI and Kiro, with the result recorded in `requests/portability-results.md`.

## Integration (coordinator)

1. Wire `tests/fixtures/kb-positive` to `okf-template/`.
2. Run pytest, `t0 kb check`, `t0 gen --check` and `claude plugin validate plugin --strict`.
3. Run the eval suite.
4. Run one real loop on a scratch KB: idea, then rapida, then slice-build to a draft PR.
