# Papéis e pods

O time tem três pods, cinco papéis e dois rodízios. Ninguém ganha papel novo por ser júnior: júnior segue três práticas.

## Os três pods

| Pod | Slug no KB | Escopo |
|---|---|---|
| Dev Tooling | `dev-tooling` | agents, skills e CLIs do SDLC para as equipes de produto |
| PACO | `paco` | produto do time para AIDLC e orquestração de agentes |
| Portal do time e Métricas | `portal-metricas` | portal do time e métricas de uso e eficiência da IA na BU |

Cada pod é um produto no KB, em `products/<slug>/`, com `product.md`, `workspace.md`, `evals.md`, ADRs, relatórios de adoção e bets. O pod PACO também cuida da infra de eval do time. O pod Portal do time e Métricas mantém o painel.

## Os cinco papéis

| Papel | Quem | Responde por |
|---|---|---|
| Lead / AI Value Architect | Chapter Lead | escolher bets com PM e RTE, arquitetura transversal, interface com o ART, a constitution do time, decidir os degraus de adoção com números |
| Bet Owner | 1 sênior por pod | facilitar a daily do pod, decidir o que vira bet, aprovar o spec, responder pelo resultado da bet |
| Builder | todos, inclusive o Bet Owner | prototipar, pegar slices, orquestrar de 2 a 5 sessões de agente em paralelo, revisar PRs de agente e de colegas |
| Harness Keeper | 1 pessoa do time, rodízio de 2 semanas | `AGENTS.md`, skills, linters, CI e agentes de limpeza; triagem do "o agente errou"; jardinagem do KB e sunset do que não pegou; facilita o Harness Health |
| Flow Steward | 1 pessoa do time, rodízio de 2 semanas | facilita a daily do time, a Demo e a Retro; cuida da fila de review; mantém Jira e KB coerentes; prepara a Demo |

Cada papel tem um arquivo em `team/roles/` no KB, e cada pessoa tem o seu em `team/people/`, só com o handle de trabalho, os pods e a flag `junior`.

### Lead / AI Value Architect

O Lead escolhe as bets candidatas com PM e RTE, cuida da arquitetura que cruza pods e é a interface do time com o ART. Ele acumula o papel de AI Value Architect do SAFe: leva adoção, valor realizado e lacunas de eval ao ART e decide os degraus de adoção. O time juntou os dois papéis para não criar mais um papel fixo num time de 10, e o custo cai na agenda do Lead.

O Lead entra na decisão de aposta em três casos: a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite. Na decisão de spec, entra em Tier 2.

### Bet Owner

Um sênior por pod. Facilita a daily do pod, decide o que vira bet, aprova o spec e responde pelo resultado. Também cumpre a capability Product do pod e chama um Domain Expert da squad para a daily do pod quando a bet toca o trabalho dela. Em Tier 2, o Bet Owner é um dos dois revisores humanos obrigatórios.

O Bet Owner do pod dono de um produto assina mudança de modelo, de prompt ou de skill quando a regressão de eval fica igual ou melhor.

### Builder

Todo mundo é Builder, inclusive o Bet Owner. O Builder prototipa, pega slices, orquestra de 2 a 5 sessões de agente em paralelo e revisa PRs de agente e de colegas. O limite é de 2 slices em construção por pessoa. Sessões de agente dentro desses slices são à vontade.

### Harness Keeper

O papel onde o ganho composto aparece: cada erro de agente que vira sensor deixa de custar review para o time inteiro. O Harness Keeper cuida do `AGENTS.md`, das skills, dos linters, do CI e dos agentes de limpeza. Faz a triagem do "o agente errou", jardina o KB (concepts vencidos, skills sem uso) e propõe sunset do que não pegou. Facilita o [Harness Health](04-rituais.md#harness-health) semanal e mostra o teto de hooks de `harness/budget.md` na Retro.

Quando sai versão nova do mattpocock-skills ou do pstack, que são as referências das skills do time, o Harness Keeper lê o CHANGELOG no Harness Health e abre um Harness Item para o que vale portar.

### Flow Steward

Facilita a daily do time, a Demo e a Retro. Cuida da fila de review e mantém Jira e KB coerentes, com a meta de chegar à Demo com drift zero. Prepara a Demo. Pela Policy `records-lane`, aprova uma vez por dia, antes da daily do time, o PR em lote dos registros de passo. Também resolve os slices que o sync do Jira marca como `conflict`.

Na trilha rápida, o Flow Steward pode aprovar a aposta no lugar do Bet Owner.

### Domain Expert de squad

Fora dos cinco papéis. É o dev de squad que o Bet Owner chama para a daily do pod quando a bet mexe no trabalho da squad. Ele traz o contexto do domínio e valida a ideia no protótipo.

## Rodízio

Todo mundo dos pods passa por Harness Keeper e por Flow Steward. Cada atribuição dura 2 semanas. Na primeira vez, júnior roda em par com um sênior. Ninguém segura os dois papéis ao mesmo tempo.

A troca acontece no fechamento da Demo. O `t0 ritual demo close` grava a atribuição nova em `team/rotations/harness-keeper.md` e `team/rotations/flow-steward.md` e move o `stale_after` para o fim dela. A skill `ritual` propõe nomes a partir do roster, e o time escolhe.

Trecho real de `team/rotations/harness-keeper.md`, do exemplo do KB:

```yaml
type: Rotation
role: /team/roles/harness-keeper.md
cadence: P2W
roster: [human:ana-exemplo, human:caio-exemplo, human:dani-exemplo]
assignments:
  - { who: human:dani-exemplo, from: 2026-10-06T09:00:00-03:00, to: 2026-10-20T09:00:00-03:00 }
  - { who: human:caio-exemplo, from: 2026-10-20T09:00:00-03:00, to: 2026-11-03T09:00:00-03:00 }
stale_after: 2026-11-03T09:00:00-03:00
```

## Três práticas para juniores

A pesquisa mostra que delegação total ao agente destrói o aprendizado, e que "gerar e depois compreender" o preserva (RCT da Anthropic, jan/2026: 50% contra 67%, com a maior perda em debugging). Júnior não ganha papel novo, só três práticas:

- review em par nos primeiros PRs;
- seção "Em minhas palavras" em PR de júnior e em todo PR Tier 2, com o que o PR faz e por quê, escrita pela pessoa, sem colar a explicação do agente;
- um slice por quinzena feito sem gerar código com o agente, por escolha da pessoa.

A flag `junior: true` no arquivo da pessoa em `team/people/` liga a regra do "Em minhas palavras". A skill `slice-build` pede o texto ao autor e cola sem editar. Enquanto o autor não manda, o PR fica com `[PRECISA DO AUTOR]`. Em Tier 1, júnior não aprova sozinho.

O painel mede se as práticas acontecem (participação, nunca nota). Dado individual dessas práticas só a própria pessoa vê.
