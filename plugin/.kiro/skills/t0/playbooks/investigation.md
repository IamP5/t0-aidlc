# Playbook investigation

Você é dono da resposta. Este playbook só lê: sai uma explicação citada ou uma recomendação, sem mudança de código e sem PR.

1. Mapeie o subsistema pela fonte: código do repo, KB (`t0 kb find|get`, ou `kb_find` e `kb_get` no MCP `t0-kb`) e `git log` e `git blame` locais. Para "por que foi feito assim", leia ADR, spec e Bet antes do código. Leitura grande vai para um subagente `t0-agent` só leitura, com ponteiros no brief. `~/.t0/inbox/` fica fora.
2. Escreva o checkpoint em uma linha: `checkpoint de vazão: n/a, investigação só leitura`.
3. Escreva a saída com as seções Visão geral, Conceitos, Como funciona, Onde mora e Pegadinhas. Pedido de decisão entre alternativas vira recomendação com tabela de tradeoffs.
4. Ligue cada afirmação ao arquivo e linha, ao doc do KB ou ao commit que a sustenta. O que você não leu leva rótulo de inferido ou palpite.
5. Se a investigação precede mudança de código, pare aqui e devolva para o roteamento da skill `t0` (`rapida`, `bet` ou `slice`).

Na resposta: a saída do passo 3. Em "a gente tem certeza?", dê seu julgamento com os motivos e conteste a premissa quando ela estiver errada.
