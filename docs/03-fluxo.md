# Fluxo

Por dentro do time não tem sprint. A ideia anda assim que aparece, e só três pontos do caminho pedem decisão humana registrada.

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

Qualquer pessoa registra a qualquer hora com a skill `idea-capture`. Ela pede só três coisas (problema, para quem e sinal), procura duplicata no KB e roda `t0 new idea`. A ideia entra como Idea `new` em `ideas/IDEA-NNNN.md`, num PR pequeno.

Ideia também sai de gravação de daily, pelo `ritual <slug> close --transcript`, e de issue aberta no Jira por squad ou pelo ART. Nos dois casos entra sem `verified` até alguém confirmar.

### 2. Protótipo

Minutos a horas, sem aprovação, sozinho ou ao vivo na daily do pod com o agente. A skill `prototype` trabalha numa branch descartável `proto/<IDEA>-<slug>` do repo de produto, que nunca vai para o main e nunca vira base de código. Só dados fictícios.

O protótipo termina num veredito gravado na Idea com `t0 idea prototype`:

| Veredito | Quando |
|---|---|
| `segue` | a ideia se sustentou e pode virar bet |
| `ajusta` | tem algo ali, mas a pergunta ou a solução muda |
| `mata` | a ideia não se sustenta; o motivo fica registrado para ela voltar só com fato novo |

No KB entram só o veredito e a referência da branch. O código do protótipo fica fora.

### 3. Aposta: vira bet?

O Bet Owner decide na daily do pod. A skill `bet-new` roda `t0 new bet` e abre o PR da aposta em draft. Aprovar esse PR é decidir. O Lead também aprova quando a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite. O `t0 gate aposta --ci` confere isso no CI.

A bet carrega `appetite`, `hypothesis`, `kill_criteria` e `success_metric`. O intent (problema, para quem, sinal, o que entra e o que fica fora) mora no corpo.

### 4. Spec e slices

Com a bet `active`, o pod fecha o spec junto com o agente, em mob, na daily do pod. A skill `grill` afia termos e decisões, a `bet-spec` escreve o spec e a `bet-slice` corta os slices. Quando o desenho cruza fronteira de função ou não tem precedente, a `architect` entra entre as duas.

Spec e slices vão para o KB no mesmo PR. O Bet Owner aprova, e o Lead também em Tier 2. O `t0 gate spec --ci` recusa enquanto houver `[PRECISA ESCLARECER]` aberto. Depois do merge, o CI espelha a bet como Feature e cada slice como Story no Jira.

### 5. Build e Verify

Um slice é um repo e um PR em draft. A skill `slice-build` confere o DoR, abre a branch `<KEY>-<slug>`, constrói teste a teste nas costuras do spec, prova no app real e abre o PR com a trilha `.audit/<KEY>.tsv`. A `slice-verify` revisa antes do humano. Depois vem o review humano pelo tier. O CI move os estados sozinho.

### 6. Ship

Merge e release. No merge do último slice, o CI roda `t0 bet ship`: congela o spec da bet e atualiza o spec vivo do produto. A Bet vai para `shipped`, e o aprendizado é escrito no corpo dela.

### 7. Degraus de adoção

Cada produto sobe por três degraus (customer zero): o time, depois 2 ou 3 squads piloto, depois o ART. O Lead/AIVA decide com números: uso semanal, retenção e eval. Os pisos estão em [Harness e qualidade](10-harness-e-qualidade.md) e são todos PROPOSTA. O comando `t0 gate degrau` ainda não está na CLI atual.

## Duas trilhas

| Trilha | Quando | O que tem | Quem aprova a aposta |
|---|---|---|---|
| Rápida | ajuste, bugfix ou melhoria que cabe em até 1 dia, sem desenho a decidir | sem spec: o slice nasce no PR da aposta com "atual, esperado, o que não muda" e o teste que vai ficar vermelho | Flow Steward ou Bet Owner, na daily |
| Bet | o resto, com apetite de até 2 semanas | protótipo, spec, desenho quando precisa, slices | Bet Owner; Lead também nos três casos |

Regras de fronteira:

- item rápido que precisa de desenho vira bet;
- bet que não cabe em 2 semanas vira duas;
- exploração acontece no protótipo;
- superfície pública (MCP, CLI, skill, API) é Tier 2 em qualquer trilha;
- kill é uma linha na Idea (veredito `mata`) ou na Bet (`t0 log kill "<motivo>" --bet <BET>`).

Bet morta conta como resultado. O registro impede que a mesma ideia volte sem fato novo.

## As três decisões humanas

| Decisão | Quem decide | O que fica registrado | Como |
|---|---|---|---|
| Aposta | Bet Owner, na daily do pod; Lead também se cruza pods, é Tier 2 ou passa de 1 semana; na trilha rápida, Flow Steward ou Bet Owner | Bet `active` com `appetite` e `verified` | aprovação do PR aberto pelo `bet-new` (`t0 gate aposta` no CI) |
| Spec | Bet Owner; em Tier 2, também o Lead | Spec `approved`, `markers_open: 0`, `verified` de cada aprovador | aprovação do PR de spec e slices (`t0 gate spec` no CI) |
| Degrau | Lead/AIVA, quando os números saem | Adoption Report `passed`; Product com `adoption_stage` novo e `verified` | `gate degrau <produto>`, ainda fora da CLI atual |

A decisão é um PR no repo do KB que muda o `state`. O `t0 gate` roda os checks no CI, na cabeça do PR. Aprovar o PR é decidir. Ninguém escreve `verified` à mão: no merge, o CI registra quem aprovou e o `kb-render` deriva `verified: { by: human:<aprovador>, at: <data com offset> }` a partir desse registro. PR de spec tem o mesmo SLO do review de código: primeira resposta em até 4 horas úteis.

Nenhuma skill aprova nada. Elas preparam a decisão, abrem o PR, mostram a evidência e param.

## Sem sprint interna

Não há compromisso de sprint nem fila semanal de triagem de ideias. A ideia é decidida na daily do pod seguinte ao protótipo. A cadência de 2 semanas fica só onde o ART precisa dela, na Demo.

## WIP

O WIP é limitado por review pendente, e a Policy `wip` do KB guarda os números:

- no máximo 2 slices em `building` ou `in-review` por pessoa;
- sessões de agente em paralelo dentro desses slices são à vontade;
- PR esperando review tem prioridade sobre slice novo;
- a daily do time olha os slices travados e os reviews parados há mais de 24h.

O `t0 slice dor <KEY>` recusa o slice quando quem vai pegar já está no limite.

## Tiers de review

O tier sai do spec ou do slice e decide quantas pessoas leem o PR. O humano só lê depois que o agente de review e o CI passaram.

| Tier | Exemplos | Review mínimo |
|---|---|---|
| 0 | docs, testes, refactor mecânico, saída de agente de limpeza, PR de estado no KB | agente de review e CI; 1 humano faz merge em lote, uma vez por dia |
| 1 | feature em ferramenta interna, slice de bet | agente de review e 1 humano; júnior não aprova sozinho |
| 2 | auth, dado de cliente, permissão de agente, superfície pública, prompt ou modelo de ferramenta que as squads usam | agente de review e 2 humanos, um deles o Bet Owner (o outro pode ser de outro pod); blast radius com prova; cadeia de rastreabilidade completa; "Em minhas palavras" |

Detalhes, incluindo a graduação de confiança, em [Harness e qualidade](10-harness-e-qualidade.md#tiers-de-review).

## Bet que mexe em vários repos

- Um slice é um repo e um PR. Uma Story que precisaria de dois repos vira dois slices ligados por `depends_on`.
- Todo PR é deployável sozinho, com expand, migrate e contract, porque não existe merge atômico entre repos.
- A ordem de merge padrão segue os `depends_on`, provedores primeiro.
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
