---
type: Spec
title: "Spec da BET-002"
description: "Uma seção nova no status com os PRs esperando review há mais de 24h."
uid: bet-002-spec
owner: human:ana-exemplo
tags: [spec, exemplo, fixture]
generated: { by: claude-code/opus-5.5, at: 2026-10-21T15:00:00-03:00 }
bet: BET-002
seams: [busca-do-forge, montagem-da-mensagem]
markers_open: 0
tier: 1
state: approved
status: stable
verified: { by: human:ana-exemplo, at: 2026-10-21T17:00:00-03:00 }
---

## Problema

Quem chega na daily do time não vê quais PRs estão esperando review há mais de um dia. A fila só aparece quando alguém lembra de perguntar.

## Solução

O status ganha uma seção Reviews parados, com cada PR esperando review há mais de 24h, a idade e quem deve o review.

## Histórias de usuário

1. Como Flow Steward, quero ver os reviews parados no status, para cobrar na daily sem abrir o forge.
2. Como Builder, quero ver quais reviews estão comigo, para resolver antes de pegar slice novo.
3. Como autor de PR, quero que meu PR parado apareça sozinho, para não precisar pedir na daily.

## Decisões de implementação

- A busca usa a API de busca do forge a cada execução, sem webhook e sem estado ([ADR-0001](/products/exemplo/adr/ADR-0001-busca-do-forge.md)).
- A idade conta a partir do último pedido de review, em horas corridas.
- A seção entra na mensagem v1 como seção nova, então o contrato do produto ganha uma versão.

## Decisões de teste

- A costura `busca-do-forge` é testada com respostas gravadas da API, incluindo PR em draft e PR sem pedido de review.
- A costura `montagem-da-mensagem` é testada pela mensagem final, comparando com um golden.
- O bot de hoje já tem testes de golden em `tests/test_mensagem.py`, que servem de modelo.

## Fora de escopo

- lembrete direto para quem deve o review;
- horas úteis em vez de corridas.

## Notas

O limite de 24h vem da metodologia. Se o time quiser mudar, vira parâmetro numa bet futura.

## Critérios de aceite

- o status tem a seção Reviews parados, depois de Merges e antes de Travas;
- a seção lista só PRs fora de draft com review pedido há mais de 24h;
- cada linha traz o link do PR, a idade em horas e quem deve o review;
- sem PR parado, a seção diz que não há nenhum.

## Como verificar

`pytest tests/test_reviews_parados.py`, e depois o roteiro do `verify-status-bot` contra o repo de teste com 3 PRs plantados (um em draft, um com 2h, um com 30h). Só o de 30h aparece.

## Tier

Tier 1. Ferramenta interna do time, sem dado de cliente e sem superfície pública.

## Design

Dois slices em ordem. O [01](/products/exemplo/bets/BET-002/slices/01-consulta-reviews-parados.md) entrega a consulta e devolve uma lista tipada, sem mexer na mensagem. O [02](/products/exemplo/bets/BET-002/slices/02-secao-no-status.md) monta a seção a partir dessa lista. A alternativa de fazer tudo num PR só passaria de 15 minutos de review.
