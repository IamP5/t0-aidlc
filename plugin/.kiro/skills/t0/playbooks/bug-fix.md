# Playbook bug-fix

Você é dono do diagnóstico. Delegue a investigação pesada e o fix para subagentes e fique na liderança. Este playbook roda dentro do passo de build do `playbooks/slice.md`.

Seja científico. Toda linha que entra tem evidência de execução por trás. "Pode ajudar" é hipótese e fica fora do diff. Quando a evidência derruba uma hipótese, reverta o que ela motivou. Entra a menor mudança que a evidência justifica.

1. Reproduza você mesmo, na superfície do bug, pelo `verify-<app>` do repo. Peça ao humano só com um motivo específico de a superfície não alcançar o alvo, e só depois de ir até onde ela vai. Se não reproduz direto, sintetize o gatilho, aperte as condições ou instrumente até disparar. O passo acaba com a saída da falha colada na trilha.
2. Faça busca binária da causa. Liste as hipóteses e elimine até sobrar uma, sempre pela divisão que corta mais do espaço restante, com evidência de execução. Semeie as hipóteses lendo o subsistema e o histórico (`git log`, ADRs e spec no KB). Estado obscuro pede log ou instrumentação, lida com o código rodando. Confirme o mecanismo com evidência antes do passo 3.
3. Planeje o fix. Se ele cruza fronteira de função, rode `architect` antes. Delegue a implementação a um `t0-agent`, com o modelo do papel na Policy `models` e escopo fechado (arquivos, mecanismo confirmado, teste que precisa ficar verde).
4. Verifique na mesma superfície: a reprodução original passa agora. "Inconclusivo" ou superfície errada conta como falha de verificação, e você sinaliza. Teste unitário mostra o comportamento de um ramo e deixa o bug em aberto.
5. Ordene os commits para o teste vermelho entrar antes do fix (`sequence-verifiable-units`). Quando o teste local é barato, siga o vermelho e verde do `slice-build`. Teste caro, de integração pesada ou incerto fica de fora, e a reprodução vai para o PR no lugar dele. Organize os commits antes do primeiro push. Depois do push, só commit novo.
6. Volte ao `slice-build` para provar no app e abrir o PR em draft.

Na resposta: o que quebrou, a causa raiz, o fix e como você verificou, com a saída da reprodução falhando e depois passando, colada sem edição.
