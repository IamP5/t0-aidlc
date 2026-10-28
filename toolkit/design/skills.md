# Portable skill set

## Rules every skill follows

1. **Skills orchestrate; `t0` decides.**
   - A skill never computes state, ids, paths, gate outcomes, Jira mappings or redaction itself.
   - When a skill needs any of those, it calls a `t0` command and acts on the exit code: 0 ok, 1 refusal (show the reasons_pt to the human), 3 KB unavailable (stop).
   - `t0 gen --check` lints every `t0 <x>` mention in a SKILL.md against `cli.COMMANDS`.
2. **Portable frontmatter only.**
   - Allowed keys: `name` (= folder), `description` (≤300 chars), `argument-hint`, `user-invocable`, `disable-model-invocation`, `metadata.credits`, `metadata.t0 {requires_bet, ships}`.
   - No `$ARGUMENTS`, because Kiro substitutes it only in its CLI. Arguments are read from the user's message.
   - Claude-only keys (`allowed-tools`, `model`, `context: fork`) are allowed only where degrading is harmless, and `gen --check` warns about them.
3. **Cycle skills are user-invoked** (`disable-model-invocation: true`), so they cost nothing in the always-on skill listing. Only primitives are model-invoked:
   - `grilling`, `domain-modeling`, `prototype`, `tdd`, `code-review`, `pr`, `diagnose`, `kb-record`
   - `gen --check` enforces ≤25 model-visible skills and ≤7,500 description chars per tool. Kiro may ignore `disable-model-invocation`, so its budget counts every skill (risk noted).
4. **Generated regions** (`<!-- t0:gen:header -->`, `<!-- t0:gen:footer -->`) are injected by `t0 gen` from `plugin/skills/_shared/`. Nobody edits them per skill. The single source of the shared header and footer is:
   - **Header:** "Escreva toda saída para humanos em pt-BR. Critérios de aceite em bullets, nunca Gherkin. Não edite chaves derivadas nem index.md/log.md/changeset.md. Para usar outra skill, invoque-a pelo nome; se a ferramenta não permitir, leia `skills/<nome>/SKILL.md` deste plugin e siga."
   - **Header, when `metadata.t0.requires_bet: true`:** "Rode `t0 bet detect --json`. Sem bet resolvida, NÃO escreva código: peça a bet ou rode `t0 bet use`."
   - **Footer:** "Ao terminar (ou ao parar), rode `t0 log <kind> \"<o que foi feito>\"`. Se `t0` sair com código 3, pare e diga 'KB indisponível'."
5. **Subagents are optional.** Any "spawn a subagent" step carries "senão, faça inline". Review subagents are generated per tool only where supported (Claude `agents/`, Copilot `.agent.md`). Kiro runs everything inline.

## Upstream diff policy (exact)

- **Vendor pristine copies.**
  - The trees `mattpocock-skills@1.3.1` and `pstack@0.15.25` are copied byte for byte into `vendor/upstream/<pkg>@<ver>/`, with their LICENSE files.
  - `THIRD_PARTY_NOTICES.md` is generated from them, and the MIT notices are kept.
  - `pr/CREDITS.md`, which credits Humanlayer `show-me`, is kept with the fork.
- **Verbs.**
  - **keep:** the skill is shipped byte-identical except for the generated regions.
  - **fork:** the skill is copied, then edited.
  - **new:** our own skill.
  - **wrap:** our skill names a kept model-invoked skill and calls it.
- **Every forked skill** carries this in its frontmatter:

  ```yaml
  metadata:
    credits:
      upstream: mattpocock-skills@1.3.1
      path: skills/engineering/to-spec/SKILL.md
      sha256: <of the vendored upstream file>
      license: MIT
  ```

  `t0 gen --check` fails if the vendored file's sha changed without the credits being bumped.
- **Allowed hunks only.** A fork may change only these classes of lines, and each changed hunk is marked with `<!-- t0:fork <class> -->`:
  1. `tracker-pointer`: "tracker doc should have been provided" becomes the `t0`/KB equivalent.
  2. `kb-paths`: `docs/bets/...`, `.scratch/...` and GitHub-issue paths become KB paths obtained from `t0 kb get` (never hard-coded).
  3. `draft-pr`: "mark ready", "commit to current branch", "merge" and "open ready" become draft PR via `t0 pr`, never ready or merge.
  4. `jira-key`: add the regex `[A-Z][A-Z0-9]+-\d+` to spec and ticket lookup, including the branch name.
  5. `ac-bullets`: Gherkin and long user stories become AC bullets, "Como verificar" and Tier.
  6. `t0-call`: replace a computation with a `t0` command.
  7. `privacy`: remove transcript/MCP sweeps and scope logs to the workspace.
  8. `model-slug`: remove grok/opus slugs; add a "same-family" label.
  9. `checkpoint`: force a human checkpoint before implementation.

  `t0 gen --upstream-diff <skill>` shows the diff, and a test fails on unmarked hunks.
- **Instruction prose stays English (upstream text).** Output language comes from the generated header, and user-facing templates (spec, slice, PR body) are pt-BR. This keeps forks small enough to rebase onto a new upstream by hand in minutes.
- **Upstream bump procedure.** Re-vendor, run `t0 gen --check`, which lists the forks whose sha changed, then re-apply the marked hunks. The changeset records the bump.

## The set

Legend for "Ships": **0.1** = this session, **0.2** = next cycle (pilot pod), **0.3** = days 31-90.

| Skill | Purpose (one line) | `t0` calls | Upstream base | Verb + hunks | Ships |
|---|---|---|---|---|---|
| `idea-capture` | Capture an idea with dedup, as a records-lane Idea | `kb find --type Idea --text`, `new idea`, `log` | none | new | **0.1** |
| `bet-new` | Open a bet of one of the 4 types (bugfix: bet + bugfix + single slice) | `kb find`, `new bet [--from IDEA] [--bugfix]`, `kb propose` | none | new | **0.1** |
| `bet-shape` | Intent → spec draft. Restates the goal, grills, sharpens terms/ADRs, 2 sketches, mandatory checkpoint; `--explore` → prototypes + Assessment | `context`, `kb get`, `new spec`, `new adr`, `new assessment`, `log decision`, `kb propose` | MP `grilling` + `domain-modeling` + `prototype` (wrap); PS `architect` Phase B text + `in-your-own-words` | new + fork text (`checkpoint`, `model-slug`) | **0.1** |
| `bet-spec` | Write/finish `spec.md` with AC bullets, "como verificar", tier, seams; show the G2 checklist | `kb get`, `gate G2 --dry-run` (KB.decide), `kb propose` | MP `to-spec` | fork (`tracker-pointer`, `kb-paths`, `ac-bullets`, `t0-call`) | **0.1** |
| `bet-plan` | Plan with bolts and the 4 checks (pass or written exception); Contract when there is a surface | `kb get`, `new plan`, `new contract`, `gate G3 --dry-run`, `kb propose` | PS `architect` (sketch section); Spec Kit gate wording | fork (`model-slug`, `checkpoint`, `t0-call`) | **0.1** |
| `bet-slice` | Vertical slices, one file per slice, `depends_on`, one repo per slice | `new slice` ×N, `kb propose` | MP `to-tickets` (steps 1-4) | fork (`tracker-pointer`, `kb-paths`, `ac-bullets`); Jira branch removed, because sync is CI | **0.1** |
| `gate` | Request any G0-G3, G6-G8 for a target: show the checklist, add the gate file to the current PR | `gate <G> <ref> [--to]`, `kb propose` | none | new | **0.1** |
| `slice-build` | Build one slice: DoR, branch, tdd at seams, audit trail, draft PR with trailers | `bet detect`, `kb get`, `slice start`, `log`, `pr` | MP `implement` (fork); wraps `tdd`, `code-review`, `pr`; PS `show-me-your-work` (`.audit/<KEY>.tsv` committed; `log.sh` kept) | fork (`tracker-pointer`, `draft-pr`, `jira-key`, `privacy`, `model-slug`) | **0.1** |
| `slice-verify` | Review agent: spec adherence + standards; blast-radius proof for Tier 2; log harness occurrences | `kb get`, `report review-queue` (read), `new harness`, `log` | MP `code-review` (fork); PS `blast-radius` (fork) | fork (`jira-key`, `kb-paths`; blast-radius: drop `arena` step and `why` ref) | **0.1** |
| `kb-record` | Record a step or decision (model-invoked); nudges contract-changing decisions to an ADR | `log`, `new adr` | none | new | **0.1** |
| `meeting-record` | Redact a recording deterministically, then extract candidate ideas and ADRs (unverified) for the ritual close | `transcript redact`, `ritual <slug> close --transcript` | `handoff` scanner idea | new | **0.1** (dry-run: nothing persisted) |
| `grilling`, `domain-modeling`, `prototype`, `tdd` | Primitives wrapped by bet-shape and slice-build | none | MP | keep | **0.1** (vendored) |
| `code-review`, `pr` | Primitives for slice-verify and slice-build | none | MP | fork (`jira-key`, `kb-paths`; `pr`: pt-BR headings + `Jira:`, `Tier:`, `Trilha:` lines) | **0.1** |
| `ritual` | ONE skill for every ritual: `ritual <slug> open\|close` (agenda from the Ritual concept; close builds one PR) | `ritual <slug> open\|close`, `transcript redact`, `report …` | none | new | 0.2 |
| `idea-triage` | G0 over the inbox; parked/rejected with a one-line reason; Ritual Record | `kb find`, `gate G0`, `ritual triagem close` | none | new | 0.2 |
| `bet-sync` | Show the Jira plan and wait for keys from KB CI before G3 | `jira sync` (plan), `kb status --wait` | MP `to-tickets` Jira branch (text) | fork (`t0-call`) | 0.2 |
| `pack-setup` | Install the t0 block, pointers, workflows, git hooks into a product repo | `setup [--check]`, `doctor --repo` | MP `setup-matt-pocock-skills` | fork (`tracker-pointer`; GitHub/GitLab branches removed) | 0.2 |
| `handoff` | Session handoff to `$TMPDIR`, or `--plantao` into the KB | `log handoff`, `new ritual-record` (plantão) | MP `handoff` | fork (`privacy` + deterministic scan via `t0 transcript redact --scan-only`) | 0.2 |
| `diagnose` | Red loop → minimise → hypothesis → fix → regression; `--tutor` makes the human write the fix | `log` | MP `diagnosing-bugs` | fork (adds tutor mode only) | 0.2 |
| `adr-new` | Number an ADR and link supersession | `new adr [--supersede]`, `kb propose` | MP `domain-modeling` ADR rules (text) | new | 0.2 |
| `bet-ship` | Freeze the bet spec, update the live product spec, publish the Contract, open the Adoption Report | `kb get`, `new adoption`, `log`, `kb propose` | none | new | 0.3 |
| `harness-fix` | Climb the harness ladder for a Harness Item; draft PR in the right repo | `kb get`, `log`, `kb propose` | MP `retro` + PS `correct` | fork (`privacy`, `draft-pr`) | 0.3 |
| `eval` | `eval run\|add <produto>`: run the suite, record the pass rate, add cases from incidents | `report …`, `kb propose` | none | new | 0.3 |
| `adoption-report` | Measure adoption against the KB Policy floors | `report adoption --commit` | none | new | 0.3 |
| `verify-app-create` | Generate the repo-local `verify-<app>` skill | `log` | PS `create-verification-skill` (+ `maintain-…` for Sweeper) | fork (paths `.cursor` → `.claude`/`.github`, `draft-pr`) | 0.3 |

**Not skills** (CLI or CI only, so the listing stays small):
- `kb-check` (`t0 kb check`)
- `digest` (CI)
- `metrics-snapshot` (inside `ritual demo close`)
- `rotate` (inside `ritual betting close`, plus `kb propose` on a Rotation)
- `kb-search` (MCP `kb_search`)
- `bet-use` (`t0 bet use`, which the card names)
- `trace` (`t0 report trace`)

**Dropped** (methodology §10 "fora do pack", plus the inventory):
- poteto-mode, recall, automate-me, reflect, why, make-bot-ui, no-comments
- interrogate, arena and swarm (until more than one approved model tier exists)
- pstack `tdd`
- the `git-guardrails` skill (its pattern list lives in `hooks.check_git`, with the blanket `git push` block removed)
