---
type: Product
title: "Dev Tooling"
description: "agents, skills e CLIs do SDLC para as equipes de produto."
uid: product-dev-tooling
owner: team:dev-tooling
tags: [produto, pod]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
stage: pre-pmf
adoption_stage: 1
repos: []
domain_contacts: []
state: discovery
status: draft
---

# Dev Tooling

Pod Dev Tooling: agents, skills e CLIs do SDLC para as equipes de produto.

## Spec vivo

Ainda não há bet entregue. No ship de cada bet, o CI congela o spec dela e traz para cá o comportamento que passou a valer. A bet é spec-first, e o produto é spec-anchored.

## Contrato

Nenhuma superfície pública ainda. Quando houver uma (MCP, CLI, skill ou API), ela ganha uma subseção aqui com versão, consumidores e o que conta como quebra. O contract test do repo é gerado desta seção, com o `uid` no cabeçalho.

## Workspace e evals

Os repos estão no [workspace](/products/dev-tooling/workspace.md), e as suítes, no [Eval Suite](/products/dev-tooling/evals.md).
