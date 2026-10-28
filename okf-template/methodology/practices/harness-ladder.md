---
type: Reference
title: "Escada do harness"
description: "O que fazer quando o agente erra a mesma coisa pela segunda vez: sensor, regra de área, skill e, por último, AGENTS.md."
uid: practice-harness-ladder
owner: role:harness-keeper
tags: [pratica, harness, agentes, qualidade]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
stale_after: 2027-01-28T00:00:00-03:00
sources:
  - id: metodologia-7-3
    resource: /methodology/methodology.md
    title: "Metodologia, seção 7.3"
---

# Escada do harness

Na primeira vez que o agente erra, o `slice-verify` abre um [Harness Item](/templates/harness-item.md). Na segunda ocorrência do mesmo padrão, o item sobe a escada e ganha um PR em draft pelo `harness-fix`, revisado no Harness Health da semana. Fonte: [metodologia §7.3](/methodology/methodology.md).

## Os degraus, de baixo para cima

1. `sensor`: lint com mensagem de correção escrita para o agente, teste, hook de git ou gate de CI.
2. `area-rule`: regra de área com uma fonte só em `agents/rules/<area>.md`, gerada para as três ferramentas.
3. `skill`: procedimento longo vira skill no toolkit.
4. `agents-md`: só por último, e o `AGENTS.md` fica com até 150 linhas.

Suba só até onde resolve. Se um sensor pega o erro, ele não vai para regra nem para `AGENTS.md`.

## Onde mora regra sem exceção

Em hook de git ou em CI, nunca em hook de agente. Cada ferramenta tem formato e semântica próprios, o Copilot no VS Code ignora matchers e o timeout de hook no Copilot falha aberto. Hook de agente fica como acelerador opcional.

## Orçamento

Teto de 20 hooks ou regras deny por repo. O Harness Keeper mantém [harness/budget.md](/harness/budget.md) e mostra o número na Retro.
