# Fluxo

Dentro do time não existe sprint. A ideia anda assim que aparece, e só três pontos do caminho pedem uma decisão humana registrada.

## O caminho inteiro

```
 Ideia -> Protótipo -[aposta]-> Spec + slices -[spec]-> Build e Verify -> Ship -> degraus -[degrau]-> time, piloto, ART

 trilha rápida:
 Ideia -[aposta]-> slice com "atual, esperado, o que não muda" + teste -> Build e Verify -> Ship

 harness, em qualquer etapa:
 agente erra pela 2ª vez -> Harness Item -> sensor, regra, skill ou AGENTS.md -> PR no Harness Health da semana
```

Os colchetes marcam as três decisões humanas.

## As sete etapas

### 1. Ideia

Qualquer pessoa registra uma ideia, a qualquer hora, com a skill `idea-capture`. A skill pede só três coisas (problema, para quem e sinal), procura duplicata no KB e roda `t0 new idea`. A ideia entra como Idea `new` em `ideas/IDEA-NNNN.md`, num PR pequeno.

Uma ideia também pode sair da gravação de uma daily, pelo `ritual <slug> close --transcript`, ou de uma issue que uma squad ou o ART abriu no Jira. Nos dois casos, a ideia entra sem `verified` até alguém confirmar.

### 2. Protótipo

O protótipo leva de minutos a horas e não pede aprovação. Ele pode ser feito sozinho ou ao vivo na daily do pod, com o agente. A skill `prototype` trabalha numa branch descartável `proto/<IDEA>-<slug>` do repo de produto. Essa branch nunca vai para o main e nunca vira base de código. O protótipo usa só dados fictícios.

O protótipo termina num veredito, que `t0 idea prototype` grava na Idea:

| Veredito | Quando |
|---|---|
| `segue` | a ideia se sustentou e pode virar bet |
| `ajusta` | tem algo ali, mas a pergunta ou a solução muda |
| `mata` | a ideia não se sustenta; o motivo fica registrado, e ela só volta com fato novo |

O KB recebe só o veredito e a referência da branch. O código do protótipo fica fora.

### 3. Aposta: vira bet?

A bet é o trabalho com apetite de até 2 semanas que o Bet Owner (o sênior que facilita a daily do pod) decide fazer depois do protótipo. O Bet Owner decide na daily do pod. A skill `bet-new` roda `t0 new bet` e abre o PR da aposta em draft. Aprovar esse PR é a decisão. O Lead também aprova em três casos: quando a bet cruza pods, quando é Tier 2 (o nível de review mais alto) ou quando passa de 1 semana de apetite. O `t0 gate aposta --ci` confere isso no CI. Um gate é o check de CI que confere uma decisão humana no PR.

A bet carrega `appetite`, `hypothesis`, `kill_criteria` e `success_metric`. O intent (problema, para quem, sinal, o que entra e o que fica fora) fica no corpo da bet.

### 4. Spec e slices

O spec é o contrato da bet, e cada slice é uma fatia vertical dela. Com a bet `active`, o pod fecha o spec junto com o agente, em mob, na daily do pod. A skill `grill` afia termos e decisões, a `bet-spec` escreve o spec e a `bet-slice` corta os slices. Quando o desenho cruza fronteira de função ou não tem precedente, a `architect` entra entre as duas.

O spec e os slices vão para o KB no mesmo PR. O Bet Owner aprova, e em Tier 2 o Lead também aprova. O `t0 gate spec --ci` recusa o PR enquanto houver `[PRECISA ESCLARECER]` aberto. Depois do merge, o CI espelha a bet como Feature e cada slice como Story no Jira.

### 5. Build e Verify

Um slice é um repo e um PR em draft. A skill `slice-build` confere o DoR, abre a branch `<KEY>-<slug>` e constrói teste a teste nas costuras do spec (os pontos do código onde o comportamento é testado). Depois ela prova o resultado no app real e abre o PR com a trilha `.audit/<KEY>.tsv`. A `slice-verify` revisa o PR antes do humano. Em seguida vem o review humano, conforme o tier. O CI move os estados sozinho.

### 6. Ship

Ship é o merge e o release. No merge do último slice, o CI roda `t0 bet ship`, que congela o spec da bet e atualiza o spec vivo do produto. A Bet vai para `shipped`, e o aprendizado é escrito no corpo dela.

### 7. Degraus de adoção

Cada produto sobe por três degraus (customer zero): primeiro o time, depois 2 ou 3 squads piloto, depois o ART. O Lead/AIVA decide a subida com números: uso semanal, retenção e eval. Os pisos estão em [Harness e qualidade](10-harness-e-qualidade.md) e são todos PROPOSTA. O comando `t0 gate degrau` ainda não está na CLI atual.

## Duas trilhas

| Trilha | Quando | O que tem | Quem aprova a aposta |
|---|---|---|---|
| Rápida | ajuste, bugfix ou melhoria que cabe em até 1 dia, sem desenho a decidir | sem spec: o slice nasce no PR da aposta com "atual, esperado, o que não muda" e o teste que vai ficar vermelho | Flow Steward ou Bet Owner, na daily |
| Bet | o resto, com apetite de até 2 semanas | protótipo, spec, desenho quando precisa, slices | Bet Owner; Lead também nos três casos |

Regras de fronteira:

- item rápido que precisa de desenho vira bet;
- bet que não cabe em 2 semanas vira duas;
- a exploração acontece no protótipo;
- superfície pública (MCP, CLI, skill, API) é Tier 2 em qualquer trilha;
- kill é uma linha na Idea (veredito `mata`) ou na Bet (`t0 log kill "<motivo>" --bet <BET>`).

Uma bet morta conta como resultado. O registro impede que a mesma ideia volte sem fato novo.

## As três decisões humanas

| Decisão | Quem decide | O que fica registrado | Como |
|---|---|---|---|
| Aposta | Bet Owner, na daily do pod; Lead também se cruza pods, é Tier 2 ou passa de 1 semana; na trilha rápida, Flow Steward ou Bet Owner | Bet `active` com `appetite` e `verified` | aprovação do PR aberto pelo `bet-new` (`t0 gate aposta` no CI) |
| Spec | Bet Owner; em Tier 2, também o Lead | Spec `approved`, `markers_open: 0`, `verified` de cada aprovador | aprovação do PR de spec e slices (`t0 gate spec` no CI) |
| Degrau | Lead/AIVA, quando os números saem | Adoption Report `passed`; Product com `adoption_stage` novo e `verified` | `gate degrau <produto>`, ainda fora da CLI atual |

Cada decisão é um PR no repo do KB que muda o `state`. O `t0 gate` roda os checks no CI, na cabeça do PR. Aprovar o PR é decidir. Ninguém escreve `verified` à mão. No merge, o CI registra quem aprovou, e o `kb-render` (o workflow que escreve os arquivos e as chaves derivados) deriva `verified: { by: human:<aprovador>, at: <data com offset> }` a partir desse registro. O PR de spec tem o mesmo SLO do review de código: primeira resposta em até 4 horas úteis.

Nenhuma skill aprova nada. As skills preparam a decisão, abrem o PR, mostram a evidência e param.

## Sem sprint interna

O time não tem compromisso de sprint nem fila semanal de triagem de ideias. O pod decide a ideia na daily do pod seguinte ao protótipo. A cadência de 2 semanas fica só onde o ART precisa dela, na Demo.

## WIP

O review pendente limita o WIP, e a Policy `wip` do KB guarda os números:

- cada pessoa tem no máximo 2 slices em `building` ou `in-review`;
- dentro desses slices, o número de sessões de agente em paralelo é livre;
- PR esperando review tem prioridade sobre slice novo;
- a daily do time olha os slices travados e os reviews parados há mais de 24h.

O `t0 slice dor <KEY>` recusa o slice quando quem vai pegá-lo já está no limite.

## Tiers de review

O tier vem do spec ou do slice e decide quantas pessoas leem o PR. O humano só lê depois que o agente de review e o CI passaram.

| Tier | Exemplos | Review mínimo |
|---|---|---|
| 0 | docs, testes, refactor mecânico, saída de agente de limpeza, PR de estado no KB | agente de review e CI; 1 humano faz merge em lote, uma vez por dia |
| 1 | feature em ferramenta interna, slice de bet | agente de review e 1 humano; júnior não aprova sozinho |
| 2 | auth, dado de cliente, permissão de agente, superfície pública, prompt ou modelo de ferramenta que as squads usam | agente de review e 2 humanos, um deles o Bet Owner (o outro pode ser de outro pod); blast radius com prova; cadeia de rastreabilidade completa; "Em minhas palavras" |

Os detalhes, incluindo a graduação de confiança, estão em [Harness e qualidade](10-harness-e-qualidade.md#tiers-de-review).

## Bet que mexe em vários repos

- Um slice é um repo e um PR. Uma Story que precisaria de dois repos vira dois slices ligados por `depends_on`.
- Todo PR pode ir para deploy sozinho, com expand, migrate e contract, porque não existe merge atômico entre repos.
- A ordem de merge padrão segue os `depends_on`, com os provedores primeiro.
- O PR leva no corpo os trailers `Bet:`, `Story:`, `Jira-Feature:`, `Depends-on:` e `KB-Context:`.

## Estados de cada etapa

| Tipo | Estados |
|---|---|
| Idea | `new` → `prototyped` → `promoted` ou `killed` |
| Bet | `proposed` → `active` → `shipped` ou `killed` |
| Spec da bet | `draft` → `approved` → `frozen` |
| Slice | `ready` → `building` → `in-review` → `done`, ou `blocked`, ou `conflict` |
| Product | `discovery` → `live` → `sunset` |

Quem pode mudar cada estado está em [KB em OKF](05-kb-okf.md).
