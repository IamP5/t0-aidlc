---
type: Slice
title: "bet-001-slice-01"
description: "Descrição de bet-001-slice-01."
uid: bet-001-slice-01
owner: human:ana
generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }
bet: BET-001
repo: api
tier: 1
depends_on: []
state: ready
status: stable
---
Corpo.

## Critérios de aceite

- retorna 422 acima do limite

## Como verificar

pytest -k limite
