---
type: Policy
title: "Pisos de customer zero"
description: "Os números que uma ferramenta precisa mostrar para subir de degrau de adoção, todos PROPOSTA."
uid: policy-adoption-floors
owner: role:lead
tags: [policy, adocao, customer-zero, degrau]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
thresholds:
  stage_1_to_2:
    active_of_team: 7
    team_size: 10
    consecutive_weeks: 2
    regression_min_pass: 0.95
  stage_2_to_3:
    active_share_pilot: 0.40
    consecutive_weeks: 3
    retention_4w_min: 0.50
    metric: "pass^3"
  episodic:
    repeat_use_weeks: 2
    window_weeks: 4
  sunset:
    weekly_use_share_max: 0.15
    active_users_min: 5
    after_weeks_in_pilot: 8
---

# Pisos de customer zero

Tudo aqui é PROPOSTA e fica em `state: proposed` até 3 ferramentas passarem pelo funil. Quem decide o degrau é o Lead/AIVA, com números (`gate degrau`, previsto para a v0.2). Fonte: [metodologia §7.5](/methodology/methodology.md).

"Ativo" é quem invocou a ferramenta em trabalho real numa semana ISO, medido por telemetria. Login não conta.

## Degrau 1 para 2 (time para 2 ou 3 squads piloto)

- pelo menos 7 dos 10 do time ativos por semana, por 2 semanas seguidas;
- regressão de eval com pelo menos 95% (Policy [eval-gate](/methodology/policies/eval-gate.md));
- confirma o Lead/AIVA.

## Degrau 2 para 3 (piloto para o ART)

- pelo menos 40% dos devs-alvo das squads piloto ativos por semana, por 3 semanas seguidas;
- retenção de pelo menos 50% em 4 semanas;
- `pass^3` na meta do produto;
- confirma o Lead/AIVA, e o degrau vira outcome do PI.

## Uso episódico

Para ferramenta de uso raro (skill de migração, por exemplo), vale uso repetido em pelo menos 2 de 4 semanas entre quem tinha tarefa elegível, no lugar do uso semanal.

## Sunset

Menos de 15% de uso semanal no público-alvo, ou menos de 5 usuários ativos, depois de 8 semanas em piloto. O Harness Keeper propõe e o Lead confirma.

## De onde vêm os números

O time é a coorte mais motivada, então 70% é razoável. 40% no piloto fica abaixo do platô de cerca de 60% atribuído à DX (não verificado) e passa do pico de novidade de uma semana. A cláusula de retenção copia a forma do gate do time do Claude Code, cujo número não é público. Os números são revistos depois de 3 ferramentas.
