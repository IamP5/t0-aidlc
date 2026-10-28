# Plugin e skills

O plugin `t0` leva o fluxo para dentro do agente. Ele traz 15 skills em pt-BR, quatro subagentes, o MCP `t0-kb` e os hooks que mantêm as travas do time. O plugin roda igual no Claude Code, no GitHub Copilot e no Kiro.

Alguns termos aparecem na página inteira:

- Uma skill é um conjunto de instruções, num `SKILL.md`, que o agente segue para fazer um passo do fluxo. No Claude Code, as skills do plugin aparecem como `/t0:<nome>`.
- Um subagente é um agente que outro agente chama para uma tarefa delimitada. Ele nasce sem memória da conversa.
- Um hook é um comando que a ferramenta roda sozinha em certos eventos, como o início da sessão ou o momento antes de usar uma ferramenta. Os hooks do t0 guardam as travas.
- O MCP `t0-kb` é o servidor local, por stdio, que deixa o agente buscar, ler e registrar no KB.
- Um playbook é a sequência de passos que a `/t0` segue para um tipo de pedido.
- Uma worktree é uma cópia de trabalho separada de um repo git.

O time escreveu as skills à mão, em pt-BR, usando as do mattpocock-skills e do pstack como referência. Cada `SKILL.md` credita a sua referência em `metadata.credits`, e o `THIRD_PARTY_NOTICES.md` do plugin carrega as licenças MIT.

## Instalação

O plugin não tem código Python. Hooks e MCP chamam o comando `t0`. Os hooks passam por `hooks/t0-hook.sh`. Esse script procura o `t0` no PATH ou fixado no workspace em `.t0/bin/t0`, subindo a partir da pasta atual. No início da sessão, ele exporta esse caminho e `T0_KB=<workspace>/kb` para o shell do agente. Assim o shell acha o `t0` e o KB mesmo depois de sair do workspace. Sem `t0` instalado, os hooks ficam desligados, com um aviso.

Um comando instala tudo. Clone o repo do t0 e rode:

```
./install.sh --kb <remote do KB>
```

O script instala a CLI a partir de `./toolkit`, com `uv` ou `pipx` (Python 3.11 ou mais novo). Depois roda o `t0 install`, que adiciona o marketplace deste repo ao Claude Code, instala o plugin `t0@t0-aidlc`, grava as configs de usuário e monta os workspaces dos seus produtos. O passo a passo está em [Workspace](06-workspace.md).

Sem o `claude` no PATH, o `t0 install` pula o plugin e imprime o comando para rodar depois. Copilot e Kiro ainda são à mão:

| Ferramenta | Como |
|---|---|
| Claude Code | `t0 install`; à mão, `claude plugin marketplace add <repo t0-aidlc>` e `claude plugin install t0@t0-aidlc`; para testar local, `claude --plugin-dir ./plugin` |
| Copilot CLI | `copilot plugin install`, que lê o formato Claude (não verificado no ambiente do banco) |
| Copilot no VS Code | como Agent Plugin, no formato Agent Plugins 1.0 (não verificado) |
| Kiro | como power, no formato Agent Plugins 1.0 (não verificado) |

Em cada repo de produto, rode `t0 setup` uma vez e commite. O comando escreve o bloco t0 no `AGENTS.md`, os ponteiros por ferramenta, os hooks e os links da skill `verify-<app>`. O `t0 ws init` lista os repos que ainda não têm o bloco.

Sem o `install.sh`, instale a CLI com `pipx install ./toolkit` e rode `t0 install --plugin-source <repo t0-aidlc> --kb <remote do KB>`.

A versão do plugin é a mesma do pacote `t0`. Quando um atualiza, o outro atualiza junto.

## `/t0`, a porta de entrada

Na dúvida, comece por `/t0` (no Claude Code, `/t0:t0`). A `/t0` entende o pedido e escolhe um playbook. Depois abre a lista de tarefas com os passos desse playbook e chama as skills de passo. As skills de passo fazem o trabalho. A `/t0` cuida das travas, do roteamento e do jeito de responder.

### Inegociáveis

Os inegociáveis valem em todo playbook e em toda skill. Um hook bloqueia boa parte deles.

- Todo PR nasce em draft e fica em draft. Marcar pronto, fazer merge, force push e `reset --hard` cabem ao humano ou ao CI.
- Sem forge (sem remote, com `gh` ausente ou com push desativado), o PR em draft do repo de produto é a branch local, com o corpo em `.t0/pr/<branch>.md`. Antes de qualquer push, `slice-build`, `harness-fix` e `verify-setup` conferem `gh repo view` e a URL de push. No KB, o `t0 kb propose` cuida disso.
- Há três decisões humanas: aposta, spec e degrau. A skill prepara a decisão, abre o PR, mostra a evidência e para. Aprovar o PR é decidir.
- Trabalho reversível dentro de um slice segue sem perguntar. Isso inclui código, teste, commit na branch do slice, rascunho na branch da bet e protótipo fora do main.
- A escrita no KB passa por comando `t0` ou por arquivo na branch da bet, que entra por PR. Arquivos e chaves derivados ficam com o `kb-render`.
- O Jira é do CI. Nenhuma skill chama Jira nem issue tracker.
- `~/.t0/inbox/` fica fora de qualquer leitura. Transcrição entra só redigida.
- O modelo de qualquer execução paralela vem da Policy `models` do KB. Quando só uma família de modelo está aprovada, a saída sai marcada `same-family`.
- PR de código nasce de um slice (`slice-build`) ou de um Harness Item (`harness-fix`). Um pedido de código sem slice termina no PR da aposta. Na rápida, `t0 new bet --track rapida "<texto>"` cria Idea, Bet e Slice juntos, sem passo de ideia.
- Quando um comando `t0` falha ou não existe, a skill mostra a saída exata e deixa o passo pendente. Escrever à mão o que o comando gravaria fura a raia.
- Toda saída para o humano é em pt-BR.

### Playbooks

A `/t0` escolhe o playbook pelo que o pedido move no KB:

| Playbook | Para quê |
|---|---|
| `ideia` | ideia nova, até o veredito do protótipo |
| `rapida` | ajuste, bug ou melhoria que cabe em 1 dia sem desenho novo; abre a aposta com um slice |
| `bet` | ideia com `segue` e apetite de até 2 semanas: aposta, spec, desenho quando precisa e slices |
| `slice` | construir e verificar um slice `ready` |
| `harness` | erro de agente repetido ou Harness Item aceito |
| `ritual` | abrir, conduzir ou fechar um ritual |

A `/t0` também escolhe pelo jeito de fazer o trabalho. Os playbooks de código rodam dentro do playbook `slice`:

| Playbook | Para quê |
|---|---|
| `investigation` | pergunta só de leitura: como funciona, por que foi feito assim, X ou Y |
| `bug-fix` | reproduzir, achar a causa e corrigir com evidência de execução |
| `feature` | comportamento novo ou mudado, a partir de um formato de dados nomeado |
| `refactoring` | mudar a estrutura e preservar o comportamento |
| `prototype` | esboço descartável para decidir um fork observando o resultado |
| `perf-issue` | lentidão medida e corrigida contra um baseline |

O roteamento segue estas regras:

- Pedido só de leitura vai para `investigation`, sem slice e sem PR.
- Pedido de código com a chave de um slice `ready` vai para `slice`.
- Pedido de código sem slice vai para `rapida` quando cabe em 1 dia. Senão, vai para `ideia` ou `bet`.
- Ship, merge, PR pronto e babysit de PR ficam fora do t0. A `/t0` diz que isso é do humano e do CI e oferece outra rodada de `slice-verify`.

Antes de perguntar "qual abordagem?", a `/t0` confere se a resposta é um fato que dá para observar rodando algo. Se for, ela prototipa e deixa o resultado decidir. As perguntas ficam para escolha de produto ou preferência, uma por vez.

### Princípios de engenharia

A `/t0` carrega 19 princípios curtos, de um parágrafo cada, em `skills/t0/references/principios.md`. A resposta nomeia cada princípio que mudou uma decisão.

| Grupo | Princípios |
|---|---|
| Base | `laziness-protocol`, `foundational-thinking`, `subtract-before-you-add`, `minimize-reader-load`, `build-the-lever` |
| Arquitetura | `model-the-domain`, `boundary-discipline`, `type-system-discipline`, `make-operations-idempotent`, `separate-before-serializing-shared-state` |
| Verificação | `prove-it-works`, `fix-root-causes`, `sequence-verifiable-units`, `test-behavior-not-implementation` |
| Desenho e mudança | `exhaust-the-design-space`, `outcome-oriented-execution`, `redesign-from-first-principles`, `encode-lessons-in-structure` |
| Delegação | `never-block-on-the-human`, só para trabalho reversível dentro de um slice |

## As 15 skills num relance

| Skill | Use quando | Grava | Nunca |
|---|---|---|---|
| `t0` | o pedido cruza mais de um passo, ou na dúvida | lista de tarefas; chama as outras | aprova, faz merge ou chama Jira |
| `idea-capture` | alguém traz ideia, pedido ou dor | Idea `new` via `t0 new idea`, PR em draft | cria sem checar duplicata |
| `grill` | ideia ou spec vaga, termo ambíguo, decisão difícil de desfazer | Glossary Term; ADR `proposed` via `t0 new adr` | age antes de vocês concordarem |
| `prototype` | testar uma ideia antes de apostar | branch `proto/`; veredito via `t0 idea prototype` | toca o main ou usa dado real |
| `bet-new` | ideia com veredito vira trabalho, ou pedido direto na rápida | Bet `proposed` e PR da aposta; na rápida, o slice | aprova a aposta ou pergunta o aprovador |
| `bet-spec` | bet `active` na trilha bet precisa de spec | `spec.md` na branch da bet | abre o PR ou fala com Jira |
| `architect` | o desenho cruza fronteira de função ou não tem precedente | seção Design do spec; ADR | grava antes do ok humano ou escreve código |
| `arena` | comparar desenhos ou código com N candidatos | artefato sintetizado e nota | faz push das worktrees ou escreve no KB |
| `swarm` | matriz de cobertura, corrida, gauntlet, partição de exploração | relatório consolidado | faz push, abre PR ou escreve no KB |
| `bet-slice` | spec pronto precisa de slices | um arquivo por slice; PR em draft do spec | fala com Jira |
| `slice-build` | construir um slice `ready` | branch, commits, `.audit/<KEY>.tsv`, PR em draft | contorna o DoR, marca pronto ou faz push sem forge |
| `slice-verify` | revisar o PR de um slice antes do humano | comentário no PR; Harness Item | aprova, commita na branch do autor ou faz merge |
| `verify-setup` | repo sem `verify-<app>`, ou mapa velho | `.t0/skills/verify-<app>/` em PR em draft | edita código de produto |
| `ritual` | abrir, conduzir ou fechar um ritual | Ritual Record via `t0 ritual`; registros | escreve ata à mão ou lê `~/.t0/inbox/` |
| `harness-fix` | erro de agente pela segunda vez, ou item aceito | correção em PR em draft no repo certo | pula a prova vermelho e verde |

## Cada skill

Cada descrição abaixo segue a mesma ordem: quando usar, o que a skill faz, o que ela grava e o que ela nunca faz.

### `idea-capture`

Use quando alguém trouxer uma ideia, um pedido ou uma dor para guardar, ou disser "anota essa ideia".

A skill tira do próprio pedido o mínimo: o problema, para quem e o sinal. O que ela não consegue inferir entra como "a confirmar". Ela faz no máximo uma pergunta, e só quando o problema está obscuro. Sinal fraco vale e entra escrito como é.

Depois ela procura duplicata no KB com pelo menos duas buscas: uma pelo termo do usuário e outra pelo termo do glossário. A busca inclui ideias `killed` e `promoted`. Uma ideia morta só volta com fato novo.

Ela grava a Idea `new` em `ideas/IDEA-NNNN.md` com `t0 new idea`, sempre em dry-run primeiro. O `t0` reserva o número e abre um PR pequeno em draft.

Ela nunca decide se a ideia vira bet. Quem decide é o pod, na daily.

### `grill`

Use para "me grelha", para estressar um plano ou para afiar um spec.

A skill entrevista em rodadas. Ela monta a árvore de decisões e pergunta a fronteira inteira de uma vez. Cada pergunta vem numerada e com uma resposta recomendada. Responder "sim" aceita a recomendação. Durante a sessão, a skill confronta os termos com o glossário, testa com cenários concretos e confere com o código.

Ela grava cada termo resolvido em `glossary/<slug>.md`, bilíngue, na branch da bet. Sem bet, ela guarda a lista para a `bet-new` ou a `bet-spec` gravarem. Ela propõe ADR via `t0 new adr` só quando a decisão é difícil de desfazer, surpreende quem não tem contexto e vem de um trade-off real. Um ramo adiado vira `[PRECISA ESCLARECER: <pergunta>]`.

Ela nunca age sobre o resultado antes de o usuário confirmar que vocês chegaram ao mesmo entendimento.

### `prototype`

Use para prototipar uma ideia, testar um modelo de estado ou ver opções de tela. A skill precisa de uma Idea.

A skill escreve a pergunta em uma frase e escolhe um de dois ramos. No ramo de lógica, ela faz um HTML único com botões e roteiros que empurram o modelo pelos casos difíceis. No ramo de UI, ela faz variações bem diferentes numa rota, trocadas por parâmetro de URL. O protótipo usa só dados fictícios e estado em memória, sem polimento.

Ela trabalha na branch local `proto/<IDEA>-<slug>` do repo de produto, sem PR e sem push. O push só acontece quando alguém pede para compartilhar. O trabalho termina com o veredito `segue`, `ajusta` ou `mata`. Quem prototipou ou o pod confirma o veredito, e a skill grava com `t0 idea prototype --verdict ... --ref ...`.

O protótipo nunca vai para o main nem para o KB.

### `bet-new`

Use para transformar uma Idea em bet ou em ajuste rápido.

A skill lê a Idea. Na rápida, ela pode partir direto do texto do pedido. Ela escolhe a trilha: `rapida` para até 1 dia sem desenho, `bet` para até 2 semanas. Depois ela mesma propõe `appetite`, `hypothesis`, `success_metric`, `kill_criteria`, tier e pods, sem rodada de perguntas. Quem aprova o PR ajusta esses valores lá, porque aprovar é decidir.

Ela roda `t0 new bet --track rapida|bet <IDEA|"texto">`. O comando cria `bet.md` numa branch da bet e abre o PR da aposta em draft. Na trilha rápida, a skill também escreve o slice com o atual, o esperado, o que não muda, o teste e os critérios de aceite em bullets. Ela confere o resultado com `t0 kb check` e `t0 gate aposta --dry-run`.

Ela nunca aprova a aposta e nunca pergunta quem aprova. O `t0 new bet` põe o Bet Owner do pod em `decision_by`. O `t0 gate aposta` deriva o Lead quando a bet cruza pods, é Tier 2 ou passa de 1 semana.

### `bet-spec`

Use para escrever ou refazer o spec de uma bet `active` na trilha bet.

A skill sintetiza o que já foi conversado, sem entrevistar de novo. Uma decisão que falta vira `[PRECISA ESCLARECER]` no ponto do spec onde ela pesa. A skill lê o `bet.md`, a Idea, o glossário, os ADRs, o spec vivo do produto e o código. Ela confere com o usuário os seams de teste, que são os pontos do código onde o comportamento é testado. A preferência é por seams que já existem, no ponto mais alto possível, e o ideal é um só.

Ela grava `products/<pod>/bets/<BET>/spec.md` na branch da bet, a partir do Template do KB. O spec traz histórias de usuário, critérios de aceite em bullets, como verificar, tier e fora de escopo. A skill commita e registra com `t0 log progress`.

Ela nunca abre o PR, porque isso é da `bet-slice`. Ela também nunca fala com Jira.

### `architect`

Use para desenhar uma bet antes dos slices, ou quando a mudança cruza fronteira de função.

A skill desenha e nunca implementa. O trabalho tem quatro fases:

1. A skill fundamenta o desenho lendo KB e código, com `arquivo:linha` para cada restrição.
2. Ela esboça dois desenhos estruturalmente diferentes pela `arena`, só no papel: uma nota de desenho e no máximo um esboço de interface, sem implementação nem build.
3. Ela para num checkpoint obrigatório com o humano.
4. Só com o ok humano, ela registra.

Ela lê o KB pelo MCP `t0-kb`. Sem o MCP, ela lê por `t0 kb` ou pelos arquivos em `kb/` do workspace. Ela só para como "KB indisponível" quando os três caminhos falham. Se a bet foi nomeada, a skill fixa a bet com `t0 bet use` sem perguntar.

Ela grava a seção `## Design` do spec da bet, na mesma branch e no mesmo PR. Quando a decisão é difícil de desfazer, ela grava também um ADR `proposed`. Exemplos desse tipo de decisão são formato persistido, contrato público e fronteira entre repos ou pods.

Ela não roda na trilha rápida: se a mudança pede desenho, ela não cabe na rápida. Nada entra no repo de produto.

### `arena`

Use para comparar desenhos ou código quando uma tentativa só travaria a forma errada.

A skill escreve a rubrica e escolhe os modelos na Policy `models`. Ela roda N candidatos em paralelo, cada um numa git worktree local a partir do mesmo commit. Um juiz só leitura pontua os candidatos sem saber qual modelo fez qual. Depois a skill escolhe a base, enxerta à mão o melhor dos outros candidatos e verifica.

Ela devolve o artefato sintetizado e uma nota. A nota traz os modelos usados, o rótulo `same-family` quando couber, a base, o veredito do juiz e os enxertos.

As branches `arena/*` são locais. A skill nunca faz push nem abre PR a partir delas, e nenhum candidato entra no KB.

### `swarm`

Use para fan-out paralelo, com vários workers ao mesmo tempo. Há quatro formatos: matriz de cobertura (critério de aceite por ponto de entrada), corrida entre tentativas, gauntlet (o mesmo artefato contra várias lentes de ataque) e partição de exploração.

Antes de lançar, a skill declara o predicado de pronto e a regra de seleção. Cada worker que escreve fica isolado numa worktree presa a um SHA. A skill usa `verifier` para quem mede e `t0-agent` para quem escreve.

Ela devolve um relatório consolidado em pt-BR, com `PASS`, `ISSUES` ou `BLOCKED` e evidência por célula, mais o rótulo `same-family` quando couber. Uma lacuna nunca conta como `PASS`.

Ninguém faz push, abre PR ou escreve no KB.

### `bet-slice`

Use depois do `bet-spec`, ou para refazer os slices.

A skill corta o spec em slices verticais (tracer bullets). Cada slice atravessa todas as camadas, se demonstra sozinho, cabe numa janela de contexto e mexe num repo só. Trabalho que cruza repos vira um slice por repo, ligado por `depends_on`. Refactor largo segue expand, migrate e contract. A skill mostra o corte numerado e itera com o usuário até ele aprovar.

Ela grava um arquivo por slice em `slices/NN-<slug>.md`, na branch do spec. Depois confere com `t0 kb check` e `t0 gate spec --dry-run` e abre o PR em draft com spec e slices. Esse PR é a decisão de spec.

Ela nunca fala com Jira. O espelho no Jira vem do CI depois do merge.

### `slice-build`

Use quando alguém pede para implementar, construir ou pegar um slice ou uma chave Jira.

A skill trabalha nesta ordem:

1. Entende o slice e reescreve o objetivo com as próprias palavras.
2. Roda `t0 slice dor` e `t0 slice start`.
3. Abre a branch `<KEY>-<slug>`.
4. Constrói teste a teste, vermelho e verde, nas costuras combinadas.
5. Prova no app real pelo `verify-<app>`.
6. Abre o PR em draft.

Em Tier 2, um revisor só leitura audita a trilha, de preferência de outra família de modelo. O que ele apontar entra numa seção "Atenção" do PR.

Ela grava commits pequenos prefixados pela chave e a trilha `.audit/<KEY>.tsv`, com uma linha por decisão e só acréscimo. O PR leva `Jira`, `Tier`, `Trilha` e, quando exigida, a seção "Em minhas palavras".

Ela nunca contorna uma recusa do `dor`, nunca escreve o "Em minhas palavras" pelo autor e nunca marca o PR como pronto. O build termina no PR em draft. A revisão é um passo à parte: a skill sugere `slice-verify <KEY>`, mas não roda.

### `slice-verify`

Use para revisar um slice antes do review humano.

A skill fixa o PR e a base e acha o slice e o spec no KB. Ela roda duas raias em paralelo, com subagentes novos e só leitura: `standards-reviewer` confere os padrões do repo, e `spec-reviewer` confere o spec do KB. A skill também confere o DoD do PR e prova cada critério de aceite por ponto de entrada no app real, com `swarm` quando dá. Em Tier 2, ela roda o blast radius com escada de prova.

Ela grava um comentário só no PR, com seções separadas por raia, a matriz de evidência e os erros de agente. Um erro repetido vira Harness Item via `t0 new harness`.

Ela nunca aprova, nunca pede mudança como decisão, nunca commita na branch do autor e nunca faz merge.

### `verify-setup`

Use quando um repo não tem um jeito roteirizado de provar comportamento, ou no Harness Health, para auditar o mapa.

A skill tem dois modos. No modo criar, ela entrevista o repo e gera `.t0/skills/verify-<app>/` com as seções Subir, Diagnóstico, Dirigir, Evidência e Limpeza, mais um mapa de features. Depois prova a skill gerada de ponta a ponta contra o app real. No modo manter, ela confere cada feature pelo código e ao vivo e conserta o mapa.

Ela grava tudo num PR em draft só. No modo manter, ela também abre um Harness Item para o Harness Health fechar com o PR.

Ela nunca edita código de produto.

### `ritual`

Use para conduzir um ritual, registrar decisões e donos ou extrair ideias de uma gravação.

A skill roda `t0 ritual <slug> open` e mostra a pauta como veio. Ela registra cada decisão e cada bloqueio com `t0 log` na hora em que são ditos. No fim, fecha com `t0 ritual <slug> close`. Ela não pede confirmação antes do close: fecha e lista o que extraiu como não verificado, com quem precisa confirmar.

Com gravação, a skill roda a redação antes de tudo e faz a passada de dado de cliente. Depois extrai ideias e decisões sem `verified`.

Um bloqueio que ninguém pegou entra como `(dono: a definir)`, sem travar o ritual, e a próxima daily do time lista os sem dono. Kill de bet só entra quando o Bet Owner disse que mata.

Ela grava o Ritual Record e os registros. Quando houve gravação e o aval de LGPD, ela grava também o Transcript.

Ela nunca lê `~/.t0/inbox/`, nunca grava 1:1, nunca registra aposta ou spec como aprovados no ritual e nunca contorna a recusa de um close.

### `harness-fix`

Use com `harness-fix <HI>`, no Harness Health ou quando o mesmo erro aparece pela segunda vez.

A skill junta a evidência de cada ocorrência: commits, reviews, trilhas `.audit` e logs de sessão só deste workspace. Ela escolhe o repo onde o erro nasce e sobe a escada do harness, parando no primeiro degrau que resolve. Para cada degrau de cima que descarta, ela escreve o motivo em uma frase.

Ela grava a correção num PR em draft no repo certo, com a prova: o check falha numa ocorrência real do passado e passa com a correção. Ela registra com `t0 log decision` e atualiza o item pelo KB.

Ela nunca pula a prova, nunca marca pronto e nunca faz merge.

## Subagentes

| Subagente | Para quê | Pode escrever? |
|---|---|---|
| `t0-agent` | delegado para trabalho de passo: código num slice, rascunho na branch da bet, script, investigação | sim, dentro das travas |
| `spec-reviewer` | raia de spec do `slice-verify`: compara o diff com slice, spec e Design | não |
| `standards-reviewer` | raia de padrões do `slice-verify`: compara o diff com os padrões do repo | não |
| `verifier` | dirige o app real numa célula da matriz e devolve `PASS`, `ISSUES` ou `BLOCKED`; se o repo não tem `verify-<app>`, roda os passos do "Como verificar" do slice e sugere `verify-setup` | não, só evidência |

Todo subagente lê a `/t0` antes de trabalhar e segue os mesmos inegociáveis. Cada tarefa nova vai para um subagente novo, com o escopo consolidado no brief. O modelo de cada papel vem da Policy `models` do KB.

## Travas

O hook `pre-tool` roda nas três ferramentas pelo mesmo comando, `t0 hook <evento> --tool claude|copilot|kiro`. Ele bloqueia tanto no shell quanto nas ferramentas MCP do GitHub:

- force push e `reset --hard`;
- `gh pr create` sem `--draft`, e criação de PR fora de draft pelo MCP;
- `gh pr ready`, `gh pr merge` e merge pelo MCP;
- edição de chave e arquivo derivado do KB;
- leitura em `~/.t0/inbox/`.

O bloqueio volta como erro do hook. A skill trata esse erro como resposta final e muda de caminho. As regras sem exceção também moram em hook de git e em CI. O motivo é que hook de agente tem semântica diferente em cada ferramenta e, no Copilot, timeout de hook falha aberto, ou seja, deixa a ação passar.

## Modelos e same-family

As skills `architect`, `arena`, `swarm` e `slice-verify` leem a Policy `methodology/policies/models.md` do KB para escolher o modelo de cada papel: `architect-runner`, `arena-runner`, `judge`, `reviewer`, `swarm-worker` e `verifier`. Mudar de modelo é um PR nessa Policy, e a regressão de eval tem que ficar igual ou melhor.

Quando só uma família de modelo está aprovada numa ferramenta, `arena` e `swarm` rodam vários candidatos no mesmo modelo. Nesse caso, toda comparação ou review sai marcada `same-family`, e quem lê sabe que a concordância vale menos. No Copilot e no Kiro, o nome exato dos modelos aprovados ainda está para confirmar (não verificado).

## O que fica fora do plugin

Algumas skills de referência ficam fora do plugin. As primeiras fazem ship ou merge, abrem PR pronto ou leem transcrição crua: `opening-a-pr`, `babysit`, `shipping`, `autopilot-*`, `orchestrate`, `multi-phase-plan` e `session-pickup`. Também ficam fora `why`, `recall`, `automate-me` e `reflect`, que leem transcrições e varrem todos os MCPs. Por último, ficam fora `make-bot-ui`, `no-comments` e `interrogate`, que dependem de uma diversidade de família de modelo que o banco não tem.
