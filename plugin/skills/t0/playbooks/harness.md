# Playbook harness

Erro de agente repetido vira sensor. Na primeira ocorrência, o `slice-verify` abre um Harness Item. Na segunda, o item sobe a escada: sensor computacional, regra de área, skill e, por último, `AGENTS.md`.

1. Ache o Harness Item em `harness/` (`t0 kb find` ou `kb_find`). Sem item, crie com `t0 new harness`. Junte a evidência das duas ocorrências: link do PR, linha do `.audit/<KEY>.tsv` ou registro no KB.
2. Rode `harness-fix <HI>`. Ela escolhe o degrau mais alto que resolve, prova o check num erro real do passado e abre um PR em draft no repo certo.
3. Quando o item é o mapa do `verify-<app>` envelhecido, rode a metade de manutenção do `verify-setup` no lugar do passo 2, com um PR em draft.
4. Pare. Review e merge do PR são do time. No Harness Health, o `ritual harness-health close` recusa fechar sem um PR por item aceito.

Na resposta: o item, as duas ocorrências com a evidência, o degrau escolhido e por que os de cima não serviam, a prova do check no erro antigo e o link do PR.
