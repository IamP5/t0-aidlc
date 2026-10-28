---
type: Ritual
title: "Daily do pod"
description: "Sessão diária do pod com o agente ao vivo para prototipar ideias, decidir o que vira bet, fechar spec junto e planejar o dia."
uid: ritual-daily-pod
owner: role:bet-owner
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=15"
duration: PT45M
facilitator: role:bet-owner
participants: [team:pod]
command: "t0 ritual daily-pod open|close"
recorded: true
transcribable: true
inputs:
  - { id: ideias-prototipadas, source: "kb:Idea state=prototyped product={pod}", desc: "ideias com veredito esperando a decisão de aposta" }
  - { id: bets-ativas, source: "kb:Bet state=active product={pod}", desc: "bets em andamento no pod" }
  - { id: specs-abertos, source: "kb:Spec state=draft product={pod}", desc: "specs para fechar em mob" }
  - { id: slices-prontos, source: "kb:Slice state=ready product={pod}", desc: "slices que alguém pode pegar hoje" }
outputs:
  - /rituals/daily-pod/
  - /ideas/
  - /transcripts/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# Daily do pod

Todo dia útil, logo depois da daily do time, de 30 a 45 minutos. Pode virar uma sessão de mob mais longa quando há spec para fechar. Facilita o Bet Owner, com o agente ao vivo. Um Domain Expert de squad entra quando a bet toca o trabalho dela.

A daily do pod conta como trabalho. É ali que o pod prototipa, especifica e planeja com o agente, no lugar do shaping solitário, do Betting e do refinamento.

## O que acontece

- validar ideias prototipando na hora;
- decidir o que vira bet (`gate aposta`);
- fechar spec e slices juntos (`bet-spec`, `bet-slice`);
- refinar e planejar as tarefas do dia;
- destravar.

## Saída no KB

Ideias, decisões, PRs de spec no KB e o registro da sessão. Se houve gravação, a transcrição redigida (Policy [transcript-retention](/methodology/policies/transcript-retention.md)).
