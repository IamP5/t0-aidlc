---
type: Slice
title: "Consultar os reviews parados no forge"
description: "Uma função que devolve os PRs fora de draft com review pedido há mais de 24h."
uid: bet-002-slice-01
owner: human:caio-exemplo
tags: [slice, exemplo, fixture]
generated: { by: process:kb-render, at: 2026-10-23T16:10:00-03:00 }
bet: BET-002
repo: status-bot
tier: 1
depends_on: []
jira: EXE-21
pr: "t0/status-bot#18"
audit: "t0/status-bot#18:.audit/EXE-21.tsv"
state: done
status: stable
verified: { by: human:ana-exemplo, at: 2026-10-23T16:00:00-03:00 }
---

## O que muda

Uma consulta nova à busca do forge, sem mexer na mensagem.

## Critérios de aceite

- devolve só PRs fora de draft com review pedido há mais de 24h;
- cada item traz link, idade em horas e quem deve o review.

## Como verificar

`pytest tests/test_reviews_parados.py`, com as respostas gravadas da API.
