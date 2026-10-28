# Brief da v2: metodologia enxuta

A v2 nasce do feedback do time de 2026-10-28: a v1 ficou burocrática. Esta é a regra que decide tudo:

> A metodologia existe para habilitar o time e deixá-lo mais rápido. Um passo de processo só entra quando protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado. Se não protege nem ensina, sai.

O que continua da v1:
- o KB em OKF como sistema de registro, com specs e tasks também no Jira;
- o workspace pattern (manifesto + clones irmãos, card de contexto, MCP `t0-kb`, três raias de escrita);
- o toolkit `t0` portátil para Copilot, Claude Code e Kiro;
- os tiers de review, a escada do harness, a política de eval e os pisos de customer zero (como PROPOSTA).

O registro de cada passo continua, mas é automático: os comandos gravam no KB. Ninguém escreve ata à mão.

## Pods (os três de hoje)

| Pod | Escopo |
|---|---|
| Dev Tooling | agents, skills e CLIs do SDLC para as equipes de produto |
| PACO | produto do time para AIDLC e orquestração de agentes |
| Portal do time e Métricas | portal do time e métricas de uso e eficiência da IA na BU |

## Papéis (os cinco do markdown original, sem eixo de arquétipos)

| Papel | Quem | Responde por |
|---|---|---|
| Lead / AI Value Architect | Chapter Lead | escolher bets com PM e RTE, arquitetura transversal, interface com o ART, a constitution do time, decidir os degraus de adoção com números |
| Bet Owner | 1 sênior por pod | facilitar a daily do pod, decidir o que vira bet, aprovar o spec, responder pelo resultado da bet |
| Builder | todos, inclusive o Bet Owner | prototipar, pegar slices, orquestrar de 2 a 5 sessões de agente em paralelo, revisar PRs de agente e de colegas |
| Harness Keeper (rotativo, a cada 2 semanas) | 1 pessoa do time | AGENTS.md, skills, linters, CI e agentes de limpeza; triagem do "o agente errou"; jardinagem do KB e sunset do que não pegou; facilita o Harness Health semanal |
| Flow Steward (rotativo, a cada 2 semanas) | 1 pessoa do time | facilita a daily do time, cuida da fila de review, mantém Jira e KB coerentes (drift), prepara a Demo |

Regras: todo mundo passa por Harness Keeper e Flow Steward. Na primeira vez, júnior roda em par com um sênior. O Harness Keeper é o papel onde o ganho composto aparece.

Juniores (sem papel novo, só três práticas): review em par nos primeiros PRs; seção "Em minhas palavras" em PR de júnior e em todo Tier 2; um slice por quinzena feito sem gerar código com o agente, por escolha.

## Fluxo contínuo, sem sprint interna

Recomendação sobre a dúvida "sprint de 2 semanas ou triagem semanal": nenhum dos dois por dentro.
- Ideia vira protótipo em minutos ou horas, na hora em que aparece, e é decidida na daily do pod seguinte. Não há fila de triagem semanal.
- A cadência de 2 semanas fica só onde o ART precisa dela: a Demo alinhada à iteração do ART. O Harness Health é semanal e a Retro do time é mensal. Não há Betting de início de ciclo nem compromisso de sprint.
- O WIP é limitado por review pendente (no máximo 2 slices em construção por pessoa), não por sprint.

O fluxo de uma ideia:
1. **Ideia.** Qualquer pessoa, a qualquer hora (`idea-capture`, ou extraída da gravação de uma daily).
2. **Protótipo.** Minutos a horas, sem aprovação, sozinho ou na daily do pod com o agente. Fica fora do main. O resultado vira uma linha na Idea: segue, ajusta ou mata.
3. **Decisão: vira bet?** O Bet Owner decide na daily do pod. O Lead só entra quando a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite. É uma decisão humana registrada por comando (`gate aposta`).
4. **Spec + slices.** O agente gera durante a daily do pod (mob). Vai para o KB em um PR que o Bet Owner aprova (`gate spec`), e mais o Lead em Tier 2. O agente espelha as Stories no Jira.
5. **Build e Verify.** Um slice é um PR em draft. O review segue o tier, e o CI move os estados sozinho.
6. **Ship.** Merge e release. O spec vivo do produto é atualizado.
7. **Degraus de adoção** (customer zero), por produto: time → 2 ou 3 squads piloto → ART. Quem decide é o Lead/AIVA, com números (`gate degrau`).

Há só três decisões humanas registradas: aposta, spec e degrau. O resto é review de PR normal ou automação.

Há duas trilhas, não quatro tipos de bet:

| Trilha | Quando | O que tem |
|---|---|---|
| Rápida | ajuste, bugfix ou melhoria que cabe em até 1 dia | sem spec: o slice já nasce com "atual, esperado, o que não muda" e um teste; o Flow Steward ou o Bet Owner aprova a aposta na daily |
| Bet | o resto, com apetite de até 2 semanas | protótipo → spec → slices |

Exploração é o passo de protótipo, não um tipo de bet. Superfície pública (MCP, CLI, skill, API) é Tier 2, e não um tipo. Kill é uma linha na Idea ou na Bet.

## Rituais (cinco internos + os do ART)

| Ritual | Quando | Duração | Quem | O que acontece | Saída no KB (automática) |
|---|---|---|---|---|---|
| Daily do time | todo dia | 10 min | todos; facilita o Flow Steward | o bot publica o status antes (merges, review parado há mais de 24h, travas); na daily só se fala de bloqueios e pedidos de review | registro curto de bloqueios e donos |
| Daily do pod (mob com agentes) | todo dia, logo depois | 30 a 45 min (pode virar sessão de mob mais longa quando há spec para fechar) | o pod, com o agente ao vivo; facilita o Bet Owner; Domain Expert de squad quando precisar | validar ideias prototipando na hora, decidir o que vira bet, fechar spec juntos, refinar e planejar as tarefas do dia, destravar | ideias, decisões, specs (PR no KB), registro da sessão |
| Harness Health | toda semana | 20 min | o time; facilita o Harness Keeper | erros de agente repetidos sobem a escada do harness; orçamento de contexto, skills sem uso e KB vencido; só fecha com PR por item aceito | Harness Items com PR |
| Demo | a cada 2 semanas, com a iteração do ART | 30 min | o time; facilita o Flow Steward | demo ao vivo + painel; bets encerradas | registro da Demo |
| Retro | mensal | 60 min | o time; facilita o Flow Steward | como o time e a metodologia estão funcionando; que passo cortar | registro da Retro; ADR se a metodologia muda |
| PI Planning / Sense & Respond do ART | quando o ART marcar | do ART | Lead/AIVA | bets candidatas e outcomes de adoção | registro com as decisões do ART |

O que sai da v1: Betting, triagem semanal de ideias, Mob Elaboration A e B, Mob Construction, Sync de bloqueios separado, preceptoria como ritual, Dia de limpeza (agora é trabalho contínuo do Harness Keeper e dos agentes de limpeza) e o eixo de arquétipos.

Tempo, em conta honesta: a cerimônia pura é a daily do time (10 min × 10 dias = 1h40) mais 2 Harness Health (40 min), 1 Demo (30 min) e meia Retro mensal (30 min), cerca de 3h20 a cada 2 semanas. A daily do pod é trabalho, não reunião: é ali que o pod prototipa, especifica e planeja com o agente, no lugar do shaping solitário, do Betting e do refinamento.

Transcrição: as dailies podem ser gravadas para o agente extrair ideias e decisões. A redação é determinística antes de qualquer modelo, 1:1 nunca é gravado, e fica em dry-run até o aval de LGPD. Tudo que o agente extrai entra sem `verified` até alguém confirmar.

## O que o KB guarda (tipos enxutos)

Ficam: Idea, Bet (o intent mora no corpo), Spec (o plano é uma seção opcional), Slice (inclui "atual / esperado / não muda" na trilha rápida), ADR, Ritual Record, Transcript, Harness Item, Product (com spec vivo e Eval Suite), Adoption Report, Policy, Template, Person, Role, Rotation, Workspace e Glossary Term.

Saem: Plan como arquivo separado, Assessment, Bugfix, Cycle Record, Accountability, PI Outcome e Contract como tipo (o contrato vira seção do spec do produto).

## Escrita

Escreva em pt-BR informal paulistano e preciso, seguindo o skill humanizer (`/Users/tuba/.claude/plugins/cache/humanizer/humanizer/2.11.2/SKILL.md`):
- sem negação de efeito ("não é X, é Y");
- sem bullets de rótulo em negrito;
- sem travessões;
- critérios de aceite sempre em bullets, nunca Gherkin.

Mantenha as fontes e as marcações PROPOSTA e "(não verificado)" da v1 onde a afirmação continua.
