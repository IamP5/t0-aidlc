---
type: Spec
uid: spec-bet-003
title: "Spec: flag --version no CLI do springboot-plugin"
description: "O CLI imprime a versão do plugin com --version."
owner: human:eval
bet: BET-003
state: draft
tier: 1
generated: { by: human:eval, at: 2026-10-28T09:00:00-03:00 }
markers_open: 0
---

## Problema

Quem abre issue do springboot-plugin não sabe dizer qual versão rodou, e a triagem perde tempo perguntando.

## Solução

`node scripts/cli.mjs --version` imprime a versão do `package.json` em JSON e sai com 0.

## Histórias de usuário

1. Como dev que usa o plugin, quero ver a versão instalada, para colar na issue.

## Decisões de implementação

- A versão vem do `package.json` da raiz do plugin, lida em tempo de execução.
- A saída segue o padrão do CLI: JSON em stdout.

## Decisões de teste

- Um teste de integração roda o CLI com `--version` e confere a saída e o exit code.

## Fora de escopo

- `--version` nos subcomandos.

## Notas

Nada.

## Critérios de aceite

- `node scripts/cli.mjs --version` imprime `{"version": "<versão do package.json>"}` e sai com 0.
- `--help` lista a flag `--version`.
- Os comandos existentes continuam iguais.

## Como verificar

- `node --test tests/*.test.mjs` passa, com um teste novo para `--version`.
- Rodar `node scripts/cli.mjs --version` e comparar com `package.json`.

## Tier

1. Muda a superfície do CLI, mas só acrescenta uma flag de leitura.
