# Skills: the portable set

Rules that apply to every skill:

- Portable frontmatter only: `name`, `description` (≤1024 chars, pt-BR), `argument-hint`, `user-invocable`, `disable-model-invocation`, `metadata.credits` (upstream path, version, license) on every fork. No `$ARGUMENTS`, no `allowed-tools`/`model` unless degradation is harmless.
- Output in pt-BR. Acceptance criteria as bullets, never Gherkin (the `no_gherkin` check backs this up in `t0`).
- Every skill ends by calling `t0 log <kind> "..."`; the records lane is how the KB sees the step even when the agent improvises.
- Code-writing skills run `t0 bet detect` first and refuse to write code without a resolved bet. Ritual and KB skills do not need a bet.
- Where a skill says "spawn a subagent", it also says "otherwise do it inline" (Copilot/Kiro have no `Agent` tool).
- Diff policy per fork: copy the upstream file, change only the lines listed, keep the upstream text otherwise. Upstream fixes are re-applied by diffing against the pinned version recorded in `metadata.credits`.

Columns: **t0 calls** = subcommands the SKILL.md invokes (checked by `t0 gen --check` against the parser).

## Cycle skills (`skills/ciclo/`)

| Skill | Purpose (one line) | `t0` calls | Upstream base → diff policy | v0.1 |
|---|---|---|---|---|
| `pack-setup` | Instala o pack num repo de produto: bloco t0 no AGENTS.md, ponteiros, workflows, `.gitignore`, `docs/agents/issue-tracker.md` | `setup`, `setup --check`, `gen --check`, `log` | MP `setup-matt-pocock-skills` → fork: Section A defaults to "Jira via t0" and seeds from `templates/issue-tracker-jira.md`; label creation removed (Jira labels come from `jira sync`); `## Agent skills` block replaced by the `<!-- t0:begin -->` block from `t0 setup` | yes |
| `kb-check` | Roda a conformidade do KB e explica os achados | `kb check --format text` | new (thin) | yes |
| `idea-capture` | Captura uma ideia no inbox com dedup pelo glossário | `kb find --type Idea`, `idea new`, `log` | new | no |
| `idea-triage` | Triagem semanal (G0): triaged / parked / rejected com motivo | `ritual triagem open`, `idea triage`, `gate G0`, `ritual triagem close`, `log` | new | no |
| `bet-new` | Abre uma bet pelo template do tipo (`<tipo> [IDEA]`); bugfix cria `bugfix.md` + slice único | `bet new`, `jira sync --dry-run` (bugfix: real), `kb propose`, `log` | new | yes |
| `bet-use` | Troca a bet ativa da sessão e re-renderiza o card | `bet use`, `bet detect`, `context --write` | new (thin) | yes |
| `bet-shape` | Shape: restate (in-your-own-words), grilling + domain-modeling, 2 esboços de arquitetura, **checkpoint humano obrigatório**, grava rascunho de spec e glossário | `bet detect`, `kb get`, `kb find --type "Glossary Term"`, `adr new` (quando decide), `log` | MP `grilling` + `domain-modeling` (wrap, model-invoked; "otherwise inline" fallback) + PS `architect` Phases A–C text (fork: 2 sequential sketches by the session model, checkpoint mandatory, no Phase D, no `.mdc`) + PS `in-your-own-words` (inline paste); `--explore` branch wraps MP `prototype` | yes |
| `bet-spec` | Escreve `spec.md`: problema, solução, AC em bullets, `verify_how`, `seams[]`, tier; conta marcadores; propõe o PR | `spec markers` (via `kb check --level L1` on the file), `kb propose`, `log` | MP `to-spec` → fork: line 9 pointer → `pack-setup`; line 19 publish-to-tracker → write `spec.md` and `t0 kb propose`; template lines 21–75 translated and extended with Critérios de aceite / Como verificar / Tier / Seams; keep the seams-confirmation step | yes |
| `bet-plan` | Plano com bolts e os 4 checks; exige Contract quando há `surface` | `kb get`, `gate G3 --dry-run` (to show what blocks), `kb propose`, `log` | PS `architect` sketch discipline (text) + Spec Kit style gates (new text) | yes |
| `bet-slice` | Fatia em slices verticais, um arquivo por slice, grafo `depends_on`, aprova com o humano | `bet new`-style scaffold via `kb propose` (slice files), `jira sync --dry-run`, `log` | MP `to-tickets` → fork: line 11 pointer; steps 1–4 kept; step 5 writes `slices/NN-slug.md` instead of publishing; templates add Tier / Como verificar / `repo` / `jira:` placeholder; "never a single combined file" kept | yes |
| `bet-sync` | Espelha no Jira (Feature + Stories + Blocks), idempotente | `jira sync <BET>`, `kb push`, `log` | MP `to-tickets` Jira branch (text) → new, thin | no (CLI `--adapter fake` only) |
| `gate` | Qualquer gate G0–G8: explica o plano, abre o PR de gate | `gate <G> <ref> --dry-run`, `gate <G> <ref>`, `log` | new (thin) | yes |
| `ritual` | `<slug> open|close`: pauta a partir do concept Ritual; close grava record, redige transcrição, dispara gates | `ritual <slug> open`, `transcript redact`, `ritual <slug> close`, `kb push` | new | yes (generic; betting/demo/mob-a specifics via CLI `pre`) |
| `slice-build` | Build de um slice: DoR, branch, TDD nas seams, review, `.audit`, PR em draft | `bet detect`, `slice dor`, `slice start`, `log`, `kb record decision`, `pr open --draft --verify`, `harness record` (on self-detected error) | MP `implement` → fork: line 9 accepts `PROJ-123`; line 17 → `t0 slice start` + draft PR via `t0 pr open`; never merge. Wraps MP `tdd`, `code-review`, `pr` (model-invoked). PS `show-me-your-work` → fork: `.audit/<KEY>.tsv` committed by default, transcript audit scoped to the current session, "Attention" reviewer labelled same-family; `log.sh` kept verbatim | yes |
| `slice-build --parallel` | Worktrees + merger (Tier 0/1, contrato aprovado) | same + `bet start --isolate` | MP `implement-spec` → fork: line 38 stays draft; Stories → In Review only | no |
| `slice-verify` | Agente de review contra o spec e padrões; blast-radius em Tier 2; registra erro de agente | `slice get --json`, `kb get`, `harness record`, `log` | MP `code-review` → fork: line 29 add Jira regex from commits **and branch**; line 31 add `kb/products/*/bets/` to spec paths; line 13 pointer. PS `blast-radius` → fork: drop line 38 (arena), line 33 `why` → `git log` + `slice get`; proof ladder verbatim | yes |
| `diagnose` | Loop vermelho → mínimo → hipótese → fix → regressão; `--tutor` explica e não escreve o fix | `bet detect`, `log` | MP `diagnosing-bugs` (wrap; keep) + tutor mode text (new) | no |
| `bet-ship` | Congela spec, atualiza spec vivo, publica Contract, abre Adoption Report | `bet ship <BET> --dry-run`, `bet ship <BET>`, `log` | new | no |
| `verify-<app>` | Skill local por repo (Launch, Doctor, Drive, Evidence) | none (generated) | PS `create-verification-skill` / `maintain-verification-skill` → fork: `.cursor/skills` → `.claude/skills`, PR → draft | no |

## Harness and KB skills (`skills/harness/`, `skills/kb/`)

| Skill | Purpose | `t0` calls | Upstream base → diff policy | v0.1 |
|---|---|---|---|---|
| `kb-record` | Registra passo/decisão/bloqueio na raia de registros; decisão que muda contrato puxa um ADR | `kb record <kind>`, `adr new` (when contract-changing), `kb push --if-due` | new | yes |
| `kb-search` | Busca no KB por texto, tipo, tag, uid; devolve caminhos e descrições | `kb find`, `kb get` | new (thin) | yes |
| `handoff` | Documento de handoff em `$TMPDIR` com varredura determinística; `--plantao` grava Ritual Record | `transcript redact --report` (scan), `bet detect`, `log handoff`, (`--plantao`: `ritual plantao close`) | MP `handoff` → fork: line 14 prose redaction → `t0 transcript redact` before writing; add Jira keys + `.audit/` pointers; pt-BR | yes |
| `harness-fix` | Erro repetido → degrau da escada (sensor / regra / skill / AGENTS.md), PR em draft | `kb get HI-*`, `rules build` (when area rule), `pr open --draft`, `log` | MP `retro` → fork: line 13 session logs scoped to this workspace; line 25 each accepted item → draft PR. PS `correct` → fork-light: line 26 commits → draft PRs; enforcement order kept | no |
| `eval-add` | Cria caso de eval a partir de incidente ou PR no `evals/` do repo | `kb get`, `log` | new | no |
| `eval-run` | Roda a suíte do produto, grava pass rate no Eval Suite, bloqueia upgrade se piorou | `eval` (product suites), `kb propose`, `log` | new | no |
| `adoption-report` | Lê telemetria e compara com os pisos | `adoption`, `kb propose` | new | no |
| `meeting-record` | Transcrição → redação determinística → Ritual Record + Transcript + Ideas/ADRs candidatos sem `verified` | `transcript redact`, `ritual <slug> close --transcript`, `idea new --source transcript`, `adr new --proposed` | new; redaction scanner from `t0.core.redact` | no (CLI `transcript redact` ships) |
| `digest` | CI agendado; não é skill (CLI) | `digest` | new | no |
| `metrics-snapshot` | Snapshot de ciclo no close da Demo | `metrics cycle` | new | no |

## Explicitly not shipped

poteto-mode, `why`, `recall`, `automate-me`, `reflect`, `make-bot-ui`, `no-comments`, `interrogate` (same-family only; blast-radius replaces it), `arena`/`swarm`, pstack `tdd` (narrow), `wizard` (writes secrets), `improve-codebase-architecture` (CDN), `ask-matt`. Listed in `.out-of-scope/` with the reason, copying the mattpocock habit.

## v0.1 count

Twelve skills ship: `pack-setup`, `kb-check`, `bet-new`, `bet-use`, `bet-shape`, `bet-spec`, `bet-plan`, `bet-slice`, `gate`, `ritual`, `slice-build`, `slice-verify`, plus `kb-record`, `kb-search`, `handoff` (fifteen if the three KB helpers count; they are thin). The ritual skill covers betting, mob-a, demo and bloqueios through the generic engine; ritual-specific `pre` computations beyond mob-a's agenda are deferred.
