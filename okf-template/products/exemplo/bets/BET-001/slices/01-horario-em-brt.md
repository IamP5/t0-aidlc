---
type: Slice
title: "Agendar o status por America/Sao_Paulo"
description: "O agendamento usa o fuso nomeado em vez do offset do servidor."
uid: bet-001-slice-01
owner: human:ana-exemplo
tags: [slice, exemplo, fixture, rapida]
generated: { by: process:kb-render, at: 2026-10-14T10:40:00-03:00 }
bet: BET-001
repo: status-bot
tier: 1
depends_on: []
jira: EXE-11
pr: "t0/status-bot#14"
audit: "t0/status-bot#14:.audit/EXE-11.tsv"
state: done
status: stable
verified: { by: human:dani-exemplo, at: 2026-10-14T10:30:00-03:00 }
---

## O que muda

O agendador do bot.

## Atual

O agendamento soma o offset do servidor. Quando o offset muda, o status sai às 07:50.

## Esperado

O agendamento usa `America/Sao_Paulo`, e o status sai às 08:50 o ano todo.

## Não muda

- o conteúdo e a ordem das seções da mensagem;
- o canal de destino.

## Critérios de aceite

- o status sai às 08:50 de Brasília antes e depois da mudança de offset;
- o horário vem da configuração, com o fuso `America/Sao_Paulo`.

## Como verificar

`pytest tests/test_agenda.py -k offset`. O teste `test_horario_sobrevive_mudanca_de_offset` ficou vermelho antes da correção e verde depois.
