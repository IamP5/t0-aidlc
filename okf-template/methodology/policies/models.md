---
type: Policy
title: "Modelos por ferramenta e papel"
description: "Que modelo cada ferramenta usa em architect, arena, swarm e slice-verify, com o Opus como padrão e o Fable como assento diverso."
uid: policy-models
owner: role:lead
tags: [policy, modelos, arena, swarm, architect, slice-verify]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
architect-runner: { claude: opus, copilot: claude-opus, kiro: claude-opus }
arena-runner: { claude: opus, copilot: claude-opus, kiro: claude-opus }
judge: { claude: opus, copilot: claude-opus, kiro: claude-opus }
reviewer: { claude: opus, copilot: claude-opus, kiro: claude-opus }
swarm-worker: { claude: opus, copilot: claude-opus, kiro: claude-opus }
verifier: { claude: fable, copilot: claude-opus, kiro: claude-opus }
families_approved:
  claude: [opus, fable]
  copilot: [claude-opus]
  kiro: [claude-opus]
---

# Modelos por ferramenta e papel

As skills `architect`, `arena`, `swarm` e `slice-verify` leem esta Policy para escolher o modelo de cada papel. Mudar de modelo é um PR aqui, e a regressão de eval tem que ficar igual ou melhor (Policy [eval-gate](/methodology/policies/eval-gate.md)).

## Os papéis

- `architect-runner` roda cada candidato de desenho do `architect`;
- `arena-runner` roda os candidatos da `arena`, um por família de `families_approved`;
- `judge` compara os candidatos e escolhe a base;
- `reviewer` é o agente de review do `slice-verify`, contra o spec;
- `swarm-worker` roda cada célula da matriz do `swarm`;
- `verifier` confere a evidência do slice e, no Claude Code, roda em outra família que o `reviewer`.

## Claude Code

O padrão é o Opus. O Fable é o assento diverso: segundo candidato na `arena` (porque `families_approved` tem as duas famílias) e `verifier`, para o review cruzar famílias. Esforço médio por padrão, e alto só no `architect-runner`, porque desenho entre vários arquivos é o trabalho mais difícil do fluxo.

## Copilot (não verificado)

O mapa assume que o Copilot do banco oferece um modelo Claude Opus com o nome `claude-opus`. Falta confirmar o nome exato e se existe uma segunda família aprovada.

## Kiro (não verificado)

Mesma situação do Copilot: falta confirmar o nome do modelo Opus no Kiro e se há segunda família.

## Regra do same-family

Quando `families_approved` de uma ferramenta tem uma família só, `arena` e `swarm` rodam vários candidatos no mesmo modelo, e toda saída de comparação ou de review leva o rótulo `same-family`. Quem lê o resultado sabe que a concordância entre candidatos vale menos.
