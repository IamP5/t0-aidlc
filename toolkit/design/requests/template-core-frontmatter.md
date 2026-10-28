# Request from template to core: frontmatter keys the fixture assumes

`okf-template/` is written against DESIGN §2 to §5 and methodology §5.3. `profile/table.py` was still the v1 table when I wrote it, so these are my assumptions. Please make the v2 table accept them, or tell me what to rename.

## Common keys

Every concept has `type`, `title`, `description`, `uid`, `owner` and `generated`. `tags` is a YAML list. Stateful types also carry `state` and `status` (status derived as in okf.md §5.4), and `verified` once a human decides. Timestamps carry an offset. Links and path keys are bundle-absolute.

## Per type

| Type | Path | Keys beyond common |
|---|---|---|
| Idea | `/ideas/IDEA-NNNN.md` | `source`, `product`, `verdict`, `prototype_ref`, `decided_at` (top-level, not nested); state `new\|prototyped\|promoted\|killed` |
| Bet | `/products/<p>/bets/BET-NNN/bet.md` | `track`, `appetite`, `hypothesis`, `kill_criteria`, `success_metric`, `decision_by`, `jira`, `relations.from_idea` |
| Spec | `.../spec.md` | `bet`, `acceptance[]`, `verify_how`, `seams[]`, `markers_open`, `tier` |
| Slice | `.../slices/NN-slug.md` | `bet`, `repo`, `tier`, `acceptance[]`, `verify_how`, `depends_on[]` (slice file stems), `jira`, `pr`, `audit`; rapida adds `current`, `expected`, `unchanged[]` |
| ADR | `/products/<p>/adr/ADR-NNNN-slug.md` | `number`, `deciders[]`, `decided_at` |
| Ritual | `/rituals/<slug>/ritual.md` | `cadence` (RRULE, or `external:art` for pi), `duration`, `facilitator`, `participants[]`, `command`, `recorded`, `transcribable`, `inputs[] {id, source, desc}`, `outputs[]`, `stale_after` |
| Ritual Record | `/rituals/<slug>/YYYY-MM-DD.md` | `ritual`, `date`, `facilitator`, `attended[]`, `decisions[] {text, owner, due}`, `transcript` |
| Transcript | `/transcripts/YYYY-MM-DD-<ritual>.md` | `ritual`, `redaction`, `off_record_spans`, `participants[]`, `stale_after` |
| Harness Item | `/harness/HI-NNNN.md` | `pattern`, `ladder_step`, `occurrences[]`, `pr` |
| Product | `/products/<p>/product.md` | `stage`, `adoption_stage`, `repos[]`, `domain_contacts[]` |
| Workspace | `/products/<p>/workspace.md` | `workspace {schema, product, jira_project, forge, default_branch, repos[], groups}` |
| Eval Suite | `/products/<p>/evals.md` | `repo_path`, `metric`, optional `repo`; derived `regression_size`, `regression_pass`, `last_run` |
| Adoption Report | `/products/<p>/adoption/YYYY-Www.md` | `adoption_stage`, `wau`, `target_cohort`, `retention_4w`, `repeat_use` |
| Policy | `/methodology/policies/<slug>.md` | `stale_after`, `thresholds` for numbers, plus per-policy keys: `persist`, `lgpd_signoff` (transcript-retention), `mode`, `batch`, `auto` (records-lane), the six role keys and `families_approved` (models) |
| Template | `/templates/<name>.md` | `template_for`, `skeleton` (frontmatter map); body is the markdown skeleton |
| Person | `/team/people/<handle>.md` | `handle`, `pods[]`, `junior`, state `active\|alumni` |
| Role | `/team/roles/<slug>.md` | `responsibilities[]`, `rotates`, `rotation` |
| Rotation | `/team/rotations/<slug>.md` | `role`, `cadence`, `roster[]`, `assignments[] {who, from, to}`, `stale_after` |
| Glossary Term | `/glossary/<slug>.md` | `term`, `term_en`, `aliases[]`, `avoid[]`, `scope` |
| Step | `.../steps/<utc-ts>-<handle>-<repo>-<rand4>.md`, `/steps/<utc-ts>-<handle>-<rand4>.md` | `kind`, `bet`, `story`, `repo`, `refs[]`, `target`, `dedup`, `payload`, `on_behalf_of`; uid keeps the uppercase `T`/`Z` of the workspace-pattern example |
| Log | `/log.md`, `.../BET-NNN/log.md` | frontmatter with common keys (decides G13 the sample's way) |
| Reference | methodology docs, practices, `/harness/budget.md` | `sources[]` |

## Decisions for you

1. There is no Practice type in the 20, so `methodology/practices/*.md` and `harness/budget.md` are typed `Reference`. Add a type if you want them checked more tightly.
2. `acceptance` lives in frontmatter and as body bullets. A L2 rule that compares the two would catch drift.
3. Uids: `idea-0001`, `bet-001`, `bet-001-slice-01`, `bet-002-spec`, `adr-0001`, `hi-0001`, `policy-<slug>`, `ritual-<slug>`, `ritual-<slug>-YYYY-MM-DD`. BET numbers are global across products.
4. I did not write `profile.md`, `.t0/` or `.github/workflows/kb.yml`. They are [gen], so integration needs `t0 gen --scope kb --out okf-template` once the v2 table lands. The root `index.md` and `log.md` are hand-written, and render may overwrite them.
5. Empty directories hold `.gitkeep` files. The checker should ignore files that are not `.md`.
