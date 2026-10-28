# Request from core to template: four fixture fixes for a clean `t0 kb check --level L2`

Core now folds every render-owned key from records. With the v2 table and `profile.md` generated
(`t0 gen --scope kb --out okf-template`, already run), `t0 kb check --kb okf-template --level L2` reports
one error and six warnings. Each one is a missing record or a version string in the fixture, not a
checker bug. Run the command after each fix; the target is `kb check: ok`.

1. **Transcript redaction version (error, `SCAN.secret`).** `/transcripts/2026-10-20-daily-pod.md` has
   `redaction: "t0-redact/0.1 segredos+cpf+..."`. The checker accepts only `t0.redact.KNOWN_RULESETS`,
   today `t0-redact/1`. Write `redaction: t0-redact/1` and keep the prose in the body.
2. **BET-001 Jira keys (warning, `L2.anomaly` x2).** `bet.md` and slice 01 carry `jira: EXE-10` /
   `EXE-11`, but no `jira-linked` record exists in `BET-001/steps/`, so `story: EXE-11` in the PR records
   resolves to nothing and the slice folds to `ready`. Add one Step like BET-002's:
   `kind: jira-linked`, `target: bet-001`, `payload: { keys: { bet-001: EXE-10, bet-001-slice-01: EXE-11 } }`,
   dated before 2026-10-13T14:05.
3. **HI-0001 `fixed` (warning, `L2.derived-drift` x2).** Harness Item `state` and `pr` are derived from
   records (coordinator decision 5). Add a Step in `/steps/` with `kind: pr-merged`, `target: hi-0001`,
   `refs: ["t0/status-bot#19"]`. That is what `t0 ci HI-0001 --pr t0/status-bot#19 --state merged` writes.
4. **Lead holder (gate refusal, not a check finding).** Every `bet`-track aposta defaults to P2W, which needs the
   Lead, and `t0 gate` resolves the Lead from `holders: [human:<handle>]` on `/team/roles/lead.md` (or `roles: [lead]`
   on a Person). `team/roles/lead.md` has neither, so `t0 gate aposta` refuses with "precisa do Lead". Add `holders`.

Slice `verified` is derived from the `pr-merged` record's `payload.approvals`, with `at` equal to the
record's `generated.at`. BET-002 already folds clean. BET-001's two drift warnings (`state`, `verified`)
go away once item 2 lands. After the three fixes the expected output is `kb check: ok`.
