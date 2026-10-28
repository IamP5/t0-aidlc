---
type: Template
title: "Template de Harness Item"
description: "Esqueleto que o slice-verify copia para harness/HI-NNNN.md na primeira vez que o agente erra."
uid: template-harness-item
owner: role:harness-keeper
tags: [template, harness]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
template_for: Harness Item
skeleton:
  type: Harness Item
  title: "<o erro do agente, em poucas palavras>"
  description: "<uma frase com o padrão do erro>"
  uid: "hi-<nnnn>"
  owner: role:harness-keeper
  tags: []
  pattern: "<o que o agente fez de errado, de forma que dê para reconhecer de novo>"
  ladder_step: sensor
  state: open
  status: draft
  generated: { by: "human:<handle>", at: "<agora com offset>" }
---

## O que aconteceu

<!-- Link para o PR e o trecho. occurrences é derivada dos registros. -->

## Degrau escolhido

<!-- sensor, area-rule, skill ou agents-md, e por que o degrau de baixo não resolve. Ver a escada do harness. -->

## Correção

<!-- Link para o PR em draft do harness-fix. -->
