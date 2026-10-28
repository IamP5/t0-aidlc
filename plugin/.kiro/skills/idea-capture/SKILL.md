---
name: idea-capture
description: "Registra uma ideia no KB com `t0 new idea`, depois de checar duplicata. Infere problema, para quem e sinal do pedido e marca o que falta como a confirmar. Use quando alguém trouxer uma ideia, pedido ou dor para guardar, ou disser \"anota essa ideia\"."
---

# idea-capture

Registre uma ideia no KB do time com o mínimo de atrito. Ela entra como Idea `new` em `ideas/IDEA-NNNN.md`, num PR pequeno da raia de conhecimento que o `t0 new idea` abre em draft. Protótipo, aposta e spec ficam para outras skills.

## 1. Junte o mínimo

Uma ideia tem problema (o que dói hoje, para quem sofre), para quem (pessoa, squad ou pod) e sinal (quem pediu, quantas vezes, um número, um incidente, um link). Tire os três do pedido e da conversa. O que não der para inferir entra no corpo como a confirmar (`Sinal: a confirmar`). Sinal fraco vale como ele é, sem inflar.

Pergunte só quando o próprio problema está obscuro, e no máximo uma pergunta.

O pod (`dev-tooling`, `paco`, `portal-metricas`) entra quando é óbvio. Quando não é, deixe em branco, que o Bet Owner resolve na daily do pod.

## 2. Procure duplicata

Busque no KB antes de criar:

```
t0 kb find --type Idea --text "<termo>"
```

Rode pelo menos duas buscas: uma com o termo que o usuário usou e outra com o termo canônico do glossário. `t0 kb find --type "Glossary Term" --text "<termo>"` mostra o termo com `aliases` e `avoid`. Inclua ideias `killed` e `promoted` no que você compara: o registro de kill existe para a mesma ideia voltar só com fato novo. Com o MCP `t0-kb` disponível, faça as mesmas buscas por ele.

Leia o corpo de cada candidata parecida com `t0 kb get IDEA-NNNN` e decida:

| Achado | O que fazer |
|---|---|
| Nenhuma parecida | siga para o passo 3 |
| A mesma ideia, `new` ou `prototyped` | pare. Mostre a existente com estado e veredito, e sugira levar o sinal novo para a daily do pod ou para o `prototype` dela |
| A mesma ideia, `killed` | mostre o motivo do kill e pergunte qual é o fato novo. Sem fato novo, pare. Com fato novo, siga para o passo 3 e cite a ideia antiga e o fato no sinal |
| A mesma ideia, `promoted` | mostre a bet que nasceu dela e pare |
| Parecida, com outra dor ou outro público | siga para o passo 3 e cite a parecida no corpo |

Na dúvida entre "a mesma" e "parecida", mostre a candidata e pergunte.

O passo termina quando você consegue dizer quais ideias comparou e por que a nova merece registro próprio.

## 3. Crie a ideia

Rode em dry-run e confira o plano:

```
t0 new idea --dry-run ...
```

Passe título curto (até umas 8 palavras), problema, para quem, sinal, `source` (`human` por padrão, `squad` ou `jira` quando veio de lá) e o pod quando houver. Os nomes exatos das opções estão em `t0 new idea --help`. O `t0` reserva o `IDEA-NNNN` olhando o `main` e as branches abertas, e abre o PR em draft.

Rode de novo sem `--dry-run`. Se o `t0` recusar (colisão em `uid-unique`, campo faltando), leia a recusa, corrija a entrada e rode de novo. O arquivo da ideia nasce sempre pelo `t0`, que também cuida de `state` e `verified`.

## 4. Feche

Responda em pt-BR numa mensagem curta: o `IDEA-NNNN`, o link do PR em draft, os campos a confirmar, as parecidas quando houve e o próximo passo (`prototype IDEA-NNNN`, ou `bet-new` na trilha rápida). Quem decide se a ideia vira bet é o pod, na daily.
