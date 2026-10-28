---
type: ADR
title: "Achar reviews parados pela busca do forge, sem webhook"
description: "O bot consulta a busca de PRs do GitHub a cada execução, em vez de manter estado vindo de webhooks."
uid: adr-0001
owner: human:ana-exemplo
tags: [adr, exemplo, fixture]
generated: { by: human:ana-exemplo, at: 2026-10-21T15:00:00-03:00 }
number: 1
deciders: [human:ana-exemplo, human:caio-exemplo]
decided_at: 2026-10-21T17:00:00-03:00
state: accepted
status: stable
verified: { by: human:ana-exemplo, at: 2026-10-21T17:00:00-03:00 }
---

# Achar reviews parados pela busca do forge, sem webhook

## Contexto

A [BET-002](/products/exemplo/bets/BET-002/bet.md) precisa saber quais PRs esperam review há mais de 24h. O bot roda uma vez por dia e não tem banco.

## Decisão

A cada execução, o bot consulta a busca de PRs abertos fora de draft com review pedido, e calcula a idade a partir do pedido de review.

## Consequências

O bot continua sem estado e sem endpoint público. O custo é uma consulta por execução, e o número fica preso ao limite de busca da API.

## Alternativas consideradas

Receber webhooks e guardar os eventos. Daria a idade exata, mas pediria um serviço sempre no ar e uma revisão de segurança para o endpoint.
