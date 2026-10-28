# Playbook slice

Construir e verificar um slice `ready`. Tudo aqui é trabalho reversível dentro do slice e segue sem perguntar. Review humano e merge ficam com o time e com o CI.

1. Rode `slice-build <KEY>` nas seções 1 a 3: entender o slice, `t0 slice dor <KEY>` (DoR e WIP de 2 por pessoa), `t0 slice start <KEY>`, branch `<KEY>-<slug>` e trilha `.audit/<KEY>.tsv`. Se o `dor` recusar, mostre a recusa exata e pare.
2. Confira se o repo tem `.t0/skills/verify-<app>/`. Sem ele, rode `verify-setup` antes de seguir. Com ele, `pular: verify-<app> existe`.
3. Escolha o método pelo slice e troque este passo pelos passos dele na lista: bug vai para `playbooks/bug-fix.md`, comportamento novo para `playbooks/feature.md`, estrutura sem mudar comportamento para `playbooks/refactoring.md`, lentidão medida para `playbooks/perf-issue.md`. Os passos do método rodam dentro das seções 4 e 5 do `slice-build` (costuras, vermelho e verde).
4. Volte ao `slice-build` nas seções 6 a 8: provar no app pelo `verify-<app>`, auditar a trilha, abrir o PR em draft com `Jira`, `Tier`, `Trilha` e "Em minhas palavras" quando exigida. O `slice-build` para no PR.
5. Rode `slice-verify <KEY>`: review contra o spec, blast radius em Tier 2, `swarm` para a matriz de cobertura e evidência pelo `verify-<app>`.
6. Corrija o que o `slice-verify` achou com commit novo na branch e volte ao passo 5 até não sobrar pendência. Erro repetido do agente vira Harness Item, que o `slice-verify` abre.
7. Pare. O review humano segue o tier, o merge é do time e o CI move os estados (`t0 ci <KEY>`).

Na resposta: o link do PR em draft, o que o slice entrega para quem usa, a evidência do `verify-<app>`, as pendências do review, os Harness Items abertos e quem revisa a seguir pelo tier.
