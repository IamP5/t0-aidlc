---
type: Reference
title: "Tiers de review"
description: "Quanto review humano cada PR precisa, do Tier 0 ao Tier 2, e como um caminho gradua de tier."
uid: practice-review-tiers
owner: role:lead
tags: [pratica, review, qualidade, tier]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
stale_after: 2027-01-28T00:00:00-03:00
sources:
  - id: metodologia-7-2
    resource: /methodology/methodology.md
    title: "Metodologia, seção 7.2"
---

# Tiers de review

O tier sai do spec ou do slice (`tier:`) e decide quantas pessoas leem o PR. O humano só lê depois que o agente de review e o CI passaram. Fonte: [metodologia §7.2](/methodology/methodology.md).

## Tier 0

Docs, testes, refactor mecânico, saída de agente de limpeza e PR de estado no KB.

- agente de review e CI verdes;
- 1 humano faz o merge em lote, uma vez por dia;
- é o único tier com merge automático.

## Tier 1

Feature em ferramenta interna e slice de bet.

- agente de review e 1 humano;
- júnior não aprova sozinho.

## Tier 2

Auth, dado de cliente, permissão de agente, superfície pública (MCP, CLI, skill, API) e prompt ou modelo de ferramenta que as squads usam.

- agente de review e 2 humanos, um deles o Bet Owner; o outro pode ser de outro pod;
- blast radius com prova executada;
- cadeia de rastreabilidade completa (requisito, slice, PR, teste);
- seção "Em minhas palavras" no PR.

## Como o review roda

O agente de review roda num subagente novo, só leitura, contra o spec. Review entre modelos da mesma família sai marcado `same-family` (ver a Policy [models](/methodology/policies/models.md)). Todo PR nasce em draft. Hook de git e CI bloqueiam force push, `reset --hard`, push em `main` e PR fora de draft.

## Graduação (PROPOSTA)

Um caminho desce de Tier 1 para Tier 0 depois de 20 PRs seguidos sem defeito escapado do agente de review, e volta no primeiro defeito. Tier 2 nunca gradua. O contador fica em `harness/trust.md`, escrito só pelo CI.
