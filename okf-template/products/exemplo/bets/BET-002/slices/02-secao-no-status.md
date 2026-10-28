---
type: Slice
title: "Seção Reviews parados no status"
description: "A mensagem de status ganha a seção Reviews parados, montada a partir da consulta do slice 01."
uid: bet-002-slice-02
owner: human:dani-exemplo
tags: [slice, exemplo, fixture]
generated: { by: process:kb-render, at: 2026-10-27T11:20:00-03:00 }
bet: BET-002
repo: status-bot
tier: 1
depends_on: [01-consulta-reviews-parados]
jira: EXE-22
pr: "t0/status-bot#21"
state: building
status: stable
---

## O que muda

A montagem da mensagem e o contrato v1 do produto, que ganha uma seção.

## Critérios de aceite

- a seção fica depois de Merges e antes de Travas;
- sem PR parado, a seção diz que não há nenhum.

## Como verificar

`pytest tests/test_mensagem.py` com o golden novo, e o roteiro do `verify-status-bot` contra o repo de teste. A Dani é júnior, então o PR leva a seção "Em minhas palavras".
