# Playbook for this run (figure-it-out)

## Done predicate

1. `methodology/` has a pt-BR methodology document and a slide deck that cover cycle, roles, rituals, artifacts, gates, metrics, SAFe interface, rollout.
2. `plugin/aidlc/` installs as a Claude Code plugin, `claude plugin validate` (or `details`) succeeds, and `claude plugin eval` runs its suite with every case scored.
3. `okf-template/` is an OKF bundle (team + projects + methodology) that passes its own conformance checker, and the plugin has skills that create, update and check it, covered by evals.

## Rigor

High for plugin and OKF shape (one-way doors: every repo of the team will copy them). Medium for prose.

## Phases

1. Research swarm: OKF, toolkit inventory, methodology deltas, plugin and eval format.
2. Arena A: methodology, roles and rituals (2 candidates, judged against a rubric, grafted).
3. Architect + arena B: plugin shape and adaptations of mattpocock/skills and pstack.
4. Build the OKF template and its checker first (the plugin depends on it).
5. Build the plugin skills, hooks and evals against the synthesized sketch.
6. Write the methodology doc and deck from the arena A synthesis.
7. Verify: run the checker, plugin validation, the eval suite; audit the decision log.

The decision trail lives in `.audit/aidlc-build.tsv`.
