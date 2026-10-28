# Playbook ritual

Rituais: `daily-time`, `daily-pod`, `harness-health`, `demo`, `retro` e `pi`. O registro sai dos comandos. Ninguém escreve ata à mão.

1. Identifique o slug e quem facilita: Flow Steward na daily do time, na Demo e na Retro; Bet Owner na daily do pod; Harness Keeper no Harness Health; Lead no PI.
2. Rode `ritual <slug> open`. Na `daily-time`, ele imprime o digest: merges, review parado há mais de 24h e travas.
3. Durante o ritual, encaminhe o que surgir pelo playbook certo. Ideia vai para `playbooks/ideia.md`. Aposta vai para `bet-new`, e a pessoa aprova o PR. Spec em mob segue os passos 4 a 9 de `playbooks/bet.md`. Erro repetido vai para `playbooks/harness.md`. Trava vira `t0 log blocker`.
4. Com gravação, entregue o arquivo só pelo `ritual <slug> close --transcript <arquivo>`. A redação (`t0 transcript redact`) roda antes de qualquer modelo, e a persistência fica em dry-run até o aval de LGPD. Conversa 1:1 fica sem gravação. Tudo que sair da transcrição entra sem `verified`.
5. Rode `ritual <slug> close`. Fechar `harness-health` recusa sem PR por item aceito. Fechar `demo` grava o rodízio. Retro que muda a metodologia abre ADR por `t0 new adr`.
6. Mostre o registro gerado e liste o que ficou esperando confirmação humana.

Na resposta: o Ritual Record (caminho ou PR), as decisões e os donos, as ideias e os ADRs extraídos sem `verified` e as recusas de fechamento com o motivo.
