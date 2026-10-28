---
name: bet-new
description: "Abre uma bet a partir de uma Idea com `t0 new bet --track rapida|bet`, que abre o PR da aposta em draft. Na trilha rápida também escreve o slice com atual, esperado, não muda e o teste. Use para transformar uma ideia em bet ou em ajuste rápido."
---

# bet-new

Transforme uma Idea numa Bet e abra o PR da aposta. Aprovar esse PR é a decisão de aposta, uma das três decisões humanas do time. Você prepara e propõe; quem decide é quem aprova o PR.

## 1. Leia a ideia

Na rápida sem Idea, pule este passo: o `t0 new bet --track rapida "<texto>"` cria a Idea junto. Com Idea, `t0 kb get <IDEA>` e confira o estado e o veredito do protótipo:

- `killed`: mostre o motivo e pare;
- `promoted`: mostre a bet que já nasceu dela e pare;
- `new` ou `prototyped`: siga.

## 2. Escolha a trilha

| Trilha | Quando |
|---|---|
| `rapida` | ajuste, bugfix ou melhoria que cabe em até 1 dia e não tem desenho a decidir |
| `bet` | o resto, com apetite de até 2 semanas |

Use a trilha que o usuário pediu (`bet-new rapida <IDEA>`). Sem pedido, escolha uma e diga o motivo em uma linha.

- Item rápido que precisa de desenho vira `bet`.
- Bet que passa de 2 semanas vira duas: proponha o corte antes de seguir.
- A trilha `bet` espera um protótipo com veredito `segue` ou `ajusta`. Sem veredito, sugira a skill `prototype` antes. Se o usuário quiser seguir assim mesmo, siga e escreva no corpo da bet que não houve protótipo.

## 3. Proponha os campos

Proponha você mesmo cada campo, tirado da Idea e do pedido, e siga sem perguntar. Quem aprova o PR revisa e ajusta lá: a aprovação é a decisão. Pergunte só quando o próprio problema estiver confuso.

- `appetite`: duração ISO (`P1D`, `P1W`, `P2W`). Na rápida, no máximo `P1D`.
- `hypothesis`: "se fizermos X, Y acontece para Z".
- `success_metric`: como o time vai saber que deu certo.
- `kill_criteria`: o que faz o time parar.
- `tier`: 0, 1 ou 2. Superfície pública (CLI, MCP, skill, API), auth, dados de cliente, permissões de agente e prompt ou modelo que as squads usam são Tier 2, que também pede o Lead. Diga isso no corpo do PR.
- `pods`: os pods que a bet toca.
- O corpo da bet guarda o intent: problema, para quem e sinal (da Idea), o que entra e o que fica fora.

Na rápida, hipótese e critério de kill cabem em uma linha cada.

Nunca pergunte `decision_by` nem os aprovadores. O `t0 new bet` propõe o Bet Owner do pod e o `t0 gate aposta` deriva o Lead dos holders em `team/roles/*.md`, do tier e dos pods.

## 4. Abra o PR da aposta

```
t0 new bet --track rapida|bet <IDEA|"texto"> --tier <N> --body-file <corpo> --set hypothesis="..." --set kill_criteria="..."
```

Os nomes das chaves estão em `t0 new bet --help`. O `t0` reserva o `BET-NNN`, cria `products/<pod>/bets/BET-NNN/bet.md` numa branch da bet no KB e abre o PR em draft. `state` e `verified` são do `t0` e do PR: o CI move a Bet para `active` quando o PR é aprovado.

Edição à mão depois disso vai na mesma branch: commit e `git push`. Termos de glossário que uma sessão de `grill` deixou pendentes entram aqui, um arquivo por termo em `glossary/`, no formato da skill `grill`.

O corpo do PR segue `references/pr-aposta.md`. Se o `t0` não preencher o corpo, use `gh pr edit <PR> --body-file <arquivo>`. O PR fica em draft: marcar pronto e fazer merge é de humano.

## 5. Na trilha rápida, escreva o slice

Na rápida não há spec: o slice nasce no mesmo PR da aposta, em `products/<pod>/bets/BET-NNN/slices/01-<slug>.md`. Se o `t0 new bet` não criar o esqueleto, crie com `t0 new slice <BET>`. Preencha seguindo `references/slice-rapida.md`:

- atual: o que acontece hoje, observável;
- esperado: o que deve acontecer depois;
- não muda: os comportamentos vizinhos que continuam iguais;
- o teste: qual teste, em que seam, o que ele afirma. Ele fica vermelho com o comportamento atual e verde com o esperado;
- critérios de aceite em bullets, como verificar, `repo` e tier.

Critério de aceite é sempre bullet com uma afirmação de comportamento. Nenhuma linha começa com "Dado que", "Quando" ou "Então".

## 6. Confira

```
t0 kb check --changed-from main
t0 gate aposta <BET> --dry-run
```

Corrija o que eles recusarem e faça push de novo. O gate lista quem aprova: copie para o corpo do PR. Registre com `t0 log progress "aposta da <BET> aberta" --bet <BET>`.

## 7. Feche

Responda em pt-BR com:

- o `BET-NNN`, a trilha e o link do PR em draft;
- quem aprova, segundo o gate, e por quê;
- os campos que você propôs, para o aprovador ajustar no PR;
- o próximo passo depois do merge: na rápida, a skill `slice-build` no slice; na bet, a skill `bet-spec` (ou a `grill` antes, se ainda há decisão aberta).
