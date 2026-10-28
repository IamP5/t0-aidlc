---
type: Ritual
title: "Demo"
description: "Demo de 30 minutos a cada 2 semanas, junto com a iteração do ART, com o que foi pro ar, o painel e o rodízio novo."
uid: ritual-demo
owner: role:flow-steward
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=TU;BYHOUR=15;BYMINUTE=0"
duration: PT30M
facilitator: role:flow-steward
participants: [team:t0]
command: "t0 ritual demo open|close"
recorded: true
transcribable: false
inputs:
  - { id: bets-encerradas, source: "kb:Bet state=shipped|killed since=last-ritual", desc: "o que foi pro ar e o que morreu" }
  - { id: painel, source: "metrics:fluxo-adocao", desc: "painel de fluxo e adoção" }
  - { id: rodizios, source: "kb:Rotation", desc: "quem assume Harness Keeper e Flow Steward" }
outputs:
  - /rituals/demo/
  - /team/rotations/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# Demo

A cada 2 semanas, 30 minutos, alinhada à iteração do ART. Facilita o Flow Steward.

## O que acontece

Demo ao vivo do que foi pro ar, o painel de fluxo e adoção, e as bets encerradas.

## Regra de fechamento

O `t0 ritual demo close` grava o rodízio novo de Harness Keeper e de Flow Steward.

## Saída no KB

O registro da Demo, Bets `shipped` ou `killed` e as Rotations atualizadas.
