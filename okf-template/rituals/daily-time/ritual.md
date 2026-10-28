---
type: Ritual
title: "Daily do time"
description: "Daily de 10 minutos do time inteiro, só sobre bloqueios e pedidos de review, com o status publicado antes pelo bot."
uid: ritual-daily-time
owner: role:flow-steward
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0"
duration: PT10M
facilitator: role:flow-steward
participants: [team:t0]
command: "t0 ritual daily-time open|close"
recorded: true
transcribable: true
inputs:
  - { id: merges, source: "forge:merged since=last-ritual", desc: "PRs que entraram desde a última daily" }
  - { id: reviews-parados, source: "forge:review-pending age>PT24H", desc: "PRs esperando review há mais de 24h" }
  - { id: bloqueios, source: "kb:Slice state=blocked", desc: "slices travados e quem destrava" }
outputs:
  - /rituals/daily-time/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# Daily do time

Todo dia útil, 10 minutos, com todo mundo. Facilita o Flow Steward.

## O que acontece

O `t0 ritual daily-time open` imprime o status antes da daily: merges desde a última, reviews parados há mais de 24h e travas. Ninguém dá status na daily. Só se fala de bloqueio e de pedido de review.

## Saída no KB

Um registro curto em `rituals/daily-time/AAAA-MM-DD.md`, com os bloqueios e os donos.
