---
type: Glossary Term
title: "raia"
description: "Cada um dos três caminhos de escrita no KB: registros, conhecimento e derivados."
uid: term-raia
owner: role:lead
tags: [glossario]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
term: raia
term_en: write lane
aliases: [raia de escrita]
avoid: [fila, canal]
scope: org
---

# raia (write lane)

Cada um dos três caminhos de escrita no KB. Registros são arquivos novos em `steps/`, que entram sem revisão humana (Policy [records-lane](/methodology/policies/records-lane.md)). Conhecimento entra por PR com CODEOWNERS. Derivados (`index.md`, `log.md` e as chaves derivadas) só o `kb-render` escreve.
