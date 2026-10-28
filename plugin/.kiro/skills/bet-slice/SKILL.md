---
name: bet-slice
description: "Corta o spec de uma bet em slices verticais (tracer bullets) com dependências, aprova o corte com o usuário e grava um arquivo por slice na branch do spec, abrindo o PR em draft da decisão de spec. Use depois do `bet-spec` ou para refazer os slices de uma bet."
metadata:
  credits: "Baseada em MP to-tickets (mattpocock-skills 1.3.1, MIT)"
---

# bet-slice

Quebre o spec da bet em slices: tracer bullets verticais, cada um declarando os slices que o bloqueiam. Um slice é um repo e vira um PR de código.

Os slices vão na mesma branch e no mesmo PR do spec. Aprovar esse PR é a decisão de spec, que o Bet Owner toma (e também o Lead em Tier 2). Você propõe o corte e abre o PR em draft. O espelho no Jira (uma Story por slice, com link Blocks) é do CI, depois do merge: nenhum passo desta skill fala com Jira ou issue tracker.

## 1. Junte o contexto

- `t0 bet detect` devolve a bet e o pod. Trabalhe no worktree da branch `bet/<BET>/...` que já tem o `spec.md`. O `git -C kb worktree list` mostra onde ele está.
- Sem spec na trilha `bet`, siga primeiro para a skill `bet-spec`. Na trilha `rapida` o slice já nasceu no `bet-new`: diga isso e pare.
- Leia o spec inteiro, o `products/<pod>/workspace.md` (repos e `depends_on` entre eles), os ADRs da área e o glossário.
- Se já existem slices em `slices/`, você está refazendo o corte. Edite os arquivos existentes e mantenha os números quando der.

## 2. Explore o código

Leia os repos que o spec toca, quando ainda não leu. Use o vocabulário do glossário nos títulos e respeite os ADRs. Procure prefactoring que facilite o resto: primeiro deixe a mudança fácil, depois faça a mudança fácil.

## 3. Rascunhe os slices

Regras do slice vertical:

- cada slice corta um caminho estreito, mas completo, por todas as camadas (schema, API, UI, testes);
- um slice pronto se demonstra ou se verifica sozinho;
- cada slice cabe numa janela de contexto nova;
- prefactoring vem primeiro;
- um slice mexe num repo só. Trabalho que cruza repos vira um slice por repo, ligados por `depends_on`, e cada PR se sustenta sozinho em deploy (expand, migrate, contract);
- todo critério de aceite do spec aparece em pelo menos um slice.

Dê a cada slice as dependências que o bloqueiam: os outros slices que precisam terminar antes. Slice sem bloqueio começa logo depois do merge.

O tier de cada slice parte do tier do spec. Slice que toca superfície pública, auth, dados de cliente ou permissões de agente é Tier 2.

Refactor largo é a exceção ao corte vertical. É uma mudança mecânica (renomear uma coluna, trocar o tipo de um símbolo compartilhado) cujo blast radius espalha pelo código inteiro, de modo que um slice vertical não fecha verde. Sequencie como expand e contract:

1. expand: acrescente a forma nova ao lado da antiga, sem quebrar nada;
2. migre os chamadores em lotes do tamanho do blast radius (por pacote, por diretório), cada lote um slice bloqueado pelo expand, com o CI verde lote a lote porque a forma antiga ainda existe;
3. contract: apague a forma antiga num slice bloqueado por todos os lotes.

Se nem os lotes fecham verdes sozinhos, mantenha a sequência e deixe os lotes numa branch de integração comum, todos bloqueando um slice final de integrar e verificar. O verde só é prometido nele.

## 4. Aprove o corte com o usuário

Mostre o corte como lista numerada:

```
1. <Título>
   Repo: <repo> · Tier: <n> · Bloqueado por: <nenhum | 01, 02>
   Entrega: <o comportamento ponta a ponta que este slice faz funcionar>
```

Pergunte:

- A granularidade está boa, ou grossa ou fina demais?
- As dependências estão certas? Cada slice depende só do que realmente o trava?
- Algum slice deve ser juntado ou quebrado?

Itere até o usuário aprovar o corte. Essa aprovação é do corte; a decisão de spec continua sendo a aprovação do PR.

## 5. Grave um arquivo por slice

Cada slice é um arquivo `products/<pod>/bets/<BET>/slices/NN-<slug>.md`, numerado a partir de `01` na ordem das dependências (quem bloqueia vem antes). Crie cada um com `t0 new slice <BET>`. Se o comando ainda não existir ou o `t0` não estiver no PATH, escreva o arquivo direto no caminho.

As seções vêm do Template `templates/slice.md` do KB quando ele tem corpo. Sem corpo, use `references/slice-template.md`. Cada slice tem:

- `repo`, um dos repos do `workspace.md`;
- `depends_on[]`, com os ids `NN-<slug>` dos slices desta bet que o bloqueiam (lista vazia quando nenhum);
- tier;
- critérios de aceite em bullets, cada um uma afirmação de comportamento. Nenhuma linha começa com "Dado que", "Quando" ou "Então";
- como verificar.

Descreva o comportamento ponta a ponta, sem caminho de arquivo e sem trecho de código, que envelhecem rápido. A exceção é o trecho de protótipo que decide algo (reducer, máquina de estados, schema): cite só a parte que decide e avise a origem. `jira`, `pr` e os estados depois de `ready` são do CI e do `kb-render`.

## 6. Confira, commite e abra o PR

1. Rode `t0 kb check --changed-from main` e corrija o que ele apontar.
2. Rode `t0 gate spec <BET> --dry-run`. Ele recusa com `[PRECISA ESCLARECER]` aberto e confere o Lead em Tier 2. Marcador aberto se resolve com o usuário, editando o spec nesta branch.
3. Commite os slices com a mensagem `slices(<BET>): <n> slices` e faça push da branch.
4. Sem PR para a branch, abra com `gh pr create --draft`, título `Spec <BET>: <título da bet>` e corpo de `references/pr-spec.md`. Com PR aberto, atualize o corpo com `gh pr edit <PR> --body-file <arquivo>`. O PR fica em draft: marcar pronto e fazer merge é de humano.
5. Registre com `t0 log progress "spec e slices da <BET> no PR" --bet <BET>`.

## 7. Feche

Responda em pt-BR com:

- o link do PR em draft;
- os slices, com repo, tier e dependências;
- a fronteira: os slices sem bloqueio, que podem começar logo depois do merge;
- quem precisa aprovar o PR;
- o que acontece depois do merge: o CI espelha a bet e os slices no Jira, e a skill `slice-build` pega os slices da fronteira.
