# Synthesis note: arena A (methodology, roles, rituals)

## Base and why

Base is candidate 2. Its engine is a tool-agnostic pack: the `t0` CLI for anything deterministic, Agent Skills (`SKILL.md`) for orchestration, and generated `AGENTS.md` adapters. That shape runs the same in GitHub Copilot, Claude Code and Kiro. Candidate 1 was built as a Claude Code plugin (slash commands namespaced to the plugin, plus a `SessionStart` hook for context), so it fails the binding tool-agnostic constraint by construction. That cannot be fixed by grafting.

## Cross-judge verdict

The judges agreed on the scores. C1 got 26 and C2 got 25. C1 was richer on gates, rituals, privacy and the Jira mirror. C2 won the base because C1 fails the binding constraint structurally. So C1 became the graft source.

## Grafts (all from candidate 1, redesigned to C2 naming)

1. **Gates as KB PRs.** Each gate has an "artefato que prova" column with `state` + `verified: {by: human:<who>, at}`. A gate is a PR in the KB repo, PR approval is the approval, and git history is the audit trail. Gate SLO equals the review SLO (4h business hours) and shows in the digest. Gates were renumbered G0 to G8 so that the diagram, the gate table, the bet-type table and §10 agree. A bugfix G1 can be approved by the Flow Steward outside Betting. Command: `gate <G>` calling `t0 gate`.
2. **One ritual table** with C1's columns. Added rituals: Triagem de ideias (`idea-triage`), Preceptoria 1:1 (never transcribed), PI Outcome Planning, and Mob Construction as its own row. Every ritual uses `ritual <slug> open|close`. Mob A stays at 45 min with a 60 min ceiling. The per-profile sync budget is new (Dev, Júnior, Preceptor, AIVA, Lead). The dev typical is stated as 4h and the ceiling as 5h. Two rules keep the ceiling arithmetic true: Mob A overrun absorbs the Mob B sync slot, and Mob Construction replaces Mob B.
3. **Transcription and privacy** (§4.4). Redaction is deterministic and runs before any model sees the text. Covered: "fora do registro", 1:1 and performance talks never recorded, 180-day `stale_after` labeled PROPOSTA, dry-run until legal sign-off. Agent-extracted ideas and ADRs enter without `verified`.
4. **Jira per-field rules.** Comments are two-way and append-only. Issues created in Jira go through intake. A nightly reconcile produces a drift report, with the goal of zero drift at Demo. C2's status rule with `state: conflict` was kept.
5. **Juniors and anti-cargo.** A junior is never sole approver of Tier 1+. Juniors can be Bet Owner of bugfix and Tier 0/1 platform bets from cycle 1, and of delivery bets from cycle 3 with the preceptor co-approving G2. A 4th consecutive same-archetype declaration is blocked unless a justification is recorded. Archetypes never appear in Jira, HR or performance review. Extra anti-vanity rules came along too.
6. **Harness Item** (`harness/HI-NNNN.md`, one per recurring error) replaces C2's single `recorrencias.md`. `harness/trust.md` is written only by CI.
7. **KB layout.** Each cycle gets a Cycle Record with rituals and transcripts under `cycles/<C>/`. Bets live under `products/<p>/bets/`. The intent sits in the body of `bet.md`, so `intent.md` was dropped. `bugfix.md` stays. Accountability became an OKF type. Contracts live only under `products/<p>/contracts/`, so the ship step no longer has to promote them.
8. **Appendix A**, with the 25 deltas. It says where C2 decided differently (deltas 12, 13, 15).

## Rejected

- **The C1 `traceability` key on Slice.** It was replaced by a full-chain check in `kb-check` plus on-demand `t0 trace`. A key that duplicates the frontmatter would drift.
- **C1's `SessionStart` context hook and `kb find` mechanism in §5.** The workspace pattern (ADR-0002) owns that mechanism, so §5.2 leaves a marker instead.
- **C1's separate Digest, Cycle Report and Retro Record types.** They were folded into Metric Snapshot and Ritual Record to keep the type count down.
- **C1's two-way assignee sync.** It adds a conflict surface for little gain.

## Errors fixed

- C2 claimed that agent hooks exist only in Claude Code and Kiro. That is wrong, because Copilot has hooks too. The corrected reason: hooks differ per tool and aren't portable (Copilot in VS Code ignores matchers, and its hook timeouts fail open). So mandatory rules live in git hooks + CI, and agent hooks are optional accelerators generated per tool.
- Bugfix path: `bet-new bugfix` now creates the single slice with its Jira key, so `slice-build <KEY>` works. The DoR states the bugfix exceptions inline.
- "Fixo (você)" became "Tech lead do time".
- The unsourced claim "nem o Skill tool existe nas três" was dropped.
- C2's "PR aberto = In Review" was aligned with G4: the PR leaves draft at G4, and that is when the Story moves to In Review.
