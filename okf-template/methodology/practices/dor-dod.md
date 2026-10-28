---
type: Reference
title: "DoR e DoD"
description: "Quando um slice pode começar e quando um slice e uma bet estão prontos."
uid: practice-dor-dod
owner: role:lead
tags: [pratica, dor, dod, slice, qualidade]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
stale_after: 2027-01-28T00:00:00-03:00
sources:
  - id: metodologia-7-1
    resource: /methodology/methodology.md
    title: "Metodologia, seção 7.1"
---

# DoR e DoD

O `t0 slice dor <KEY>` confere o DoR antes do `slice-build` abrir branch. Fonte: [metodologia §7.1](/methodology/methodology.md).

## DoR do slice

- critérios de aceite em bullets, "como verificar", `tier` e `repo` no slice;
- na trilha bet, spec `approved` sem nenhum `[PRECISA ESCLARECER]`;
- na trilha rápida, "atual, esperado, o que não muda" e o teste que vai ficar vermelho;
- chave Jira gravada no slice;
- quem pega o slice tem menos de 2 slices em construção (Policy [wip](/methodology/policies/wip.md)).

## DoD do slice

- CI verde e agente de review sem pendência, depois o review humano do [tier](/methodology/practices/review-tiers.md);
- teste nas costuras do spec e verificação executada pelo `verify-<app>` do repo;
- em Tier 2, blast radius com prova executada;
- `.audit/<KEY>.tsv` commitado no PR e "Em minhas palavras" quando exigida;
- erro do agente no caminho registrado num Harness Item;
- superfície pública alterada com contract tests verdes e versão atualizada no spec vivo do produto.

## DoD da bet

- todos os slices `done`;
- spec da bet congelado e spec vivo do produto atualizado;
- regressão de eval registrada, se for ferramenta de agente;
- aprendizado escrito na Bet.
