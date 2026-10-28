---
type: Research
title: "Workspace topology: KB repo plus multi-repo products"
description: Compares ways to put an OKF knowledge-base repo next to 5-6 product repos (submodules, subtree, manifest tools, monorepo, MCP-served KB, hybrids), judged on agent context quality, dev friction, cross-repo change, CI, access control, onboarding and KB freshness. Ends with a recommendation.
tags: [repo-topology, submodules, monorepo, workspace, agent-context, research]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-27T00:00:00Z }
sources:
  - id: git-book-submodules
    resource: https://git-scm.com/book/en/v2/Git-Tools-Submodules
    title: Pro Git, Git Tools - Submodules
  - id: git-subtree
    resource: https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc
    title: git-subtree documentation (git contrib)
  - id: west-why
    resource: https://docs.zephyrproject.org/latest/develop/west/why.html
    title: Zephyr, "History and Motivation" for west
  - id: west-manifest
    resource: https://docs.zephyrproject.org/latest/develop/west/manifest.html
    title: Zephyr west manifest reference
  - id: android-repo
    resource: https://source.android.com/docs/setup/reference/repo
    title: Android repo command reference
  - id: meta
    resource: https://github.com/mateodelnorte/meta
    title: meta (mateodelnorte/meta) README
  - id: cc-large
    resource: https://code.claude.com/docs/en/large-codebases.md
    title: Claude Code docs, "Set up Claude Code in a monorepo or large codebase"
  - id: cc-workflows
    resource: https://code.claude.com/docs/en/common-workflows
    title: Claude Code docs, "Common workflows" (worktrees)
  - id: openai-harness
    resource: https://ericfode.github.io/agent-harness-wiki/raw/articles/openai-harness-engineering
    title: Mirror of OpenAI "Harness engineering: leveraging Codex in an agent-first world" (openai.com returned 403)
  - id: nx-ai
    resource: https://nx.dev/blog/nx-and-ai-why-they-work-together
    title: Nx blog, "Nx and AI: why they work together"
  - id: nx-effect
    resource: https://nx.dev/blog/the-effect-of-monorepos-on-the-effectiveness-of-ai-agents
    title: Nx blog, "The effect of monorepos on the effectiveness of AI agents"
  - id: nx-polygraph
    resource: https://nx.dev/blog/nx-cloud-introducing-polygraph
    title: Nx blog, "Introducing Polygraph"
  - id: sg-mcp
    resource: https://sourcegraph.com/mcp
    title: Sourcegraph MCP product page
---

# Workspace topology: KB repo plus multi-repo products

**Question.** The team asked: "Can we have the OKF repo with git submodules for our project repos? Is there a better strategy?"

**Short answer.** Yes, it works mechanically, but it is the wrong direction for this team. It makes the KB repo carry code pointers it does not own, and every agent and developer pays the submodule tax (detached HEAD, pointer bumps, recursive init, access failures) on every task. A better setup is a **manifest-driven workspace**: a small manifest per product (which can live in the KB repo) plus a bootstrap script. The script clones the KB and the product repos as siblings, and the agent config for the workspace root is generated. Product repos then reference bets by ID. For CI and remote agents, the KB is also served read-only over MCP. See §9.

Provenance tags: **(web: id)** means a source in frontmatter that I actually fetched. **(inferred)** is my own reasoning or general knowledge that I did not verify against a source in this session.

---

## 0. Constraints that drive the choice

1. **The KB must be in context on every interaction.** That covers rituals, spec writing and code generation, so the agent needs both the KB and the code in one session. OpenAI's harness post puts it as "What Codex can't see doesn't exist," and it encodes decisions as markdown in the repo, with a roughly 100-line AGENTS.md acting as a "Table of Contents" (web: openai-harness).
2. **One bet often touches 3 of a product's 5-6 repos**, so cross-repo change coordination is the common case.
3. **Bank access control is per repo.** Not every dev or agent identity can read every repo, and CI runners use scoped tokens (inferred, typical of regulated environments).
4. **SAFe/Jira sits outside the team.** Jira keys are the shared IDs. Bets live in the KB.
5. **Team size is about 10 devs.** Tooling has to be maintainable by the team itself, with no platform team behind it.

---

## A. KB repo with git submodules of the product repos (the user's idea)

**How it works.** `kb/` is the superproject, with `products/payments/{api,web,worker,...}` added as submodules. The superproject stores each submodule as a gitlink: "a particular commit from that repository", stored in mode `160000` (web: git-book-submodules).

**Day to day (devs).**
- Cloning requires `--recurse-submodules` or `git submodule update --init --recursive`. Plain `git pull` and branch switches do not update submodules unless you pass `--recurse-submodules` or set `submodule.recurse true` (web: git-book-submodules).
- `submodule update` leaves each repo in **detached HEAD**. Per Pro Git, commits made there "will quite possibly be lost the next time you run `git submodule update`" (web: git-book-submodules). Devs have to remember to run `git checkout <branch>` inside each repo before working.
- To make others see newer code, someone has to commit a pointer bump in the KB repo. That puts code-sync noise into the KB history and creates merge conflicts on gitlinks, which "Git will not auto-merge" (web: git-book-submodules).
- Pushing the KB without first pushing the submodule commits breaks everyone else. Pro Git recommends `push.recurseSubmodules on-demand` or `check` to prevent this (web: git-book-submodules).

**Day to day (coding agents).**
- Agents tend to commit wherever HEAD is. In a detached submodule, that produces orphaned commits that get silently dropped on the next update (inferred from web: git-book-submodules).
- Worktrees: `claude --worktree` and similar per-task worktrees create a new checkout of the **superproject**, and submodules in it are uninitialised until someone runs `submodule update --init` (inferred; the Claude Code worktree docs describe worktrees as "a separate checkout on its own branch" (web: cc-workflows) and say nothing about submodules). Parallel agents on different bets also share one pointer set per KB branch.
- Context: starting at the KB root loads the KB CLAUDE.md, plus product-repo CLAUDE.md files on demand (web: cc-large). That part is good. But every session sees every product, which costs context unless you add `claudeMdExcludes` (web: cc-large).
- A cross-repo PR means an agent opens N product PRs plus one KB PR for the pointer bump, and has to sequence them.

**CI.** Product-repo CI is unaffected because product repos don't know about the KB. KB CI that checks out submodules needs a token that can read **all** product repos (inferred). That is a cross-cutting credential a bank security review will object to.

**Access control.** `.gitmodules` exposes every product repo URL to anyone who can read the KB. A dev without access to one repo gets a hard failure on `submodule update --init` unless they hand-pick paths (inferred). The KB, which should be the most widely readable artifact, ends up gated by the least readable product.

**Failure modes.**
- Commits made on a detached HEAD get lost.
- Pointers go stale: the KB pins code from weeks ago and agents reason over old code.
- Someone forgets `--recurse-submodules`, which leaves empty directories, and an agent concludes "the repo is empty".
- Pointer bumps cause merge conflicts.
- KB history fills up with "bump api" commits.
- One product's access policy blocks KB clones.

**Verdict.** It works, but it inverts ownership, because the KB ends up versioning code. Avoid it.

## B. Inverse: each product repo includes the KB (submodule or subtree)

**How it works.** Each of the 5-6 product repos runs `git submodule add kb docs/kb` (or uses subtree, see C).

**Pros.** Any session opened in a product repo has the KB on disk, and product CI can lint spec references against it. Access control is simple because the KB is broadly readable.

**Cons.**
- **KB freshness is the main problem.** Each product repo pins its own KB SHA, so six repos can sit on six different versions of the methodology and bet specs. Ritual outputs land in the KB daily, and a pointer that is days old means the agent codes against a stale spec (inferred).
- A KB edit made from a product session, like updating `tasks.md` while coding, has to be committed inside the submodule, which is detached by default (web: git-book-submodules), pushed to the KB, and then bumped in the product. That is three steps every time.
- You need bump automation, a bot that opens a "bump KB" PR in 6 repos on every KB merge, which means a lot of PR noise. Many teams turn the automatic bump off and then the pointers go stale (inferred).
- Context: the agent sees one product repo plus the KB, but not the sibling repos the bet also touches.

**Verdict.** Better than A for access control, but worse for freshness, and it still lacks sibling-repo context. Use only for a read-only, release-pinned "methodology" slice, if at all.

## C. git subtree

**How it works.** `git subtree add -P docs/kb <kb-remote> main --squash` copies the KB's content into the product repo. `pull` merges upstream, and `split`/`push` sends local edits back (web: git-subtree).

**Pros.** Subtrees "do not force end-users of your repository to do anything special" (web: git-subtree). There is no `.gitmodules`, no detached HEAD, and clones just work. CI needs no extra token.

**Cons.**
- The KB is **copied** into 6 repos. Freshness depends on someone running `subtree pull` in each repo, and in practice it drifts (inferred).
- Edits flowing back are fragile. Commits that mix KB and code changes make split histories confusing, and the docs advise committing them separately. Mixing `--squash` across merge and `split --rejoin` has rules you must follow consistently (web: git-subtree). Agents will not reliably keep KB and code changes in separate commits (inferred).
- It inflates each product repo's history with KB commits unless you use `--squash`.

**Verdict.** It fits vendoring a slow-moving, read-only artifact. That might be the methodology plus glossary, published on a version tag. It does not fit a living bet/spec KB that receives writes from code sessions.

## D. Workspace manifest tools and the plain workspace repo

All of these share one model. A **manifest** lists repos (and optionally revisions). A tool or script clones them as **siblings** under one workspace directory, and each repo stays a normal clone on normal branches. Nothing gets committed into anyone else's history.

| Tool | Manifest | Notes |
|---|---|---|
| **Google `repo`** (Android) | XML in a manifest repo, `repo init -u <url> -m <file> -b <branch>` | `repo start <branch>` creates a topic branch across the projects you name. `repo upload --topic` groups related changes, but it **assumes Gerrit**. Android advises against mixing `git submodule` with repo (web: android-repo). Zephyr also notes repo assumes Gerrit and is weak on Windows (web: west-why). |
| **`west`** (Zephyr) | `west.yml`: `projects` with `revision` (branch, tag, SHA or PR ref), `import`, `group-filter` | `west update` checks out pinned revisions **as detached HEAD by default** "to avoid conflicting with local branch names". `--freeze` pins every project to a SHA. Groups make projects inactive, so they are skipped (web: west-manifest). Zephyr built west because submodules "require hardcoding the paths", can't track the latest HEAD, and are hard for downstreams to override (web: west-why). |
| **`meta`** | `.meta` JSON listing projects, with child dirs gitignored | `meta git clone` clones the parent and all children. `meta exec "<cmd>" --parallel`, `--include-only`. Node plugins (web: meta). |
| `gita`, `mu-repo`, `vcstool`, `myrepos` (`mr`) | gita: registered paths. vcstool: `.repos` YAML. mr: `.mrconfig` | Bulk status/pull/exec across many clones. vcstool (ROS) has a `.repos` manifest with versions. None do cross-repo PRs (inferred; not fetched this session). |
| **Plain workspace repo** | `workspace.yaml` plus `bootstrap.sh` (about 50 lines: clone if missing, fetch otherwise) | No dependencies and fully auditable, which matters for bank tooling approval. The script can skip repos that return 403 and keep going (inferred). |

**Day to day (devs).** `./bootstrap payments` gives you `~/ws/payments/{kb,api,web,worker,...}`, all on normal branches, and you work in each repo as usual. The script skips repos the user can't read and prints a warning, so per-repo ACLs don't break the setup. There are no pointer bumps unless you choose to pin.

**Day to day (agents).** Start the agent at the workspace root, or in one repo with `--add-dir ../kb ../web`. Claude Code supports `--add-dir` / `additionalDirectories` for "a separately checked-out repository". Note that `additionalDirectories` **never** loads the added dir's CLAUDE.md or skills. `--add-dir` loads skills, and loads CLAUDE.md only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` (web: cc-large). A workspace root that is not itself a git repo has no git context for worktrees. Per-task worktrees then have to be created per repo, or the root has to be a tiny git repo itself (inferred).

**Cross-repo change.** Use one branch name across repos. Android's `repo start` does exactly this (web: android-repo), and `meta exec "git checkout -b bet/PAY-123-limits"` or the bootstrap script does the same thing. PRs stay separate, with a GitHub/GitLab-agnostic link convention (see §8).

**CI.** Unchanged per product repo. Only an optional "integration" job needs multi-repo read.

**Failure modes.** Siblings at different points in time ("my api is from last week"). Fix this with a `ws sync` step at session start. With west/repo, people may not realise they're on a detached pinned revision (web: west-manifest). Manifests can also drift from reality when a new repo is added and nobody updates the manifest (inferred).

**Verdict.** This is the right building block. For a 10-person team, use a plain script or `meta`. `west` and `repo` are heavier than needed, and `repo` effectively requires Gerrit.

## E. Monorepo consolidation per product (Nx, Turborepo, Bazel)

**How it works.** Merge a product's 5-6 repos into one, keeping history with `git subtree add` or filter-repo (inferred). Tooling handles affected-only builds: Nx and Turborepo for JS/TS-heavy stacks, Bazel for polyglot, hermetic builds.

**What vendors claim.** Nx argues that monorepos give agents "consolidated context" and a "map" of architecture, ownership and CI, and that polyrepo cross-cutting changes are "effortful and non-atomic" (web: nx-ai). A second Nx post says "every repo boundary wipes the agent's context", says cross-project changes can be up to about 20% of commits, and reports a "4x faster" demo. It also admits its own synthetic-monorepo product gives an "eventually consistent" result rather than atomic changes (web: nx-effect). These are vendor claims backed by small demos with no methodology.

**When it's worth it.** It pays when a product's repos **share an owner, release cadence and language toolchain**, and when bets routinely change 3+ of them at once, which is this team's case. Cross-repo changes become one PR and one review, and the agent sees everything (web: nx-effect, framing; applicability inferred).

**When it is not.** It doesn't pay when repos have different deploy pipelines owned by other bank teams, different access populations (a core-banking adapter readable only by a subset), or regulatory change-management records tied to the existing repo identity (inferred). Migrating is a one-off cost of a few days per product plus CI rework. With Bazel it is weeks (inferred).

**KB placement.** Even with a product monorepo, the KB stays separate because it spans products and teams. So you still need D, F or G for the KB.

## F. No co-location: KB served via MCP/HTTP, or as a package

**How it works.** A small read-only MCP server (or HTTP endpoint) over the KB's git `main` exposes tools like `kb_search`, `kb_get(path)` and `bet_get(BET-ID)` (intent/spec/plan/tasks) and `glossary_lookup`. Product repos carry only a thin AGENTS.md that tells the agent to query the KB for the bet in the branch name. An alternative is publishing a versioned KB package (npm/pip/OCI artifact) that CI pulls.

**Precedent.** Claude Code's large-codebase guide recommends exactly this escape hatch: "if your organization already runs a code search or RAG index … expose it as an MCP tool so Claude queries it instead of reading files directly" (web: cc-large). Sourcegraph MCP gives "cross-repository code intelligence through the open Model Context Protocol" (search, go-to-definition across repos) (web: sg-mcp). That is the same pattern applied to code.

**Pros.** The KB is always fresh because it reads `main`. Nothing is cloned into product repos. Access control is enforced centrally at the server. It works the same for local agents, CI agents and cloud agents.

**Cons.** Agents don't see KB files unless they call the tool. "Every interaction" then depends on hooks or instructions that force the call. A `SessionStart` hook can print context into the session (web: cc-large). Writing back to the KB (ritual records, task status) needs a write path with review, so prefer PRs to the KB repo over direct writes. It is also one more service to run and get approved in a bank (inferred).

**Verdict.** It is the best channel for **CI and remote agents**, and a good complement locally. On its own it is weaker for heavy interactive spec writing, which goes better with the files on disk.

## G. Hybrids (recommended shape)

**Workspace = manifest + KB clone + generated agent config.**

```
kb/                         # OKF bundle (own repo, broadly readable)
  workspaces/
    payments.yaml           # repos, default branch, groups, roles
    onboarding.yaml
  tools/ws                  # bootstrap/sync/branch/pr script
~/ws/payments/              # created by `kb/tools/ws init payments`
  kb/                       # sibling clone of the KB (normal branch)
  api/ web/ worker/ ...     # sibling clones, normal branches, skipped if 403
  CLAUDE.md / AGENTS.md     # GENERATED: ~100-line map -> kb paths, repo roles, conventions
  .claude/settings.json     # GENERATED: additionalDirectories, claudeMdExcludes, SessionStart hook
```

- The generated root AGENTS.md is a short **map** rather than a full manual, following the OpenAI harness pattern (web: openai-harness). It points to `kb/methodology/`, `kb/bets/<id>/`, the glossary and ADRs, and lists each repo's role.
- A `SessionStart` hook prints the current bet (derived from the branch name `bet/PAY-123-*`) and its `intent.md`/`spec.md` paths into context (mechanism: web: cc-large; usage inferred).
- Each product repo keeps its own thin AGENTS.md covering build/test commands, plus one line: "Bet specs live in the KB; if `../kb` exists read `../kb/bets/<id>/`, else use the `kb` MCP server." That way a single-repo session degrades gracefully.
- An MCP server (F) serves CI and remote agents.
- Optionally, products that qualify per E graduate to a monorepo later, and the workspace manifest just shrinks to `kb` + `product-monorepo`.

---

## 8. Cross-repo change coordination (one bet touches 3 repos)

| Pattern | How | Who uses it |
|---|---|---|
| **Shared branch name** | `bet/<JIRA-KEY>-<slug>` in every touched repo. `ws branch PAY-123-limits` runs `git switch -c` in the repos listed in the bet's `plan.md` | Android `repo start` (web: android-repo); meta `exec` (web: meta) |
| **Topic / change set** | Group related changes under one topic ID. Gerrit topics via `repo upload --topic` (web: android-repo). Off Gerrit: the Jira key in every PR title plus a `kb/bets/<id>/changeset.md` listing PR URLs, merge order and status | Android; Polygraph "opens a PR in each" repo and tests downstream before merge (web: nx-polygraph) |
| **Linked PRs with merge order** | Each PR body holds `Bet: PAY-123`, `Depends-on: <url>` and `Merge order: 2/3`. A CI check fails if a dependency is unmerged (inferred) | Common in polyrepo orgs (inferred) |
| **Backward-compatible sequencing** | Expand, migrate, contract: ship the provider change first behind compatibility, then consumers, then remove the old path. Each PR is independently safe (inferred) | Standard practice for APIs |
| **Pinned integration manifest** | A frozen manifest (`west manifest --freeze`-style SHAs) for "this set of SHAs was tested together" (web: west-manifest), stored in `changeset.md` | Zephyr/Chromium-style pinning |
| **Atomic (monorepo only)** | One PR | E |

**How the big multi-repo projects do it.**
- **Android:** `repo` plus an XML manifest. Projects don't nest, and Android advises against submodules. Topic branches are created with `repo start`, and changes go to Gerrit, grouped by `--topic` (web: android-repo).
- **Zephyr:** `west` and a `west.yml` in the main zephyr repo. Pinned revisions are checked out detached. Imports and groups let downstreams compose and override. West was built because submodules and `repo` fell short (web: west-why, west-manifest).
- **Chromium:** `gclient` with a `.gclient` file and a `DEPS` file in `src/` that pins dependency revisions. `gclient sync` checks them out, and dependency "rolls" are automated CLs that bump pins (inferred: the depot_tools README fetch returned 503, so this is from general knowledge).

All three projects pick a **manifest + sibling clones**. None use submodules for the main workflow.

---

## 9. Comparison

Scale: ++ strong, + ok, 0 neutral, - weak, -- poor. "Agent context" means the agent can see the KB plus every repo a bet touches in one session.

| Criterion | A. KB ⊃ submodules | B. Product ⊃ KB submodule | C. Subtree | D. Manifest workspace | E. Product monorepo (+KB via D/F) | F. KB via MCP only | G. Hybrid (D + gen. config + F) |
|---|---|---|---|---|---|---|---|
| Agent context quality | + (all on disk, but code may be stale) | 0 (KB + 1 repo, KB stale) | 0 (KB copy + 1 repo) | + (all on disk, fresh) | ++ (one tree) | - (KB only via tool calls, 1 repo) | ++ (on disk + map + hook + MCP fallback) |
| Dev friction | -- (detached HEAD, recurse flags, bumps) | - (bumps x6) | 0 (transparent reads, painful writes) | + (normal clones, one script) | + after migration | ++ (nothing to clone) | + |
| Cross-repo change | - (N PRs + pointer PR) | - | - | + (shared branch + changeset) | ++ (atomic) | 0 | + |
| CI | - (KB CI needs all-repo token) | - (bump bots, checkout auth) | + | + (unchanged) | 0 (rework, affected builds) | + | + |
| Access control (per-repo ACL) | -- (KB gated by every product, URLs exposed) | + | + | ++ (skip what you can't read) | - (merges ACL populations) | ++ (central) | ++ |
| Onboarding | - (submodule literacy) | 0 | + | + (`ws init <product>`) | ++ | ++ | + |
| KB freshness | + (KB is the root) | -- (6 pins) | -- (6 copies) | + (sync at start) | per D/F | ++ (reads main) | ++ |

---

## 10. Recommendation

1. **Don't put product repos as submodules inside the KB repo.** It inverts ownership, exposes every repo to the KB's audience, and fills KB history with pointer bumps. Every agent session also inherits detached-HEAD and recursive-init hazards (web: git-book-submodules). Android, Zephyr and Chromium all avoid submodules for this job (web: android-repo, west-why).
2. **Adopt G.** Keep the KB as its own broadly readable repo. Add `kb/workspaces/<product>.yaml` and a small `ws` script (`init`, `sync`, `branch <BET>`, `status`, `pr`) that clones the KB and the product repos as siblings and generates the workspace-root `AGENTS.md`/`CLAUDE.md` map, `.claude/settings.json` (`additionalDirectories`, `claudeMdExcludes`) and a `SessionStart` hook that injects the current bet. Start with a plain script. Switch to `meta` only if the script grows past about 150 lines.
3. **Product repos reference bets by ID**, never by copying specs. Use the branch name `bet/<JIRA-KEY>-<slug>`, `Bet: <KEY>` in commit trailers and PR bodies, and `kb/bets/<id>/changeset.md` listing PRs, merge order and tested SHAs. Each product repo's AGENTS.md has a two-line fallback: use `../kb` if present, else the KB MCP server.
4. **Stand up a read-only KB MCP server** (search, get, bet lookup, glossary) for CI and remote agents. Make KB writes go through PRs to the KB repo.
5. **Re-evaluate E per product after 2-3 bets.** If a product's bets touch 3 or more of its repos most of the time, and those repos share owners, pipeline and ACL population, consolidate that product into a monorepo. Keep the KB separate regardless.
6. Use subtree (C) only to vendor a **tagged, read-only methodology/glossary release** into repos that must build offline. Don't use it for living bet specs.

Open questions for the team:
- Is the forge GitHub, GitLab or Bitbucket? That decides whether linked-PR checks are a native feature or a custom CI step.
- Will security approve a long-lived MCP service?
- Which repos have restricted read populations? Those repos decide whether the E candidates are real.
