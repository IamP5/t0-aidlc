# Repository layouts

Legend: **[gen]** = written only by `t0 gen`, and `t0 gen --check` fails on drift. **[src]** = hand-written. **[vendor]** = byte-identical upstream.

## Toolkit repo `t0-toolkit`

```
t0-toolkit/
  pyproject.toml                 [src] name t0-toolkit, version (THE version: plugin manifests derive from it),
                                       deps: PyYAML, mcp; scripts: t0 = t0.cli:main; import-linter contract
  README.md                      [src] quickstart (usage section of rationale.md)
  THIRD_PARTY_NOTICES.md         [gen] from vendor/upstream/*/LICENSE + metadata.credits
  CHANGELOG.md                   [src]
  .out-of-scope/                 [src] rejected ideas (mattpocock habit): poteto-mode.md, hosted-mcp.md, rulesync.md ...
  docs/
    adr/ADR-0001-event-folded-kb.md   [src] toolkit's own ADRs (mirrored to KB products/t0-toolkit/adr by PR)
    cli.md                       [gen] from cli.COMMANDS
    skills.md                    [gen] from SKILL.md frontmatter
  src/t0/                        [src] the Python package (module map: sketch/MODULES.md)
    __init__.py  kb.py  view.py  check.py  gates.py  context.py  redact.py  render.py  write.py  _forge.py
    ws.py  rituals.py  reports.py  gen.py  hooks.py  mcp_server.py  cli.py
    okf/document.py
    profile/spec.py  profile/table.py
    tracker/port.py  tracker/sync.py  tracker/_jira_rest.py  tracker/_file.py
    templates/                   [src] jinja-free string templates for generated files (hooks.json shapes, workflows)
  plugin/                        the distributable plugin (Claude marketplace, `copilot plugin install`, Kiro power)
    .claude-plugin/plugin.json   [gen] Claude manifest: name t0, version, explicit `skills` list (ships <= current)
    .claude-plugin/marketplace.json [gen] internal marketplace entry (pin by tag)
    plugin.json                  [gen] Agent Plugins 1.0 ($schema, name, version, description, author, keywords)
    mcp.json                     [gen] {"mcpServers":{"t0-kb":{"command":"t0","args":["mcp"]}}}  (Agent Plugins)
    .mcp.json                    [gen] same content (Claude plugin root)
    hooks/hooks.json             [gen] Claude-format registrations -> `t0 hook <name>` (Copilot CLI/VS Code read it)
    agents/                      [gen] review subagents (Claude): standards-reviewer.md, spec-reviewer.md
    com.github.copilot/agents/   [gen] same reviewers as .agent.md (Agent Plugins Copilot namespace)
    skills/
      _shared/header.md          [src] generated-region sources (pt-BR output rule, bet guard, fallback)
      _shared/footer.md          [src]
      idea-capture/SKILL.md      [src + gen regions]
      bet-new/SKILL.md  bet-shape/SKILL.md  bet-spec/SKILL.md  bet-plan/SKILL.md  bet-slice/SKILL.md
      gate/SKILL.md  slice-build/SKILL.md  slice-verify/SKILL.md  kb-record/SKILL.md  meeting-record/SKILL.md
      grilling/ domain-modeling/ prototype/ tdd/          [vendor + gen regions] kept MI primitives
      code-review/ pr/                                    [src fork + gen regions]
      slice-build/references/audit-log.sh                 [vendor] PS show-me-your-work log.sh (CSV-injection guard)
      slice-verify/references/blast-radius.md             [src fork]
  vendor/upstream/
    mattpocock-skills@1.3.1/     [vendor] pristine tree subset + LICENSE (+ pr/CREDITS.md)
    pstack@0.15.25/              [vendor] pristine subset + LICENSE
  templates/okf-kb/              the KB bundle template (below); `t0 setup --kb` copies it into a new t0-kb
  evals/                         `claude plugin eval` suite (plugin.json experimental.evals -> ../evals)
    <case>/prompt.md  <case>/graders/*.md  <case>/scaffold.sh
    mocks/t0-kb/<tool>.md        [gen] recorded from real `t0 mcp` over tests/fixtures/kb-payments
    mocks/t0-kb-down/<tool>.md   [src] error: true mocks (KB unavailable cases)
    results/                     gitignored
  tests/
    unit/ golden/ property/ tracker/ mcp/ hooks/ gen/
    fixtures/
      kb-payments/               a complete fixture bundle: product payments, BET-042 (3 slices, 3 repos), BET-051
                                 bugfix, ideas, rituals, steps, gates; the eval and MCP-mock source of truth
      okf/positive/<case>/       valid bundles (minimal, full, v0.1 fallbacks)
      okf/negative/<rule-id>/    one per check.RULES id (test enumerates RULES; missing fixture = failure)
      redact/corpus/             positive (PII/secret) and negative (false-positive guards) lines
      jira/cassettes/{cloud,dc}/ recorded HTTP for the tracker contract suite
    smoke/                       cross-agent smoke runner (design in evals.md; v0.2)
  .github/workflows/
    ci.yml                       pytest, `t0 gen --check`, `claude plugin validate plugin --strict`, import-linter
    evals.yml                    `claude plugin eval` on PR (label-gated), nightly full
    smoke.yml                    nightly Copilot CLI + kiro-cli smoke (v0.2)
    release.yml                  build wheel + t0.pyz zipapp -> internal registry; tag plugin
    reusable/t0-pr-check.yml     [src] product repos call these at a pinned SHA
    reusable/t0-kb-sync.yml      [src]
    reusable/kb-check.yml  reusable/kb-render.yml  reusable/kb-batch.yml  reusable/jira-reconcile.yml   [src]
```

Packaging bets:

- **One wheel plus one zipapp.** `pipx install t0-toolkit` from the internal registry is the default. `t0.pyz`, built with shiv and carrying vendored PyYAML and mcp, is the fallback for laptops without pipx. Both expose the same `t0` command.
- **The plugin directory contains no Python.** Every hook and the MCP server call `t0` on PATH. `t0 doctor` verifies PATH as each tool sees it, which covers the cases where the IDE was launched from the Dock or from a GUI.
- **Version single-sourced.** The plugin version equals the package version. `t0 doctor` warns when the plugin and the CLI differ.

## OKF KB template `templates/okf-kb/` (becomes `t0-kb`)

```
t0-kb/
  index.md                       [gen by kb-render] frontmatter ONLY `okf_version: "0.2"`; body = sections
  profile.md                     [gen by t0 gen --scope kb] type: OKF Profile, profile t0-team, profile_version 0.2,
                                 timestamps offset-required, link_style bundle-absolute; body = type, gate,
                                 bet-type tables rendered from REGISTRY
  log.md                         [gen by kb-render] type: Log; team events only
  .t0/
    schemas/<type>.json          [gen] JSON Schema per type (editor completion/validation; never authoritative)
    toolkit.lock                 [src] pinned toolkit version + sha used by KB workflows (bumped by PR)
  .github/
    CODEOWNERS                   [src skeleton] /methodology/** steward; /products/<p>/** product lead;
                                 **/bets/BET-*/** bet owner (written by `bet-new` PR); **/gates/** per GateSpec
                                 approver roles; /cycles/*/rituals/** facilitator; NO owner for **/steps/**, /ideas/*.md
    workflows/kb.yml             [gen] check on PR; render + jira sync on main (concurrency kb-render);
                                 nightly reconcile + digest; hourly batch only if fallback enabled
  glossary/                      Glossary Term (bilingual), empty + 3 seed terms (bet, slice, gate)
  methodology/
    methodology.md               Playbook (the methodology document)
    workspace-pattern.md         Playbook (ADR-0002)
    pack.md                      [gen] Reference: every skill + t0 command, from the toolkit (replaces 35
                                 hand-written per-skill playbooks)
    principles/P01-...P10.md     Principle (10)
    practices/                   Practice: dor-dod.md, harness-ladder.md, review-tiers.md, trust-graduation.md
    policies/                    Policy (state proposed): adoption-floors.md (thresholds), eval-gate.md,
                                 transcript-retention.md (ttl P180D, persist: false = dry-run), trust-graduation.md
    rituals/                     Ritual (13): digest, bloqueios, triagem, betting, mob-a, mob-b, mob-construction,
                                 demo, harness-retro, preceptoria, limpeza, sense-respond, pi-outcome
    adr/ADR-0001-kb-sistema-de-registro.md, ADR-0002-workspace-pattern.md, ADR-0003-estado-derivado-de-eventos.md
  team/
    people/  roles/<5 archetypes>.md  accountabilities/<lead,aiva,...>.md  rotations/<flow-steward,sweeper,...>.md
  ideas/                         Idea (records lane, add-only), gates/ (G0 files)
  cycles/<C>/                    cycle.md, report.md, digests/, rituals/, transcripts/, steps/
  products/
    t0-toolkit/                  THE FIRST PRODUCT (customer zero): product.md, workspace.md (repos: t0-toolkit,
                                 t0-kb), spec.md (live), contracts/{t0-cli,t0-kb-mcp,skills}.md, evals.md,
                                 bets/BET-001/ (bet.md "toolkit v0.1", spec.md, plan.md, slices/, gates/, steps/)
  pi/
  harness/                       HI-*.md, trust.md (process:ci only), budget.md
  research/                      Research | Reference (frozen)
```

Bet folder (derived files are never authored):

```
products/<p>/bets/BET-NNN/
  bet.md  bugfix.md|assessment.md|spec.md  plan.md  slices/NN-slug.md     knowledge lane (authored keys + body)
  gates/G1.md G2.md G3.md G6.md                                         knowledge lane, add-only, CODEOWNERS
  steps/<utc-ts>-<handle>-<repo>-<rand4>.md                              records lane, add-only, auto-merge
  index.md  log.md  changeset.md                                        derived (kb-render)
```
