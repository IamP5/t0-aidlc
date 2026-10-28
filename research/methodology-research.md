# Methodology research: gaps and corrections for the AIDLC operating model

Date: 2026-10-27. Scope: checks `research/living-doc.md` against current (2025–2026) primary sources.
Convention: every claim carries a URL that was actually fetched for this note, or is marked **(unverified)**. "(secondary)" means the fetched URL is not the original author's own publication.

---

## 1. AWS AI-DLC

### What the sources say

- **Original framing (Jul 2025).** Three phases. **Inception:** AI turns business intent into requirements, stories and units through **Mob Elaboration**, where "the entire team actively validates AI's questions and proposals". **Construction:** AI proposes architecture, domain model, code and tests through **Mob Construction**, where the team settles technical and architectural decisions in real time. **Operations:** AI manages IaC and deployments under team oversight. **Bolts** replace sprints ("measured in hours or days rather than weeks"). **Units of Work** replace epics. No formal human roles are defined. — https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/
- **Open-source rules (Nov 2025).** Shipped as Amazon Q Rules and Kiro steering files. Every stage runs one loop: AI plans and asks questions, humans clarify, AI refines, humans approve, AI executes, humans verify. "Human approvals are embedded at every decision gate", and every human action is recorded. Depth adapts to the work (Principle 10, "No Hard-Wired, Opinionated SDLC Workflows"): a simple defect fix skips elaborate requirements analysis. — https://aws.amazon.com/blogs/devops/open-sourcing-adaptive-workflows-for-ai-driven-development-life-cycle-ai-dlc
- **Current version (v2.x; badge reads 2.11.1).** The README describes **5 phases / 33 stages**, **11 workflow profiles**, 14 agents (11 domain experts, 2 reviewers, 1 composer), a 126-event audit trail, persistent state, team knowledge and learned rules. — https://github.com/awslabs/aidlc-workflows
  - The phases are now **Initialization, Ideation, Inception, Construction, Operation**. — https://awslabs.github.io/aidlc-workflows/
  - Per-intent records live under `aidlc/spaces/<space>/intents/<YYMMDD>-<label>/`, state in `aidlc-state.md`, decisions in `audit/` shards. "A mob of 3-5 people covers an entire feature." — https://awslabs.github.io/aidlc-workflows/guide/00-introduction/
- **Inception stages (v2).** 2.1 Reverse Engineering (brownfield only), 2.2 Practices Discovery (writes `team-practices.md`, `discovered-rules.md` and promotes them to `team.md`/`project.md`), 2.3 Requirements Analysis (**always**: `requirements.md`, questions file, `traceability.json`), 2.4 User Stories (conditional), 2.5 UX (conditional), 2.6 Domain Design (conditional: `components.md`, `decisions.md` ADR log), 2.7 **Units Generation (always)**, 2.8 **Contract Design** (skipped only for a single self-contained unit with no public API), 2.9 **Delivery Planning (always)**: `bolt-plan.md`, `team-allocation.md`, `risk-and-sequencing-rationale.md`, plus a phase-boundary check. Every stage ends in an Approve / Request Changes gate. — https://awslabs.github.io/aidlc-workflows/reference/04-stages/inception/
- **Bolt, precisely.** "Planned Construction delivery slice" made of one or more Units, **each with a Definition of Done, a confidence hypothesis, and an owner**. Each Bolt runs in its own worktree (`.aidlc/worktrees/bolt-<id8>_<slug>`). Execution order follows the Unit dependency graph, not the Bolt grouping. — https://awslabs.github.io/aidlc-workflows/reference/04-stages/construction/ and the Inception URL above
- **Construction stages.** 3.1 Functional Design, 3.2 NFR Requirements, 3.3 NFR Design, 3.4 Infra Design (all conditional), 3.5 Code Generation (always, per Unit, with **plan approval per Unit**), 3.6 Build & Test (always, once after all Units), 3.7 CI Pipeline (conditional). The v2 reference does **not** use the term "Mob Construction". It describes team-owned Units instead: teams claim Units through git refs, publish when done, and main validates and lands them behind **one human merge gate**. — https://awslabs.github.io/aidlc-workflows/reference/04-stages/construction/
- **Profiles.** Classic (15 stages, the v1-style default), Express (7: skips Ideation, design, unit decomposition and delivery planning), Bugfix (6), Refactor (7), PoC (5), MVP (20), Feature (30), Enterprise (30, comprehensive, "regulated or high-assurance"), Security Patch (7), Infrastructure (10), Workshop (23). — https://awslabs.github.io/aidlc-workflows/guide/workflow-profiles/
- **Facilitated sessions.** These are run as a "workshop": a facilitator does a readiness pass before the day, teams bring a vision note and a tech-environment note, and Standard depth asks about 5–8 questions per stage (Minimal: 2–4). After each group correction the tool asks "Keep that for next time?", which is a built-in learned-rule loop. No duration or group size is given. — https://awslabs.github.io/aidlc-workflows/guide/facilitator-guide/

### Where the draft is wrong or thin

- It says "three phases". That holds for the 2025 blog; v2 has five (Initialization and Ideation were added).
- It uses "bolt" as a loose time word. In AI-DLC a bolt is a **planned artifact**: DoD + confidence hypothesis + owner.
- Mob Elaboration in the draft compresses intent → spec → plan → slices into one 60–90 min meeting. AI-DLC puts a **gate after every stage** and treats Units and Contracts as distinct outputs. The draft has no **contract** artifact, though MCPs and CLIs consumed by 130+ squads are exactly public interfaces.
- Mob Construction is absent from the draft. Its v2 replacement (claim Unit → publish → single human merge gate) maps well onto cross-pod work.
- The draft runs one DoR/DoD for every bet. AI-DLC's main lesson is **adaptive depth by profile**.

---

## 2. AI-Native SAFe (Scaled Agile, 2026)

### Verifiable

- **AI-Native Team.** "Three to seven team members, augmented with AI", which explicitly "does not imply a reduction in the workforce". Humans stay in the loop. Work flows through **Align** ("make key decisions and maintain a shared direction"), **Sense** ("use data and feedback to monitor products, workflows, and the user environment") and **Respond** ("adjust their workflows based on insights"). — https://framework.scaledagile.com/ain-safe-ai-native-teams
- **Four team capabilities** (capabilities, not roles): **Product** (the "why", vision, synthesizing customer feedback), **Builder** (uses AI to produce outputs), **Domain Expert** (turns generic AI proposals into fit-for-purpose ones), **AI** (supervised automation of "tedious, repetitive tasks within clear guidelines"). Teams organize around flow activities "instead of fixed meeting intervals". — https://framework.scaledagile.com/blog/ai-native-safe-session-3-ai-native-teams-roles-and-arts (Session 3 aired 14 Jul 2026; post published 21 Jul 2026)
- **AI Value Architect (AIVA).** Exists to close the gap between AI investment and value. Its responsibilities: *coaching AI adoption* ("a coaching discipline rather than a training exercise"), unlocking value in AI features already inside existing tools, bridging business and tech on risk, legal, data and ethics, facilitating AI solution development (flagging data-quality shift, model drift, **evaluation gaps**), and optimizing outcomes. The course was scheduled for 25 Aug 2026. — same URL
- **Sense and Respond.** A **2-hour ART event held at least once every iteration**. The first hour senses (metrics, customer feedback, demos); the second responds (pivots, capacity). The RTE facilitates; AI-Native Teams, PM, System Architects, Business Owners and **AI Value Architects** attend. It **replaces the half-day Inspect & Adapt** and **absorbs the System Demo**. — https://framework.scaledagile.com/ain-safe-sense-and-respond
- **PI Outcome Planning.** **One day** (replaces the 2-day PI Planning). Teams "establish commitments to measurable PI and team outcomes", not features, and the event ends with a confidence vote. — https://framework.scaledagile.com/ain-safe-pi-outcome-planning
- Iteration length, PI length and team-level metrics for AI-Native ARTs are not stated on the public pages; parts sit behind login. Secondary claims of "1-week iterations / ~1-month PI" are **(unverified)**.

### Where the draft is wrong or thin

- **AIVA is mis-assigned.** The draft gives "Lead / AI Value Architect" to the tech lead who chooses bets and owns architecture. In SAFe the AIVA is an **adoption-coaching and value-realization role at ART level**, and it attends Sense & Respond and PI Outcome Planning. For this team the closest fit is whoever owns **squad adoption** (the Insights & Enablement pod), not the architect.
- **The SAFe mapping table is out of date** if the ART adopts AI-Native SAFe. System Demo and I&A collapse into Sense & Respond every iteration, and PI Planning becomes outcome commitments. That **weakens** the draft's argument that SAFe means "Feature commitment closed in the PI": AI-Native SAFe asks for *outcomes*, and the team's adoption numbers are exactly such outcomes. The "SAFe outside" recommendation still holds, but the interface should be outcomes, not mirrored Features.
- **The capability check is missing.** No pod has an explicit **Product** capability (who owns the "why" and synthesizes squad feedback?), and the Domain Expert appears only as a Mob Elaboration guest.
- Pods of 3 sit at the **floor** of SAFe's 3–7 range. That is defensible, but it should be stated, because a single absence halves a pod's review capacity.

---

## 3. Spec-driven development (Spec Kit, Kiro, BMAD, Tessl)

- **Taxonomy (Böckeler, Thoughtworks, 15 Oct 2025).**
  - *Spec-first*: written up front, used for the task.
  - *Spec-anchored*: kept and evolved with the feature.
  - *Spec-as-source*: humans edit only the spec.
  - She also separates **specs** (per change) from **memory banks** (project-wide context).
  - Her critiques: one workflow for every size (Kiro turned a small bug into 4 stories / 16 acceptance criteria; Spec Kit was overkill for a 3–5-point feature), **markdown review overload** ("would rather review code"), a false sense of control (the agent ignored notes or over-applied the constitution), and spec-as-source non-determinism.
  - — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- **Spec Kit.**
  - Commands: `/speckit-constitution` (once per project) → `specify` → `plan` → `tasks` → `implement` → **`/speckit-converge`**, which loops until the report says "Converged".
  - Separate flows: bugs (`.specify/bugs/<slug>/`, verdict verified/partial/failed) and **idea assessment** (`.specify/assessments/<slug>/`, decision **go / needs-clarification / kill**).
  - A "Spec Kit 1.0" video is dated 16 Oct 2026.
  - — https://github.com/github/spec-kit
- **Spec Kit gates.** The plan template has "Phase -1: Pre-Implementation Gates": **Simplicity Gate** (≤3 projects, no future-proofing), **Anti-Abstraction Gate** (use the framework directly), **Integration-First Gate** (contracts and contract tests defined) and **Test-First** (tests confirmed failing before implementation). Specs must mark ambiguity as `[NEEDS CLARIFICATION: …]`, and a spec is not complete while any marker remains. A failed gate needs a justified exception in "Complexity Tracking". — https://github.com/github/spec-kit/blob/main/spec-driven.md
- **Kiro.** Three files per spec: `requirements.md` (or **`bugfix.md`**, which records *current, expected and unchanged* behavior), `design.md` and `tasks.md`. There are Requirements-First and Design-First variants, plus a "Quick Spec" that skips approval gates. tasks.md becomes a dependency graph executed in parallel waves. — https://kiro.dev/docs/specs/
- **BMAD.**
  - MIT licensed, ~54.6k stars, stable v6.12, V7 alpha.
  - It is scale-adaptive: "go directly to implementation for clear changes or add deeper planning for larger initiatives".
  - A "BMad Loop" module builds, verifies and retros an epic unattended.
  - The README does not list its named personas.
  - — https://github.com/bmad-code-org/BMAD-METHOD
- **Tessl.** A spec registry of "tiles" (`tessl-labs/spec-driven-development` 2.0.x with eval scenarios). The spec-as-source regeneration engine is described as closed-beta and non-deterministic. **(unverified: search snippets only, pages not fetched)**
- **Thoughtworks Radar Vol. 34** placing SDD in "Assess" is **(unverified: secondary)**.

**Fit for a 10-person team.**
- Keep spec-first per bet and **spec-anchored only for long-lived products** (each MCP/CLI/skill keeps a living `spec.md` + contract).
- Take three cheap mechanisms: `[NEEDS CLARIFICATION]` markers, the constitution gates as a plan checklist, and Kiro's "unchanged behavior" bugfix template.
- Take the go/needs-clarification/kill assessment as the Prototyper's output format.
- Do **not** adopt spec-as-source or BMAD's persona chain. Both add markdown review load that the team, already review-bound, cannot absorb.

---

## 4. AI-native team practice: rituals, review load, evals, adoption

### Anthropic, Claude Code team

- **Dogfooding.** First prototype around Sep 2024; dogfood build in Nov 2024. Adoption was ~**20% of Engineering on day one and ~50% by day five**, but these were observations, **not gates** (no formal shipping threshold is stated). Other figures: ~60–100 internal releases/day, ~5 PRs/engineer/day, ~20 prototypes of the todo feature in two days. — https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built
- **Ship gate and review (Cat Wu & Thariq, Jul 2026).**
  - Features ship only with strong retention in the employee cohort: "an internal bar for the number of active users and the amount of retention". The number itself is not disclosed.
  - Review: an automated review bot reviews every PR, code owners approve sensitive areas (e.g., the system prompt), and **trust in automated review is earned per file area** ("when a review system catches all issues in a file area, humans can step back").
  - **Incident PRs are added to eval sets.** User feedback is ranked and turned into evals, and a new model must be strictly better on the eval set before swapping in.
  - Launch calendars and status updates are automated.
  - — https://simonwillison.net/2026/jul/21/cat-and-thariq/
- **Five archetypes.** Cherny's post (around 28 Jun 2026, x.com/bcherny/status/2071379474277613732) names Prototyper, Builder, Sweeper ("unships features"), Grower and Maintainer. Most people span 2–3. **Stage mixes:** pre-PMF = Prototyper + Builder + Sweeper; post-PMF = Builder + Sweeper + Grower; mature = Sweeper + Grower + Maintainer. — https://braindetox.kr/en/posts/claude_code_work_archetypes_2026.html (secondary; the X post was not fetched)
- "Customer zero" as a term, and the Product School / Meaghan Choi claims ("3 months internal", "minimum daily internal users"), could **not** be verified. **(unverified)**

### Anthropic, organization-wide

- **Employment report (16 Oct 2026).**
  - Agent hours outnumber human hours 6:1, and sessions are ~**80% idle waiting for human input**.
  - Meta-work went from 10% to **22%** of sessions, and meeting time rose **+20%** (+16% for technical ICs).
  - Standing agent instructions grew from a few hundred to **8,500** in a year.
  - "Private work, in unlogged meetings and direct messages, is invisible, confusing and discouraged."
  - Junior share of technical hires fell from 27% to **9%**.
  - — https://www.anthropic.com/research/employment-at-anthropic
- **Internal survey (Dec 2025, data from Aug 2025).**
  - More than half can "fully delegate" only **0–20%** of their work.
  - One engineer moved "70%+" of their work to reviewing and revising code.
  - "Paradox of supervision": oversight needs the very skills that atrophy.
  - Merged PRs per engineer per day rose **+67%**.
  - — https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic

### Evals for agent tooling

- **Getting started:** **20–50 tasks drawn from real failures**, with both positive and negative cases. A 0% pass rate usually signals a broken task, so build a reference solution.
- **Two suites:** **capability evals** start low and are something to climb; **regression evals** sit near 100%. Graduate a capability eval into the regression suite once it saturates.
- **Graders:** prefer deterministic graders. Use an LLM judge per dimension with an "Unknown" option, and humans sparingly. Grade outcomes, not paths.
- **Metric choice:** **pass@k** fits when one good result is enough; **pass^k** fits when consistency matters (75% per trial gives ~42% for all 3).
- **Ownership:** an evals team owns the infrastructure, while product and domain people contribute tasks. Treat eval maintenance like unit tests.
- **Eval-driven development:** write evals before the capability exists.
- — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

### OpenAI harness engineering

- **Team and throughput:** 3 engineers (Aug 2025) grew to 7 over five months, producing ~1M LOC with zero hand-written code at ~**3.5 PRs/engineer/day**.
- **Repo layout:** a ~100-line AGENTS.md as a table of contents ("progressive disclosure"). `docs/` holds `design-docs/`, `exec-plans/{active,completed}/`, `tech-debt-tracker.md`, `generated/`, `product-specs/`, `references/`, `QUALITY_SCORE.md`.
- **Review and enforcement:** agent-to-agent review loop. Custom linters carry remediation text written for the agent, and background tasks open refactor PRs on a schedule.
- **Mindset:** "What Codex can't see doesn't exist."
- — https://ericfode.github.io/agent-harness-wiki/raw/articles/openai-harness-engineering (mirror; openai.com returned 403)
- The "~1,500 PRs" total in the draft is **(unverified)**: the mirror gives no total.

### Measurement

- **DX AI Measurement Framework.** Primary adoption metric is **DAU/WAU**, and "Total logins can be misleading". Cohorts: none/light/moderate/heavy. The page gives **no benchmark threshold**. — https://getdx.com/blog/how-to-implement-ai-measurement-framework/
- **"Leading orgs plateau around 60% weekly active usage"** (attributed to DX) is **(unverified: secondary snippets only)**.
- **Faros.** 10K developers across 1,255 teams; "twice as many code changes, but company metrics remain flat". — https://www.faros.ai/ai-productivity-paradox
  - The widely quoted "+91% PR review time, +154% PR size" is **(unverified)**: those figures are not on that page.
- **DORA AI Capabilities (23 Sep 2025).** Seven capabilities: clear AI stance, healthy data ecosystems, AI-accessible internal data, strong version control, small batches, user-centric focus, quality internal platforms. "Without user-centric focus, AI adoption can have a negative impact." — https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model
  - The draft's "raises throughput *and* instability" comes from the full DORA report and is **(unverified)** here.

---

## 5. Knowledge and context management

- **AGENTS.md** is now stewarded by the **Agentic AI Foundation (Linux Foundation)** and used by "over 60k open-source projects". Nested files are allowed ("closest AGENTS.md to the edited file wins"), and the user's prompt overrides all of them. — https://agents.md/
- **Claude Code guidance.**
  - Keep CLAUDE.md to what Claude "couldn't work out from the code". Stay **under 200 lines**; `/doctor` suggests cuts.
  - Use `.claude/rules/` with `paths:` for area-specific rules, and skills for long procedures (they load on demand).
  - **"If something has to happen every time, make it a hook, a deny rule, or a managed setting"**; CLAUDE.md lines are guidelines Claude may decide not to apply. If you add emphasis and Claude still misses a line, it belongs in a hook. "If you ever find yourself at forty [hooks/deny rules], most are probably preferences."
  - Review in a fresh subagent with read-only tools, against SPEC.md, with "skip style", because a reviewer asked to find problems "will always find something".
  - — https://code.claude.com/docs/en/best-practices
- **Context engineering.** Find "the smallest set of high-signal tokens". Context rot means attention is a budget. Use just-in-time retrieval through references, compaction, structured note-taking outside the window, and sub-agents returning distilled summaries. — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Harness = guides + sensors (Böckeler, 2 Apr 2026).**
  - Guides are feedforward (AGENTS.md, skills, codemods); sensors are feedback (linters, ArchUnit, AI review). Each can be computational or inferential, and you need both.
  - "Whenever an issue happens **multiple times**, the feedforward and feedback controls should be improved."
  - Keep quality left: cheap sensors pre-integration, expensive ones (mutation, architecture review) post-integration, drift monitored continuously.
  - — https://martinfowler.com/articles/harness-engineering.html
- **AI-DLC** keeps team knowledge as files promoted through a gate (`team.md`, `project.md`, `discovered-rules.md`) plus per-intent `traceability.json` and an audit log. That is a ready model for a bank's audit trail. — https://awslabs.github.io/aidlc-workflows/reference/04-stages/inception/

**Where the draft is wrong or thin.**
- "Every agent error → a rule in CLAUDE.md" will bloat context. Anthropic's own instructions reached 8,500.
- The correct ladder is: second occurrence → prefer a **computational sensor** (lint/test/hook) → then a path-scoped rule or skill → CLAUDE.md as last resort.
- The draft also lacks a budget for context artifacts and a canonical-file decision (AGENTS.md vs CLAUDE.md).

---

## 6. Risks: skill atrophy, review bottleneck, juniors

- **Skill formation RCT (Anthropic, 29 Jan 2026).**
  - Setup: 52 mostly junior engineers learning the Trio library. The AI group scored **50% vs 67%** (d = 0.738, p = 0.01) and was only ~2 min faster (not significant). The largest gap was on **debugging** questions.
  - Patterns that preserved learning: *generation-then-comprehension* (~86%), *hybrid code + explanation* (~68%), *conceptual inquiry* (~65%).
  - Patterns that destroyed it: *full delegation* (~39%), *progressive reliance* (~35%), *iterative AI debugging* (~24%).
  - — https://www.anthropic.com/research/AI-assistance-coding-skills
- **Supervision paradox and self-reported atrophy;** some engineers practice without AI on purpose. — https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- **Preceptor model.** Russinovich & Hanselman (CACM opinion, early 2026) propose pairing early-career developers with senior preceptors at **3:1–5:1** and an "EiC mode" in which assistants coach instead of complete. **(unverified: secondary coverage only)**
- **Review bottleneck.** Agents sit ~80% idle on humans (employment report above). Claude Code's answer is a review bot on every PR, code owners on sensitive areas, per-area trust graduation and incidents fed into evals (Simon Willison URL above).

---

## Deltas for our model

**Roles**

1. **Split "Lead / AI Value Architect".**
   - Keep **Lead** (bets, architecture, ART interface).
   - Give **AI Value Architect** to the person who owns squad adoption (Insights & Enablement). This matches SAFe's definition: adoption coaching, value realization, flagging eval gaps. That person represents the team at the ART's Sense & Respond and PI Outcome Planning.
2. **Add a named Product capability per pod.** It can be the Bet Owner on rotation, but explicitly owns the "why" and synthesizes squad feedback. The **Domain Expert** is a standing pod contact (one squad tech lead per pilot), not just a Mob Elaboration guest.
3. **Set archetype mix by product stage (Cherny).**
   - Dev Tooling and Insights are growth stage: Builder + Sweeper + Grower.
   - Agent Platform is heading to mature: Maintainer + Sweeper + Grower.
   - New exploratory bets are Prototyper + Builder + Sweeper.
   - Replace the current "everyone declares one archetype" with "each pod must cover its stage mix".
4. **Add an Eval Owner per product.** Usually the Maintainer or Grower. They own its regression suite. Infrastructure for evals is a shared Agent Platform concern.
5. **Add a preceptor pairing.** Every junior or early-career developer has a named senior preceptor (≤3 juniors per senior across the 10). This lives inside pods, not as a separate track.

**Rituals**

6. **Add Sense & Respond attendance (2h/iteration, ART-level).** It replaces System Demo and I&A if the ART adopts AI-Native SAFe. The team Demo then becomes its input, not a separate System Demo artifact. The ritual budget becomes ~3h team + 2h for the Lead and AIVA only.
7. **Split Mob Elaboration into two gated steps (AI-DLC).**
   - **(a)** Intent → requirements + clarifications, with a gate.
   - **(b)** Units/slices + **contracts** + bolt plan, with a gate.
   - Run (b) async if (a) leaves no `[NEEDS CLARIFICATION]`.
   - Add **Mob Construction** only for Tier 2 or cross-pod contract work: the pods meet live to settle the contract before parallel builds.
8. **Add an eval review to the Harness Retro.** Every escaped defect or incident in a team-built tool becomes an eval case before the retro closes, mirroring Claude Code's "incident PRs → eval set".
9. **Use the Prototyper output format** go / needs-clarification / kill (Spec Kit assessment). Kill decisions are logged so the Sweeper has a record.

**Artifacts**

10. **Bolt plan per bet** (`bolt-plan.md`). Each bolt states its **DoD, confidence hypothesis and owner**. This replaces the loose "bolts of hours/days".
11. **Contract file per public surface** (`contract.md` for each MCP tool, CLI and skill interface consumed by squads). Breaking a contract requires Tier 2 review.
12. **Bet profiles with adaptive depth** (AI-DLC Express/Bugfix/Refactor/PoC; Kiro Quick Spec).
    - **Explore**: prototype + assessment only.
    - **Fix**: `bugfix.md` with current, expected and *unchanged* behavior.
    - **Feature**: intent/spec/plan/tasks/contract.
    - **Regulated**: Feature + NFR + audit.
    - Tier 0 work never requires `plan.md`. This answers Böckeler's markdown-overload critique.
13. **Spec-anchored product specs.** Each long-lived tool keeps `docs/products/<tool>/spec.md` + `contract.md` + `evals/`. Bet folders are spec-first and archived after ship.
14. **Context budget, codified.**
    - AGENTS.md is canonical (LF standard, tool-neutral); CLAUDE.md only imports or points to it.
    - Root file ≤150 lines, which leaves headroom under Claude Code's 200-line guidance.
    - Area rules in `.claude/rules/` with `paths:`.
    - Enforced hooks/deny rules ≤20 per repo.
    - The Sweeper reports these counts every cycle.
15. **Audit trail.** Keep show-me-your-work TSV, but add AI-DLC-style `traceability.json` (requirement → slice → PR → test) for Tier 2 bets. Bank auditors will ask for exactly that chain.

**Gates**

16. **Harness ladder replaces "every error → CLAUDE.md".**
    - On the **second** occurrence (Böckeler), add a computational sensor first (lint with agent-readable remediation, test, hook).
    - If that is impossible, a path-scoped rule or skill.
    - CLAUDE.md last.
    - Rules with zero exceptions go into hooks/deny rules, never CLAUDE.md.
17. **DoR adds "no `[NEEDS CLARIFICATION]` markers"** and the four Spec Kit plan gates as a checklist: simplicity, anti-abstraction, contract defined, failing test first. Exceptions are written into the plan.
18. **Eval gate for agent tooling.**
    - No skill, MCP or agent goes to pilot squads without a **regression suite of 20–50 tasks** from real usage and failures, at ≥95% pass.
    - For customer-facing agents, report **pass^3**, not pass@1.
    - Model upgrades and prompt changes ship only if regression results are equal or better (Claude Code's "strictly better on the eval set").
19. **Per-area review trust graduation** (replaces fixed Tier 0 lists).
    - A code area moves to "agent review + batch human merge" after **20 consecutive agent-reviewed PRs with zero escaped defects**.
    - It drops back on the first escaped defect.
    - This proposed number operationalizes Claude Code's "humans step back per file area".
20. **Adoption gates (customer zero), with concrete numbers.** "Active" means the user invoked the tool on real work in a given ISO week. Telemetry, not logins: DX warns logins mislead.
    - **Degrau 1 → 2 (team → pilot squads):** ≥**7 of 10** team members WAU for **2 consecutive weeks**, and the eval gate (item 18) passes.
    - **Degrau 2 → 3 (pilot → ART):** in 2–3 pilot squads, **≥40% of the target developers WAU for 3 consecutive weeks**, and **≥50% four-week retention** (share of week-1 users still active in week 4).
    - **Episodic tools** (e.g., a migration skill): replace WAU with **repeat use**, ≥2 separate weeks out of 4 among users who had a qualifying task.
    - **Sunset floor (Sweeper):** <**15%** WAU of the target cohort, or <5 absolute WAU, after 8 weeks in pilot → unship or merge into a general tool.
    - **Rationale:**
      - Claude Code went from 20% to 50% of Anthropic Engineering in five days of organic use (Pragmatic Engineer, observation not gate). A team-internal bar of 70% is reasonable because the team is the most motivated cohort.
      - DX reports even leading orgs plateau near ~60% weekly active (unverified). A 40% pilot gate sits well under that ceiling while clearing a one-week novelty spike.
      - Anthropic's own gate pairs active users **with retention**, hence the 4-week retention clause.
      - Revisit after 3 tools have passed through, and publish the numbers to the ART as PI outcomes.

**Metrics**

21. **Add a utilization/impact/cost triad (DX).**
    - Per tool: WAU, 4-week retention, repeat-use rate, cohort split (none/light/moderate/heavy).
    - Per squad: time saved, self-reported and sampled.
    - Cost per active user.
    - These are what the AIVA reports at Sense & Respond.
22. **Add review-load SLOs.**
    - Median PR wait for first human review ≤4 working hours.
    - Human review minutes per PR (target ≤15 for Tier 1).
    - % of PRs where the agent review found the issue before the human did.
    - "Agent idle on human" from session telemetry (Anthropic: ~80%). This makes the "human attention is the bottleneck" principle measurable.
23. **Add harness-health metrics.** CLAUDE.md/AGENTS.md line counts, hook count, rule-recurrence rate, eval suite size and pass rate per tool, and evals added per cycle.
24. **Add skill-health metrics** (atrophy mitigation, from the Anthropic RCT patterns).
    - % of Tier 1–2 PRs with an author "explain-back" section (pstack `in-your-own-words` is already in the toolkit; make it mandatory for Tier 2 and for anyone under preceptorship).
    - Juniors do **first-pass debugging without delegating** (the largest RCT gap). Agents explain; juniors fix.
    - One slice per person per cycle in "tutor mode": conceptual questions allowed, code generation not.
    - Maintainer on-call rotation includes juniors with a preceptor.
    - Track participation, not scores.
25. **Fix sources in the draft.**
    - Cite Cherny's X post (not Aakash Gupta) for archetypes.
    - Cite Cat Wu/Thariq via simonwillison.net for the retention gate.
    - Mark "customer zero", "3 months internal" and the Product School DAU claim as unverified until the podcast transcript is checked.
    - Drop "~1,500 PRs" or source it.
    - Update AI-DLC to v2 (5 phases, profiles).
    - Update the SAFe mapping to Sense & Respond / PI Outcome Planning.
