---
type: Policy
title: "Limite de WIP"
description: "Cada pessoa tem no máximo 2 slices em construção, e PR esperando review vem antes de slice novo."
uid: policy-wip
owner: role:flow-steward
tags: [policy, wip, fluxo, slice]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
thresholds:
  slices_building_per_person: 2
---

# Limite de WIP

O WIP é limitado por review pendente, e não por sprint. O `t0 slice dor <KEY>` recusa o slice quando quem vai pegar já tem 2 slices em `building` ou `in-review`. Fonte: [metodologia §2.4](/methodology/methodology.md).

## Regras

- No máximo 2 slices em construção por pessoa.
- Sessões de agente em paralelo dentro desses slices são à vontade.
- PR esperando review tem prioridade sobre slice novo.
- A daily do time olha os slices travados e os reviews parados há mais de 24h.
