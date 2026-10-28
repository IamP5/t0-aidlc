---
type: Template
title: "Template de Bet"
description: "Esqueleto que o t0 new bet copia para products/<pod>/bets/BET-NNN/bet.md, nas duas trilhas."
uid: template-bet
owner: role:harness-keeper
tags: [template, bet]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
template_for: Bet
skeleton:
  type: Bet
  title: "<o que muda, em poucas palavras>"
  description: "<uma frase com o resultado esperado>"
  uid: "bet-<nnn>"
  owner: "human:<bet-owner>"
  tags: []
  track: bet
  appetite: P2W
  hypothesis: "<se fizermos X, Y acontece>"
  kill_criteria: "<o que faz a gente parar>"
  success_metric: "<número e onde ele é medido>"
  decision_by: "human:<quem aprova a aposta>"
  state: proposed
  status: draft
  generated: { by: "human:<handle>", at: "<agora com offset>" }
---

## Intenção

<!-- Por que agora, para quem, e o que muda para essa pessoa. Link para a Idea. -->

## Apetite e critério de kill

<!-- Trilha rápida: até 1 dia. Trilha bet: até 2 semanas. Bet que não cabe vira duas. -->

## Fora de escopo

## Aprendizado

<!-- Preenchido no ship ou no kill. -->
