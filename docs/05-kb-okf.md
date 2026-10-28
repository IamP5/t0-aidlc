# KB em OKF

O KB (knowledge base) é o sistema de registro do time. Ele fica num repositório próprio, `t0-kb`, que o time inteiro pode ler. O KB guarda tudo o que foi decidido, por quem e quando. Jira, painel e PR são projeções dele.

## O que é OKF

OKF é o formato do bundle de conhecimento. Um bundle é uma árvore de arquivos Markdown, e cada arquivo é um concept:

- cada arquivo começa com frontmatter YAML, e a chave `type` diz o tipo do concept;
- cada pasta tem um `index.md` que lista o que tem dentro, uma linha por item;
- o `log.md` guarda o histórico, do mais novo para o mais antigo, com títulos `## AAAA-MM-DD`;
- o `index.md` da raiz declara a versão, `okf_version: "0.2"`;
- um profile define os tipos, as chaves obrigatórias e os estados. O do time é o `t0-team`, gerado em `profile.md`.

O `t0 kb check` confere a conformidade em três níveis. L0 é o piso do OKF v0.2: frontmatter válido, `type` presente, forma do `index.md` e do `log.md`. L1 confere o profile `t0-team`: tipo registrado, chaves obrigatórias, tipos de valor e `uid` único. L2 dá avisos de integridade. Falha em L0 ou L1 bloqueia o PR no CI do KB. Falha em L2 vira aviso no status do bot.

## O que mora onde

| Lugar | Conteúdo |
|---|---|
| KB (`t0-kb`) | metodologia, time, ideias, produtos (spec vivo com contratos, ADRs, adoção, evals), bets (corpo, spec, slices, registros), registros de ritual, transcrições redigidas, harness |
| Repos de produto | código, testes, `evals/`, `.audit/<KEY>.tsv` no PR, `AGENTS.md` canônico, skill `verify-<app>` em `.t0/skills/` |
| Jira | Feature (bet) e Story (slice) espelhadas, status, comentários do ART |
| Painel | métricas geradas |

A regra para decidir: se o agente precisa da informação para editar código, ela mora no repo. Se precisa dela para decidir o que fazer, ela mora no KB. Ninguém cola conteúdo do KB em repo de código. O repo só aponta para o KB pelo `uid` ou pela chave. A única cópia permitida é o contract test, gerado da seção de contrato do spec vivo (a seção do `product.md` com o comportamento atual do produto), com o `uid` no cabeçalho.

## A árvore do bundle

A estrutura abaixo é a do `okf-template`, o ponto de partida para o KB real:

```
t0-kb/
  index.md  profile.md  log.md        gerados
  .github/CODEOWNERS                  donos da raia de conhecimento
  methodology/
    methodology.md  workspace-pattern.md
    practices/   review-tiers.md  harness-ladder.md  dor-dod.md
    policies/    adoption-floors.md  eval-gate.md  transcript-retention.md
                 models.md  records-lane.md  wip.md
    adr/
  templates/     idea bet spec slice adr harness-item ritual-record (.md)
  team/          people/  roles/ (5)  rotations/ (harness-keeper, flow-steward)
  ideas/         IDEA-NNNN.md
  rituals/       <slug>/ritual.md  e  <slug>/AAAA-MM-DD.md
                 daily-time daily-pod harness-health demo retro pi
  transcripts/   AAAA-MM-DD-<ritual>.md (só redigidas)
  steps/         registros de passo fora de uma bet
  glossary/      um arquivo por termo
  harness/       HI-NNNN.md  budget.md
  products/<pod>/                     dev-tooling  paco  portal-metricas  exemplo
    product.md  workspace.md  evals.md
    adr/  adoption/
    bets/BET-NNN/  bet.md  spec.md  slices/NN-slug.md  steps/  log.md
```

O produto `exemplo` é fictício e exercita todos os tipos, as duas trilhas (rápida e bet) e as três raias de escrita, descritas mais abaixo. É o melhor lugar para ver um arquivo de verdade. Quando o KB real tiver os próprios concepts, `products/exemplo/` e os concepts com a tag `exemplo` saem do KB.

## Os tipos

Uma Bet é uma aposta de até 2 semanas. O Spec é o contrato da bet, e cada Slice é uma fatia vertical dela, com um repo e um PR. Um ADR registra uma decisão difícil de desfazer. A chave `tier` é o nível de review do PR (0, 1 ou 2).

| Tipo | Onde | Chaves específicas | Estados |
|---|---|---|---|
| Idea | `ideas/IDEA-NNNN.md` | `source` (human, squad, transcript, jira), `product`, `verdict` (`segue`, `ajusta`, `mata`), `prototype_ref`, `decided_at` | new → prototyped → promoted ou killed |
| Bet | `products/<p>/bets/BET-NNN/bet.md` | `track` (`rapida` ou `bet`), `appetite`, `hypothesis`, `kill_criteria`, `success_metric`, `decision_by`, `jira`; intent no corpo | proposed → active → shipped ou killed |
| Spec | `products/<p>/bets/BET-NNN/spec.md` | `markers_open`, `seams[]`, `tier`; no corpo, as seções `## Critérios de aceite` e `## Como verificar`, mais Plano e Design opcionais | draft → approved → frozen |
| Slice | `products/<p>/bets/BET-NNN/slices/NN-slug.md` | `bet`, `repo`, `tier`, `depends_on[]`, `jira`, `pr`; no corpo, `## Critérios de aceite` e `## Como verificar` e, na rápida, `## Atual`, `## Esperado` e `## Não muda` | ready → building → in-review → done, blocked ou conflict |
| ADR | `methodology/adr/` ou `products/<p>/adr/` | `number`, `deciders[]`, `decided_at` | proposed → accepted → superseded ou rejected |
| Ritual | `rituals/<slug>/ritual.md` | `cadence`, `duration`, `facilitator`, `inputs`, `outputs` | active, paused, retired |
| Ritual Record | `rituals/<slug>/AAAA-MM-DD.md` | `ritual`, `date`, `facilitator`, `decisions[] {text, owner, due}`, `transcript` | sem estado |
| Transcript | `transcripts/` | `ritual`, `redaction`, `off_record_spans`, `participants[]`; `stale_after` obrigatório | sem estado |
| Harness Item | `harness/HI-NNNN.md` | `pattern`, `occurrences[]`, `ladder_step` (`sensor`, `area-rule`, `skill`, `agents-md`), `pr` | open → fixed ou wontfix |
| Product | `products/<p>/product.md` | `stage`, `adoption_stage` (1, 2 ou 3), `repos[]`, `domain_contacts[]`; spec vivo e contrato no corpo | discovery → live → sunset |
| Workspace | `products/<p>/workspace.md` | bloco `workspace:` com repos, papéis, `depends_on` e grupos | sem estado |
| Eval Suite | `products/<p>/evals.md` | `metric` (`pass@1` ou `pass^3`), `regression_pass`, `last_run`, `repo_path` | sem estado |
| Adoption Report | `products/<p>/adoption/<semana>.md` | `adoption_stage`, `wau`, `retention_4w`, `repeat_use`, `verdict` | open → passed ou failed |
| Policy | `methodology/policies/` | depende da Policy | proposed → in-force → retired |
| Template | `templates/` | esqueleto em pt-BR que o `t0 new` copia | sem estado |
| Person | `team/people/` | `handle`, `pods`, `junior` | active, alumni |
| Role | `team/roles/` | descrição do papel | sem estado |
| Rotation | `team/rotations/` | `role`, `cadence`, `roster`, `assignments` | sem estado |
| Glossary Term | `glossary/` | `term`, `term_en`, `aliases`, `avoid`, `scope` | sem estado |
| Step | `steps/` ou `products/<p>/bets/BET-NNN/steps/` | `kind`, `bet`, `story`, `repo`, `refs`, `on_behalf_of` | sem estado |

Além desses, o OKF traz Reference (documento de apoio, como a metodologia e o `harness/budget.md`) e Log (o `log.md` gerado).

O spec da bet congela no ship, quando a bet chega a `shipped`. O que continua valendo passa para o spec vivo do produto. Por isso a bet é spec-first e o produto é spec-anchored.

## Frontmatter: o essencial

Todo concept tem estas chaves comuns:

| Chave | Obrigatória | O que é |
|---|---|---|
| `type` | sim | o tipo, como na tabela acima |
| `title` | sim | título curto |
| `description` | sim | uma frase; vira a linha do `index.md` |
| `uid` | sim | id estável, kebab-case, único no bundle |
| `owner` | sim | dono, como ator: `human:`, `team:`, `role:` ou `process:` |
| `generated` | sim | `{ by: <ator>, at: <data com offset> }` |
| `tags` | não | lista livre |
| `relations` | não | ligações com outros concepts |
| `stale_after` | não | data em que o concept envelhece |

Mais três regras:

- Toda data leva o offset de fuso (`2026-10-20T09:40:00-03:00`).
- Link entre concepts é absoluto, a partir da raiz do bundle (`/products/exemplo/bets/BET-002/bet.md`).
- `verified: { by: human:<quem>, at: <data> }` marca o que um humano confirmou. Decisão sem `verified` ainda é proposta. Em decisão tomada por PR, ninguém escreve essa chave à mão: ela vem das aprovações do PR.

Exemplo real: a Idea que virou a BET-002 no produto exemplo:

```yaml
---
type: Idea
title: "Mostrar review parado no status da daily"
description: "O status da daily devia listar os PRs esperando review há mais de 24h, para a daily do time destravar review."
uid: idea-0001
owner: human:ana-exemplo
generated: { by: human:ana-exemplo, at: 2026-10-20T09:40:00-03:00 }
source: human
product: exemplo
verdict: segue
prototype_ref: "t0/status-bot@proto/IDEA-0001"
decided_at: 2026-10-20T09:40:00-03:00
state: promoted
verified: { by: human:ana-exemplo, at: 2026-10-20T09:40:00-03:00 }
---
```

E o slice da trilha rápida da BET-001 (a trilha para ajuste que cabe em 1 dia, sem spec), com "atual, esperado, o que não muda". O frontmatter guarda só as chaves que a máquina lê. Critério de aceite e verificação ficam em seções do corpo, que o `t0 gate spec` (um gate, o check de CI que confere uma decisão humana no PR) lê direto:

```markdown
---
type: Slice
bet: BET-001
repo: status-bot
tier: 1
depends_on: []
jira: EXE-11
pr: "t0/status-bot#14"
state: done
---

## Atual

O agendamento soma o offset do servidor. Quando o offset muda, o status sai às 07:50.

## Esperado

O agendamento usa `America/Sao_Paulo`, e o status sai às 08:50 o ano todo.

## Não muda

- o conteúdo e a ordem das seções da mensagem;
- o canal de destino.

## Critérios de aceite

- o status sai às 08:50 de Brasília antes e depois da mudança de offset;
- o horário vem da configuração, com o fuso `America/Sao_Paulo`.

## Como verificar

`pytest tests/test_agenda.py -k offset`. O teste ficou vermelho antes da correção e verde depois.
```

## As três raias de escrita

O KB tem três raias, ou caminhos de escrita. O princípio: o agente adiciona arquivos, o humano revisa o conhecimento e um bot escreve os derivados (os arquivos e as chaves que só o `kb-render` escreve). Em nenhuma raia mais de um escritor edita à mão o mesmo arquivo compartilhado.

| Raia | O quê | Como entra | Revisão |
|---|---|---|---|
| Registros | passos (`t0 log`), decisão em voo, bloqueio, handoff, eventos de PR, linhas do `.audit`, chaves Jira criadas | arquivo novo com nome único em `steps/`, gravado no spool local (`~/.t0/spool/`) e empurrado pelo `t0 kb push` | modo `batch`: um PR por dia, antes da daily do time, aprovado com um clique pelo Flow Steward (papel de rodízio de 2 semanas) |
| Conhecimento | ideia, bet, spec, slices, ADR, glossário, metodologia, rituais, transcrições redigidas, mudanças de `state` por gate | branch `bet/BET-NNN/<handle>` ou `kb/<handle>/<tema>` no clone do KB, e PR em draft | CODEOWNERS do caminho; transcrição sempre com humano confirmando a redação |
| Derivados | todo `index.md`, o `log.md` de cada bet, `changeset.md` e as chaves derivadas | só o workflow `kb-render`, serializado, no push para `main` | o check de PR e o hook local rejeitam edição humana ou de agente |

Registros nunca dão conflito porque o nome do arquivo é único por construção (`<utc-ts>-<handle>-<repo>-<rand4>.md`) e o PR só adiciona arquivos. Dez pessoas registram ao mesmo tempo sem disputar arquivo.

O modo `auto` da raia de registros (PR com auto-merge, sem aprovação) só liga quando a segurança confirmar que a proteção de branch do banco aceita esse modo. Até lá vale o `batch`.

Na raia de conhecimento, conflito git é possível e desejado: duas pessoas mudando o mesmo spec precisam conversar. Por isso cada bet tem um dono, os arquivos são pequenos (um ADR, um slice, um registro por arquivo) e o `kb-check` avisa quando um PR de conhecimento está aberto há mais de 48 horas e o alvo mudou.

Trecho real do `CODEOWNERS` do template:

```
/methodology/              @t0-org/t0-lead
/templates/                @t0-org/t0-harness-keeper
/team/rotations/           @t0-org/t0-flow-steward
/rituals/                  @t0-org/t0-flow-steward
/harness/                  @t0-org/t0-harness-keeper
/products/dev-tooling/     @t0-org/t0-dev-tooling

# Raia de registros e entrada de ideias: sem code owner.
/ideas/
/steps/
**/steps/
```

Cloud agent e CI não empurram para o KB, porque o token deles só lê. Em vez disso, eles põem os registros no corpo do PR de produto, e o workflow `t0-kb-sync` colhe esses registros para a raia de registros, sem `verified`. A única credencial que cruza repos é o GitHub App KB-writer, instalado só no `t0-kb`.

## Quem é dono de cada estado

Em cada tipo, cada chave de estado tem um dono só.

| Chave | Quem muda |
|---|---|
| `state` de Idea (depois de `new`), Bet, Spec, ADR, Policy, Rotation e `adoption_stage` do Product | só o PR de decisão. `t0 gate aposta` e `t0 gate spec` rodam os checks no CI, e aprovar o PR é a decisão. O ADR passa a `accepted` pelo `t0 adr accept`, num PR em draft para quem decide |
| `verified` de todo tipo com estado | só o `kb-render`, a partir do registro `pr-merged` que o `t0 ci` grava no merge com as aprovações do PR |
| `state` do Slice depois de `ready` (`building`, `in-review`, `done`, `blocked`), `pr`, `audit`, `jira`, `markers_open`, `status` | só o `kb-render`, a partir dos registros |
| `index.md`, `log.md`, `changeset.md` | só o `kb-render` |
| Na trilha rápida | o PR da aposta grava a Bet `active` e o único Slice `ready`; o último merge roda `t0 bet ship` |

Na prática: você escreve conteúdo, o gate escreve decisão e o `kb-render` escreve o resto. O hook do plugin bloqueia a edição de chave derivada antes de ela sair da sua máquina.

O `kb-render` gera o `log.md` de cada bet a partir dos registros em `steps/`. Trecho real da BET-002:

```
## 2026-10-21

* **Jira** por process:t0-sync: EXE-20, EXE-21 e EXE-22 criadas (registro)
* **Spec** por human:ana-exemplo: spec `approved` com dois slices e o ADR-0001 (registro)

## 2026-10-20

* **Aposta** por human:ana-exemplo: BET-002 `active`, trilha bet, apetite de 1 semana (bet)
```

## Como ler e navegar

- Comece pelo `index.md` da raiz. Ele leva às seções, e cada pasta tem o próprio índice.
- Para uma bet, abra `products/<pod>/bets/BET-NNN/`. Lá, o `bet.md` traz o intent, o `spec.md` traz critérios e desenho, `slices/` traz o trabalho e o `log.md` traz a história.
- Para a história do KB inteiro, abra o `log.md` da raiz.
- Na linha de comando, `t0 kb find --type Idea --text "review"` busca, e `t0 kb get IDEA-0001` lê um concept pelo id ou pelo caminho.
- Dentro de uma sessão de agente, o MCP `t0-kb` faz o mesmo com `kb_find`, `kb_get` e `kb_context`. Ver [Workspace](06-workspace.md).
- Para um termo desconhecido, `t0 kb find --type "Glossary Term" --text "<termo>"` traz o verbete, com `aliases` e `avoid`.

## Jira como espelho

O KB vem sempre primeiro. Depois do merge no KB, o CI chama `t0 jira sync`, que lê o KB, escreve no Jira e grava a chave de volta como registro. Se não há diff, rodar de novo não cria nada. Nenhuma skill fala com o Jira.

| Campo | Direção | Regra |
|---|---|---|
| Feature e Story (título, descrição, apetite, critérios em bullets, Tier, link para o KB, label `ready-for-agent`, link Blocks por `depends_on`) | KB → Jira | o Jira não é lugar de edição; uma edição feita lá é revertida no próximo sync, com comentário apontando para o PR no KB |
| Chave Jira (`jira:`) | Jira → KB | escrita uma vez, no create |
| Status da Story | duas vias, com fonte declarada | PR sai de draft = In Review; merge = Done. Transição humana no Jira (o RTE bloqueia, por exemplo) vira `state: blocked`. Transição que contradiz o fluxo (Done sem merge, Story andando antes do spec aprovado) é revertida com comentário |
| Comentários | duas vias, só acréscimo | comentário do ART entra no `log.md` como externo; resumo de merge e decisões vão para o Jira |
| Issue criada no Jira (bug de squad, pedido do ART) | Jira → KB | vira Idea `new` ou item da trilha rápida; daí em diante, mão única |
| Story points | KB → Jira | 1 fixo por slice, só se o ART exigir; nunca estimado |

O que o sync não resolve vira `state: conflict` e um item para o Flow Steward. Toda escrita do sync vai para o `log.md`, sem sobrescrita silenciosa. Um reconcile noturno (`t0 jira sync --reconcile`) gera o relatório de drift, e a meta é chegar à Demo com drift zero. A Feature só vai para "Done" quando todos os slices da bet tiverem sido mergeados.
