---
type: Ritual
title: "Harness Health"
description: "Sessão semanal de 20 minutos em que erros repetidos do agente sobem a escada do harness, e que só fecha com um PR por item aceito."
uid: ritual-harness-health
owner: role:harness-keeper
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=16;BYMINUTE=0"
duration: PT20M
facilitator: role:harness-keeper
participants: [team:t0]
command: "t0 ritual harness-health open|close"
recorded: true
transcribable: false
inputs:
  - { id: harness-abertos, source: "kb:Harness Item state=open", desc: "erros de agente registrados na semana" }
  - { id: orcamento, source: "kb:/harness/budget.md", desc: "linhas de AGENTS.md, hooks por repo, tamanho do card" }
  - { id: kb-vencido, source: "kb:* stale", desc: "concepts com stale_after vencido" }
  - { id: skills-sem-uso, source: "telemetry:skill-usage unused>P4W", desc: "skills candidatas a sunset" }
outputs:
  - /rituals/harness-health/
  - /harness/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# Harness Health

Toda semana, 20 minutos, com o time. Facilita o Harness Keeper.

## O que acontece

- erros de agente que se repetiram na semana sobem a [escada do harness](/methodology/practices/harness-ladder.md);
- olhar o orçamento de contexto em [harness/budget.md](/harness/budget.md);
- marcar skills sem uso para sunset e concepts vencidos no KB;
- incidente vira caso de eval;
- ler o CHANGELOG das skills de referência (mattpocock-skills e pstack) quando sai versão nova e abrir Harness Item para o que vale portar.

## Regra de fechamento

O `t0 ritual harness-health close` recusa enquanto algum Harness Item aceito na sessão estiver sem PR.

## Saída no KB

Harness Items com PR e casos de eval.
