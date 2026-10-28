# Formato do termo no glossário

Um termo por arquivo em `glossary/<slug>.md`, com o slug tirado do termo em pt-BR (`review-parado.md`). O tipo é `Glossary Term`.

```markdown
---
type: Glossary Term
title: "review parado"
term: "review parado"
aliases: ["stale review"]
avoid: ["PR esquecido", "PR travado"]
scope: products/<pod>
---
**review parado** (en: *stale review*): PR de slice sem nenhum review há mais de 24h úteis.
```

- `term` é o termo canônico em pt-BR.
- `aliases` traz primeiro o equivalente em inglês, depois outros nomes aceitos.
- `avoid` lista os sinônimos que o time decidiu largar. O `t0 kb check` L2 avisa quando um deles aparece em outro documento.
- `scope` é `org` quando o termo vale para o time todo, ou `products/<pod>` quando é de um produto.

## Regras

- Seja opinativo. Quando há várias palavras para o mesmo conceito, escolha a melhor e mande as outras para `avoid`.
- Defina em uma ou duas frases o que a coisa é.
- Guarde só termos do domínio do time. Conceito genérico de programação (timeout, retry, tipo de erro) fica fora, mesmo que o código use muito.
- Mantenha o glossário livre de detalhe de implementação. Decisão de implementação vai para o spec ou para um ADR.
- Antes de criar, busque o termo e os aliases com `t0 kb find --type "Glossary Term" --text "<termo>"`. Achou, edite o arquivo existente.

Depois de gravar, rode `t0 kb check --changed-from main` e corrija o que ele apontar.
