---
type: Reference
title: "Orçamento do harness"
description: "Os tetos de contexto e de hooks que o Harness Keeper acompanha e mostra no Harness Health e na Retro."
uid: harness-budget
owner: role:harness-keeper
tags: [harness, orcamento, contexto]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
stale_after: 2026-11-28T00:00:00-03:00
sources:
  - id: metodologia-7-3
    resource: /methodology/methodology.md
    title: "Metodologia, seções 1 e 7.3"
  - id: workspace-2-6
    resource: /methodology/workspace-pattern.md
    title: "Workspace pattern, seção 2.6"
limits:
  agents_md_lines: 150
  hooks_per_repo: 20
  card_chars: 8000
  delta_chars: 3000
  subagent_card_chars: 1500
  mcp_instructions_chars: 1500
---

# Orçamento do harness

Contexto é orçamento. O Harness Keeper atualiza a tabela de uso a cada Harness Health e mostra o teto de hooks na Retro. Quando um número passa do teto, o item vira Harness Item. Os tetos vêm da [metodologia](/methodology/methodology.md) e do [workspace pattern](/methodology/workspace-pattern.md).

## Tetos

- `AGENTS.md` com até 150 linhas por repo;
- até 20 hooks ou regras deny por repo;
- card do workspace com até 8.000 caracteres, delta com até 3.000;
- card de subagente e instruções do MCP com até 1.500 caracteres cada.

## Uso atual

| Repo ou superfície | Linhas de AGENTS.md | Hooks e deny | Medido em |
|---|---|---|---|
| (nenhum repo ainda) | | | |
