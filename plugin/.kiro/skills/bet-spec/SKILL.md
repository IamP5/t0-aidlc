---
name: bet-spec
description: "Escreve o spec de uma bet ativa em `products/<pod>/bets/<BET>/spec.md`, na branch da bet, sintetizando a conversa em pt-BR com critérios de aceite, como verificar e tier. Confere os seams de teste com o usuário. Use para escrever ou refazer o spec de uma bet."
metadata:
  credits: "Baseada em MP to-spec (mattpocock-skills 1.3.1, MIT)"
---

# bet-spec

Transforme o que já foi conversado (daily do pod, `grill`, protótipo) no spec da bet. Sintetize o que você já sabe, sem entrevistar. Decisão que ficou faltando vira `[PRECISA ESCLARECER: <pergunta>]` no ponto onde ela pesa. Quando são várias, sugira a skill `grill` antes.

O spec mora no KB, na pasta da bet, e chega ao `main` junto com os slices, num PR só. Aprovar esse PR é a decisão de spec (Bet Owner, e também o Lead em Tier 2). Esta skill escreve e commita o spec; quem abre o PR é a skill `bet-slice`.

O spec fica só no KB. Nenhum passo desta skill fala com Jira ou issue tracker: o espelho no Jira é do CI, depois do merge.

## 1. Ache a bet e a branch

- `t0 bet detect` devolve a bet e o pod. Sem o `t0`, leia `.t0/bet.json` ou o nome da branch (`bet/<BET>/...`).
- `t0 kb get <BET>`, ou `products/<pod>/bets/<BET>/bet.md`. A bet precisa estar `active` e na trilha `bet`.
  - `proposed`: a aposta ainda não foi aprovada. Diga isso e pare.
  - trilha `rapida`: não tem spec, o slice já nasceu no `bet-new`. Diga isso e pare.
- Trabalhe no worktree da branch da bet, que o `t0` imprime e o `git -C kb worktree list` lista. Sem worktree, o `t0 new spec <BET>` cria um e imprime o caminho. Nunca troque a branch do clone do KB: ele fica no `main`.

## 2. Explore

Leia o que já existe antes de escrever:

- o `bet.md` (intent, hipótese, fora de escopo) e a Idea de origem, com o veredito e a ref do protótipo;
- o glossário em `glossary/` e os ADRs do produto (`products/<pod>/adr/`) e da metodologia (`methodology/adr/`);
- o spec vivo do produto (`products/<pod>/spec.md`), com os contratos das superfícies;
- os repos do `products/<pod>/workspace.md`, e o código deles quando ajudar.

Use o vocabulário do glossário em todo o spec e respeite os ADRs da área. Se o combinado contradiz um ADR, aponte isso ao usuário. Termos que uma sessão de `grill` deixou pendentes vão agora para `glossary/`, nesta branch, no formato da skill `grill`.

## 3. Confira os seams de teste

Desenhe os seams onde a feature vai ser testada:

- prefira seams que já existem;
- use o seam mais alto possível;
- seam novo, proponha no ponto mais alto que der;
- quanto menos seams pelo código, melhor; o ideal é um.

Confira com o usuário que os seams batem com o que ele espera. Se nesta conversa o usuário já disse quais seams foram combinados, conte como confirmado: repita os seams na sua resposta e siga.

## 4. Escreva o spec

O caminho é `products/<pod>/bets/<BET>/spec.md`. Crie com `t0 new spec <BET>`, que parte do Template do KB. Se o comando ainda não existir ou o `t0` não estiver no PATH, escreva o arquivo direto nesse caminho.

As seções vêm do Template `templates/spec.md` do KB quando ele tem corpo. Sem corpo, use `references/spec-template.md`. Leia o template escolhido antes de escrever e mantenha os títulos dele, em pt-BR, na ordem.

Regras de conteúdo:

- Histórias de usuário: lista longa e numerada, cobrindo todos os aspectos da feature, no formato "Como <ator>, quero <capacidade>, para <benefício>".
- Critérios de aceite: bullets, cada um uma afirmação de comportamento observável e verificável ("o job posta no canal do time o link e o autor de cada PR parado"). Em todo o spec, nenhuma linha começa com "Dado que", "Quando" ou "Então": escreva a condição no meio da frase ("o job ignora PR em draft").
- Como verificar: os testes nas seams combinadas, os comandos e o `verify-<app>` do repo quando existir.
- Tier: 0, 1 ou 2, com o motivo em uma linha. Superfície pública (MCP, CLI, skill, API), auth, dados de cliente e permissões de agente são Tier 2.
- Fora de escopo: cada coisa que ficou de fora, com as palavras que o usuário usou.
- Decisões de implementação ficam sem caminho de arquivo e sem trecho de código, porque envelhecem rápido. A exceção é o trecho de protótipo que codifica uma decisão melhor que prosa (reducer, máquina de estados, schema): cite só a parte que decide e avise que veio do protótipo.
- Design é opcional. Deixe a seção de fora, a menos que a conversa já tenha fechado um desenho ou a skill `architect` tenha rodado.

Critérios e como verificar moram só nas seções do corpo, que é o que o `t0 gate spec` lê. No frontmatter, `seams` lista os seams confirmados. `markers_open`, `jira` e `status` são derivados: o `kb-render` escreve.

Decisão que é difícil de desfazer, surpreendente sem contexto e fruto de trade-off real vira ADR com `t0 new adr` (`--dry-run` primeiro), citado no spec.

## 5. Confira e commite

- Rode `t0 kb check --changed-from main` e corrija o que ele apontar.
- Releia o spec contra a conversa: toda decisão combinada está nele, e todo item que o usuário tirou está em Fora de escopo.
- Commite o spec (e os termos de glossário, se houver) na branch da bet, com a mensagem `spec(<BET>): <título da bet>`.
- Registre com `t0 log progress "spec da <BET> escrito" --bet <BET>`.

## 6. Feche

Responda em pt-BR com:

- o caminho do spec e a branch;
- o resumo: o problema em uma linha, quantas histórias, os critérios de aceite, o tier e os seams;
- os `[PRECISA ESCLARECER]` abertos, que bloqueiam o `t0 gate spec` até serem resolvidos;
- os ADRs propostos, se houver;
- o próximo passo: a skill `bet-slice` corta os slices e abre o PR em draft com spec e slices.
