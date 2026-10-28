---
type: Bet
title: "Review parado no status da daily"
description: "O status da daily passa a listar os PRs esperando review há mais de 24h, com o dono do review."
uid: bet-002
owner: human:ana-exemplo
tags: [bet, exemplo, fixture]
generated: { by: human:ana-exemplo, at: 2026-10-20T10:30:00-03:00 }
track: bet
appetite: P1W
hypothesis: "Com o review parado no status, a mediana até a primeira resposta cai para menos de 4h úteis."
kill_criteria: "Se a busca do forge não der a idade do pedido de review, a gente para."
success_metric: "Mediana até a primeira resposta humana, no painel, por 2 semanas."
decision_by: human:ana-exemplo
jira: EXE-20
state: active
status: stable
verified: { by: human:ana-exemplo, at: 2026-10-20T10:30:00-03:00 }
relations:
  from_idea: [/ideas/IDEA-0001.md]
---

## Intenção

Saiu da [IDEA-0001](/ideas/IDEA-0001.md), com veredito segue na [daily do pod de 2026-10-20](/rituals/daily-pod/2026-10-20.md). A Ana aprovou a aposta sozinha: um pod, Tier 1 e apetite de 1 semana. O [spec](/products/exemplo/bets/BET-002/spec.md) tem dois slices.

## Apetite e critério de kill

Uma semana. Se a busca do forge não der a idade do pedido de review, a bet morre e o aprendizado fica aqui.

## Fora de escopo

Lembrete direto para quem deve o review.

## Aprendizado

<!-- Preenchido no ship ou no kill. -->
