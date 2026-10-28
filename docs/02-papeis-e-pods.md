# Papéis e pods

O time tem três pods, cinco papéis e dois rodízios. Ninguém ganha papel novo por ser júnior: quem é júnior segue três práticas.

## Os três pods

| Pod | Slug no KB | Escopo |
|---|---|---|
| Dev Tooling | `dev-tooling` | agents, skills e CLIs do SDLC para as equipes de produto |
| PACO | `paco` | produto do time para AIDLC e orquestração de agentes |
| Portal do time e Métricas | `portal-metricas` | portal do time e métricas de uso e eficiência da IA na BU |

Cada pod é um produto no KB, em `products/<slug>/`. A pasta tem `product.md`, `workspace.md`, `evals.md`, ADRs, relatórios de adoção e bets (as apostas de trabalho de até 2 semanas). O pod PACO também cuida da infra de eval do time. O pod Portal do time e Métricas mantém o painel.

## Os cinco papéis

| Papel | Quem | Responde por |
|---|---|---|
| Lead / AI Value Architect | Chapter Lead | escolher bets com PM e RTE, arquitetura transversal, interface com o ART, a constitution do time, decidir os degraus de adoção com números |
| Bet Owner | 1 sênior por pod | facilitar a daily do pod, decidir o que vira bet, aprovar o spec, responder pelo resultado da bet |
| Builder | todos, inclusive o Bet Owner | prototipar, pegar slices, orquestrar de 2 a 5 sessões de agente em paralelo, revisar PRs de agente e de colegas |
| Harness Keeper | 1 pessoa do time, rodízio de 2 semanas | `AGENTS.md`, skills, linters, CI e agentes de limpeza; triagem do "o agente errou"; jardinagem do KB e sunset do que não pegou; facilita o Harness Health |
| Flow Steward | 1 pessoa do time, rodízio de 2 semanas | facilita a daily do time, a Demo e a Retro; cuida da fila de review; mantém Jira e KB coerentes; prepara a Demo |

Cada papel tem um arquivo em `team/roles/` no KB. Cada pessoa tem o seu arquivo em `team/people/`, só com o handle de trabalho, os pods e a flag `junior`.

### Lead / AI Value Architect

O Lead escolhe as bets candidatas com PM e RTE, cuida da arquitetura que cruza pods e é a interface do time com o ART. Ele também acumula o papel de AI Value Architect do SAFe: leva adoção, valor realizado e lacunas de eval ao ART e decide os degraus de adoção (cada passo de adoção de um produto: o time, as squads piloto, o ART). O time juntou os dois papéis para não criar mais um papel fixo num time de 10. O custo cai na agenda do Lead.

O Lead entra na decisão de aposta em três casos: quando a bet cruza pods, quando é Tier 2 (o nível de review mais alto) ou quando passa de 1 semana de apetite. Na decisão de spec (o contrato da bet), ele entra em Tier 2.

### Bet Owner

O Bet Owner é um sênior por pod. Ele facilita a daily do pod, decide o que vira bet, aprova o spec e responde pelo resultado. Ele também cumpre a capability Product do pod. Quando a bet toca o trabalho de uma squad, ele chama um Domain Expert dessa squad para a daily do pod. Em Tier 2, o Bet Owner é um dos dois revisores humanos obrigatórios.

O Bet Owner do pod dono de um produto assina mudança de modelo, de prompt ou de skill quando a regressão de eval fica igual ou melhor.

### Builder

Todo mundo é Builder, inclusive o Bet Owner. O Builder prototipa, pega slices (fatias de uma bet, cada uma com um repo e um PR), orquestra de 2 a 5 sessões de agente em paralelo e revisa PRs de agente e de colegas. Cada pessoa tem no máximo 2 slices em construção. Dentro desses slices, o número de sessões de agente é livre.

### Harness Keeper

Neste papel o ganho se acumula: cada erro de agente que vira sensor deixa de custar review para o time inteiro. O Harness Keeper cuida do harness (tudo o que cerca o agente para ele errar menos): o `AGENTS.md`, as skills, os linters, o CI e os agentes de limpeza. Ele faz a triagem do "o agente errou", jardina o KB (concepts vencidos, skills sem uso) e propõe o sunset do que não pegou. Ele facilita o [Harness Health](04-rituais.md#harness-health) semanal e mostra na Retro o teto de hooks de `harness/budget.md`.

O mattpocock-skills e o pstack são as referências das skills do time. Quando sai versão nova de um deles, o Harness Keeper lê o CHANGELOG no Harness Health e abre um Harness Item para o que vale portar.

### Flow Steward

O Flow Steward facilita a daily do time, a Demo e a Retro. Ele cuida da fila de review e mantém Jira e KB coerentes, com a meta de chegar à Demo com drift zero. Ele também prepara a Demo. Pela Policy `records-lane`, ele aprova uma vez por dia, antes da daily do time, o PR em lote dos registros de passo. Ele ainda resolve os slices que o sync do Jira marca como `conflict`.

Na trilha rápida, o Flow Steward pode aprovar a aposta no lugar do Bet Owner.

### Domain Expert de squad

O Domain Expert fica fora dos cinco papéis. É o dev de squad que o Bet Owner chama para a daily do pod quando a bet mexe no trabalho da squad. Ele traz o contexto do domínio e valida a ideia no protótipo.

## Rodízio

Todo mundo dos pods passa por Harness Keeper e por Flow Steward. Cada atribuição dura 2 semanas. Na primeira vez, quem é júnior roda em par com um sênior. Ninguém segura os dois papéis ao mesmo tempo.

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

Segundo a pesquisa, delegar tudo ao agente destrói o aprendizado, e "gerar e depois compreender" preserva o aprendizado (RCT da Anthropic, jan/2026: 50% contra 67%, com a maior perda em debugging). Por isso o júnior não ganha papel novo, só três práticas:

- review em par nos primeiros PRs;
- seção "Em minhas palavras" em PR de júnior e em todo PR Tier 2. A própria pessoa escreve o que o PR faz e por quê, sem colar a explicação do agente;
- um slice por quinzena feito sem gerar código com o agente, por escolha da pessoa.

A flag `junior: true` no arquivo da pessoa em `team/people/` liga a regra do "Em minhas palavras". A skill `slice-build` pede o texto ao autor e cola sem editar. Enquanto o autor não manda o texto, o PR fica com `[PRECISA DO AUTOR]`. Em Tier 1, júnior não aprova sozinho.

O painel mede se as práticas acontecem (participação, nunca nota). Só a própria pessoa vê o dado individual dessas práticas.
