# Plugin e skills

O plugin `t0` leva o fluxo para dentro do agente. Ele traz 15 skills em pt-BR, quatro subagentes, o MCP `t0-kb` e os hooks que mantêm as travas do time. Roda igual no Claude Code, no GitHub Copilot e no Kiro.

As skills foram escritas à mão pelo time, em pt-BR, tendo as do mattpocock-skills e do pstack como referência. Cada `SKILL.md` credita a sua em `metadata.credits`, e o `THIRD_PARTY_NOTICES.md` do plugin carrega as licenças MIT.

## Instalação

O plugin não tem código Python. Hooks e MCP chamam o comando `t0`, então ele precisa estar no PATH antes de tudo.

1. Instale a CLI a partir do repo do toolkit (Python 3.11 ou mais novo):

   ```
   pipx install ./toolkit
   t0 doctor
   ```

2. Instale o plugin na sua ferramenta:

   | Ferramenta | Como |
   |---|---|
   | Claude Code | pelo marketplace do time; para testar local, `claude --plugin-dir ./plugin` |
   | Copilot CLI | `copilot plugin install`, que lê o formato Claude (não verificado no ambiente do banco) |
   | Copilot no VS Code | como Agent Plugin, no formato Agent Plugins 1.0 (não verificado) |
   | Kiro | como power, no formato Agent Plugins 1.0 (não verificado) |

3. Em cada repo de produto, rode `t0 setup` uma vez. Ele escreve o bloco t0 no `AGENTS.md`, os ponteiros por ferramenta, os hooks e os links da skill `verify-<app>`.

4. Monte o workspace do produto, como em [Workspace](06-workspace.md).

A versão do plugin é a mesma do pacote `t0`. Quando um atualiza, o outro atualiza junto.

## `/t0`, a porta de entrada

Na dúvida, comece por `/t0` (no Claude Code, `/t0:t0`). Ela entende o pedido, escolhe um playbook, abre a lista de tarefas com os passos dele e chama as skills de passo. As skills de passo fazem o trabalho. A `/t0` guarda as travas, o roteamento e o jeito de responder.

### Inegociáveis

Valem em todo playbook e em toda skill. Um hook bloqueia boa parte deles.

- Todo PR nasce em draft e fica em draft. Marcar pronto, fazer merge, force push e `reset --hard` são do humano ou do CI.
- Há três decisões humanas: aposta, spec e degrau. A skill prepara a decisão, abre o PR, mostra a evidência e para. Aprovar o PR é decidir.
- Trabalho reversível dentro de um slice segue sem perguntar: código, teste, commit na branch do slice, rascunho na branch da bet, protótipo fora do main.
- Escrita no KB passa por comando `t0` ou por arquivo na branch da bet, que entra por PR. Arquivos e chaves derivados ficam com o `kb-render`.
- O Jira é do CI. Nenhuma skill chama Jira nem issue tracker.
- `~/.t0/inbox/` fica fora de qualquer leitura. Transcrição entra só redigida.
- O modelo de qualquer execução paralela vem da Policy `models` do KB. Com uma família só aprovada, a saída sai marcada `same-family`.
- PR de código nasce de um slice (`slice-build`) ou de um Harness Item (`harness-fix`). Pedido de código sem slice passa antes pela trilha rápida ou pela bet.
- Comando `t0` que falha ou não existe: a skill mostra a saída exata e deixa o passo pendente. Escrever à mão o que o comando gravaria fura a raia.
- Toda saída para o humano é em pt-BR.

### Playbooks

A `/t0` escolhe o playbook pelo que o pedido move no KB:

| Playbook | Para quê |
|---|---|
| `ideia` | ideia nova até o veredito do protótipo |
| `rapida` | ajuste, bug ou melhoria que cabe em 1 dia sem desenho novo; abre a aposta com um slice |
| `bet` | ideia com `segue` e apetite de até 2 semanas: aposta, spec, desenho quando precisa, slices |
| `slice` | construir e verificar um slice `ready` |
| `harness` | erro de agente repetido ou Harness Item aceito |
| `ritual` | abrir, conduzir ou fechar um ritual |

E pelo jeito de fazer o trabalho. Os de código rodam dentro do playbook `slice`:

| Playbook | Para quê |
|---|---|
| `investigation` | pergunta só de leitura: como funciona, por que foi feito assim, X ou Y |
| `bug-fix` | reproduzir, achar a causa e corrigir com evidência de execução |
| `feature` | comportamento novo ou mudado, a partir de um formato de dados nomeado |
| `refactoring` | mudar estrutura preservando comportamento |
| `prototype` | esboço descartável para decidir um fork observando |
| `perf-issue` | lentidão medida, corrigida contra um baseline |

Roteamento: pedido só de leitura vai para `investigation`, sem slice e sem PR. Pedido de código com a chave de um slice `ready` vai para `slice`. Pedido de código sem slice vai para `rapida` quando cabe em 1 dia, senão para `ideia` ou `bet`. Ship, merge, PR pronto e babysit de PR ficam fora do t0: a `/t0` diz que isso é do humano e do CI e oferece outra rodada de `slice-verify`.

Antes de perguntar "qual abordagem?", a `/t0` confere se a resposta é um fato que dá para observar rodando algo. Se for, ela prototipa e deixa o resultado decidir. Pergunta fica para escolha de produto ou preferência, uma por vez.

### Princípios de engenharia

A `/t0` carrega 19 princípios curtos, um parágrafo cada, em `skills/t0/references/principios.md`. A resposta nomeia cada princípio que mudou uma decisão.

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
| `bet-new` | ideia com veredito vira trabalho | Bet `proposed` e PR da aposta; na rápida, o slice | aprova a aposta |
| `bet-spec` | bet `active` na trilha bet precisa de spec | `spec.md` na branch da bet | abre o PR ou fala com Jira |
| `architect` | desenho cruza fronteira de função ou não tem precedente | seção Design do spec; ADR | grava antes do ok humano ou escreve código |
| `arena` | comparar desenhos ou código com N candidatos | artefato sintetizado e nota | faz push das worktrees ou escreve no KB |
| `swarm` | matriz de cobertura, corrida, gauntlet, partição de exploração | relatório consolidado | faz push, abre PR ou escreve no KB |
| `bet-slice` | spec pronto precisa de slices | um arquivo por slice; PR em draft do spec | fala com Jira |
| `slice-build` | construir um slice `ready` | branch, commits, `.audit/<KEY>.tsv`, PR em draft | contorna o DoR ou marca pronto |
| `slice-verify` | revisar o PR de um slice antes do humano | comentário no PR; Harness Item | aprova, commita na branch do autor ou faz merge |
| `verify-setup` | repo sem `verify-<app>`, ou mapa velho | `.t0/skills/verify-<app>/` em PR em draft | edita código de produto |
| `ritual` | abrir, conduzir ou fechar um ritual | Ritual Record via `t0 ritual`; registros | escreve ata à mão ou lê `~/.t0/inbox/` |
| `harness-fix` | erro de agente pela segunda vez, ou item aceito | correção em PR em draft no repo certo | pula a prova vermelho e verde |

## Cada skill

### `idea-capture`

Use quando alguém trouxer uma ideia, um pedido ou uma dor para guardar, ou disser "anota essa ideia". A skill junta o mínimo: problema, para quem e sinal. Sinal fraco vale, escrito como é. Depois procura duplicata no KB com pelo menos duas buscas, uma pelo termo do usuário e outra pelo termo do glossário, incluindo ideias `killed` e `promoted`. Ideia morta só volta com fato novo.

Grava a Idea `new` em `ideas/IDEA-NNNN.md` com `t0 new idea`, sempre em dry-run primeiro. O `t0` reserva o número e abre um PR pequeno em draft. Ela nunca decide se a ideia vira bet: quem decide é o pod, na daily.

### `grill`

Use para "me grelha", para estressar um plano ou afiar um spec. A skill entrevista em rodadas: monta a árvore de decisões, pergunta a fronteira inteira de uma vez, numera cada pergunta e dá uma resposta recomendada. Responder "sim" aceita a recomendação. Durante a sessão, ela confronta os termos com o glossário, testa com cenários concretos e confere com o código.

Grava termo resolvido em `glossary/<slug>.md`, bilíngue, na branch da bet. Sem bet, guarda a lista para a `bet-new` ou a `bet-spec` gravarem. Propõe ADR só quando a decisão é difícil de desfazer, surpreendente sem contexto e fruto de trade-off real, via `t0 new adr`. Ramo adiado vira `[PRECISA ESCLARECER: <pergunta>]`. Ela nunca age sobre o resultado antes de o usuário confirmar que vocês chegaram ao mesmo entendimento.

### `prototype`

Use para prototipar uma ideia, testar um modelo de estado ou ver opções de tela. Precisa de uma Idea. A skill escreve a pergunta em uma frase e escolhe o ramo: lógica (um HTML único com botões e roteiros que empurram o modelo pelos casos difíceis) ou UI (variações bem diferentes numa rota, trocadas por parâmetro de URL).

Trabalha na branch `proto/<IDEA>-<slug>` do repo de produto, com push e sem PR. Só dados fictícios, estado em memória, sem polimento. Termina com o veredito `segue`, `ajusta` ou `mata`, confirmado por quem prototipou ou pelo pod, gravado com `t0 idea prototype --verdict ... --ref ...`. O protótipo nunca vai para o main nem para o KB.

### `bet-new`

Use para transformar uma Idea em bet ou em ajuste rápido. A skill lê a Idea, escolhe a trilha (`rapida` até 1 dia sem desenho, `bet` até 2 semanas) e junta `appetite`, `hypothesis`, `success_metric`, `kill_criteria`, tier e pods. Diz quem aprova: Bet Owner na bet, Flow Steward ou Bet Owner na rápida, e o Lead quando cruza pods, é Tier 2 ou passa de 1 semana.

Roda `t0 new bet --track rapida|bet <IDEA>`, que cria `bet.md` numa branch da bet e abre o PR da aposta em draft. Na trilha rápida, escreve também o slice com atual, esperado, o que não muda, o teste e os critérios de aceite em bullets. Confere com `t0 kb check` e `t0 gate aposta --dry-run`. Ela nunca aprova a aposta.

### `bet-spec`

Use para escrever ou refazer o spec de uma bet `active` na trilha bet. A skill sintetiza o que já foi conversado, sem entrevistar de novo. Decisão que falta vira `[PRECISA ESCLARECER]` no ponto onde pesa. Ela lê o `bet.md`, a Idea, o glossário, os ADRs, o spec vivo do produto e o código, e confere com o usuário os seams de teste: os que já existem, o mais alto possível, idealmente um só.

Grava `products/<pod>/bets/<BET>/spec.md` na branch da bet, a partir do Template do KB: histórias de usuário, critérios de aceite em bullets, como verificar, tier, fora de escopo. Commita e registra com `t0 log progress`. Ela nunca abre o PR (isso é da `bet-slice`) e nunca fala com Jira.

### `architect`

Use para desenhar uma bet antes dos slices, ou quando a mudança cruza fronteira de função. A skill desenha e nunca implementa. Em quatro fases: fundamenta lendo KB e código, com `arquivo:linha` para cada restrição; esboça pelo menos dois desenhos estruturalmente diferentes pela `arena`; para num checkpoint obrigatório com o humano; e só com o ok registra.

Grava a seção `## Design` do spec da bet, na mesma branch e no mesmo PR, e um ADR `proposed` quando a decisão é difícil de desfazer (formato persistido, contrato público, fronteira entre repos ou pods). Na trilha rápida ela não roda: se a mudança pede desenho, ela não cabe na rápida. Nada entra no repo de produto.

### `arena`

Use para comparar desenhos ou código quando uma tentativa só travaria a forma errada. A skill escreve a rubrica, escolhe os modelos na Policy `models` e roda N candidatos em paralelo, cada um numa git worktree local a partir do mesmo commit. Um juiz só leitura pontua os candidatos sem saber qual modelo fez qual. Ela escolhe a base, enxerta à mão o melhor dos outros e verifica.

Devolve o artefato sintetizado e uma nota com os modelos usados, o rótulo `same-family` quando couber, a base, o veredito do juiz e os enxertos. As branches `arena/*` são locais: ela nunca faz push, nunca abre PR a partir delas e candidato nunca entra no KB.

### `swarm`

Use para fan-out paralelo: matriz de cobertura (critério de aceite por ponto de entrada), corrida entre tentativas, gauntlet (o mesmo artefato contra várias lentes de ataque) ou partição de exploração. A skill declara o predicado de pronto e a regra de seleção antes de lançar, isola cada worker que escreve numa worktree presa a um SHA e usa `verifier` para quem mede e `t0-agent` para quem escreve.

Devolve um relatório consolidado em pt-BR, com `PASS`, `ISSUES` ou `BLOCKED` e evidência por célula, e o rótulo `same-family` quando couber. Lacuna nunca conta como `PASS`. Ninguém faz push, abre PR ou escreve no KB.

### `bet-slice`

Use depois do `bet-spec`, ou para refazer os slices. A skill corta o spec em slices verticais (tracer bullets): cada um atravessa todas as camadas, se demonstra sozinho, cabe numa janela de contexto e mexe num repo só. Trabalho que cruza repos vira um slice por repo, ligado por `depends_on`. Refactor largo segue expand, migrate e contract. Ela mostra o corte numerado e itera com o usuário até ele aprovar.

Grava um arquivo por slice em `slices/NN-<slug>.md`, na branch do spec, confere com `t0 kb check` e `t0 gate spec --dry-run` e abre o PR em draft com spec e slices. Esse PR é a decisão de spec. Ela nunca fala com Jira: o espelho vem do CI depois do merge.

### `slice-build`

Use quando alguém pede para implementar, construir ou pegar um slice ou uma chave Jira. A skill entende o slice e reescreve o objetivo com as próprias palavras, roda `t0 slice dor` e `t0 slice start`, abre a branch `<KEY>-<slug>` e constrói teste a teste, vermelho e verde, nas costuras combinadas. Depois prova no app real pelo `verify-<app>`, audita a trilha com um revisor só leitura e abre o PR em draft.

Grava commits pequenos prefixados pela chave, a trilha `.audit/<KEY>.tsv` (uma linha por decisão, só acréscimo) e o PR com `Jira`, `Tier`, `Trilha` e "Em minhas palavras" quando exigida. Ela nunca contorna uma recusa do `dor`, nunca escreve o "Em minhas palavras" pelo autor e nunca marca o PR como pronto. No fim, chama a `slice-verify`.

### `slice-verify`

Use para revisar um slice antes do review humano. A skill fixa o PR e a base, acha o slice e o spec no KB e roda duas raias em paralelo, com subagentes novos e só leitura: `standards-reviewer` (padrões do repo) e `spec-reviewer` (spec do KB). Confere o DoD do PR, prova cada critério de aceite por ponto de entrada no app real (com `swarm` quando dá) e, em Tier 2, roda o blast radius com escada de prova.

Grava um comentário só no PR, com seções separadas por raia, a matriz de evidência e os erros de agente. Erro repetido vira Harness Item via `t0 new harness`. Ela nunca aprova, nunca pede mudança como decisão, nunca commita na branch do autor e nunca faz merge.

### `verify-setup`

Use quando um repo não tem jeito roteirizado de provar comportamento, ou no Harness Health para auditar o mapa. No modo criar, a skill entrevista o repo e gera `.t0/skills/verify-<app>/` com as seções Subir, Diagnóstico, Dirigir, Evidência e Limpeza, mais um mapa de features. Depois prova a skill gerada de ponta a ponta contra o app real. No modo manter, confere cada feature pelo código e ao vivo e conserta o mapa.

Grava tudo num PR em draft só, e no modo manter abre um Harness Item para o Harness Health fechar com o PR. Ela nunca edita código de produto.

### `ritual`

Use para conduzir um ritual, registrar decisões e donos ou extrair ideias de uma gravação. A skill roda `t0 ritual <slug> open`, mostra a pauta como veio, registra decisão e bloqueio com `t0 log` na hora em que são ditos e fecha com `t0 ritual <slug> close`. Com gravação, roda a redação antes de tudo, faz a passada de dado de cliente e extrai ideias e decisões sem `verified`.

Grava o Ritual Record, os registros e, quando houve gravação e o aval de LGPD, o Transcript. Ela nunca lê `~/.t0/inbox/`, nunca grava 1:1, nunca registra aposta ou spec como aprovados no ritual e nunca contorna a recusa de um close.

### `harness-fix`

Use com `harness-fix <HI>`, no Harness Health ou quando o mesmo erro aparece pela segunda vez. A skill junta a evidência de cada ocorrência (commits, reviews, trilhas `.audit`, logs de sessão só deste workspace), escolhe o repo onde o erro nasce e sobe a escada do harness parando no primeiro degrau que resolve. Para cada degrau de cima descartado, escreve o motivo em uma frase.

Grava a correção num PR em draft no repo certo, com a prova: o check falhando numa ocorrência real do passado e passando com a correção. Registra com `t0 log decision` e atualiza o item pelo KB. Ela nunca pula a prova, nunca marca pronto e nunca faz merge.

## Subagentes

| Subagente | Para quê | Pode escrever? |
|---|---|---|
| `t0-agent` | delegado para trabalho de passo: código num slice, rascunho na branch da bet, script, investigação | sim, dentro das travas |
| `spec-reviewer` | raia de spec do `slice-verify`: diff contra slice, spec e Design | não |
| `standards-reviewer` | raia de padrões do `slice-verify`: diff contra os padrões do repo | não |
| `verifier` | dirige o app real numa célula da matriz e devolve `PASS`, `ISSUES` ou `BLOCKED` | não, só evidência |

Todo subagente lê a `/t0` antes de trabalhar e segue os mesmos inegociáveis. Tarefa nova vai para subagente novo, com o escopo consolidado no brief. O modelo de cada papel vem da Policy `models` do KB.

## Travas

O hook `pre-tool` roda nas três ferramentas, pelo mesmo `t0 hook <evento> --tool claude|copilot|kiro`, e bloqueia tanto no shell quanto nas ferramentas MCP do GitHub:

- force push e `reset --hard`;
- `gh pr create` sem `--draft`, e criação de PR fora de draft pelo MCP;
- `gh pr ready`, `gh pr merge` e merge pelo MCP;
- edição de chave e arquivo derivado do KB;
- leitura em `~/.t0/inbox/`.

O bloqueio volta como erro do hook. A skill trata como resposta final e muda de caminho. Regra sem exceção também mora em hook de git e em CI, porque hook de agente tem semântica diferente em cada ferramenta e, no Copilot, timeout de hook falha aberto.

## Modelos e same-family

As skills `architect`, `arena`, `swarm` e `slice-verify` leem a Policy `methodology/policies/models.md` do KB para escolher o modelo de cada papel: `architect-runner`, `arena-runner`, `judge`, `reviewer`, `swarm-worker` e `verifier`. Mudar de modelo é um PR nessa Policy, e a regressão de eval tem que ficar igual ou melhor.

Quando só uma família de modelo está aprovada numa ferramenta, `arena` e `swarm` rodam vários candidatos no mesmo modelo, e toda comparação ou review sai marcada `same-family`. Quem lê sabe que a concordância vale menos. No Copilot e no Kiro, o nome exato dos modelos aprovados ainda está para confirmar (não verificado).

## O que fica fora do plugin

Ficam fora as skills de referência que fazem ship ou merge, abrem PR pronto ou leem transcrição crua: `opening-a-pr`, `babysit`, `shipping`, `autopilot-*`, `orchestrate`, `multi-phase-plan` e `session-pickup`. Também ficam fora `why`, `recall`, `automate-me` e `reflect`, que leem transcrições e varrem todos os MCPs, e `make-bot-ui`, `no-comments` e `interrogate`, que dependem de diversidade de família de modelo que o banco não tem.
