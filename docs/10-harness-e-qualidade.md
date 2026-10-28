# Harness e qualidade

O harness é tudo o que cerca o agente para ele errar menos: `AGENTS.md`, regras, skills, linters, testes, hooks e CI. Qualidade no t0 vem de três lugares: erro repetido vira sensor, o review segue o tier com o agente na frente, e ferramenta de agente só sai com eval.

## Escada do harness

A `slice-verify` marca todo erro de agente no comentário do PR. Quando o padrão se repete (duas vezes no mesmo PR, ou com um Harness Item já aberto para ele), ela registra a ocorrência num Harness Item com `t0 new harness`. Da segunda ocorrência em diante, o item sobe a escada e ganha um PR em draft pelo `harness-fix`, revisado no Harness Health da semana.

Os degraus, do mais forte para o mais fraco. Suba só até onde resolve:

1. `sensor`: o degrau computacional. Arquitetura que esconde o caminho errado, tipo que não deixa escrever o estado ruim, lint ou check de CI com mensagem de correção escrita para o agente, teste do comportamento, hook de git ou gate de CI.
2. `area-rule`: regra de área com uma fonte só, em `agents/rules/<area>.md`, gerada para as três ferramentas. Serve para erro de julgamento que ninguém consegue transformar em check.
3. `skill`: procedimento longo vira skill no toolkit.
4. `agents-md`: só por último, uma linha no `AGENTS.md`, que tem teto de 150 linhas. Nada falha quando o agente pula essa linha.

Se um sensor pega o erro, ele não vai para regra nem para `AGENTS.md`. O PR do `harness-fix` explica, em uma frase por degrau, por que os de cima não serviram, e traz a prova: o check falhando numa ocorrência real do passado e passando com a correção.

Regra sem exceção mora em hook de git ou em CI, nunca em hook de agente. Cada ferramenta tem formato e semântica próprios, o Copilot no VS Code ignora matchers e o timeout de hook no Copilot falha aberto. Hook de agente fica como acelerador opcional.

O teto é de 20 hooks ou regras deny por repo. Estourou, o item precisa tirar um antes de pôr outro.

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

Rodízio de 2 semanas. É o papel onde o ganho composto aparece: cada erro que vira sensor deixa de custar review para o time inteiro. O Harness Keeper:

- facilita o [Harness Health](04-rituais.md#harness-health) semanal;
- faz a triagem do "o agente errou";
- cuida de `AGENTS.md`, skills, linters, CI e agentes de limpeza;
- mantém `harness/budget.md` e mostra o teto de hooks na Retro;
- jardina o KB: concepts com `stale_after` vencido, skills sem uso há 4 semanas, métricas que não informam decisão;
- propõe sunset de ferramenta que não pegou, e o Lead confirma;
- lê o CHANGELOG de versão nova do mattpocock-skills ou do pstack e abre Harness Item para o que vale portar.

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
| 2 | auth, dado de cliente, permissão de agente, superfície pública (MCP, CLI, skill, API), prompt ou modelo de ferramenta que as squads usam | agente de review e 2 humanos, um deles o Bet Owner (o outro pode ser de outro pod); blast radius com prova executada; cadeia de rastreabilidade completa (requisito, slice, PR, teste); "Em minhas palavras" |

Como o review roda:

- o humano só lê depois que o agente de review e o CI passaram;
- o agente de review roda num subagente novo, só leitura, contra o spec;
- review entre modelos da mesma família sai marcado `same-family`;
- todo PR nasce em draft;
- hooks de git e CI bloqueiam force push, `reset --hard`, push em `main` e PR fora de draft;
- a primeira resposta humana sai em até 4 horas úteis, e PR de spec tem o mesmo SLO.

### Graduação de confiança (PROPOSTA)

Um caminho do código desce de Tier 1 para Tier 0 depois de 20 PRs seguidos sem defeito escapado do agente de review, e volta no primeiro defeito. Tier 2 nunca gradua. O contador fica em `harness/trust.md`, escrito só pelo CI. O número 20 ainda vai ser calibrado.

## DoR e DoD

O `t0 slice dor <KEY>` confere o DoR antes de abrir a branch.

DoR do slice:

- critérios de aceite em bullets, "como verificar", `tier` e `repo`;
- na trilha bet, spec `approved` sem nenhum `[PRECISA ESCLARECER]`;
- na trilha rápida, "atual, esperado, o que não muda" e o teste que vai ficar vermelho;
- chave Jira gravada no slice;
- quem pega o slice tem menos de 2 em construção.

DoD do slice:

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

Teste verde ainda é proxy. Todo slice prova o comportamento contra o app real, e três peças fazem isso.

### `verify-<app>`

Cada repo de produto tem uma skill local, `.t0/skills/verify-<app>/`, que roteiriza como subir o app, conferir se a instância vale (diagnóstico), dirigir uma feature como o usuário faz, capturar evidência e limpar. Ela traz um mapa de features, um arquivo por feature visível ao usuário. A skill `verify-setup` cria essa skill e a prova de ponta a ponta. No Harness Health, o modo manter confere cada feature pelo código e ao vivo, porque o mapa apodrece no momento em que o app muda.

### `slice-build` e a trilha `.audit`

A `slice-build` captura a evidência de antes, constrói vermelho e verde nas costuras do spec, prova no app pelo `verify-<app>` e grava cada decisão em `.audit/<KEY>.tsv`, com evidência por ponteiro (SHA, `arquivo:linha`, teste, screenshot). Antes do PR, um revisor só leitura audita a trilha contra o `git log`, as saídas e o diff. No merge, o CI copia para o Slice as linhas de decisão.

### `slice-verify`

O agente de review que roda antes do humano. Duas raias separadas (padrões do repo e spec do KB), uma matriz de evidência no app (cada critério de aceite por cada ponto de entrada, com `swarm` e workers `verifier` quando as instâncias isolam) e, em Tier 2, blast radius com escada de prova. O que não chegou à prova sai marcado `BLOCKED` ou "não provado".

## Política de eval

Vale para skills, MCPs, agentes e o próprio toolkit. Os números são PROPOSTA.

- Ferramenta que vai para squads piloto tem suíte de regressão de 20 a 50 tarefas, tiradas de uso e de falhas reais, com casos positivos e negativos.
- O degrau 1 para 2 pede pelo menos 95% na regressão (PROPOSTA). Tarefa com 0% é suspeita: monte uma solução de referência antes de culpar o agente.
- Cada produto tem duas suítes: capacidade (começa baixa) e regressão (perto de 100%). Capacidade que satura vira regressão.
- `pass@1` quando um resultado bom basta, `pass^3` para agente que a squad usa sem olhar. O `evals.md` do produto declara qual.
- Grader determinístico sempre que der. Juiz LLM por dimensão, com a opção "não sei". Humano só em amostra. Avalia-se o resultado.
- Upgrade de modelo, mudança de prompt ou de skill só entra se a regressão fica igual ou melhor. O Bet Owner do pod dono do produto assina.
- Incidente ou defeito escapado vira caso de eval no Harness Health seguinte. Em superfície pública, os primeiros casos saem junto com o spec.
- A infra de eval fica com o pod PACO. O Eval Suite no KB (`products/<pod>/evals.md`) aponta para `evals/` no repo e guarda o último resultado.
- O próprio plugin segue a regra, com casos de eval para cada comportamento em que as skills do t0 se afastam da referência: PR sempre em draft, segredo recusado no registro, transcrição redigida, hook bloqueando edição de derivado, architect parando no desenho, entre outros.

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

Todos PROPOSTA. Ficam na Policy `methodology/policies/adoption-floors.md` com `state: proposed`, até 3 ferramentas passarem pelo funil. Quem decide o degrau é o Lead/AIVA, com números.

"Ativo" é quem invocou a ferramenta em trabalho real numa semana ISO, medido por telemetria. Login não conta.

| Degrau | Critério proposto | Quem confirma |
|---|---|---|
| 1 → 2 (time → 2 ou 3 squads piloto) | PROPOSTA: pelo menos 7 dos 10 do time ativos por semana por 2 semanas seguidas, e regressão de pelo menos 95% | Lead/AIVA |
| 2 → 3 (piloto → ART) | PROPOSTA: pelo menos 40% dos devs-alvo das squads piloto ativos por semana por 3 semanas seguidas, retenção de pelo menos 50% em 4 semanas e `pass^3` na meta do produto | Lead/AIVA; vira outcome do PI |
| Uso episódico (skill de migração, por exemplo) | PROPOSTA: uso repetido em pelo menos 2 de 4 semanas entre quem tinha tarefa elegível, no lugar do uso semanal | quem confirma o degrau |
| Sunset | PROPOSTA: menos de 15% de uso semanal no público-alvo, ou menos de 5 usuários ativos, depois de 8 semanas em piloto | Harness Keeper propõe; Lead confirma |

De onde vêm os números: o time é a coorte mais motivada, então 70% é razoável. O Claude Code foi de 20% a 50% da engenharia da Anthropic em 5 dias, um dado observado que nunca foi gate. 40% no piloto fica abaixo do platô de cerca de 60% atribuído à DX (não verificado) e passa do pico de novidade de uma semana. A cláusula de retenção copia a forma do gate do time do Claude Code (usuários ativos e retenção), cujo número não é público. O gate é do time, independente dessas fontes, e é revisto depois de 3 ferramentas.

O comando `t0 gate degrau`, que confere os pisos e a regressão antes de gravar o degrau, ainda não está na CLI atual.

## Métricas

Um painel só, mantido pelo pod Portal do time e Métricas, alimentado por Git, CI, Jira, telemetria dos agentes e o KB. Ninguém reporta nada à mão.

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
- toda métrica nomeia a decisão que informa, e a que não informou nenhuma em 2 PIs é removida pelo Harness Keeper;
- métrica que sai do time é só de produto e de fluxo (adoção, retenção, DORA, ideia → produção), nunca de atividade;
- dado individual das práticas de júnior só a própria pessoa vê.
