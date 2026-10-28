---
type: Product
title: "Bot de status da daily (exemplo)"
description: "Produto fictício que exercita todos os tipos do profile: o bot que publica o status antes da daily do time."
uid: product-exemplo
owner: team:exemplo
tags: [produto, exemplo, fixture]
generated: { by: process:kb-render, at: 2026-10-14T10:40:00-03:00 }
stage: crescimento
adoption_stage: 1
repos: [status-bot]
domain_contacts: []
state: live
status: stable
---

# Bot de status da daily (exemplo)

Este produto é a fixture positiva do `t0 kb check` e um exemplo para o time copiar. Apague `products/exemplo/` e os concepts com a tag `exemplo` quando o KB real tiver os próprios.

## Spec vivo

O bot publica o status no canal do time às 08:50 no horário de Brasília, em todo dia útil, antes da [daily do time](/rituals/daily-time/ritual.md).

- a mensagem lista os PRs que entraram desde a última daily;
- a mensagem lista os slices em `blocked` com o dono;
- o horário segue `America/Sao_Paulo`, inclusive em horário de verão (desde a [BET-001](/products/exemplo/bets/BET-001/bet.md)).

A [BET-002](/products/exemplo/bets/BET-002/bet.md) está em construção e vai acrescentar os reviews parados há mais de 24h.

## Contrato

### Mensagem de status, v1

- consumidor: o `t0 ritual daily-time open`, que lê a mesma estrutura;
- seções, nesta ordem: Merges, Travas;
- cada linha leva o link do PR ou do slice;
- conta como quebra: renomear ou reordenar seção, ou tirar o link.

## Workspace e evals

Os repos estão no [workspace](/products/exemplo/workspace.md), as suítes no [Eval Suite](/products/exemplo/evals.md) e o último relatório de adoção em [2026-W43](/products/exemplo/adoption/2026-W43.md).
