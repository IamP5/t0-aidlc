---
type: Bet
title: "Status no horário de Brasília"
description: "Corrigir o horário do status para seguir America/Sao_Paulo e não o offset do servidor."
uid: bet-001
owner: human:caio-exemplo
tags: [bet, exemplo, fixture, rapida]
generated: { by: process:kb-render, at: 2026-10-14T10:40:00-03:00 }
track: rapida
appetite: P1D
hypothesis: "Agendar pelo fuso nomeado faz o status sair às 08:50 o ano todo."
kill_criteria: "Se pedir mudança no agendador da plataforma, vira bet."
success_metric: "Status às 08:50 por 10 dias úteis seguidos."
decision_by: human:caio-exemplo
jira: EXE-10
state: shipped
status: stable
verified: { by: human:caio-exemplo, at: 2026-10-13T11:00:00-03:00 }
relations:
  from_idea: [/ideas/IDEA-0003.md]
---

## Intenção

Saiu da [IDEA-0003](/ideas/IDEA-0003.md), um bug de squad. Trilha rápida, aprovada pelo Caio como Flow Steward na daily de 2026-10-13. Um slice só: [01-horario-em-brt](/products/exemplo/bets/BET-001/slices/01-horario-em-brt.md).

## Apetite e critério de kill

Um dia. Se a correção pedisse mudança no agendador da plataforma, a gente parava e abria uma bet.

## Fora de escopo

Feriados.

## Aprendizado

O agente escreveu `datetime.now()` sem fuso no primeiro rascunho, igual ao código que causou o bug. Virou o [HI-0001](/harness/HI-0001.md).
