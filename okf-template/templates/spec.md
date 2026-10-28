---
type: Template
title: "Template de Spec"
description: "Esqueleto que o bet-spec copia para products/<pod>/bets/BET-NNN/spec.md, com as seções em pt-BR."
uid: template-spec
owner: role:harness-keeper
tags: [template, spec]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
template_for: Spec
skeleton:
  type: Spec
  title: "Spec da BET-<nnn>"
  description: "<uma frase com o que o spec entrega>"
  uid: "bet-<nnn>-spec"
  owner: "human:<bet-owner>"
  tags: []
  bet: "BET-<nnn>"
  seams: []
  tier: 1
  state: draft
  status: draft
  generated: { by: "human:<handle>", at: "<agora com offset>" }
---

## Problema

<!-- Do ponto de vista de quem usa. -->

## Solução

<!-- Do ponto de vista de quem usa. -->

## Histórias de usuário

<!-- Lista numerada: "Como <ator>, quero <recurso>, para <benefício>". -->

1. Como <ator>, quero <recurso>, para <benefício>.

## Decisões de implementação

<!-- Módulos, interfaces, esquema, contratos de API. Sem caminho de arquivo nem trecho de código. Decisão difícil de desfazer vira ADR. -->

## Decisões de teste

<!-- O que é um bom teste aqui, quais módulos e costuras (seams) testar, e o que já existe de parecido. -->

## Fora de escopo

## Notas

<!-- Use [PRECISA ESCLARECER: <pergunta>] para o que falta. O gate spec recusa com marcador aberto. -->

## Critérios de aceite

<!-- Bullets curtos e verificáveis. Nunca Gherkin. Esta seção é a única fonte dos critérios: o gate spec lê daqui. -->

- <comportamento observável>

## Como verificar

<!-- O comando, o roteiro do verify-<app> ou o passo manual que prova cada critério. O gate spec recusa a seção vazia. -->

## Tier

<!-- 0, 1 ou 2, com o motivo. Superfície pública é sempre Tier 2. -->

## Design

<!-- Opcional. Preenchido pelo architect quando há desenho a escolher. -->
