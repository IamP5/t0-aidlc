# Template do slice da trilha bet

Use quando o Template `templates/slice.md` do KB está vazio ou não existe. Atual, esperado, não muda, critérios e como verificar moram só no corpo; o `t0` lê as seções.

```markdown
---
type: Slice
title: "<NN>: <título>"
bet: <BET-NNN>
repo: <repo do workspace do produto>
tier: <0 | 1 | 2>
state: ready
depends_on: [<NN-slug>, <NN-slug>]
---

# <NN>: <título>

## O que entrega

<O comportamento ponta a ponta que este slice faz funcionar, do ponto de vista de quem usa. Nada de lista camada por camada.>

## Critérios de aceite

- <afirmação de comportamento observável>

## Como verificar

<Os testes nos seams do spec, os comandos e o `verify-<app>` do repo, quando houver.>
```

Slice sem bloqueio fica com `depends_on: []`.
