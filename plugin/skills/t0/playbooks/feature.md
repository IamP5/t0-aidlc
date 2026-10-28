# Playbook feature

Você é dono do desenho. Delegue a implementação e fique na liderança. Este playbook roda dentro do passo de build do `playbooks/slice.md`.

1. Leia o subsistema afetado e o spec no KB: critérios de aceite, costuras, Como verificar e a seção Design quando existir.
2. Nomeie o formato dos dados primeiro e escolha a estrutura que o organiza (`model-the-domain`): máquina de estados no lugar de booleanos espalhados, tabela ou registro no lugar de ramos, modelo tipado no lugar de suposição de formato repetida. Se o desenho cruza fronteira de função e o spec não tem Design, rode `architect`.
3. Escreva o checkpoint de vazão como quatro itens da lista. Dimensão que não se aplica fica com `n/a: <motivo>`.
   - Primeiros passos bloqueantes: o que roda antes de abrir em paralelo.
   - Frentes independentes: arquivos, serviços ou camadas disjuntos andam em paralelo. Escrita compartilhada serializa.
   - Estado mutável compartilhado: por padrão, divida o alvo (`separate-before-serializing-shared-state`). Serialize só por invariante real.
   - Menor decomposição segura: se um trabalhador só é o melhor, diga por quê.
4. Delegue o código a um `t0-agent`, com o modelo do papel na Policy `models` e escopo fechado: caminhos, formato dos dados e estrutura escolhidos no passo 2, critério de pronto. Quando a implementação admite mais de um formato válido (tratamento de erro, camada de abstração, estrutura de teste), delegue pela `arena`, que mostra as alternativas e julga entre elas, com `same-family` quando for o caso. Edição cirúrgica. Melhoria num primitivo compartilhado vai para todos os consumidores, e cada um é verificado. Commit à vontade na branch do slice.
5. Verifique na superfície certa pelo `verify-<app>`. "Inconclusivo" ou superfície errada conta como falha de verificação, e você sinaliza.
6. Organize em commits pequenos e ordenados antes do primeiro push (`sequence-verifiable-units`). Cada unidade é construída, verificada e commitada antes da próxima.
7. Volte ao `slice-build` para provar no app e abrir o PR em draft.

Trabalho acoplado (uma feature, uma migração) fica com um dono só, com o checkpoint no brief, e ele abre em paralelo depois da fase bloqueante. Fan-out no nível do pai serve para frentes que produzem artefatos independentes. Reescreva o checkpoint a cada fronteira de fase.

Na resposta: o que você construiu e para quem, o que escolheu e por quê, o checkpoint e as decisões em aberto. Use tabela para alternativas de desenho.
