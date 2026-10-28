---
type: Playbook
title: "AIDLC t0 v2: metodologia enxuta"
description: Como o time de Inovação em IA vai da ideia ao protótipo e à produção com agentes, em fluxo contínuo sem sprint interna, com três decisões humanas registradas, seis rituais, o KB em OKF como sistema de registro gravado pelos próprios comandos, o Jira como espelho e o toolkit t0 rodando igual no Copilot, no Claude Code e no Kiro.
uid: methodology-aidlc-t0
owner: role:lead
tags: [metodologia, aidlc, okf, rituais, papeis, fluxo-continuo]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
---

# AIDLC t0 v2: metodologia enxuta

Rev 25 do living doc. A v2 sai do feedback do time de 2026-10-28, que achou a v1 burocrática, e segue as decisões do Lead registradas em `methodology/v2-brief.md`. Fontes que continuam valendo: living doc rev 23, os 25 deltas da pesquisa de metodologia, OKF v0.2 com o profile `t0-team` e o inventário do toolkit. Todo piso e todo número de graduação está marcado como PROPOSTA: entra no profile com `state: proposed` e só vira `in-force` depois de 3 ferramentas passarem pelo funil.

## TL;DR

A ideia vira protótipo na hora, em minutos ou horas, e o pod decide na daily seguinte se ela vira bet. Bet tem apetite de até 2 semanas e passa por spec e slices; ajuste que cabe em um dia vai pela trilha rápida, sem spec. Só três decisões humanas ficam registradas: aposta, spec e degrau de adoção. O resto é review de PR ou automação.

Por dentro não tem sprint. A Demo a cada 2 semanas segue a iteração do ART, o Harness Health é semanal e a Retro é mensal; o WIP é limitado por review pendente. São seis rituais, com cerca de 3h20 de cerimônia pura por pessoa a cada 2 semanas. Todo comando do toolkit `t0` grava o passo no KB, e ninguém escreve ata à mão. O Jira é espelho gerado; o código mora nos repos de produto.

Convenções: KB é o repositório OKF do time (`t0-kb`). O toolkit `t0` junta skills no padrão Agent Skills, o `AGENTS.md` modelo, a CLI `t0` e hooks de git e CI. Comando é uma skill, grafada `bet-spec` e chamada pelo nome em qualquer ferramenta; o que precisa ser determinístico mora na CLI (`t0 <subcomando>`). O Kiro entra só como harness de agente, com o recurso de specs dele desligado.

---

## 1. Princípios

1. Um passo de processo só entra quando protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado. Se não protege nem ensina, sai.
2. Humanos decidem e verificam, agentes executam. O dev é dono da intenção, do critério de aceite e da verificação; a digitação e o Jira ficam com o agente.
3. O KB é o sistema de registro, e quem grava é o comando. Jira, painel e PR são projeções. Se KB e Jira divergem, vale o KB, com as exceções de status da §6.
4. Protótipo antes de documento. Spec só existe para ideia que sobreviveu a um protótipo.
5. Atenção humana é o gargalo, e ela é medida: 1 slice = 1 PR revisável em até 15 min, WIP limitado por review pendente, primeira resposta em até 4h úteis.
6. Erro repetido do agente vira sensor. Na segunda ocorrência sobe a escada do harness, com `AGENTS.md` por último (§7.3).
7. Contexto é orçamento: link em vez de cópia, KB carregado por índice e busca, `AGENTS.md` com até 150 linhas, e o que não pegou é desligado.
8. Ferramenta de agente só sai com eval, e incidente vira caso de eval no Harness Health seguinte.

---

## 2. Fluxo

### 2.1 As sete etapas

```
 Ideia ──> Protótipo ──[aposta]──> Spec + slices ──[spec]──> Build e Verify ──> Ship ──> degraus ──[degrau]──> time → piloto → ART
 trilha rápida: Ideia ──[aposta]──> slice com "atual, esperado, o que não muda" + teste ──> Build e Verify ──> Ship
 harness, em qualquer etapa: agente erra pela 2ª vez ──> Harness Item ──> sensor, regra, skill ou AGENTS.md ──> PR aberto no Harness Health da semana
```

1. Ideia. Qualquer pessoa registra a qualquer hora com `idea-capture`, ou ela sai da gravação de uma daily pelo `meeting-record`.
2. Protótipo. Minutos a horas, sem aprovação, sozinho ou na daily do pod com o agente. Fica fora do main e nunca vira base de código. O `prototype` grava o resultado como uma linha na Idea: segue, ajusta ou mata.
3. Decisão: vira bet? O Bet Owner decide na daily do pod (`gate aposta`). O Lead só entra quando a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite.
4. Spec + slices. O agente gera durante a daily do pod, em mob (`bet-spec`, `bet-slice`). O spec vai para o KB num PR que o Bet Owner aprova (`gate spec`), e o Lead também em Tier 2. O `bet-sync` espelha as Stories no Jira.
5. Build e Verify. Um slice é um PR em draft (`slice-build`), revisado primeiro pelo agente (`slice-verify`) e depois por humanos conforme o tier. O CI move os estados sozinho.
6. Ship. Merge e release. No merge do último slice, o CI congela o spec da bet e atualiza o spec vivo do produto.
7. Degraus de adoção (customer zero), por produto: time, depois 2 ou 3 squads piloto, depois o ART. O Lead/AIVA decide com números (`gate degrau`).

### 2.2 As três decisões humanas

| Decisão | Quem decide | O que fica registrado | Comando |
|---|---|---|---|
| Aposta | Bet Owner, na daily do pod; Lead também se cruza pods, é Tier 2 ou passa de 1 semana; na trilha rápida, Flow Steward ou Bet Owner | Bet `active` com `appetite` e `verified` | `gate aposta <IDEA\|BET>` |
| Spec | Bet Owner; em Tier 2, também o Lead | Spec `approved`, `markers_open: 0`, `verified` de cada aprovador | `gate spec <BET>` |
| Degrau | Lead/AIVA, quando os números saem | Adoption Report `passed`; Product com `adoption_stage` novo e `verified` | `gate degrau <produto>` |

O `t0 gate` grava a decisão como PR no repo do KB, mudando `state` e acrescentando `verified: { by: human:<aprovador>, at: <data com offset> }`. Aprovar o PR é decidir. O histórico git do KB é a trilha de auditoria que o banco pede, e `t0 trace <BET>` gera para o auditor o JSON requisito → slice → PR → teste a partir do frontmatter. PR de spec tem o mesmo SLO do review de código.

Kill é uma linha na Idea (veredito do protótipo) ou na Bet (`kb log <BET> kill "<motivo>"`). Bet morta conta como resultado, e o registro impede que a mesma ideia volte sem fato novo.

### 2.3 Duas trilhas

| Trilha | Quando | O que tem |
|---|---|---|
| Rápida | ajuste, bugfix ou melhoria que cabe em até 1 dia | sem spec: o slice já nasce com "atual, esperado, o que não muda" e um teste; o Flow Steward ou o Bet Owner aprova a aposta na daily |
| Bet | o resto, com apetite de até 2 semanas | protótipo → spec → slices |

Exploração acontece no protótipo, e superfície pública (MCP, CLI, skill, API) é Tier 2 em qualquer trilha. Item rápido que precisa de design vira bet; bet que não cabe em 2 semanas vira duas.

### 2.4 Sem sprint interna

Não há compromisso de sprint, Betting de início de ciclo nem fila de triagem semanal. Ideia é decidida na daily do pod seguinte ao protótipo. O WIP é limitado por review pendente: no máximo 2 slices em construção por pessoa, sessões de agente em paralelo à vontade, e PR esperando review tem prioridade sobre slice novo.

---

## 3. Pods e papéis

### 3.1 Os três pods

| Pod | Escopo |
|---|---|
| Dev Tooling | agents, skills e CLIs do SDLC para as equipes de produto |
| PACO | produto do time para AIDLC e orquestração de agentes |
| Portal do time e Métricas | portal do time e métricas de uso e eficiência da IA na BU |

### 3.2 Os cinco papéis

| Papel | Quem | Responde por |
|---|---|---|
| Lead / AI Value Architect | Chapter Lead | escolher bets com PM e RTE, arquitetura transversal, interface com o ART, a constitution do time, decidir os degraus de adoção com números |
| Bet Owner | 1 sênior por pod | facilitar a daily do pod, decidir o que vira bet, aprovar o spec, responder pelo resultado da bet |
| Builder | todos, inclusive o Bet Owner | prototipar, pegar slices, orquestrar de 2 a 5 sessões de agente em paralelo, revisar PRs de agente e de colegas |
| Harness Keeper (rotativo, a cada 2 semanas) | 1 pessoa do time | AGENTS.md, skills, linters, CI e agentes de limpeza; triagem do "o agente errou"; jardinagem do KB e sunset do que não pegou; facilita o Harness Health semanal |
| Flow Steward (rotativo, a cada 2 semanas) | 1 pessoa do time | facilita a daily do time e a Retro mensal, cuida da fila de review, mantém Jira e KB coerentes (drift), prepara a Demo |

O Bet Owner também cumpre a capability Product do pod e chama um Domain Expert da squad para a daily do pod quando a bet toca o trabalho dela.

### 3.3 Rodízio

Todo mundo dos pods passa por Harness Keeper e por Flow Steward. Na primeira vez, júnior roda em par com um sênior. A troca acontece no `ritual demo close`, que grava a Rotation nova com `stale_after` no fim da atribuição. Ninguém segura os dois papéis ao mesmo tempo.

O Harness Keeper é o papel onde o ganho composto aparece: cada erro de agente que vira sensor deixa de custar review para o time inteiro.

### 3.4 Três práticas para juniores

Na pesquisa (RCT da Anthropic, jan/2026: 50% contra 67%, com a maior perda em debugging), delegação total destrói o aprendizado e "gerar e depois compreender" o preserva. Júnior não ganha papel novo, só três práticas:

- review em par nos primeiros PRs;
- seção "Em minhas palavras" em PR de júnior e em todo PR Tier 2, com o que o PR faz e por quê, sem colar a explicação do agente;
- um slice por quinzena feito sem gerar código com o agente, por escolha da pessoa.

---

## 4. Rituais

### 4.1 Os seis

| Ritual | Quando | Duração | Quem | O que acontece | Saída no KB (automática) |
|---|---|---|---|---|---|
| Daily do time | todo dia | 10 min | todos; facilita o Flow Steward | o bot publica o status antes (merges, review parado há mais de 24h, travas); na daily só se fala de bloqueios e pedidos de review | registro curto de bloqueios e donos |
| Daily do pod (mob com agentes) | todo dia, logo depois | 30 a 45 min (pode virar sessão de mob mais longa quando há spec para fechar) | o pod, com o agente ao vivo; facilita o Bet Owner; Domain Expert de squad quando precisar | validar ideias prototipando na hora, decidir o que vira bet, fechar spec juntos, refinar e planejar as tarefas do dia, destravar | ideias, decisões, specs (PR no KB), registro da sessão |
| Harness Health | toda semana | 20 min | o time; facilita o Harness Keeper | erros de agente que se repetiram na semana sobem a escada do harness; olhar o orçamento de contexto (linhas de `AGENTS.md`, hooks), skills sem uso para sunset e concepts vencidos no KB; incidente vira caso de eval; só fecha com um PR aberto por item aceito | Harness Items com PR, casos de eval |
| Demo | a cada 2 semanas, junto com a iteração do ART | 30 min | o time; facilita o Flow Steward | demo ao vivo do que foi pro ar + painel de fluxo e adoção; bets encerradas | registro da Demo, Bets `shipped` ou `killed`, rodízio novo |
| Retro | uma vez por mês | 60 min | o time; facilita o Flow Steward | como o time e a própria metodologia estão funcionando: o que atrapalha, que passo de processo cortar, o que mudar nas dailies e nos papéis | registro da Retro; ADR quando a metodologia muda |
| PI Planning / Sense & Respond do ART | quando o ART marcar | do ART | Lead/AIVA | bets candidatas e outcomes de adoção | registro com as decisões do ART |

Os cinco rituais internos abrem e fecham com `ritual daily-time|daily-pod|harness-health|demo|retro open|close`. O `open` monta a pauta a partir do KB; o `close` grava o Ritual Record com decisões e donos, roda o `meeting-record` se houve gravação e abre os PRs de decisão que saíram dali. O registro do PI Planning e do Sense & Respond sai do `meeting-record` sobre a pauta ou a gravação, se o ART permitir. Status quem dá é o bot, e ritual nenhum serve para isso.

### 4.2 Conta de tempo honesta

A cerimônia pura, a cada 2 semanas, é a daily do time (10 min × 10 dias = 1h40), dois Harness Health (2 × 20 = 40 min), uma Demo (30 min) e meia Retro mensal (30 min): cerca de 3h20. O Lead soma o PI Planning e o Sense & Respond, no ritmo do ART.

A daily do pod conta como trabalho. É ali que o pod prototipa, especifica e planeja com o agente, no lugar do shaping solitário, do Betting e do refinamento.

### 4.3 Transcrição

As dailies podem ser gravadas, com aviso, para o agente extrair ideias e decisões. A redação é determinística e vem antes de qualquer modelo: `meeting-record` chama `t0 transcript redact`, que roda o scanner de segredo e as regex de CPF, conta, e-mail e telefone; depois o agente faz uma passada para dado de cliente. Qualquer pessoa pode pedir "fora do registro" para um trecho, e o Transcript guarda só a contagem (`off_record_spans`). 1:1 nunca é gravado. Até o aval de LGPD, tudo fica em dry-run (redige e não persiste). Tudo que o agente extrai entra sem `verified` até alguém confirmar.

Retenção: Transcript com `stale_after` de 180 dias (PROPOSTA, pendente de validação com jurídico/LGPD). Vencido o prazo, a transcrição é apagada e o Ritual Record fica.

---

## 5. KB e contexto

### 5.1 O que mora onde

| Lugar | Conteúdo |
|---|---|
| KB (`t0-kb`, OKF v0.2, profile `t0-team`) | metodologia, time, ideias, produtos (spec vivo com contratos, ADRs, adoção, evals), bets (corpo, spec, slices, log), registros de ritual, transcrições, harness |
| Repos de produto (N por produto) | código, testes, `evals/`, `.audit/<KEY>.tsv` no PR, `tech-debt.md`, `AGENTS.md` canônico (`CLAUDE.md`, `.github/copilot-instructions.md` e `.kiro/steering/` só apontam para ele), regras de área geradas, skill `verify-<app>` |
| Jira | Feature (bet) e Story (slice) espelhadas, status, comentários do ART |
| Painel | métricas geradas (§8) |

Se o agente precisa disso para editar código, mora no repo; se precisa para decidir o que fazer, mora no KB. Conteúdo do KB nunca é colado em repo de código, só linkado por `uid`. A única cópia permitida é o contract test, gerado da seção de contrato do spec do produto com o `uid` no cabeçalho.

No KB, cada produto tem `products/<p>/` com `product.md`, `spec.md` (vivo), `evals.md`, `workspace.md` e `bets/BET-NNN/` (`bet.md`, `spec.md`, `slices/`, `log.md`). Ideias ficam em `ideas/`, registros em `rituals/AAAA-MM-DD-<slug>.md` e `transcripts/`, e o harness em `harness/`.

### 5.2 Workspace pattern

O mecanismo que deixa o KB alcançável e carregado em toda sessão está no ADR-0002 e em `methodology/workspace-pattern.md`. Resumo:

- A gente não usa submodules no KB. Funciona, mas dá HEAD destacado (agente perde commit), bump de ponteiro diário, código velho, KB preso ao repo menos legível e token de CI que lê todos os repos. Android, Zephyr e Chromium usam manifesto + clones irmãos, e a gente faz igual.
- O manifesto fica no KB, em `/products/<p>/workspace.md`: um concept `type: Workspace` com os repos, papéis, `depends_on` e grupos. Muda por PR revisado.
- Cada produto tem um workspace. `t0 ws init <p>` monta `~/ws/<p>/` com `kb/` e os repos como clones normais. Repo sem acesso fica `absent`. Para bet paralela, `t0 bet start BET-NNN --isolate` cria `~/ws/<p>@BET-NNN/` com worktrees.
- Toda sessão recebe contexto: a raiz do workspace tem um `AGENTS.md` gerado, o card (≤8.000 chars), com bet ativa, critérios de aceite, repos e mapa do KB. Claude Code, Copilot e Kiro leem AGENTS.md de raiz nativamente. Abra sempre a pasta do workspace, nunca multi-root.
- Por cima do card vêm o plugin `t0` com hooks (card velho vira delta de ≤3.000 chars, subagente ganha card, aviso de bet trocada) e o MCP local `t0-kb` (stdio, sem serviço hospedado). No Copilot CLI, `source .t0/env.sh`; no Kiro, steering `t0.md`.
- Cloud agent e CI fazem checkout read-only do `t0-kb` em `.kb/` e rodam `t0 mcp --kb .kb`. Sem KB, o agente para e avisa.
- A bet ativa sai de `T0_BET`, depois da branch `bet/BET-NNN/<STORY>-<slug>`, depois de `.t0/bet.json`, depois da chave Jira por lookup. Sem bet, skill de código não escreve código.
- Cross-repo: um slice = um repo = um PR. Trailers `Bet:`, `Story:`, `Jira-Feature:`, `Depends-on:`, `KB-Context:`. O status obrigatório `t0/merge-order` lê o change set no KB, nunca a API de outro repo. Todo PR é deployável sozinho (expand → migrate → contract).
- A escrita no KB segue três raias:
  - Registros (`t0 log`, decisões, eventos de PR): arquivo novo com nome único em `steps/`, PR com auto-merge. Como ninguém edita o mesmo arquivo, não tem conflito.
  - Conhecimento (spec, plan, slices, ADR, rituais, transcrições redigidas): PR com CODEOWNERS.
  - Derivados (`index.md`, `log.md`, `changeset.md`, chaves `jira:` e `state`): só o workflow `kb-render`, serializado.
- Só uma credencial cruza repos: o GitHub App KB-writer, instalado só no `t0-kb`.
- Falta verificar antes do rollout: auto-merge sob a proteção do banco (fallback: lote horário aprovado pelo Flow Steward), setup steps e MCP stdio no cloud agent, stdout de hook no Copilot CLI e no Kiro.

### 5.3 Tipos enxutos

Todos usam as chaves comuns do profile (`type`, `title`, `description`, `tags`, `uid`, `owner`, `generated`, `verified`, `status`, `stale_after` quando envelhece, `relations`). A tabela traz só o específico.

| Tipo | Chaves específicas | `state` |
|---|---|---|
| Idea | `source` (human / squad / transcript / jira), `product?`, `prototype {path, verdict: segue \| ajusta \| mata}` | new → prototyped → promoted \| killed |
| Bet | `track: rapida \| bet`, `appetite`, `hypothesis`, `kill_criteria`, `success_metric`, `decision_by`, `jira`; o intent mora no corpo | proposed → active → shipped \| killed |
| Spec | `acceptance[]` em bullets, `verify_how`, `markers_open`, `seams[]`, `tier`; plano como seção opcional; no spec vivo do produto, seção de contrato por superfície | bet: draft → approved → frozen; produto: approved → superseded |
| Slice | `bet`, `repo`, `tier`, `acceptance[]`, `verify_how`, `depends_on[]`, `jira`, `pr`; na trilha rápida, `current`, `expected`, `unchanged[]` | ready → building → in-review → done \| blocked \| conflict |
| ADR | `number`, `deciders[]`, `decided_at` | proposed → accepted → superseded \| rejected |
| Ritual Record | `ritual`, `date`, `facilitator`, `decisions[] {text, owner, due}`, `transcript?` | sem `state` |
| Transcript | `ritual`, `redaction`, `off_record_spans`, `participants[]` | sem `state`; `stale_after` obrigatório |
| Harness Item | `pattern`, `occurrences[]`, `ladder_step: sensor \| area-rule \| skill \| agents-md`, `pr` | open → fixed \| wontfix |
| Product | `stage`, `adoption_stage: 1\|2\|3`, `repos[]`, `domain_contacts[]`; spec vivo em `spec.md`; Eval Suite em `evals.md` (`regression_pass`, `metric: pass@1 \| pass^3`, `last_run`) | discovery → live → sunset |
| Adoption Report | `adoption_stage`, `wau`, `retention_4w`, `repeat_use`, `verdict` | open → passed \| failed |
| Policy, Template, Person, Role, Rotation, Workspace, Glossary Term | como no profile `t0-team` | idem |

Seguem no profile como infraestrutura, fora do fluxo: Playbook (este documento), Log (o `log.md` gerado) e Metric Snapshot (o que o CI escreve). O spec da bet congela no ship e o conteúdo vivo migra para `products/<p>/spec.md`: a bet é spec-first, o produto é spec-anchored.

### 5.4 O registro automático de cada passo

Toda skill termina chamando `t0 log`, que grava um registro de passo novo em `steps/` pela raia de registros. O `kb-render` é o único escritor do `log.md` da bet, com linhas `## YYYY-MM-DD` / `**Verbo** por <actor>: o quê (link)`; decisão leva o nome de quem aprovou. Decisões finas de implementação ficam no `.audit/<KEY>.tsv` do PR, e no merge o CI copia para o Slice as linhas de decisão. O `kb check` confere a conformidade: L0 e L1 bloqueiam no CI do KB, L2 vira aviso no status do bot.

---

## 6. Jira como espelho

KB primeiro, sempre. `bet-sync` chama `t0 jira sync`, que lê o KB, escreve no Jira pela API/MCP do Atlassian e grava a chave de volta no frontmatter. Rodar de novo sem diff não cria nada.

| Campo | Direção | Regra |
|---|---|---|
| Feature e Story (título, descrição, apetite, AC em bullets, Tier, link para o KB, label `ready-for-agent`, link Blocks por `depends_on`) | KB → Jira | o Jira nunca edita; edição feita lá é revertida no próximo sync, com comentário apontando para o PR no KB, e o diff vai para o `log.md` |
| Chave Jira (`jira:`) | Jira → KB | escrita uma vez, no create |
| Status da Story | duas vias, com fonte declarada | Git/CI escrevem no Jira e no slice (PR sai de draft = In Review; merge = Done). Transição humana no Jira (o RTE bloqueia, por exemplo) vira `state: blocked` com `blocked_by: jira:<quem>`. Transição que contradiz o fluxo (Done sem merge, Story andando antes do spec aprovado) é revertida com comentário |
| Comentários | duas vias, só acréscimo | comentário do ART entra no `log.md` como "externo"; resumo de merge e decisões vão para o Jira |
| Issue criada no Jira (bug de squad, pedido do ART) | Jira → KB (intake) | vira Idea `new` ou item da trilha rápida; daí em diante, mão única KB → Jira |
| Story points | KB → Jira | 1 fixo por slice, só se o ART exigir; nunca estimado |
| Outcomes do PI | KB → Jira/Confluence | gerados dos Adoption Reports e do registro da Demo; o Lead/AIVA leva |

Conteúdo é sempre do KB. Em status, vence a última transição com fonte registrada; o que o sync não resolve vira `state: conflict` e item para o Flow Steward. Toda escrita do sync vai para o `log.md`, sem sobrescrita silenciosa. O sync roda a cada comando que escreve no KB e num reconcile noturno (`t0 jira sync --reconcile`), que gera o relatório de drift. A meta é chegar à Demo com drift zero.

---

## 7. Qualidade

### 7.1 DoR e DoD

DoR do slice, checado pelo `slice-build`:

- critérios de aceite em bullets, "como verificar", tier e `repo`;
- na trilha bet, spec `approved` sem `[PRECISA ESCLARECER]`; na rápida, "atual, esperado, o que não muda" e o teste que vai ficar vermelho;
- chave Jira gravada.

DoD do slice:

- CI verde e agente de review sem pendência, depois review humano do tier;
- teste nas costuras do spec e verificação executada (`verify-<app>`); em Tier 2, blast radius com prova executada;
- `.audit/<KEY>.tsv` commitado e "Em minhas palavras" quando exigida;
- erro do agente no caminho registrado num Harness Item;
- superfície pública alterada com contract tests verdes e versão atualizada no spec do produto.

DoD da bet: slices `done`, spec congelado, spec vivo atualizado, regressão de eval registrada se for ferramenta de agente e aprendizado escrito na Bet.

### 7.2 Tiers de review

| Tier | Exemplos | Review mínimo |
|---|---|---|
| 0 | docs, testes, refactor mecânico, saída de agente de limpeza, PR de estado no KB | agente de review + CI; 1 humano faz merge em lote, diário |
| 1 | feature em ferramenta interna, slice de bet | agente de review + 1 humano; júnior não aprova sozinho |
| 2 | auth, dados de cliente, permissões de agente, superfície pública, prompt ou modelo de ferramenta que as squads usam | agente de review + 2 humanos, um deles o Bet Owner (o outro pode ser de outro pod); blast radius; cadeia de rastreabilidade completa |

O humano só lê depois que o agente de review e o CI passaram. O agente de review roda num subagente novo, só leitura, contra o spec; review entre modelos da mesma família fica marcado "same-family". PR nasce em draft e só tem merge automático em Tier 0. Hooks de git e CI bloqueiam force push, `reset --hard`, push em `main` e PR sem draft.

Graduação de confiança (PROPOSTA): um path desce de Tier 1 para Tier 0 depois de 20 PRs seguidos sem defeito escapado do agente de review e volta no primeiro defeito. Tier 2 nunca gradua. O contador fica em `harness/trust.md`, escrito só pelo CI.

### 7.3 Escada do harness

Na segunda ocorrência do mesmo erro, o Harness Item (aberto na primeira pelo `slice-verify`) sobe a escada:

1. sensor computacional: lint com mensagem de correção escrita para o agente, teste, hook de git ou gate de CI;
2. se não dá, regra de área, de uma fonte só em `agents/rules/<area>.md`, gerada por `t0 rules build` para as três ferramentas;
3. se é procedimento longo, skill no toolkit;
4. por último, `AGENTS.md`, com até 150 linhas.

Regra sem exceção mora em hook de git ou CI, e nunca em hook de agente: cada ferramenta tem formato e semântica próprios, o Copilot no VS Code ignora matchers e timeout de hook no Copilot falha aberto. Hook de agente fica como acelerador opcional. Teto de 20 hooks/deny por repo, reportado pelo Harness Keeper em `harness/budget.md` a cada Retro.

### 7.4 Política de eval

Vale para skills, MCPs, agentes e o próprio toolkit.

- Ferramenta que vai para squads piloto tem suíte de regressão de 20 a 50 tarefas tiradas de uso e falhas reais, com casos positivos e negativos, e precisa de pelo menos 95% para o degrau 1 → 2 (PROPOSTA). Tarefa com 0% é suspeita: monta uma solução de referência.
- Duas suítes por produto: capacidade (começa baixa) e regressão (perto de 100%). Capacidade que satura vira regressão.
- `pass@1` quando um resultado bom basta; `pass^3` para agente que a squad usa sem olhar. O `product.md` declara qual.
- Grader determinístico sempre que der; juiz LLM por dimensão, com opção "não sei"; humano só em amostra. Avalia-se o resultado.
- Upgrade de modelo, mudança de prompt ou de skill só entra se a regressão fica igual ou melhor. O Bet Owner do pod dono do produto assina, e `t0 eval run` registra.
- Incidente ou defeito escapado vira caso de eval (`t0 eval add`) no Harness Health seguinte. Em superfície pública, os primeiros casos saem junto com o spec.
- A infra de eval fica com o pod PACO. O Eval Suite no KB aponta para `evals/` no repo e guarda o último resultado.
- O toolkit segue a mesma regra, com goldens de spec e slice e a mesma skill rodando nas três ferramentas.

### 7.5 Pisos de customer zero (todos PROPOSTA)

Em `methodology/policies/adoption-floors.md`, `state: proposed`. "Ativo" é quem invocou a ferramenta em trabalho real numa semana ISO, medido por telemetria; login não conta.

| Degrau | Critério proposto | Quem confirma |
|---|---|---|
| 1 → 2 (time → 2 ou 3 squads piloto) | PROPOSTA: pelo menos 7 dos 10 do time ativos por semana por 2 semanas seguidas, e regressão de pelo menos 95% | Lead/AIVA |
| 2 → 3 (piloto → ART) | PROPOSTA: pelo menos 40% dos devs-alvo das squads piloto ativos por semana por 3 semanas seguidas, retenção de pelo menos 50% em 4 semanas e `pass^3` na meta do produto | Lead/AIVA; vira outcome do PI |
| Uso episódico (skill de migração, por exemplo) | PROPOSTA: uso repetido em pelo menos 2 de 4 semanas entre quem tinha tarefa elegível, no lugar do uso semanal | quem confirma o degrau |
| Sunset | PROPOSTA: menos de 15% de uso semanal no público-alvo, ou menos de 5 usuários ativos, depois de 8 semanas em piloto | Harness Keeper propõe; Lead confirma |

De onde vêm os números: o time é a coorte mais motivada, então 70% é razoável (o Claude Code foi de 20% a 50% da engenharia da Anthropic em 5 dias, um dado observado, que nunca foi gate). 40% no piloto fica abaixo do platô de ~60% atribuído à DX (não verificado) e passa do pico de novidade de uma semana. A cláusula de retenção copia a forma do gate do time do Claude Code (usuários ativos e retenção), cujo número não é público. O gate é nosso, independente dessas fontes, e é revisto depois de 3 ferramentas passarem pelo funil.

---

## 8. Métricas

Um painel só, mantido pelo pod Portal do time e Métricas, alimentado por Git, CI, Jira, telemetria dos agentes e o KB. Ninguém reporta nada à mão.

| Camada | Métrica | Decisão que ela informa |
|---|---|---|
| Velocidade | tempo ideia → protótipo; tempo ideia → produção | se o fluxo cumpre o que promete: ideia testada no mesmo dia, bet em produção dentro do apetite |
| Fluxo e visibilidade | slices por pessoa e estado; cycle time por slice; idade da fila de review e dos PRs de spec | quem destravar na daily do time; onde o trabalho espera |
| Review | mediana até a primeira resposta humana (até 4h úteis); minutos humanos por PR; % de problemas achados pelo agente antes do humano | redistribuir review; graduar área |
| Entrega (DORA) | frequência de deploy, lead time, taxa de falha de mudança, tempo de recuperação | pegar o "mais rápido e mais frágil" |
| Adoção | uso semanal, retenção em 4 semanas, uso repetido, custo por usuário ativo; tempo economizado por squad (auto-reportado + amostrado) | degraus e sunset; o que vai ao ART |
| Uso de IA | % de PRs de autoria de agente, custo de tokens por slice, sessões por dev/dia (só como piso, para oferecer ajuda) | custo do AIDLC; revisão mensal de modelo pelo Lead |
| Harness e evals | linhas de `AGENTS.md`, hooks por repo, recorrência do mesmo erro, Harness Items abertos e fechados, pass rate das suítes | se o time compõe ganho ou incha contexto; troca de modelo |
| KB | `stale_after` vencido, % de decisões com `verified: human:`, drift do Jira | se o sistema de registro está vivo |
| Práticas de júnior | % de PRs com "Em minhas palavras" onde é exigida; slices feitos sem geração de código | se as práticas acontecem (participação, nunca nota) |

Regra anti-vaidade, sem exceção:

- Nenhum ranking de pessoa por token, PR, linha ou sessão. A visão por pessoa mostra só o que está em andamento e travado. Dashboard que mostra pessoa por volume de agente é bug Tier 1.
- Token é piso e custo, nunca meta.
- Toda métrica nomeia a decisão que informa; a que não informou nenhuma em 2 PIs é removida pelo Harness Keeper.
- Métrica que sai do time é só de produto e de fluxo (adoção, retenção, DORA, ideia → produção), nunca de atividade.
- Dado individual das práticas de júnior só a própria pessoa vê.

---

## 9. Interface SAFe

SAFe por fora, builder pods por dentro. O AI-Native SAFe pede outcomes no PI em vez de features comprometidas, e os degraus de adoção já são outcomes, então a interface fica fina.

| SAFe (AI-Native) | Neste modelo |
|---|---|
| AI-Native Team (3 a 7 pessoas) | 3 pods + Lead; o segundo revisor de Tier 2 pode vir de outro pod |
| Epic / tema | Idea promovida e outcome de PI |
| Feature / Story | Bet / Slice, espelhadas pelo `bet-sync` |
| Iteração (2 semanas) | fluxo contínuo por dentro; Demo no fim de cada iteração do ART |
| PI Planning / PI Outcome Planning | compromisso com degraus de adoção, pisos de eval, SLO de review e DORA por produto; bets candidatas com apetite e risco entram como meio |
| Sense & Respond | registro da Demo e snapshot da quinzena como insumo; decisões do ART voltam como ADR ou Idea |
| Capacidades Product, Builder, Domain Expert, AI | Bet Owner; todo mundo; dev de squad chamado para a daily do pod; agentes com as skills do toolkit |
| AI Value Architect | o Lead (Chapter Lead) acumula: leva adoção, valor realizado e lacunas de eval ao ART e decide os degraus |
| Capacidade / pontos | throughput de slices e cycle time; 1 ponto fixo por slice se exigirem |

O SAFe descreve o AIVA como coaching de adoção em nível de ART. O time juntou o papel com o Lead para não criar mais um papel fixo num time de 10, e o custo cai na agenda do Lead. Se o ART rodar SAFe clássico, a Demo alimenta a System Demo, as Retros mensais e o Harness Health alimentam o I&A, e o PI Planning recebe bets candidatas além dos outcomes.

A interface volta à mesa se houver mais de 3 pods no mesmo produto, se a BU exigir pontos por PI, se o ART pedir a cadência dele por dentro ou se a agenda de Lead/AIVA estourar.

---

## 10. Rollout em 90 dias e decisões em aberto

Dias 0 a 30, um pod piloto (provavelmente Dev Tooling): `t0-kb` com profile, este documento, templates de bet e de slice da trilha rápida e `kb check`; toolkit v0 com a superfície da §11, hooks de git e gates de CI, com `jira sync` só na direção KB → Jira; `docs/agents/issue-tracker.md` nos repos do piloto, confirmando os nomes das ferramentas no MCP do Atlassian do banco; status do bot antes da daily; transcrição em dry-run. Sai quando houver 3 ideias prototipadas e decididas, 1 bet e 2 itens da trilha rápida em produção, 100% das decisões com `verified`, drift zero na Demo e o pod achando o fluxo mais leve que a v1.

Dias 31 a 60, os três pods: rodízio rodando, com juniores em par na primeira vez; `jira sync` completo com reconcile noturno; agente de review obrigatório antes do humano e `harness/trust.md` contando; primeiros Harness Health fechando com PRs e primeira Retro mensal; primeira suíte de eval (20 casos) e primeira ferramenta tentando o degrau 1 → 2; painel com ideia → protótipo, ideia → produção, DORA e adoção do próprio time. Sai com 1 ferramenta no degrau 2 com números e a cerimônia medida contra as 2h40 da §4.2.

Dias 61 a 90, automação e governança: agentes de limpeza abrindo PRs Tier 0; transcrição ligada se o aval saiu; primeira revisão dos pisos com dados; Lead/AIVA no Sense & Respond com os snapshots; toolkit v1 empacotado para as squads, com `THIRD_PARTY_NOTICES.md` (MIT do mattpocock/skills e do pstack). Sai com o time dentro do Sense & Respond e 1 piso virando `in-force` ou revisado com motivo.

Decisões em aberto:

- aval de LGPD para persistir transcrições e o prazo de retenção de 180 dias;
- auto-merge da raia de registros sob a proteção de branch do banco (fallback: lote horário aprovado pelo Flow Steward), MCP stdio no cloud agent e stdout de hook no Copilot CLI e no Kiro;
- calibração dos pisos de customer zero e do número 20 da graduação de confiança;
- gravação do PI Planning e do Sense & Respond, que depende do ART;
- plantão dos produtos que as squads já usam, que fica sem dono até a primeira ferramenta chegar ao degrau 2.

---

## 11. Passo → comando → artefato OKF

Cada comando é uma skill `SKILL.md`, descoberta pelas três ferramentas; quando há base upstream, é fork com `metadata.credits`.

| Passo | Comando | Determinístico via `t0` | Escreve (tipo OKF) |
|---|---|---|---|
| Capturar ideia | `idea-capture` | `t0 idea new`, com dedup | Idea `new` |
| Prototipar | `prototype <IDEA>` | grava o protótipo fora do main | veredito na Idea (`prototyped` ou `killed`) |
| Abrir bet ou trilha rápida | `bet-new rapida\|bet <IDEA>` | `t0 bet new`; na rápida, também o slice único | Bet `proposed`; Slice na rápida; Idea `promoted` |
| Decisão: aposta | `gate aposta <IDEA\|BET>` | `t0 gate aposta`: exige o Lead quando cruza pods, Tier 2 ou mais de 1 semana | Bet `active` + `verified` |
| Spec | `bet-spec <BET>` | conta `markers_open`; numera ADR (`t0 adr new`) | Spec `draft`; ADR `proposed`; Glossary Term |
| Slices | `bet-slice <BET>` | um arquivo por slice; grafo de dependências | Slice `ready` |
| Decisão: spec | `gate spec <BET>` | `t0 gate spec`: recusa com marcador aberto; exige o Lead em Tier 2 | Spec `approved` + `verified` |
| Espelhar no Jira | `bet-sync <BET>` | `t0 jira sync` | chaves `jira:`; Idea de intake; `log.md` |
| Build | `slice-build <KEY>` | checa o DoR; branch, PR em draft, `.audit/<KEY>.tsv` | Slice `building` + `pr` |
| Verify | `slice-verify <KEY>` | review contra o spec; blast radius em Tier 2; `t0 harness record` | comentário no PR; Harness Item |
| Estados e ship | CI | `t0 ci <KEY>` (In Review, Done, `verified` copiado das aprovações); no último merge, `t0 bet ship` | Slice; Spec `frozen`; spec vivo; Adoption Report `open`; Bet `shipped` |
| Kill | `kb log <BET> kill "<motivo>"` | `t0 log` | Bet `killed` |
| Decisão: degrau | `gate degrau <produto>` | `t0 adoption` contra os pisos e `t0 eval run`; recusa sem os dois | Adoption Report; Product `adoption_stage` + `verified` |
| Rituais | `ritual daily-time\|daily-pod\|harness-health\|demo\|retro open\|close` | `t0 digest` antes da daily do time; o close do Harness Health falha sem PR por item aceito; o close da Demo grava o rodízio | Ritual Record; Harness Item; Rotation; Metric Snapshot |
| Transcrição | `meeting-record <arquivo>` | `t0 transcript redact` antes do modelo | Transcript; Idea e ADR sem `verified` |
| Erro repetido → sensor | `harness-fix <HI>` | escolhe o degrau da escada; PR em draft no repo certo | Harness Item `fixed` + `pr` |
| KB | `kb find\|check\|log` | `t0 kb find`, `t0 kb check` (L0 a L2), `t0 log` | registro de passo em `steps/` |

Só na CLI: `t0 setup` (instala o toolkit num repo: `AGENTS.md`, ponteiros, regras, hooks, gates), `t0 ws init` e `t0 bet start --isolate`, `t0 mcp`, `t0 rules build`, `t0 eval run|add`, `t0 jira sync --reconcile`, `t0 review-queue` e `t0 trace`.

Ficam fora do toolkit, de propósito: poteto-mode (PR pronto, force push, "proceed without asking"), `why`/`recall`/`automate-me`/`reflect` (leem transcrições e varrem todos os MCPs), `make-bot-ui`, `no-comments`, `interrogate` (sem diversidade de família de modelo no banco) e `arena`/`swarm` (até o banco aprovar mais de um tier em paralelo).

---

## O que mudou da v1 e por quê

- O ciclo de 2 semanas com Betting, triagem semanal e compromisso de sprint saiu. Ideia vira protótipo na hora e é decidida na daily do pod seguinte, porque a fila semanal atrasava justamente o que o agente deixa barato testar.
- Os nove gates (G0 a G8) viraram três decisões humanas: aposta, spec e degrau. Build, review e merge ficaram com o CI, onde a prova já está no PR.
- Os quatro tipos de bet viraram duas trilhas. Exploração passou para o protótipo, plataforma virou Tier 2 e bugfix entrou na trilha rápida.
- Os rituais caíram de treze para seis. O trabalho das Mobs foi para a daily do pod, e o do Dia de limpeza e do Sweeper foi para o Harness Keeper e o Harness Health semanal. A Harness Retro quinzenal virou Harness Health semanal, e a Retro do time passou a ser mensal. A cerimônia pura caiu de 4h a 5h para cerca de 3h20 por quinzena.
- Saíram o eixo de arquétipos, a regra dos 3 ciclos e as accountabilities extras (AIVA separado, Eval Owner, Plantão, Preceptor). Ficaram cinco papéis, e as salvaguardas de júnior viraram três práticas.
- Saíram os tipos Plan, Assessment, Bugfix, Cycle Record, Accountability, PI Outcome e Contract. Plano e contrato viraram seções de spec, com menos arquivo para revisar.
- O registro ficou automático: cada comando grava o passo no KB, e a trilha de auditoria do banco continua sem custo de cerimônia.
- Entraram as métricas ideia → protótipo e ideia → produção, que dizem se a v2 cumpre o que promete.
