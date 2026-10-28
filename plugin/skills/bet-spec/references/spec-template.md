# Template do spec da bet

Use quando o Template `templates/spec.md` do KB está vazio ou não existe. Troque cada `<...>` e cada instrução em itálico pelo conteúdo. Mantenha os títulos e a ordem.

```markdown
---
type: Spec
title: "Spec: <título da bet>"
bet: <BET-NNN>
tier: <0 | 1 | 2>
state: draft
seams:
  - "<seam confirmado>"
---

# Spec: <título da bet>

## Problema

_O problema que o usuário enfrenta, do ponto de vista dele._

## Solução

_A solução, do ponto de vista do usuário._

## Histórias de usuário

_Lista longa e numerada, cobrindo todos os aspectos da feature._

1. Como <ator>, quero <capacidade>, para <benefício>.

## Decisões de implementação

_As decisões tomadas: módulos construídos ou alterados e suas interfaces, esclarecimentos técnicos, decisões de arquitetura, mudanças de schema, contratos de API, interações específicas. Sem caminho de arquivo e sem trecho de código, exceto trecho de protótipo que decide algo (avise a origem)._

- <decisão>

## Decisões de teste

_O que é um bom teste aqui (comportamento externo, sem detalhe de implementação), os seams confirmados, os módulos testados e os testes parecidos que já existem no código._

- <decisão>

## Critérios de aceite

- <afirmação de comportamento observável>

## Como verificar

_Os testes nos seams, os comandos e o `verify-<app>` do repo, quando houver._

## Tier

<0, 1 ou 2>: <motivo em uma linha>

## Design

_Opcional. Preenchida pela skill `architect` ou quando a conversa já fechou um desenho. Sem desenho, apague a seção._

## Fora de escopo

- <item, com as palavras do usuário>

## Notas

_Qualquer outra coisa que o próximo leitor precisa saber, incluindo os `[PRECISA ESCLARECER: <pergunta>]` abertos._
```
