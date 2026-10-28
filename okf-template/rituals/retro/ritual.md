---
type: Ritual
title: "Retro"
description: "Retro mensal de 60 minutos sobre como o time e a própria metodologia estão funcionando, e que passo de processo cortar."
uid: ritual-retro
owner: role:flow-steward
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "RRULE:FREQ=MONTHLY;BYDAY=-1FR;BYHOUR=15;BYMINUTE=0"
duration: PT1H
facilitator: role:flow-steward
participants: [team:t0]
command: "t0 ritual retro open|close"
recorded: true
transcribable: false
inputs:
  - { id: registros-do-mes, source: "kb:Ritual Record since=P1M", desc: "o que os rituais registraram no mês" }
  - { id: orcamento, source: "kb:/harness/budget.md", desc: "teto de hooks reportado pelo Harness Keeper" }
  - { id: adrs-metodologia, source: "kb:ADR path=/methodology/adr/", desc: "decisões da metodologia em vigor" }
outputs:
  - /rituals/retro/
  - /methodology/adr/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# Retro

Uma vez por mês, 60 minutos, com o time. Facilita o Flow Steward.

## O que acontece

Como o time e a metodologia estão funcionando: o que atrapalha, que passo de processo cortar, o que mudar nas dailies e nos papéis.

## Saída no KB

O registro da Retro e um ADR em `methodology/adr/` quando a metodologia muda.
