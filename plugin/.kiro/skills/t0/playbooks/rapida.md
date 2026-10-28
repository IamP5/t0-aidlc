# Playbook rapida

Trilha rápida: ajuste, bug ou melhoria que cabe em até 1 dia. Não tem spec. O slice já nasce com "atual, esperado, o que não muda" e um teste que fica vermelho antes do fix. Superfície pública (MCP, CLI, skill, API) continua Tier 2.

1. Confirme que cabe na trilha: até 1 dia, sem desenho novo, uma mudança só. Item que precisa de desenho vai para `playbooks/bet.md`.
2. Ache a Idea no KB (`t0 kb find` ou `kb_find`). Sem Idea, siga com o texto do pedido: o `t0 new bet --track rapida "<texto>"` cria Idea, Bet e Slice no mesmo PR da aposta. Sem passo de `idea-capture`.
3. Observe o "atual" no produto. Bug: reproduza na mesma superfície pelo `verify-<app>` do repo e guarde a saída. Melhoria: registre o comportamento de hoje.
4. Escreva "atual", "esperado", "o que não muda" e o teste que vai ficar vermelho. Critérios de aceite em bullets. Escolha o tier por `methodology/practices/review-tiers.md` no KB.
5. Rode `bet-new rapida <IDEA|"texto">`. Ela roda `t0 new bet --track rapida`, escreve a Bet e o único Slice (e a Idea, quando veio texto) e abre o PR da aposta em draft.
6. Pare. A aposta é decisão humana: o Flow Steward ou o Bet Owner aprova o PR na daily. Entregue o link e o resumo para quem decide.
7. Depois do merge, o CI espelha no Jira e o slice fica `ready`. Siga para `playbooks/slice.md` com a chave.

Na resposta: atual, esperado e o que não muda; a saída da reprodução; o tier; o link do PR da aposta; quem aprova.
