---
type: Research
title: "Open Knowledge Format (OKF): spec summary and team-profile proposal"
description: What OKF is, its normative rules (v0.2), what our local harness encodes (v0.1), the gaps, and a proposed team profile for methodology, team and project knowledge.
tags: [okf, knowledge-management, research]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-27T00:00:00Z }
sources:
  - id: spec-v02
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: OKF v0.2 SPEC.md (canonical repo)
    author: team:google-cloud-data-cloud
    last_modified: 2026-08-21T00:00:00Z
  - id: spec-v01
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/ee67a5ca27/okf/SPEC.md
    title: OKF v0.1 SPEC.md (original import, 2026-06-12)
  - id: frozen
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
    title: Frozen OKF snapshot in knowledge-catalog (README says stop using it)
  - id: blog
    resource: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
    title: "Introducing the Open Knowledge Format" (Google Cloud blog, 2026-06-12)
  - id: ref-code
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/src/reference_agent/bundle
    title: Reference agent bundle code (document.py, index.py, paths.py)
  - id: issues
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/issues
    title: Open OKF issues and proposals
  - id: local-skill
    resource: /Users/tuba/.claude/skills/setup-agent-harness/
    title: setup-agent-harness skill (local)
---

# Open Knowledge Format (OKF): spec summary and team profile

Provenance tags used throughout:
- **(local skill)**: from `/Users/tuba/.claude/skills/setup-agent-harness/`. The copy at `/Users/tuba/.agents/skills/setup-agent-harness/` is identical for OKF purposes; the only diffs are `CLAUDE.md`/`.claude` vs `AGENTS.md`/`.Codex` naming in SKILL.md.
- **(web: URL)**: from the cited source. The spec text was fetched directly through the GitHub API, and the canonical v0.2 `SPEC.md` matches the frozen snapshot byte for byte.
- **(inferred)**: my reading or recommendation, not stated by any source.

`/Users/tuba/.agents/skills/harness-creator/` has no OKF content (rg found no matches). It uses a different model (`feature-list.json`, `progress.md`), and setup-agent-harness explicitly rejects it.

---

## 1. What OKF is, and where it comes from

- **Definition.** OKF is "an open, human- and agent-friendly format for representing knowledge". A bundle is a directory of markdown files with YAML frontmatter, with no schema registry, central authority, or required tooling. (web: [SPEC §0](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md))
- **Publisher.** Google Cloud's Data Cloud team. The announcement post, "Introducing the Open Knowledge Format", went out on **2026-06-12** and was written by Sam McVeety and Amir Hormati. It calls OKF "vendor-neutral" and a "starting point, not a finished standard". The only concrete adoption it names is Google Cloud Knowledge Catalog, which can ingest OKF. (web: [blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing))
- **License.** Apache-2.0. (web: GitHub repo metadata)
- **Version history.** (web: GitHub commit history)
  - **v0.1**: imported into `GoogleCloudPlatform/knowledge-catalog/okf/` on 2026-06-12 (commit `ee67a5ca27`).
  - **v0.2**: migrated on 2026-07-24 (commit `780fe9d30b`, PR #227).
  - **2026-08-21 tightening**: every timestamp became an ISO 8601 datetime with an explicit offset (commit `62432a09`, PR #323 / #6). This was not given a version bump. Issue #24 points out that `okf_version: "0.2"` now names two different documents.
- **Canonical home moved.** Since about 2026-08-14 the canonical repo has been **[GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format)**. The `knowledge-catalog/okf/` README now says: "Stop using the copy under `okf/` … It is a frozen snapshot." (web: [frozen README](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf))
- **Current version: 0.2.** No v0.3 spec is published yet. Open proposals include #51 `sections` registry, #52 `priority`/`scope`, #49 `language`, #45/#46 source `digest`/`revision`, #30 typed relationships, #28 `revised`, and #53 `transferable`. (web: [issues](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues))
- **Other things named OKF.** "OKF/OKFN" is also the common abbreviation for the **Open Knowledge Foundation**, which publishes Frictionless Data Package and is unrelated. Search results note that metadata on one of Google's own v0.2 pages mislabels the spec as an Open Knowledge Foundation spec. **The local usage matches Google's OKF**: SKILL.md links `GoogleCloudPlatform/knowledge-catalog/tree/main/okf`. (local skill; web: search results such as [specification.website](https://specification.website/spec/agent-readiness/okf-bundle/) and [nowledge.co](https://nowledge.co/blog/open-knowledge-format))
- **Third-party ecosystem.** Exporters such as Nowledge Mem and Hjarni, plus a skills.sh "okf-open-knowledge-format" skill. These come from secondary sources only and were not verified. (web: search results)

### Drift between our local harness and the current spec (important)

| Topic | Local skill encodes | Current spec (v0.2) |
|---|---|---|
| Version | `okf_version: "0.1"` | 0.2. The v0.1 rules are still consumable through §13 fallbacks. |
| Spec link | `knowledge-catalog/tree/main/okf` | That copy is frozen. Use `open-knowledge-format`. |
| Last-change time | `timestamp:` | Superseded by `generated: { by, at }`. Consumers MAY fall back to `timestamp` (§13.1). |
| Citations | not used | `# Citations` is superseded by `sources` plus footnotes (§13.1). |
| Lifecycle | ADR `status: accepted \| proposed` | §5.4 defines `status: draft \| stable \| deprecated`, and absent means `stable`. **Collision**: a spec-aware consumer would read `accepted`/`proposed` as unknown values, or treat a proposed ADR as stable. (inferred) |
| Links | relative (`./x.md`) | Both forms are allowed, and bundle-absolute (`/x.md`) is *recommended* (§6.1). |
| `log.md` | forbidden by local convention | Optional (§9). |

---

## 2. Normative rules (OKF v0.2)

Everything in this section cites the spec (web: [SPEC.md](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)) unless it is tagged otherwise.

### 2.1 Bundle and manifest
- A **bundle** is a self-contained directory tree of markdown files. It can be shipped as a git repo (recommended), a tarball or zip, or a subdirectory of a larger repo (§3).
- **There is no manifest file.** The only bundle-level metadata is an optional `okf_version: "0.2"` key in the frontmatter of the bundle-root `index.md`. That is the only place frontmatter is allowed in an index (§8, §12).
- Consumers that don't understand the declared version SHOULD attempt best-effort consumption (§12).
- Versioning is `<major>.<minor>`: a minor bump is backward-compatible and a major bump may break (§12).

### 2.2 Directory layout
- Layout is **domain-free**: "producers organize concepts however makes sense" (§3). OKF has no fixed taxonomy (§1 non-goals).
- **Reserved filenames** at any level: `index.md` (directory listing) and `log.md` (update history). They MUST NOT be used for concept documents. Every other `.md` file is a concept (§3.1).
- **`references/`** is a conventional, non-required subdirectory that mirrors external material, run instructions, or code (§6.3).
- Tag pages are not specified. Consumers synthesize them from `tags` (§3.1).

### 2.3 Concepts and IDs
- A **concept** is one UTF-8 markdown file, made of a frontmatter block (`---` … `---`) followed by a markdown body (§4).
- The **Concept ID** is the file's path within the bundle minus `.md`, for example `tables/customers` (§2). **There is no separate `id` field.** Renaming or moving a file changes its identity. (inferred)
- The reference code validates each ID segment against `[A-Za-z0-9_][A-Za-z0-9_.\-]*` (web: [paths.py](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/src/reference_agent/bundle/paths.py)). This rule exists only in the code, not the spec.

### 2.4 Frontmatter schema

| Field | Type | Status | Notes |
|---|---|---|---|
| `type` | string, non-empty | **REQUIRED** | Not centrally registered. Consumers MUST tolerate unknown types (§4.1). Examples: `BigQuery Table`, `Metric`, `Playbook`, `Reference`, `Attested Computation`. |
| `title` | string | recommended | Consumers MAY derive a title from the filename. |
| `description` | string (one sentence) | recommended | Reused by index entries and search snippets. |
| `resource` | URI or path | recommended | Canonical URI of the underlying asset. Omit for abstract concepts. |
| `tags` | list of strings | recommended | Must be a YAML list. Issue #39 shows the failure mode of a comma-separated string. |
| `sources[]` | list of maps | optional (§5.1) | Each entry: `resource` (REQUIRED within an entry; a URL, a path, or a scope descriptor), `id` (SHOULD be present when the body cites it), `title`, `author` (actor), `usage_count` (int), `last_modified` (datetime). |
| `usage_window` | `{from, to}` datetimes | optional | Sibling of `sources`. An individual entry may override it. |
| `generated` | `{by: actor, at: datetime}` | optional (§5.2) | `by` is REQUIRED inside the map. `at` is the last meaningful content change. |
| `verified` | list of `{by, at}`, or a single map | optional (§5.2) | Consumers MUST treat a bare map as a one-element list. |
| `status` | `draft \| stable \| deprecated` | optional (§5.4) | Absent means `stable`. |
| `stale_after` | datetime | optional (§5.5) | The concept is stale when `now >= stale_after`. |
| `runtime`, `parameters[] {name,type,required}`, `computation`, `executor {resource, receipt[]}`, `attester {resource}` | | only for `type: Attested Computation` (§10.2) | `runtime` is required for that type. |
| any other key | any | allowed | Consumers SHOULD preserve unknown keys and MUST NOT reject them (§4.1). |

- **Timestamps.** Every timestamp-valued key is an ISO 8601 datetime with an explicit offset, for example `2026-06-30T14:00:00Z` (§5).
- **Actors (§7).** `<producer>/<version>` for agents and tools, `human:<id>` for people, `process:<id>` for automated processes. Producers MUST use `human:` for human-authored or human-confirmed content. The spec examples also use `team:<id>` for `author`, but §7 does not define that prefix. (inferred)
- **Trust tier (§5.3)**, which is derived and never stored:
  - no `verified` means **unverified**
  - only non-`human:` verifiers means **machine-confirmed**
  - any `human:` verifier means **human-reviewed**
- **Body (§4.2).** Free markdown, with structure preferred. The conventional headings are `# Schema`, `# Examples`, and `# Computation`. Per-claim attribution uses a footnote whose label equals a `sources[].id`, for example `[^ga4-schema]` (§5.1).

### 2.5 Index files (§8)
- Optional. Allowed in any directory. They have **no frontmatter**, except `okf_version` in the bundle root.
- Body format: one or more `# Section` headings, each followed by `* [Title](relative-url) - short description`. Subdirectories are listed as `* [Subdir](subdir/) - …`.
- Entries SHOULD reuse the target's frontmatter `description`. Indexes MAY be auto-generated, and consumers MAY synthesize them when missing.

### 2.6 Log files (§9)
- Optional `log.md` at any level, as a flat list of date-grouped entries, newest first.
- Date headings MUST use the form `## YYYY-MM-DD`. A leading bold verb (`**Update**`, `**Creation**`, `**Deprecation**`) is conventional, not required.
- The spec does not say whether `log.md` may have frontmatter. The official `acme_retail/log.md` sample does carry frontmatter (`type: Log`). (web: [sample](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/log.md))

### 2.7 Links and references (§6)
- Use standard markdown links in one of two forms:
  - **bundle-absolute**, `/tables/customers.md`, which is RECOMMENDED because it stays stable when files move within their subdirectory
  - **relative**, `./other.md`
- Links are **untyped** directed edges. The kind of relationship is carried by the surrounding prose (§6.1).
- **Broken links are legal** and consumers MUST tolerate them, because a broken link may point at knowledge not yet written.
- Path-valued fields (`resource`, `sources[].resource`, `computation`, `executor.resource`, `attester.resource`) accept an absolute URL, a `/`-rooted bundle path, or a relative path (§6.2).
- Issue #29 notes that the spec examples write non-slash paths as bundle-root-relative while §6.2 calls them file-relative. Avoid the ambiguity by always using `/` or `./` explicitly. (inferred)

### 2.8 Conformance (§11): a single permissive level
A bundle conforms to v0.2 if:
1. every non-reserved `.md` file contains a **parseable** YAML frontmatter block,
2. every frontmatter block has a **non-empty `type`**, and
3. `index.md` and `log.md` follow §8 and §9 when they are present.

Consumer obligations:
- MUST treat a bare `verified` map as a list.
- MUST NOT reject a document for missing optional families, unknown types, unknown keys, broken links, or missing indexes.
- SHOULD derive trust and staleness only from the spec fields.
- SHOULD surface, not silently drop, a failing attestation.

Everything else is soft guidance. **The spec defines no conformance levels or profiles**, and the attestation runtime protocol is deferred (§12).

---

## 3. Reference conformance logic found

### 3.1 Local: `okf-check.sh` (local skill)
Source: `/Users/tuba/.claude/skills/setup-agent-harness/templates/okf-check.sh`. It is installed to `.t0-harness/knowledge/okf-check.sh` and run by `init.sh`. Logic path:

```bash
cd "$(dirname "$0")/../.."          # assumes .t0-harness/knowledge/ location
BUNDLE="docs"
for f in $(find docs -name '*.md' | sort):
  if basename in {index.md, log.md}:
     if first line == '---' and f != docs/index.md -> FAIL "reserved file must not have frontmatter"
     continue
  if first line != '---'              -> FAIL "missing YAML frontmatter"
  awk: scan lines 2..next '---'; require /^type:[[:space:]]*[^[:space:]]/  else FAIL "no non-empty type"
exit fail
```

Its validation rules (references/validation.md) require the check to pass, plus a negative test: strip the frontmatter from one document and confirm the check fails.

**Weaknesses (inferred):**
- It does not actually YAML-parse, so an unterminated block or invalid YAML still passes. That is weaker than §11.1.
- `type: ""` and `type: ~` pass the regex.
- It does not check index body structure (§8) or log date headings (§9).
- It bans frontmatter in `log.md`, which the spec does not require, and the official sample violates that rule.
- It does not cross-check index descriptions against frontmatter.
- It ignores `okf_version` and does not validate `status` values or datetime format.

### 3.2 Official reference code (web: [ref-code](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main/src/reference_agent/bundle))
The repo ships no standalone validator. The relevant logic sits in `document.py`, `index.py`, and `paths.py`.

**`OKFDocument.parse`:**
- If line 1 is not `---`, it treats the file as having no frontmatter (body only).
- It looks for the next `---`. If none is found, it raises "Unterminated YAML frontmatter block".
- It runs `yaml.load` with a SafeLoader *with the timestamp resolver removed*, so datetimes stay strings and round-trip exactly.
- It raises on a YAMLError or on a non-mapping result. Issue #38 notes that falsy non-mappings slip through because of `or {}`.

**`validate()`:** `REQUIRED_FRONTMATTER_KEYS = ("type",)`. Any key that is not truthy raises "Missing required frontmatter keys".

**`normalize_verified`:** a dict becomes `[dict]`, a list keeps only its dict entries, and anything else becomes `[]`.

**`trust_tier`:** no events gives `unverified`; any `by` starting with `human:` gives `human-reviewed`; otherwise `machine-confirmed`.

**`is_stale`:**
- It requires a `T` in the value, a successful `fromisoformat`, and a non-null tzinfo. Otherwise it returns False, because date-only values are ignored rather than guessed.
- If those checks pass, it returns `now >= stale_after`.

**`regenerate_indexes`:**
- It walks directories deepest first.
- For each directory it groups child `.md` files by `type`, with an "Other" fallback, and adds subdirectories under a `# Subdirectories` heading.
- It writes `# <Type>` sections containing `* [title or stem](file.md) - description` lines, sorted by title.
- Subdirectory descriptions are LLM-synthesized unless the subdirectory has a single entry.
- It overwrites the root index and **drops `okf_version`** (issue #25).

**`paths.py`:** checks each concept ID segment against `[A-Za-z0-9_][A-Za-z0-9_.\-]*`.

---

## 4. Gaps: where the spec is silent and we must define a profile

| # | Gap | Why it matters for us |
|---|---|---|
| G1 | No profile or conformance-level mechanism, and no place to declare one. Only `okf_version` is allowed in the root index. | We need machine-checkable team rules on top of the §11 floor. |
| G2 | No type registry, and no type-conditioned required fields. Proposal #50 is open. | Each of Person, Role, Bet, and ADR needs its own fields. |
| G3 | No stable `id` independent of path. | Renames break references, which matters for people, ADR numbers, and glossary terms. |
| G4 | Links are untyped (#30, #22 are open). | "supersedes", "owned-by", "plays-role", and "decided-in" carry meaning for us. |
| G5 | `status` has only draft, stable, and deprecated. | ADRs need proposed, accepted, superseded, and rejected. Bets need active, killed, and shipped. |
| G6 | No ownership or accountability field. `generated.by` is authorship, not ownership. | Rotation-aware docs need an owner or steward. |
| G7 | No time-bounded assignment semantics beyond `stale_after`. | Role rotations, cycles, and bet appetites all need validity windows. |
| G8 | No glossary or term format. | Our CONTEXT.md glossary currently sits outside the bundle. |
| G9 | No privacy or visibility semantics (#32). | Person docs hold personal data. |
| G10 | No multi-bundle composition or merge rules (#26). | Methodology, team, and per-project bundles may be composed. |
| G11 | `okf_version: "0.2"` is ambiguous about timestamp strictness (#24). | Pin the post-2026-08-21 rules in our profile. |
| G12 | Path semantics for non-slash relative paths are ambiguous (#29). | Mandate an explicit `/` or `./`. |
| G13 | `log.md` frontmatter is unspecified, and the sample contradicts our checker. | Decide on one rule. |
| G14 | The `team:` actor prefix is used in the spec examples but not defined in §7. | We want `team:` and probably `role:` actors. |

---

## 5. Recommended team profile: "t0-team" (inferred, proposal)

**Design principles:**
- Stay **strictly OKF v0.2 conformant**: everything below uses extension keys, which §4.1 permits.
- Put profile-specific rules in a separate profile check instead of overloading `type`.
- Avoid collisions with spec-defined keys (`status`, `verified`, `generated`, `stale_after`). Domain lifecycle states therefore get their own key, `state`, so `status` keeps its spec meaning for consumers.

### 5.1 Profile declaration (fills G1 and G11)
- The root `docs/index.md` carries only `okf_version: "0.2"`, as the spec allows.
- The profile is itself a concept, `/profile.md` with `type: OKF Profile`. It carries:
  - `profile: t0-team`
  - `profile_version: "0.1"`
  - `timestamps: offset-required`
  - `link_style: bundle-absolute`
- The body holds the type table below. Consumers that don't know the profile still see a valid concept.

### 5.2 Common keys (every concept, enforced by the profile check)
```yaml
type: <registered profile type>          # spec-required
title: "…"                               # profile-required
description: "…"                         # profile-required; one sentence; copied into index
tags: [ … ]                              # YAML list
uid: adr-0007                            # profile: stable id, kebab-case, unique in bundle (G3)
owner: role:methodology-steward          # profile: actor; human:/team:/role: (G6, G14)
generated: { by: human:bruno, at: 2026-10-27T10:00:00Z }  # replaces local `timestamp`
verified: { by: human:…, at: … }         # optional; review sign-off -> human-reviewed tier
status: stable                           # spec lifecycle ONLY: draft|stable|deprecated
stale_after: 2027-01-31T00:00:00Z        # required for time-sensitive types (see table)
relations:                               # profile: typed edges (G4); targets are /bundle-paths
  supersedes: [/adr/0003-old-choice.md]
```
Typed edges in `relations` must *also* appear as body links. That way spec-only consumers still see the graph edge, and the profile adds the edge type.

**Actor prefixes (G14):** `human:<handle>`, `team:<slug>`, `role:<archetype-slug>`, `process:<id>`, `<agent>/<version>`. Trust tiers still key off `human:` only, as §5.3 requires.

### 5.3 Bundle layout

The directories split into three groups: methodology, team, and projects/products.

```
docs/                                  # bundle root (or one bundle per area, see G10)
  index.md                             # okf_version only
  profile.md                           # type: OKF Profile
  glossary/                            # type: Glossary Term (one term per file) (G8)
  methodology/
    index.md
    principles/                        # type: Principle
    practices/                         # type: Practice
    playbooks/                         # type: Playbook (spec example type)
    policies/                          # type: Policy
  team/
    people/                            # type: Person
    roles/                             # type: Role Archetype
    rotations/                         # type: Rotation
    rituals/                           # type: Ritual
  projects/<project-slug>/
    index.md
    project.md                         # type: Project (or Product)
    bets/                              # type: Bet
    adr/                               # type: ADR
    glossary/                          # project-local Glossary Term overrides
  research/                            # type: Research | Reference (frozen point-in-time)
```

### 5.4 Type registry (profile-required keys beyond the common ones)

| Type | Extra profile keys (type) | `state` enum | `stale_after` |
|---|---|---|---|
| **Principle** | `rationale_ref?` (path) | — | no |
| **Practice** | `applies_to: [project-paths or "all"]`, `level: must\|should\|may` | adopted \| trial \| retired | yes (review cadence) |
| **Playbook** | `trigger` (string), `steps_owner` (actor) | — | yes |
| **Policy** | `effective_from` (datetime), `approved_by` (actor) | proposed \| in-force \| retired | yes |
| **Person** | `handle` (string, matches `human:<handle>`), `teams: [team:…]`, `skills: [string]`. **No personal data beyond work handle** (G9). | active \| alumni | no |
| **Role Archetype** | `responsibilities: [string]`, `rotates: bool`, `rotation?` (path to Rotation) | — | no |
| **Rotation** | `role` (path to Role Archetype), `cadence` (ISO 8601 duration, e.g. `P2W`), `roster: [human:…]`, `assignments: [{who: human:…, from: datetime, to: datetime}]` (G7) | — | **yes**: set to the end of the current assignment so a stale rotation is detectable |
| **Ritual** | `cadence` (ISO 8601 duration or RRULE string), `duration` (ISO 8601), `facilitator` (actor, often `role:`), `participants: [actor]`, `inputs: [path]`, `outputs: [path]` | active \| paused \| retired | yes |
| **Project** / **Product** | `project_id` (slug), `lead` (actor), `repo?` (URL), `started` (datetime) | discovery \| building \| live \| sunset | no |
| **Bet** | `project` (path), `appetite` (ISO 8601 duration), `hypothesis` (string), `success_metric` (string), `cycle_start`, `cycle_end` (datetimes), `decision_by` (actor) | proposed \| active \| shipped \| killed \| extended | **yes** (= `cycle_end`) |
| **ADR** | `number` (int), `project` (path or "org"), `deciders: [actor]`, `decided_at?` (datetime) | proposed \| accepted \| superseded \| rejected | no |
| **Glossary Term** | `term` (string), `aliases: [string]`, `avoid: [string]` (banned synonyms), `scope: org \| <project path>` | — | no |
| **Research** / **Reference** | `sources` required (spec family) | — | no; frozen, so `status: stable` and never edited |

**Mapping rules:**
- Domain lifecycle goes in `state`. Spec `status` is derived from it:
  - superseded, retired, killed, or alumni maps to `status: deprecated`
  - proposed maps to `status: draft`
  - anything else maps to `stable`
- This keeps generic OKF consumers correct. For example, a proposed ADR reads as `draft`, which fixes the local `status: proposed` collision.
- ADR supersession is recorded as `relations.supersedes` on the new ADR plus `state: superseded` on the old one.

### 5.5 Profile conformance levels (our own, layered on spec §11)
- **L0, OKF floor (spec §11).** The YAML actually parses with a SafeLoader that keeps timestamps as strings. `type` is non-empty. Non-root `index.md` has no frontmatter. Index bodies use `# heading` plus `* [..](..) - ..`. `log.md` date headings are `## YYYY-MM-DD`. *Decide G13*: allow a `log.md` frontmatter of `type: Log`, matching the official sample, or keep forbidding `log.md` entirely as the harness does.
- **L1, profile structure.** `type` is in the registry. Common keys are present. `uid` is unique. Every datetime has an explicit offset. Actors match the prefix grammar. Enums are valid. Path-valued keys start with `/` or `./`. ID segments match `[A-Za-z0-9_][A-Za-z0-9_.\-]*`. Each index entry's description equals the target's `description`.
- **L2, profile integrity (warnings only, since the spec forbids rejecting broken links).** `relations` and path-valued targets exist. Every `relations` edge also appears as a body link. Each `Rotation` has exactly one assignment covering now. No `stale_after` is in the past for types that require it. Every `Person` referenced by `human:` in `owner`/`roster`/`deciders` exists. Each glossary `avoid` term is flagged where it appears in other docs.

**Implementation note (inferred):** replace the bash/awk check with a small Python (`-I`, PyYAML) or Node script. Reuse the reference `OKFDocument.parse` semantics, including the no-timestamp-resolver loader, so the floor matches the official parser. Run L0 and L1 in `init.sh` as blocking checks, and L2 as non-blocking warnings.

### 5.6 Migration from the current harness (inferred)
1. Bump the root index to `okf_version: "0.2"`.
2. Rewrite `timestamp:` as `generated: { by: <actor>, at: <timestamp> }`, using `git log` for `at` and `human:` or the agent id for `by`.
3. Move the ADR `status: accepted|proposed` value to `state`, then set the spec `status` per the mapping in §5.4.
4. Update the spec URLs in SKILL.md, design-rationale.md, and knowledge.template.md to `GoogleCloudPlatform/open-knowledge-format`.
5. Decide whether to keep relative links, which are conformant, or switch to the recommended bundle-absolute form. Absolute links render on GitHub only from the repo root, so keep relative links if GitHub rendering of `docs/` matters.
6. Bring `CONTEXT.md` terms into `glossary/` as `Glossary Term` concepts, or keep it outside the bundle and link it, as the harness does today. The domain-modeling skill hard-codes the CONTEXT.md path. (local skill)
