# Slice da trilha rápida

Se o KB tiver um Template de slice com corpo (`templates/slice.md`), siga as seções dele. Sem isso, use este. Atual, esperado, não muda, critérios e como verificar moram só no corpo; o `t0` lê as seções.

```markdown
---
type: Slice
title: "01: <título>"
bet: <BET-NNN>
repo: <repo do workspace do produto>
tier: <0 | 1 | 2>
state: ready
---

# 01: <título>

## Atual

<O que acontece hoje, observável por quem usa. Inclua como reproduzir.>

## Esperado

<O que deve acontecer depois do slice.>

## Não muda

- <comportamento vizinho que continua igual>

## Teste

<Qual teste, em que seam e o que ele afirma. Ele fica vermelho com o comportamento atual e verde com o esperado.>

## Critérios de aceite

- <afirmação de comportamento observável>

## Como verificar

<Comandos, testes e o `verify-<app>` do repo, quando houver.>
```

Deixe `jira`, `pr` e os estados depois de `ready` para o CI e o `kb-render`.
