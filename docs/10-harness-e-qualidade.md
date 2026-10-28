# Harness e qualidade

O harness é tudo o que cerca o agente para ele errar menos: `AGENTS.md`, regras, skills, linters, testes, hooks e CI. No t0, a qualidade vem de três lugares. Erro repetido vira sensor (um check automático, como lint ou teste). O review segue o tier (o nível de review do PR: 0, 1 ou 2), e o agente revisa antes do humano. E ferramenta de agente só sai com eval (suíte de casos que mede a ferramenta).

## Escada do harness

A `slice-verify` (o agente de review que roda antes do humano) marca todo erro de agente no comentário do PR. Quando o padrão se repete (duas vezes no mesmo PR, ou com um Harness Item já aberto para ele), ela registra a ocorrência num Harness Item (o registro de uma classe de erro de agente) com `t0 new harness`. Da segunda ocorrência em diante, o item sobe a escada e ganha um PR em draft pelo `harness-fix`. O time revisa esse PR no Harness Health da semana.

Os degraus vão do mais forte para o mais fraco. Suba só até o degrau que resolve:

1. `sensor`: o degrau computacional. Entram aqui arquitetura que esconde o caminho errado, tipo que não deixa escrever o estado ruim, lint ou check de CI com mensagem de correção escrita para o agente, teste do comportamento, hook de git ou gate de CI.
2. `area-rule`: regra de área com uma fonte só, em `agents/rules/<area>.md`, gerada para as três ferramentas. Serve para o erro de julgamento que ninguém consegue transformar em check.
3. `skill`: o procedimento longo vira skill no toolkit.
4. `agents-md`: só por último, uma linha no `AGENTS.md`, que tem teto de 150 linhas. É o degrau mais fraco porque nada falha quando o agente pula essa linha.

Se um sensor pega o erro, o erro não vai para regra nem para `AGENTS.md`. O PR do `harness-fix` explica, em uma frase por degrau, por que os degraus de cima não serviram. Ele também traz a prova: o check falhando numa ocorrência real do passado e passando com a correção.

Regra sem exceção mora em hook de git ou em CI, nunca em hook de agente. O motivo: cada ferramenta tem formato e semântica próprios, o Copilot no VS Code ignora matchers e, no Copilot, o timeout de hook falha aberto (deixa passar). Hook de agente fica como acelerador opcional.

O teto é de 20 hooks ou regras deny por repo. Se o repo estourou o teto, o item precisa tirar um antes de pôr outro.

Exemplo real do KB, `harness/HI-0001.md`:

```yaml
type: Harness Item
pattern: "datetime.now() ou datetime.utcnow() sem tz em código que agenda ou compara horário"
ladder_step: sensor
occurrences: ["t0/status-bot#14", "t0/status-bot#18"]
pr: "t0/status-bot#19"
state: fixed
```

O degrau escolhido foi o sensor: o ruff já tem as regras DTZ, que pegam o padrão no CI com uma mensagem que o agente entende.

## O Harness Keeper

O Harness Keeper é um rodízio de 2 semanas. É nesse papel que o ganho composto aparece: cada erro que vira sensor deixa de custar review para o time inteiro. O Harness Keeper:

- facilita o [Harness Health](04-rituais.md#harness-health) semanal;
- faz a triagem do "o agente errou";
- cuida de `AGENTS.md`, skills, linters, CI e agentes de limpeza;
- mantém `harness/budget.md` e mostra o teto de hooks na Retro;
- faz a jardinagem do KB: concepts com `stale_after` vencido, skills sem uso há 4 semanas, métricas que não informam decisão;
- propõe sunset de ferramenta que não pegou, e o Lead confirma;
- lê o CHANGELOG de cada versão nova do mattpocock-skills ou do pstack e abre Harness Item para o que vale portar.

### Orçamento de contexto

| Teto | Valor |
|---|---|
| `AGENTS.md` por repo | 150 linhas |
| Hooks ou regras deny por repo | 20 |
| Card do workspace | 8.000 caracteres |
| Delta do card | 3.000 caracteres |
| Card de subagente | 1.500 caracteres |
| Instruções do MCP `t0-kb` | 1.500 caracteres |

## Tiers de review

| Tier | Exemplos | Review mínimo |
|---|---|---|
| 0 | docs, testes, refactor mecânico, saída de agente de limpeza, PR de estado no KB | agente de review e CI verdes; 1 humano faz o merge em lote, uma vez por dia; é o único tier em que o merge pode ser automático |
| 1 | feature em ferramenta interna, slice de bet | agente de review e 1 humano; júnior não aprova sozinho |
| 2 | auth, dado de cliente, permissão de agente, superfície pública (MCP, CLI, skill, API), prompt ou modelo de ferramenta que as squads usam | agente de review e 2 humanos, um deles o Bet Owner (o sênior que decide o que vira bet e responde pelo resultado; o outro humano pode ser de outro pod); blast radius (a análise do que a mudança pode quebrar) com prova executada; cadeia de rastreabilidade completa (requisito, slice, PR, teste); "Em minhas palavras" |

Como o review roda:

- o humano só lê depois que o agente de review e o CI passaram;
- o agente de review roda num subagente novo, só de leitura, contra o spec;
- review entre modelos da mesma família sai marcado `same-family`;
- todo PR nasce em draft;
- hooks de git e CI bloqueiam force push, `reset --hard`, push em `main` e PR fora de draft;
- a primeira resposta humana sai em até 4 horas úteis, e PR de spec tem o mesmo SLO.

### Graduação de confiança (PROPOSTA)

Um caminho do código desce de Tier 1 para Tier 0 depois de 20 PRs seguidos sem defeito que tenha escapado do agente de review. No primeiro defeito, o caminho volta para Tier 1. Tier 2 nunca gradua. O contador fica em `harness/trust.md`, e só o CI escreve nele. O número 20 ainda vai ser calibrado.

## DoR e DoD

O `t0 slice dor <KEY>` confere o DoR (o que o slice precisa ter para começar) antes de abrir a branch.

DoR do slice:

- critérios de aceite em bullets, "como verificar", `tier` e `repo`;
- na trilha bet, spec `approved` sem nenhum `[PRECISA ESCLARECER]`;
- na trilha rápida, "atual, esperado, o que não muda" e o teste que vai ficar vermelho;
- chave Jira gravada no slice;
- quem pega o slice tem menos de 2 slices em construção.

DoD do slice (o que ele precisa ter para terminar):

- CI verde e agente de review sem pendência, depois o review humano do tier;
- teste nas costuras do spec e verificação executada pelo `verify-<app>` do repo;
- em Tier 2, blast radius com prova executada;
- `.audit/<KEY>.tsv` commitado no PR e "Em minhas palavras" quando exigida;
- erro do agente no caminho registrado num Harness Item;
- superfície pública alterada com contract tests verdes e versão atualizada no spec vivo do produto.

DoD da bet:

- todos os slices `done`;
- spec da bet congelado e spec vivo do produto atualizado;
- regressão de eval registrada, se for ferramenta de agente;
- aprendizado escrito na Bet.

## Verificação

Teste verde ainda é só um proxy do comportamento. Por isso, todo slice prova o comportamento contra o app real. Três peças fazem isso.

### `verify-<app>`

Cada repo de produto tem uma skill local, `.t0/skills/verify-<app>/`. Ela roteiriza como subir o app, conferir se a instância vale (diagnóstico), dirigir uma feature como o usuário faz, capturar evidência e limpar. A skill traz um mapa de features, com um arquivo por feature visível ao usuário. A skill `verify-setup` cria a `verify-<app>` e a prova de ponta a ponta. No Harness Health, o modo manter confere cada feature pelo código e ao vivo, porque o mapa fica desatualizado assim que o app muda.

### `slice-build` e a trilha `.audit`

A `slice-build` captura a evidência de antes e constrói o teste vermelho e depois o verde nas costuras do spec (os pontos do código onde o comportamento é testado). Depois, prova no app pelo `verify-<app>` e grava cada decisão em `.audit/<KEY>.tsv`, com evidência por ponteiro (SHA, `arquivo:linha`, teste, screenshot). Antes do PR, um revisor só de leitura audita a trilha contra o `git log`, as saídas e o diff. No merge, o CI copia as linhas de decisão para o Slice.

### `slice-verify`

É o agente de review que roda antes do humano. Ele revisa em duas raias separadas: padrões do repo e spec do KB. Também monta uma matriz de evidência no app, com cada critério de aceite cruzado com cada ponto de entrada; quando as instâncias isolam, usa `swarm` e workers `verifier`. Em Tier 2, faz o blast radius com escada de prova. O que não chegou à prova sai marcado `BLOCKED` ou "não provado".

## Política de eval

A política vale para skills, MCPs, agentes e o próprio toolkit. Os números são PROPOSTA.

- Ferramenta que vai para squads piloto tem uma suíte de regressão de 20 a 50 tarefas. As tarefas vêm de uso e de falhas reais, com casos positivos e negativos.
- O degrau de adoção 1 para 2 (cada degrau é um passo de adoção: 1 é o time, 2 são de 2 a 3 squads piloto, 3 é o ART) pede pelo menos 95% na regressão (PROPOSTA). Tarefa com 0% é suspeita: monte uma solução de referência antes de culpar o agente.
- Cada produto tem duas suítes: capacidade, que começa baixa, e regressão, que fica perto de 100%. Quando a suíte de capacidade satura, ela vira regressão.
- Use `pass@1` quando um resultado bom basta e `pass^3` para agente que a squad usa sem olhar. O `evals.md` do produto declara qual dos dois vale.
- Use grader determinístico sempre que der. O juiz LLM avalia por dimensão, com a opção "não sei". Humano entra só em amostra. O que se avalia é o resultado.
- Upgrade de modelo, mudança de prompt ou mudança de skill só entra se a regressão fica igual ou melhor. Quem assina é o Bet Owner do pod dono do produto.
- Incidente ou defeito escapado vira caso de eval no Harness Health seguinte. Em superfície pública, os primeiros casos saem junto com o spec.
- A infra de eval fica com o pod PACO. O Eval Suite no KB (`products/<pod>/evals.md`) aponta para `evals/` no repo e guarda o último resultado.
- O próprio plugin segue a regra. Ele tem casos de eval para cada comportamento em que as skills do t0 se afastam da referência: PR sempre em draft, segredo recusado no registro, transcrição redigida, hook bloqueando edição de derivado, architect parando no desenho, entre outros.

### A suíte do plugin hoje

A suíte do plugin mora em `plugin/evals/` e tem 21 casos que cobrem o fluxo inteiro: captura de ideia, veredito de protótipo, aposta, spec, slices, build, verificação, rápida em um PR, roteamento sem slice, checkpoint do architect, swarm de cobertura, harness-fix, close do Harness Health, os rituais (daily do time, transcrição, Demo, Retro), kill de bet, merge recusado e verify-setup. Cada caso roda contra um KB semeado do `okf-template` com repos reais. A nota vem de um grader determinístico e de um juiz Opus por dimensão (sonnet fica fora de juiz).

Foram seis rodadas em 2026-10-28. Elas geraram 37 achados, registrados e corrigidos em `toolkit/design/eval-findings.md`. A última rodada fechou com 21 de 21 casos passando nas duas execuções de cada um, a cerca de US$ 29 por rodada. Boa parte dos achados virou regra de skill, e esta documentação já reflete essas regras: menos perguntas (a `bet-new` propõe os campos, a `idea-capture` pergunta no máximo uma vez, o close de ritual não pede confirmação), a `slice-build` parando no PR em draft, a regra de "sem forge" e o fallback de leitura do KB.

Trecho real de `products/exemplo/evals.md`:

```yaml
type: Eval Suite
repo: status-bot
repo_path: evals/
metric: "pass@1"
regression_size: 24
regression_pass: "0.96"
last_run: 2026-10-24T17:55:00-03:00
```

## Pisos de adoção

Todos os pisos são PROPOSTA. Eles ficam na Policy `methodology/policies/adoption-floors.md` com `state: proposed` até 3 ferramentas passarem pelo funil. Quem decide o degrau é o Lead/AIVA, com números.

"Ativo" é quem invocou a ferramenta em trabalho real numa semana ISO, medido por telemetria. Login não conta.

| Degrau | Critério proposto | Quem confirma |
|---|---|---|
| 1 → 2 (time → 2 ou 3 squads piloto) | PROPOSTA: pelo menos 7 dos 10 do time ativos por semana por 2 semanas seguidas, e regressão de pelo menos 95% | Lead/AIVA |
| 2 → 3 (piloto → ART) | PROPOSTA: pelo menos 40% dos devs-alvo das squads piloto ativos por semana por 3 semanas seguidas, retenção de pelo menos 50% em 4 semanas e `pass^3` na meta do produto | Lead/AIVA; vira outcome do PI |
| Uso episódico (skill de migração, por exemplo) | PROPOSTA: uso repetido em pelo menos 2 de 4 semanas entre quem tinha tarefa elegível, no lugar do uso semanal | quem confirma o degrau |
| Sunset | PROPOSTA: menos de 15% de uso semanal no público-alvo, ou menos de 5 usuários ativos, depois de 8 semanas em piloto | Harness Keeper propõe; Lead confirma |

De onde vêm os números: o time é a coorte mais motivada, então 70% é razoável. O Claude Code foi de 20% a 50% da engenharia da Anthropic em 5 dias; esse é um dado observado e nunca foi gate. Os 40% no piloto ficam abaixo do platô de cerca de 60% atribuído à DX (não verificado) e passam do pico de novidade de uma semana. A cláusula de retenção copia a forma do gate do time do Claude Code (usuários ativos e retenção), cujo número não é público. O gate é do time, independe dessas fontes e é revisto depois de 3 ferramentas.

O comando `t0 gate degrau` confere os pisos e a regressão antes de gravar o degrau, mas ainda não está na CLI atual.

## Métricas

Todas as métricas ficam num painel só. O pod Portal do time e Métricas mantém o painel, e os dados vêm de Git, CI, Jira, telemetria dos agentes e KB. Ninguém reporta nada à mão.

| Camada | Métrica | Decisão que ela informa |
|---|---|---|
| Velocidade | tempo ideia → protótipo; tempo ideia → produção | se o fluxo cumpre o que promete: ideia testada no mesmo dia, bet em produção dentro do apetite |
| Fluxo | slices por pessoa e estado; cycle time por slice; idade da fila de review e dos PRs de spec | quem destravar na daily do time; onde o trabalho espera |
| Review | mediana até a primeira resposta humana; minutos humanos por PR; % de problemas achados pelo agente antes do humano | redistribuir review; graduar área |
| Entrega (DORA) | frequência de deploy, lead time, taxa de falha de mudança, tempo de recuperação | pegar o "mais rápido e mais frágil" |
| Adoção | uso semanal, retenção em 4 semanas, uso repetido, custo por usuário ativo; tempo economizado por squad | degraus e sunset; o que vai ao ART |
| Uso de IA | % de PRs de autoria de agente, custo de tokens por slice, sessões por dev por dia (só como piso, para oferecer ajuda) | custo do fluxo; revisão mensal de modelo pelo Lead |
| Harness e evals | linhas de `AGENTS.md`, hooks por repo, recorrência do mesmo erro, Harness Items abertos e fechados, pass rate das suítes | se o time compõe ganho ou incha contexto; troca de modelo |
| KB | `stale_after` vencido, % de decisões com `verified`, drift do Jira | se o sistema de registro está vivo |
| Práticas de júnior | % de PRs com "Em minhas palavras" onde é exigida; slices feitos sem geração de código | se as práticas acontecem |

Regras anti-vaidade, sem exceção:

- nenhum ranking de pessoa por token, PR, linha ou sessão; a visão por pessoa mostra só o que está em andamento e travado;
- dashboard que mostra pessoa por volume de agente é bug Tier 1;
- token é piso e custo, nunca meta;
- toda métrica nomeia a decisão que informa, e o Harness Keeper remove a métrica que não informou nenhuma decisão em 2 PIs;
- métrica que sai do time é só de produto e de fluxo (adoção, retenção, DORA, ideia → produção), nunca de atividade;
- dado individual das práticas de júnior só a própria pessoa vê.
