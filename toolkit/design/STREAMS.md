# Build streams for v0.1 (run in parallel in one working tree)

Contract: `toolkit/design/DESIGN.md` (wins over the sketch), sketch signatures in `toolkit/src/t0/` (copied from `design/sketch-c1/`). Functional spec: `methodology/methodology.md` §2, §5, §6, §10 and `methodology/workspace-pattern.md`.

Environment: `cd toolkit && .venv/bin/python`, tests with `.venv/bin/pytest`. Never run `git commit`, `git push`, or touch files outside your stream's ownership. If you need a signature another stream owns to change, do not edit it: write the request in `toolkit/design/requests/<stream>-<topic>.md` and work around with the frozen signature.

| Stream | Owns (only these paths) | Done when |
|---|---|---|
| **core** | `toolkit/src/t0/{__init__,okf/*,profile/*,check,view,render,gates,write,_forge,kb,cli,rituals,reports}.py`, `toolkit/tests/test_{okf,profile,check,render,gates,write,kb,cli,rituals}*.py`, `toolkit/tests/fixtures/kb-negative/**` | `t0 kb check --level L2` clean on `okf-template/` (once it exists) and a negative fixture fails per L0/L1 rule; `pytest` green; every v0.1 CLI command in DESIGN.md runs (edge commands may call edge modules) |
| **edges** | `toolkit/src/t0/{redact,context,hooks,mcp_server,ws,gen}.py`, `toolkit/src/t0/tracker/**`, `toolkit/tests/test_{redact,context,hooks,mcp,ws,gen,tracker}*.py` | redaction corpus green; card budgets enforced; `t0 hook pre-tool` blocks force-push / reset --hard / derived-key edits / reads under `~/.t0/inbox`; MCP stdio server lists its tools; FileTracker sync idempotent; `t0 gen` renders plugin adapter files and `profile.md` with `--check` drift |
| **template** | `okf-template/**` | an OKF v0.2 bundle in pt-BR that is the team KB starter; passes `t0 kb check --level L2` when core lands |
| **plugin** | `plugin/**` | `claude plugin validate plugin --strict` passes; skills flat with portable frontmatter; evals in `plugin/evals/` loadable by `claude plugin eval` |

Integration (by the coordinator, after all four): wire `tests/fixtures/kb-positive` → `okf-template`, run pytest, `t0 kb check`, `t0 gen --check`, `claude plugin validate`, then the eval suite.
