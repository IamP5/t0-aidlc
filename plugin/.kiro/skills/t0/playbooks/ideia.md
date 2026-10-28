# Playbook ideia

Você responde pelo veredito. A ideia sai daqui com uma linha na Idea (`segue`, `ajusta` ou `mata`) e a evidência do protótipo. O protótipo fica fora do main e é descartável.

1. Rode `idea-capture`. Ela procura duplicata e roda `t0 new idea`. Se achar uma Idea que já cobre o pedido, use essa e diga qual. O passo acaba com um `IDEA-NNNN` em mãos.
2. Se a ideia está vaga (problema sem dono, termo ambíguo, nenhum sinal do que seria sucesso), rode `grill` até dar para escrever a pergunta do passo 3. Ideia clara fica com `pular: ideia já tem pergunta testável`.
3. Escreva, em uma frase, a pergunta que o protótipo vai responder. Sem pergunta, sem protótipo.
4. Rode `prototype <IDEA>`. Fora do main, de minutos a horas. Com mais de uma direção, as variantes ficam atrás de um seletor.
5. Observe a resposta na superfície certa (tela, saída, tempo) e junte a evidência.
6. Grave o veredito pela skill `prototype`, que roda `t0 idea prototype <IDEA> --verdict segue|ajusta|mata --ref <R>`. Proponha o veredito com a evidência e deixe quem prototipou confirmar. Com `ajusta`, volte ao passo 3.
7. Com `segue`, diga qual trilha cabe: `rapida` (até 1 dia, sem desenho novo) ou `bet` (até 2 semanas). A aposta é do Bet Owner na daily do pod. Você só prepara.

Na resposta: o `IDEA-NNNN`, a pergunta, as variantes com a evidência, o veredito gravado, o caminho do protótipo (descartável) e a trilha sugerida.
