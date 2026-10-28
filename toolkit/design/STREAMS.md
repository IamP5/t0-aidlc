# Build streams for v0.1 (v2 contract)

Contract: `toolkit/design/DESIGN.md`, which wins over the sketch signatures in `toolkit/src/t0/`. Functional spec: `methodology/methodology.md` §2, §5, §6, §10, §11 and `methodology/workspace-pattern.md`.

Environment: `cd toolkit && .venv/bin/python`, tests with `.venv/bin/pytest`. Never `git commit`, `git push`, or touch files outside your stream's ownership. If you need a signature that another stream owns, write the request in `toolkit/design/requests/<stream>-<topic>.md` and work around it with the frozen signature.

Already done (edges, 149 tests): `redact`, `context`, `ws`, `hooks`, `mcp_server`, `tracker/`, `gen` (adapters, `profile.md`). Requests still open: `requests/edges-cli-wiring.md`. Its mcp pin and card budget points are settled: `mcp>=2.3,<3`, subagent card 1,500.

## Phase 0: tracer (one stream, before anything else)

This phase proves the riskiest part of the design before any of the other 14 skills exist. The risks are build-time composition and real install on the three tools.

| Stream | Owns | Done when |
|---|---|---|
| **tracer** | `toolkit/src/t0/upstream.py`, `toolkit/src/t0/compose.py`, `toolkit/tests/test_{upstream,compose}*.py`, `vendor/mattpocock/**`, `upstream/**`, `skills-src/bet-spec/**`, `plugin/**` (manifests + `skills/bet-spec/` + `evals/bet-spec-no-tracker-publish/`) | see the list below |

The tracer is done when all of these hold:

- `t0 upstream pull mattpocock --ref v1.3.1` vendors `to-spec` from the local cache and writes the lock. A second run is a no-op.
- `t0 gen --scope plugin` composes `plugin/skills/bet-spec/SKILL.md` with both patches applied, and `--check` is clean.
- A fake bumped tree with one moved anchor makes `gen` fail, naming `bet-spec` and the patch. A vanished path makes `upstream status` exit non-zero.
- `claude plugin validate plugin --strict` passes.
- The `bet-spec-no-tracker-publish` eval passes in Claude Code.
- The plugin installs in Copilot CLI and Kiro. A manual run of `bet-spec` there writes the KB file and never touches the tracker. Record the result in `toolkit/design/requests/tracer-results.md`.
- If a tool fails, write down why and stop for the coordinator. Phase 1 waits on this.

## Phase 1: parallel streams (after the tracer is green)

| Stream | Owns (only these paths) | Done when |
|---|---|---|
| **core** | `toolkit/src/t0/{__init__,okf/*,profile/*,check,view,render,gates,write,_forge,kb,cli,rituals,reports}.py`, matching `toolkit/tests/test_*.py`, `toolkit/tests/fixtures/kb-negative/**` | profile table has the 20 v2 types; `t0 gate aposta\|spec`; `t0 slice dor` enforces WIP from Policy; `t0 ritual` with the daily-time digest, harness-health and demo closers; every command in DESIGN §10 runs; `t0 kb check --level L2` is clean on `okf-template/`; one negative fixture per rule fails; pytest green |
| **edges** | `toolkit/src/t0/{redact,context,hooks,mcp_server,ws,gen}.py`, `toolkit/src/t0/tracker/**`, matching tests | pre-tool guard also blocks GitHub MCP tools (non-draft `create_pull_request`, `merge_pull_request`) and `gh pr ready`; `gen` emits agents/ per tool and `THIRD_PARTY_NOTICES.md`; `t0 setup` links `.t0/skills/verify-*` per tool |
| **template** | `okf-template/**` | the DESIGN §4 tree in pt-BR, with `products/exemplo/` covering every type, both tracks and every lane; Policies `models`, `records-lane` (batch), `wip`; passes `t0 kb check --level L2` once core lands |
| **skills** | `vendor/**` (beyond the tracer's files), `upstream/streams.toml`, `skills-src/**` (beyond bet-spec), `plugin/evals/**` (beyond the tracer's case) | the 14 remaining skills and the `/t0` playbooks per DESIGN §6; all 19 principles and 6 playbooks vendored; `t0 gen --check` clean; one eval per removing patch; humanizer pass on every pt-BR text |

## Integration (coordinator, after phase 1)

1. Wire `tests/fixtures/kb-positive` to `okf-template/`.
2. Run pytest, `t0 kb check`, `t0 gen --check`, `t0 upstream status`, `claude plugin validate plugin --strict`.
3. Run the eval suite.
4. Run one real loop on a scratch KB: idea, then rapida, then slice-build to a draft PR.
