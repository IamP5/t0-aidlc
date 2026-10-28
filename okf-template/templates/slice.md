---
type: Template
title: "Template de Slice"
description: "Esqueleto que o bet-slice e o bet-new rapida copiam para products/<pod>/bets/BET-NNN/slices/NN-slug.md."
uid: template-slice
owner: role:harness-keeper
tags: [template, slice]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
template_for: Slice
skeleton:
  type: Slice
  title: "<o que este PR entrega>"
  description: "<uma frase>"
  uid: "bet-<nnn>-slice-<nn>"
  owner: "human:<builder>"
  tags: []
  bet: "BET-<nnn>"
  repo: "<nome do repo no workspace.md>"
  tier: 1
  depends_on: []
  state: ready
  status: stable
  generated: { by: "human:<handle>", at: "<agora com offset>" }
---

<!-- Um slice é um repo e um PR revisável em até 15 minutos. As chaves state (depois de ready), jira, pr e audit são do kb-render: ninguém edita na mão. -->

## O que muda

## Atual

<!-- Só na trilha rápida. Na trilha bet, apague Atual, Esperado e Não muda. -->

## Esperado

## Não muda

## Critérios de aceite

- <comportamento observável>

## Como verificar

<!-- Na trilha rápida, nomeie o teste que fica vermelho antes e verde depois. -->
