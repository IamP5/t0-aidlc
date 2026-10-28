---
type: Playbook
title: "AIDLC t0: metodologia, papéis e rituais"
description: Como o time de Inovação em IA decide, constrói, verifica e registra trabalho com agentes, com o KB em OKF como sistema de registro, o Jira como espelho e um pack tool-agnóstico (CLI t0 + skills) que roda igual no Copilot, no Claude Code e no Kiro.
uid: methodology-aidlc-t0
owner: role:lead
tags: [metodologia, aidlc, okf, rituais, papeis, gates]
status: draft
generated: { by: claude-code/opus-5.5, at: 2026-10-27T22:30:00-03:00 }
---

# AIDLC t0: metodologia, papéis e rituais

Rev 24 do living doc. Sai da síntese da arena A: a base é o candidato 2 (pack tool-agnóstico), com gates, rituais, privacidade, espelho Jira e salvaguardas de júnior enxertados do candidato 1. Fontes: living doc rev 23, os 25 deltas da pesquisa de metodologia, OKF v0.2 com o profile `t0-team` e o inventário do toolkit. Todo número de gate e todo piso de adoção está marcado como **proposta**: entra no profile com `state: proposed` e só vira `in-force` depois de 3 ferramentas passarem pelo funil.

**Em uma frase:** humano define a intenção e verifica, agente executa, e todo passo e toda decisão caem no KB por um comando do pack. O Jira é espelho gerado. O código mora nos repos de produto, que podem ser 5 ou 6 por produto.

Convenções deste documento:

- **KB** = o repositório OKF do time (`t0-kb`). Sistema de registro de tudo: método, rituais, bets, gates, decisões, ideias, transcrições. Código fica nos repos de produto; conhecimento fica no KB.
- **Pack** = o pacote `t0-method`: skills no padrão Agent Skills (`SKILL.md`), o `AGENTS.md` modelo, a CLI `t0` e os hooks de git e CI. No Claude Code se instala como plugin; no Copilot e no Kiro, como diretório de skills. Mesmo conteúdo, três pontos de descoberta.
- **Comando** = uma skill do pack, grafada `bet-shape`. Invoca-se pelo nome em qualquer das três ferramentas (`/bet-shape` onde há slash, ou "roda a skill bet-shape" em linguagem natural). O que precisa ser determinístico mora na CLI, grafada `t0 <subcomando>`; a skill só orquestra. Nenhum comando depende de recurso exclusivo de uma ferramenta.
- **Kiro** entra só como harness de agente de código. O recurso de specs do Kiro não é usado: os arquivos de bet no KB são o único sistema de spec.
- **Ciclo** = 2 semanas, alinhado à iteração do ART. Identificador `<C>`, por exemplo `2026-C22`.

---

## 1. Princípios

Dez regras. Elas decidem o que o processo não cobre. A coluna "mudou" diz o que é diferente do rev 23 e por quê.

| # | Princípio | O que diz | Mudou vs. draft? Por quê |
|---|---|---|---|
| P1 | **Humanos guiam, agentes executam** | O dev é dono da intenção, do critério de aceite e da verificação. Não é dono da digitação nem do Jira. | Mantido. |
| P2 | **O KB é o sistema de registro** | Spec, plano, slices, gate, decisão, ritual e ideia nascem no KB (OKF). Jira, dashboards e PRs são projeções. Se KB e Jira divergem, vale o KB, com as exceções de status da §5.5. | **Mudou.** Antes era "o repo é o sistema de registro". Com produto espalhado em 5 ou 6 repos, não existe "o" repo. O repo de produto guarda só o que é dele (§5.1). |
| P3 | **Profundidade proporcional** | O tipo de bet e o tier decidem quanto markdown existe. Bugfix não escreve spec, exploração não escreve plano, plataforma não pula contrato. | **Novo.** Substitui "spec antes de código" como regra universal (delta 12; crítica da Böckeler à sobrecarga de markdown). |
| P4 | **Lotes pequenos** | 1 slice = 1 PR revisável em ≤15 min. Bet que não cabe no apetite vira duas. | Mantido. |
| P5 | **Erro repetido do agente vira sensor, não prompt** | Na segunda ocorrência do mesmo erro, sobe a escada: lint/teste/hook de git/CI → regra de área → skill → `AGENTS.md` por último (§6.3). | **Mudou.** O draft dizia "todo erro → regra no CLAUDE.md", que é a receita das 8.500 instruções da Anthropic (delta 16). |
| P6 | **Atenção humana é o gargalo, e ela é medida** | WIP limitado por review pendente, não por tarefa aberta. PR e PR de gate esperando review têm prioridade sobre slice novo, com SLO de 4h úteis. | Ganhou SLO medível (§7). |
| P7 | **Visibilidade por telemetria** | Se alguém precisa perguntar o status, o que falta é automação, e uma reunião não resolve isso. Ritual síncrono só decide e alinha; nunca reporta. | Mantido. |
| P8 | **Passo e decisão registrados, ou não aconteceram** | Todo comando do ciclo e todo ritual grava no KB, e quem grava o registro é o pack, sem depender da boa vontade de ninguém. Gate é PR no KB; decisão vai para ADR (difícil de reverter) ou para o `log.md` da bet. | **Mudou de escopo.** Antes aceitava "thread no canal". Canal é efêmero e o agente não lê. Agora cobre todo passo, não só decisão. |
| P9 | **Contexto é orçamento; geral antes de específico** | Antes de criar skill de nicho, melhora o contexto geral. Link em vez de cópia. O KB entra no contexto por índice e busca, nunca despejado inteiro. O Sweeper desliga o que não pegou. | Funde "geral antes de específico" com engenharia de contexto. O KB vai estar em toda sessão; sem orçamento, apodrece o contexto. |
| P10 | **Ferramenta de agente só sai com eval** | Skill, MCP ou agente que o time entrega tem suíte de regressão antes do piloto, e incidente vira caso de eval antes da retro fechar. | **Novo** (deltas 8 e 18). O time vende ferramenta de IA; sem eval, não dá para saber se um upgrade de modelo quebrou alguma coisa. |

Dois princípios do draft saíram: "spec antes de código" (virou P3) e "repo como registro" (virou P2). Custo de token não virou princípio porque já é tratado como métrica (§7). A formação de quem supervisiona (debug sem delegar, explain-back) não virou princípio porque já tem regra própria e mensurável (§3.4).

---

## 2. Ciclo de vida

### 2.1 Fases, gates e o loop

```
 Ideia ──G0──> Intent ──G1──> Shape ──G2──> Slice ──G3──> Build ──G4──> Verify ──G5──> Ship ──G6──> bet encerrada
 (triagem)    (Betting)                                                                    │
                                                                                           └─> produto: degrau 1 ──G7──> degrau 2 ──G8──> degrau 3

 loop de harness (P5), em qualquer fase:
   erro de agente pela 2ª vez → Harness Item → sensor / regra de área / skill / AGENTS.md → PR fechado na Harness Retro
```

| Fase | Pergunta que responde | Quem está no volante | Artefato principal (tipo OKF) |
|---|---|---|---|
| **Ideia** (contínua) | Isso merece ir para o Betting? | Qualquer um escreve; Lead + AIVA triam | `ideas/IDEA-NNNN-slug.md` (Idea) |
| **Intent** | Qual problema, para quem, com que apetite, qual critério de kill, o que fica fora? | Bet Owner + agente; Lead aposta no Betting | `bet.md` (Bet; intent no corpo) ou `bugfix.md` (Bugfix) |
| **Shape** | O que vamos construir e como saberemos que ficou pronto? Em exploratória: qual das 3 a 5 versões sobrevive? | Pod inteiro (Mob Elaboration A) | `spec.md` (Spec) ou `assessment.md` (Assessment) |
| **Slice** | Em que fatias verticais isso vira PR, em que ordem, com que contrato? | Bet Owner + agente, pod assíncrono (Mob Elaboration B) | `plan.md` (Plan), `slices/NN-slug.md` (Slice), Contract em `products/` |
| **Build** | O slice está implementado com teste nas costuras combinadas? | Agente; dev supervisiona | PR em draft + `.audit/<KEY>.tsv` no repo de produto |
| **Verify** | Passou pelo agente de review, pelo CI e pelo humano do tier? | Revisores do tier (§6.2) | Slice `state: done` com `verified` |
| **Ship** | Saiu? O spec vivo do produto e o contrato estão atualizados? | Bet Owner + Grower | `bet.md` encerrada na Demo; Adoption Report aberto |
| **Degraus** (do produto, fora da bet) | Quem está usando? O degrau abriu? | Grower + AIVA + Eval Owner | Adoption Report (`passed`), Product com `adoption_stage` |

**Bolt.** Um bolt é um bloco planejado de 1 a 3 slices com **dono, DoD e hipótese de confiança** ("ao fim deste bolt, X funciona; risco Y"). Mora como seção do `plan.md`, sem arquivo próprio, para sobrar menos markdown para revisar. É a unidade que o Sync de bloqueios olha.

### 2.2 Gates: quem aprova, o que prova

**Como um gate funciona.** `gate <G> <alvo>` chama `t0 gate`, que abre um PR **no repo do KB**. O PR muda o `state` do artefato e acrescenta `verified: { by: human:<aprovador>, at: <data com offset> }`. A aprovação do PR é a aprovação do gate: não precisa de reunião. O merge gera um registro de passo (Step) e o workflow `kb-render` atualiza o `log.md` da bet e dispara `t0 jira sync`. O histórico git do KB é a trilha de auditoria que o banco vai pedir, sem `traceability.json` paralelo (a cadeia requisito → slice → PR → teste sai do frontmatter: `relations`, `jira`, `pr`; `t0 trace <BET>` gera o JSON para auditor sob demanda).

**SLO de gate = SLO de review:** primeira resposta humana em ≤4h úteis. PR de gate acima do SLO aparece no digest e vira item do Sync de bloqueios. G4 e G5 são exceção ao "PR no KB": quem escreve é o CI, porque a prova está no PR de código.

| Gate | Entre | Quem aprova | Artefato que prova (`state` + `verified`) | Comando |
|---|---|---|---|---|
| **G0 Ideia triada** | inbox → pilha do Betting | Lead + AIVA, na triagem assíncrona semanal | Idea com `state: triaged` e `verified: human:<lead\|aiva>`. Ideia extraída de transcrição entra sem `verified` e só passa daqui confirmada | `idea-triage` → `t0 gate G0` |
| **G1 Bet apostada** | Intent → Shape | Lead, no Betting, ouvindo o pod. **Bugfix:** o Flow Steward aprova fora do Betting, a qualquer momento | Bet com `state: active`, `appetite`, `cycle_end` e `verified: human:<lead>` (bugfix: `bugfix.md` `approved` + `verified: human:<flow-steward>`) | `ritual betting close` → `t0 gate G1`; bugfix: `gate G1 <BET>` |
| **G2 Spec aprovado** | Shape → Slice | Bet Owner + Domain Expert (quando a bet toca uma squad). Tier 2: também o Lead. Bet Owner júnior: preceptor co-aprova | Spec com `state: approved`, `markers_open: 0` (nenhum `[PRECISA ESCLARECER]`), critérios de aceite em bullets, "como verificar", `verified` com cada aprovador | `gate G2 <BET>`; `t0 gate` recusa com marcador aberto |
| **G3 Pronto para construir** | Slice → Build | Bet Owner; pod tem 24h no PR. Contrato que cruza pods: Mob Construction + Lead | Plan `approved` com os 4 checks (`pass` ou exceção escrita) e bolts; Contract `approved` se há superfície pública; cada Slice `ready` com chave Jira gravada | `bet-plan` → `bet-slice` → `gate G3 <BET>` |
| **G4 Pronto para review** | Build → Verify | Automático: CI verde + agente de review sem pendência | Slice `state: in-review`, `verified: process:ci`; PR sai de draft; Story em In Review | CI roda `t0 gate G4 <KEY>` depois de `slice-verify` |
| **G5 Merge (DoD)** | Verify → mergeado | Revisores conforme o tier (§6.2) | Slice `state: done`, `verified: [human:<revisor>, …]` copiado das aprovações do PR, `.audit/<KEY>.tsv` no PR; Story em Done. Bugfix: o G5 também fecha a bet (`state: shipped`) | CI roda `t0 gate G5 <KEY>` no merge |
| **G6 Bet encerrada** | Ship → fim | Bet Owner + Lead, na Demo | Bet com `state: shipped\|killed\|extended`, aprendizado no corpo, `verified: [human:<bet-owner>, human:<lead>]`; Ritual Record da Demo cita a bet | `ritual demo close` → `t0 gate G6` |
| **G7 Degrau 1 → 2** | time → 2 ou 3 squads piloto | AIVA + Eval Owner | Adoption Report `passed` contra os pisos da §6.5; Eval Suite de regressão ≥95%; Product `adoption_stage: 2` + `verified` | `adoption-report <produto>` → `gate G7 <produto>` |
| **G8 Degrau 2 → 3** | piloto → ART | AIVA + Lead + Eval Owner; vira outcome do PI | Adoption Report `passed`; `pass^3` dentro da meta do Eval Owner; Product `adoption_stage: 3` + `verified` | `gate G8 <produto>` |

Toda aprovação humana vira também uma linha no `log.md` da bet: data, quem (`human:<handle>`), o quê, link do PR.

### 2.3 Tipos de bet e o que cada um pula

Quatro tipos. O tipo entra no `bet.md` como `bet_type`, decide o caminho, e o pack usa isso para saber quais comandos oferecer.

| | **Exploratória** | **Entrega** | **Bugfix** | **Plataforma** |
|---|---|---|---|---|
| Para quê | Descobrir se a ideia vale | Valor novo num produto, sem mexer em superfície pública | Corrigir comportamento errado | Criar ou mudar superfície pública (MCP, CLI, skill, API), infra, migração, upgrade de modelo |
| Apetite | ≤1 semana | 1 a 2 semanas | ≤2 dias | 1 a 2 semanas (estende 1 vez) |
| Ideia / G0 | sim | sim | **pula**: entra por intake do Jira, incidente ou `bet-new bugfix` direto | sim |
| Intent / G1 | `bet.md` curto: hipótese + critério de kill | `bet.md` completo | `bugfix.md` (atual, esperado e **o que não muda**); G1 pelo Flow Steward | `bet.md` + NFRs + o que **não** pode mudar |
| Shape / G2 | 3 a 5 protótipos de ~30 min + `assessment.md` (go / needs-clarification / kill); **sem G2** | Mob A → `spec.md`; G2 | **pula** | Mob A → `spec.md` focado em contrato e NFR; primeiros casos de eval escritos aqui; G2 com Lead (Tier 2) |
| Slice / G3 | **pula** | `plan.md` + slices; G3 | **pula**: o `bet-new bugfix` cria o slice único com chave Jira | `plan.md` + Contract obrigatório + slices; Mob Construction se cruza pods; G3 |
| Build / G4 | protótipo descartável, fora do repo de produto, nunca no main | normal; G4 | teste de regressão vermelho primeiro; G4 | normal; `slice-build --parallel` só com contrato aprovado; G4 |
| Verify / G5 | **pula** | tier por risco; G5 | tier por risco (Tier 0 se só teste + fix local); G5 fecha a bet | **Tier 2 por padrão**; contract tests + eval de regressão + blast-radius; G5 |
| Ship / G6 | Assessment apresentado na Demo; G6 | `bet-ship`; G6 | merge = ship; sem G6 (a Demo só lista) | `bet-ship` + não-regressão de eval; G6 |
| Degraus G7/G8 | não | quando a bet leva o produto a degrau novo | não | quando cria produto ou superfície nova; migração, refactor e upgrade de modelo trocam G7/G8 por não-regressão de eval + migração dos consumidores, checadas no G6 |
| Eval | não | se é ferramenta de agente | caso de eval se foi incidente | sempre |
| **Gates** | **G0, G1, G6** | **G0 a G6, mais G7/G8 do produto** | **G1, G4, G5** | **G0 a G6, mais G7/G8 se superfície nova** |

**Sobreposição Tier 2** (não é tipo): qualquer bet que toque auth, dados de cliente, permissões de agente ou contrato público ganha review de 2 humanos, Lead no G2 e cadeia de rastreabilidade completa (spec → slice → Jira → PR → teste citado em `verify_how`); o `kb-check` bloqueia Slice Tier 2 `done` sem ela. Substitui o perfil "Regulated" da pesquisa.

Regras de transição:

- Exploratória fecha no G6 pelo veredito: `go` → `state: shipped` e nasce uma Bet de entrega `proposed` com `relations.derived_from`; `kill` → `state: killed` com o aprendizado; `needs-clarification` → `state: extended`, uma vez só. O protótipo fica anexado ao spec e nunca vira base de código.
- Bugfix que descobre que precisa de design vira bet de entrega. O agente abre o `bet.md` novo e para.
- Entrega que vai expor MCP, CLI ou skill às squads **é** plataforma, mesmo pequena. O critério é a superfície pública; o tamanho não entra na conta.
- Bet morta (kill) conta como resultado da bet. O Sweeper usa o registro de bets mortas para a mesma ideia não voltar sem fato novo.

---

## 3. Papéis em dois eixos

Os dois eixos são independentes:

- **Arquétipo** = modo de trabalho da quinzena. Responde "como estou trabalhando agora". Muda com o estágio do produto. Ninguém "é" Prototyper; alguém "está" Prototyper nesta bet.
- **Accountability** = quem responde se der errado. Tem nome, prazo e um concept `Accountability` no KB.

A mesma pessoa pode estar como Sweeper e ser Bet Owner de uma bet de plataforma.

### 3.1 Arquétipos (eixo 1)

Os cinco do Boris Cherny, adaptados. A maioria das pessoas cobre 2 ou 3.

| Arquétipo | O que faz aqui | Sinal de que falta |
|---|---|---|
| **Prototyper** | 3 a 5 versões de ~30 min por ideia; mata a maioria; escreve o `assessment.md` | Bet entra em build sem alternativa testada |
| **Builder** | Leva o protótipo sobrevivente a produção: testes, permissões, telemetria, contrato | Protótipo bom que nunca sai do time |
| **Grower** | Acompanha uso nas squads piloto, fala com usuário, itera toda semana até o degrau abrir | Ferramenta que ninguém usa duas vezes |
| **Sweeper** | Desliga o que está abaixo do piso, poda `AGENTS.md` e regras, cuida do jardim do KB (`stale_after` vencido, drift do Jira), reporta o orçamento de contexto | Catálogo cresce mais rápido que o uso; `AGENTS.md` passa de 150 linhas |
| **Maintainer** | Mantém rápido e confiável o que as squads já usam; dono da suíte de regressão | Incidente e chamado repetidos |

**Cobertura por pod, conforme o estágio do produto (obrigatória):**

| Pod / produto | Estágio hoje | Mistura mínima no ciclo |
|---|---|---|
| Dev Tooling | crescimento | Builder + Sweeper + Grower |
| Insights & Enablement | crescimento | Builder + Sweeper + Grower |
| Agent Platform | indo para maduro | Maintainer + Sweeper + Grower |
| Qualquer bet exploratória | pré-PMF | Prototyper + Builder + Sweeper |

No Betting, cada pessoa declara 1 arquétipo principal e até 1 secundário, gravados no Cycle Record. O `ritual betting close` checa se cada pod cobre a mistura do estágio e avisa se não cobrir. Com 3 pessoas por pod, uma pessoa cobre dois arquétipos: é o esperado.

### 3.2 Accountabilities (eixo 2)

| Accountability | Responde por | Quem / duração | Registro no KB |
|---|---|---|---|
| **Lead** | Escolhe bets (G1), arquitetura transversal, interface com o ART, orçamento de modelo, G6, mudança na metodologia (via ADR) | Tech lead do time; fixo | `team/accountabilities/lead.md` |
| **AI Value Architect (AIVA)** | Adoção nas squads, valor realizado, lacunas de eval, triagem de ideias (G0) com o Lead, G7/G8, representa o time no Sense & Respond e no PI Outcome Planning | 1 pessoa do pod Insights & Enablement, por PI. **Não é o Lead** (delta 1): o SAFe define AIVA como coaching de adoção | `team/accountabilities/aiva.md` |
| **Bet Owner** | Resultado de uma bet; conduz a Mob A; aprova G2 e G3; é a capability **Product** do pod na bet (dono do "porquê", sintetiza feedback das squads) | Qualquer dev do pod, pela bet; rotativo (elegibilidade de júnior na §3.4) | `bet.md: decision_by` |
| **Flow Steward** | Fila de review e de gates, relatório de drift do Jira, pauta da Demo, facilita o Sync de bloqueios, aprova G1 de bugfix | Rotativo por ciclo entre todos menos o Lead | `team/rotations/flow-steward.md` |
| **Sweeper de plantão** | O arquétipo Sweeper sempre tem um nome: facilita Harness Retro e Dia de limpeza, reporta orçamento de contexto e pisos de sunset | Rotativo por ciclo | `team/rotations/sweeper.md` |
| **Eval Owner** | Suítes de regressão e capacidade de um produto; nenhum degrau sobe e nenhum upgrade de modelo entra sem a suíte passar | Um por produto que as squads usam; normalmente o Maintainer ou o Grower; por PI | `products/<p>/product.md: eval_owner` |
| **Plantão** | On-call do produto em uso pelas squads | Rotativo semanal entre quem conhece o produto; júnior só em dupla com o preceptor | `team/rotations/plantao-<p>.md` |
| **Preceptor** | Formação de até 3 juniores: 1:1, revisão do explain-back, regra de debug | Sênior nomeado; ≥2 ciclos, normalmente por semestre | `team/rotations/preceptor.md` |
| **Domain Expert de contato** | Transformar proposta genérica em proposta que serve; consultado no Shape (G2) e no Ship | 1 tech lead de squad piloto por produto, por PI; não é do time | `products/<p>/product.md: domain_contacts` |

### 3.3 Regras de rotação

- **Flow Steward** e **Sweeper de plantão** giram a cada ciclo. Ninguém repete Flow Steward em ciclos seguidos, e ninguém segura os dois ao mesmo tempo. O Lead fica fora do rodízio.
- **Bet Owner** gira por bet dentro do pod. Em 90 dias, todo mundo do pod foi Bet Owner pelo menos uma vez.
- **Lead, AIVA, Eval Owner** não giram por ciclo. Eval Owner muda quando o produto muda de estágio.
- **Em 90 dias, todo mundo passou por Builder e por Sweeper** pelo menos uma vez. É a mitigação de atrofia mais barata: quem só revisa esquece como se constrói.
- Toda Rotation tem `stale_after` igual ao fim da atribuição corrente. Rodízio vencido aparece no digest e no `kb-check` L2. `rotate` grava a troca; o `ritual betting close` chama `rotate` para Flow Steward e Sweeper.

### 3.4 Salvaguardas para juniores

Na pesquisa (RCT da Anthropic, jan/2026: 50% vs. 67%, maior perda em debugging), delegação total e "debug iterativo com IA" destroem o aprendizado, e "gerar e depois compreender" o preserva. Por isso:

- Preceptor nomeado, ≤3 juniores por sênior, dentro do pod. *Proposta:* a razão 3:1 é nossa; a fonte citada na pesquisa não foi verificada. O preceptor faz o review humano dos PRs Tier 1 e 2 do júnior nos 2 primeiros ciclos.
- Júnior nunca é aprovador único de Tier 1 ou acima. Pode ser segundo revisor.
- Júnior pode ser Bet Owner de bugfix e de plataforma Tier 0/1 desde o 1º ciclo, e de entrega a partir do 3º ciclo, com o preceptor co-aprovando o G2.
- O explain-back é obrigatório: todo PR Tier 1 ou 2 de júnior leva uma seção "Em minhas palavras" (o que o PR faz e por quê, sem colar a explicação do agente). Em Tier 2, vale para todo mundo.
- O primeiro debug é da pessoa: em bug atribuído a júnior, o agente explica e instrumenta, e quem escreve o fix é a pessoa (`diagnose --tutor`).
- Um slice por ciclo roda em modo tutor, com perguntas conceituais liberadas e geração de código bloqueada. É escolhido no Betting e registrado no slice como `mode: tutor`. Opcional para sênior.
- Júnior faz plantão em dupla com o preceptor.
- A preceptoria 1:1 não é transcrita (§4.4). Mede-se participação nessas práticas, nunca nota, e os dados individuais só o preceptor e a própria pessoa veem (§7).

### 3.5 Anti-"arquétipo vira cargo"

- Arquétipo **não existe** no Jira, no RH nem na avaliação de desempenho. Mora só no Cycle Record do KB e vale por 2 semanas.
- Ninguém declara o mesmo arquétipo principal por mais de **3 ciclos seguidos**. A 4ª declaração seguida é **bloqueada** pelo `ritual betting close`; só passa com justificativa registrada no Cycle Record. Exceção prevista: Maintainer em produto maduro, e mesmo aí o plantão gira.
- Título continua dizendo especialidade (front, plataforma, dados), nunca arquétipo.
- A pergunta do Betting é "o que este produto precisa agora?", nunca "o que você é?".
- Accountability tem nome e prazo. Arquétipo tem só prazo.

---

## 4. Rituais

### 4.1 Padrão de todo ritual

Todo ritual segue Align / Sense / Respond do AI-Native SAFe, é um concept `Ritual` em `methodology/rituals/<slug>.md` e é aberto e fechado pelo mesmo comando:

- `ritual <slug> open` chama `t0 ritual <slug> open`, que lê as `inputs` declaradas no concept e monta a pauta.
- `ritual <slug> close` grava o Ritual Record em `cycles/<C>/rituals/<data>-<slug>.md` (decisões, donos, prazos, links), roda `meeting-record` quando o ritual é gravado (§4.4) e abre os PRs de gate que o ritual decidiu.

Ritual sem Ritual Record não aconteceu (P8). Nenhum ritual serve para reportar status; quem faz isso é o digest.

### 4.2 Tabela de rituais

| Ritual | Propósito | Cadência | Duração | Facilitador | Participantes | Entradas (KB lido, tipo) | Saídas (KB escrito, tipo) | Comando | Cancelamento |
|---|---|---|---|---|---|---|---|---|---|
| **Digest diário** (Sense, assíncrono) | Status sem ninguém perguntar: merges, review >24h, PR de gate acima do SLO, bolt atrasado, drift do Jira, `stale_after` vencido | Todo dia útil, 9h | 0 min (bot) | `process:t0-digest` | O canal lê | Bet, Slice, Rotation, PRs de gate abertos, `.audit/`, Git/CI/Jira, relatório de drift | Metric Snapshot `cycles/<C>/digests/AAAA-MM-DD.md`; post no canal com link | `digest` (CI agendado roda `t0 digest`) | Não cancela. Falhou = bug Tier 1 do pod Insights |
| **Sync de bloqueios** (Respond) | Destravar, distribuir review, bolt em risco | Ter e qui | 15 min | Flow Steward | Time; quem não tem bloqueio nem review pendente pode faltar | Digest do dia, `t0 review-queue` | Ritual Record (≤10 linhas: bloqueio → dono → prazo); bloqueio que vira decisão vai para o `log.md` da bet | `ritual bloqueios open\|close` | Cancela sozinho se o digest não tem PR acima do SLO, bloqueio aberto nem bolt vencido; o bot avisa às 9h05 |
| **Triagem de ideias** (Align, assíncrono) | Inbox curta e decidida (G0) | Semanal | 0 min síncrono | AIVA | AIVA + Lead | Idea `new` (inclusive extraídas de transcrição e intake do Jira) | Idea `triaged` com `verified` (G0) ou `parked\|rejected` com motivo de uma linha; Ritual Record | `idea-triage` | Não cancela; inbox vazia dá record de uma linha |
| **Betting** (Align) | Apostar bets com apetite (G1), declarar arquétipos, girar rodízios, escolher slices em modo tutor. O resto volta para a pilha | Dia 1 do ciclo | 45 min | Lead (AIVA, se o Lead falta) | Time todo; AIVA traz adoção | Idea `triaged`, Bet `proposed\|extended` (intent no corpo), Assessment, Adoption Report, Cycle Record e report do ciclo anterior, Rotation | Cycle Record novo; Bet `active` + `verified` (G1); Rotation; Idea `parked` com motivo; Ritual Record; Transcript | `ritual betting open\|close` | Não cancela. Sem ideia triada, vira 15 min só de rodízio |
| **Mob Elaboration A** (Align) | Intent → spec aprovado (G2); em exploratória, escolher o protótipo sobrevivente | Por bet de entrega ou plataforma (~2 por pod por ciclo) | 45 min (teto 60) | Bet Owner | Pod + Domain Expert + agente ao vivo projetado; + Lead se Tier 2 | Bet, Spec vivo do Product, Glossary Term, ADR, Contract, Assessment | Spec `approved` (G2), Glossary Term, ADR, linha no `log.md`, Ritual Record, Transcript | `ritual mob-a <BET> open\|close` (roda `bet-shape` e `bet-spec` ao vivo) | Cancela se o `bet-shape` assíncrono zerou os marcadores e o PR do G2 foi aprovado em 24h; o record diz "aprovado assíncrono" |
| **Mob Elaboration B** (Align, assíncrona por padrão) | Aprovar plano, bolts, contrato e quebra em slices (G3) | Por bet, logo depois do G2 | 0 min; 30 min síncrona só se sobrou marcador ou alguém pediu no PR do G3 | Bet Owner | Pod | Spec `approved`, Contract, Plan rascunho | Plan `approved`, Slice `ready` com chave Jira, Contract `approved` (G3); Ritual Record só se síncrona | `bet-plan` → `bet-slice` → `gate G3`; síncrona: `ritual mob-b <BET> open\|close` | Assíncrona é o padrão. Se as Mob A do ciclo já somaram mais de 90 min para a pessoa, fica assíncrona |
| **Mob Construction** (Align) | Fechar contrato que cruza pods antes do build paralelo | Só com contrato cruzando pods | 30 min (ocupa o lugar da Mob B síncrona daquela bet) | Lead | Bet Owners dos pods envolvidos + Lead | Contract, Plan | Contract `approved` (parte do G3), ADR, Ritual Record, Transcript | `ritual mob-construction <BET> open\|close` | Não roda sem contrato cruzado |
| **Demo** (Sense) | Mostrar funcionando ao vivo + números; encerrar bets (G6). Vira insumo do Sense & Respond | Último dia do ciclo | 45 min | Flow Steward | Time + squads piloto convidadas (opcional) | Bet `active`, Assessment, Adoption Report, digests do ciclo | Metric Snapshot `cycles/<C>/report.md`; Bet com estado final + `verified` (G6); Ritual Record; Transcript | `ritual demo open\|close` (o close chama `metrics-snapshot`) | Não cancela. Sem bet fechando, 15 min só de painel |
| **Harness Retro** (Respond) | Erro repetido → sensor (P5); incidente → caso de eval; relatório do Sweeper | Último dia, logo depois da Demo | 30 min | Sweeper de plantão | Time | Harness Item `open`, `.audit/` do ciclo, comentários de review, incidentes, `harness/budget.md` | Harness Item com `ladder_step` e `pr`; casos de eval; Ritual Record; Transcript | `ritual harness-retro open\|close` → `harness-fix <HI>`, `eval-add` | Não cancela; sem item, 10 min (é dado bom). **O close falha sem PR aberto para cada item aceito** |
| **Preceptoria 1:1** | Desenvolvimento do júnior | Semanal | 30 min | Preceptor | Preceptor + júnior | Explain-backs e slices em modo tutor do júnior | Ritual Record mínimo (só as ações combinadas); **nunca** Transcript | `ritual preceptoria open\|close` | Pode remarcar; não pula 2 seguidas |
| **Dia de limpeza** (Respond; dia de trabalho, sem reunião) | Dívida técnica, jardinagem de docs e do KB, sunset | Dia 2 do ciclo | Dia de trabalho focado; fora do orçamento síncrono | Sweeper de plantão | Time | `tech-debt.md` dos repos, `kb-check` L2, relatório de sunset, Harness Item | PRs; Product `sunset`; Harness Item; Ritual Record curto | `ritual limpeza open\|close` (o open roda `sweep`) | Quando o `sweep` voltar vazio 2 ciclos seguidos, cai para meio dia. A meta é o ritual deixar de ser necessário |
| **Sense & Respond do ART** (externo) | Interface com o ART; substitui System Demo e I&A | 1× por iteração | 2h | RTE | Lead + AIVA | Report do ciclo, Adoption Report, Ritual Record da Demo, PI Outcome | Ritual Record (decisões do ART que afetam o time); ADR ou Idea nova; Transcript se o ART permitir | `ritual sense-respond open\|close` (o open monta o pacote de entrada) | Do ART |
| **PI Outcome Planning** (externo) | Compromisso com outcomes do PI | 1× por PI | 1 dia | RTE | Lead + AIVA + Bet Owners do próximo ciclo | Product (degraus), Adoption Report, reports dos ciclos, Idea `triaged`, Bet `proposed` | PI Outcome `pi/<PI>/outcomes.md`; Ritual Record | `ritual pi-outcome open\|close` | Do ART |

### 4.3 Orçamento síncrono por pessoa a cada 2 semanas

A conta usa a duração agendada de cada ritual. "Típico" supõe metade dos Syncs de bloqueios cancelada e Mob B assíncrona; "teto" supõe nada cancelado.

| Perfil | Conta | Típico | Teto |
|---|---|---|---|
| **Dev** | Betting 45 + Mob A 2×45 (90) + Mob B 0 a 30 + Bloqueios 30 a 60 (4×15) + Demo 45 + Retro 30 | **240 min (4h)** | **300 min (5h)** |
| Júnior | Dev + Preceptoria 2×30 (60) | 300 min (5h) | 360 min (6h) |
| Preceptor | Dev + 60 por júnior (até 3) | 360 min (6h), com 2 juniores | 480 min (8h), com 3 juniores |
| AIVA | Dev + Sense & Respond 120 (a triagem é assíncrona) | 360 min (6h) | 420 min (7h) |
| Lead (fora dos pods) | Betting 45 + Bloqueios 30 a 60 + Demo 45 + Retro 30 + Sense & Respond 120 + Mob A das Tier 2 45 a 90 + Mob Construction 0 a 30 | 315 min (5h15) | 420 min (7h) |

Conferência do Dev: típico 45 + 90 + 0 + 30 + 45 + 30 = 240; teto 45 + 90 + 30 + 60 + 45 + 30 = 300. Duas regras seguram o teto quando a Mob A estoura até 60 min: Mob A acima de 90 min somados no ciclo deixa a Mob B assíncrona (2×60 + 0 = 90 + 30), e a Mob Construction ocupa o lugar da Mob B síncrona em vez de somar a ela. O PI Outcome Planning (1 dia por PI) e o Dia de limpeza (que é trabalho, e não reunião) ficam fora da conta.

O draft dizia ~3h. Com tudo somado, a conta dá ~4h típico e 5h teto para o dev. A diferença é a Mob A por bet, que o draft contava por baixo. O relatório da Anthropic mostrou tempo de reunião subindo 20% em times AI-native; alinhamento curto e bom é onde o humano rende mais, então o orçamento se justifica. Para compensar, Mob B, triagem e todos os gates são assíncronos, e o Sync de bloqueios cancela por regra. Não há reunião de status.

### 4.4 Transcrição e privacidade

- Gravam-se Betting, Mob A, Mob Construction, Demo e Harness Retro, com aviso no começo. Sense & Respond só se o ART permitir. O Sync de bloqueios não é gravado, porque o record basta.
- Qualquer pessoa pode pedir "fora do registro" para um trecho, e o trecho sai da transcrição. O Transcript guarda só a contagem (`off_record_spans`).
- Preceptoria, 1:1 e conversa de desempenho nunca são gravadas. Nesses casos o registro é só a ação combinada.
- A redação determinística vem antes do agente: `meeting-record` chama `t0 transcript redact`, que roda o scanner de segredo e as regex de CPF, conta, e-mail e telefone **antes** de qualquer modelo ver o texto. Depois, o agente faz uma passada para dado de cliente. O Transcript fica sem `verified` até o facilitador confirmar.
- Retenção: Transcript tem `stale_after` de 180 dias (**PROPOSTA**, pendente de validação com jurídico/LGPD). Vencido o prazo, o Sweeper apaga a transcrição e mantém o Ritual Record, que guarda as decisões para sempre.
- Ideias e decisões candidatas que o agente extrai da transcrição entram como Idea `new` ou ADR `proposed` **sem `verified`**. Só valem depois de confirmadas por um humano (Idea no G0; ADR no PR do KB).
- No rollout, os dias 0 a 30 rodam em **dry-run** (redige, mas não persiste) até o aval de privacidade/LGPD (§9).

---

## 5. Artefatos: o KB e o espelho Jira

### 5.1 Onde mora o quê

| Lugar | Conteúdo | Por quê |
|---|---|---|
| **KB** (`t0-kb`, bundle OKF v0.2, profile `t0-team`) | Metodologia, rituais, time, ideias, produtos (spec vivo, contratos, ADRs, adoção, índice de evals), bets (intent, spec, plan, slices, assessment, bugfix, log), ciclos (records, transcrições, digests), harness | Sistema de registro (P2) |
| **Repos de produto** (N por produto) | Código, testes, código dos evals (`evals/`), `.audit/<KEY>.tsv` no PR, `tech-debt.md`, `AGENTS.md` (≤150 linhas, canônico; `CLAUDE.md`, `.github/copilot-instructions.md` e `.kiro/steering/` só apontam para ele), regras de área geradas, skill `verify-<app>` | A prova fica perto do código |
| **Jira** | Feature (bet) e Story (slice) espelhadas, status do workflow, comentários do ART | Governança e rastreabilidade do PI |
| **Painel** | Métricas geradas (§7) | Visibilidade sem cerimônia |

A regra: **se o agente precisa disso para editar código, mora no repo; se precisa para decidir o que fazer, mora no KB.** É proibido colar conteúdo do KB em repo de código: linka-se por `uid`. A única cópia permitida é o arquivo de contract test, gerado a partir do Contract com o `uid` no cabeçalho.

### 5.2 KB como contexto em toda interação

O mecanismo que deixa o KB alcançável e carregado em toda sessão (rituais, spec e código, inclusive em produto com 5 ou 6 repos) é definido pelo workspace pattern: ADR-0002 e `methodology/workspace-pattern.md`. Esta metodologia só assume que o KB é alcançável de toda sessão nas três ferramentas, e que todo ritual aberto por `ritual <slug> open` carrega as entradas declaradas no seu concept `Ritual`.

**Workspace pattern em 20 linhas** (detalhe em `methodology/workspace-pattern.md`, ADR-0002):

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

### 5.3 Layout do KB

```
t0-kb/
  index.md                          # okf_version: "0.2", nada mais
  profile.md                        # OKF Profile (t0-team 0.1)
  log.md                            # Log do bundle: só eventos de time (ritual, política, rotação)
  glossary/<termo>.md               # Glossary Term, bilíngue
  methodology/
    methodology.md                  # este documento (Playbook)
    workspace-pattern.md            # Playbook do workspace (ADR-0002)
    principles/P01-*.md             # Principle
    practices/*.md                  # Practice (DoR, DoD, escada do harness, tiers)
    policies/*.md                   # Policy (pisos de adoção, eval gate, retenção de transcrição)
    playbooks/<skill>.md            # Playbook, um por comando do pack
    rituals/<slug>.md               # Ritual
    adr/ADR-NNNN-slug.md            # ADR de método
  team/
    people/<handle>.md              # Person (só handle de trabalho)
    roles/<arquetipo>.md            # Role Archetype (os 5)
    accountabilities/<slug>.md      # Accountability
    rotations/<slug>.md             # Rotation (flow-steward, sweeper, preceptor, plantao-<p>)
  ideas/IDEA-NNNN-slug.md           # Idea (inbox do Betting)
  cycles/<C>/
    cycle.md                        # Cycle Record (bets, arquétipos declarados, rotações)
    report.md                       # Metric Snapshot do ciclo
    digests/AAAA-MM-DD.md           # Metric Snapshot diário
    rituals/<data>-<slug>.md        # Ritual Record
    transcripts/<data>-<slug>.md    # Transcript (redigida, stale_after 180d)
  products/<p>/
    product.md                      # Product (stage, adoption_stage, eval_owner, domain_contacts, repos)
    spec.md                         # Spec vivo do produto (spec-anchored)
    contracts/<superficie>.md       # Contract
    adr/ADR-NNNN-slug.md            # ADR do produto
    evals.md                        # Eval Suite (aponta para evals/ no repo, guarda o último resultado)
    adoption/AAAA-Www.md            # Adoption Report
    bets/BET-NNN/
      bet.md                        # Bet; o intent mora no corpo
      bugfix.md                     # Bugfix (só em bet bugfix)
      assessment.md                 # Assessment (só exploratória)
      spec.md                       # Spec da bet (spec-first; congela no ship)
      plan.md                       # Plan (bolts + 4 checks)
      slices/NN-slug.md             # Slice, um por arquivo
      log.md                        # Log: todo passo e decisão da bet
  pi/<PI>/outcomes.md               # PI Outcome
  harness/
    HI-NNNN.md                      # Harness Item, um por erro recorrente
    trust.md                        # Metric Snapshot da graduação por área; escrito só por process:ci
    budget.md                       # Metric Snapshot: linhas de AGENTS.md, hooks, regras por repo
  research/                         # Research | Reference (congelado)
```

Harness Item é um arquivo por erro recorrente, e não um contador único, para que 10 pessoas não editem o mesmo arquivo. O `harness/trust.md` só é escrito pelo CI (`generated.by: process:ci`); ninguém edita à mão.

### 5.4 Tipos OKF que o método produz e consome

Todos usam as chaves comuns do profile: `type`, `title`, `description`, `tags`, `uid`, `owner`, `generated`, `verified`, `status` (derivado de `state`), `stale_after` quando o tipo envelhece, e `relations`. A tabela lista só o que é específico.

| Tipo | Chaves específicas | `state` | Quem escreve | Quem lê |
|---|---|---|---|---|
| **Idea** | `source` (human / squad / transcript / jira), `product?`, `bet?` | new → triaged → parked \| rejected \| promoted | `idea-capture`; `meeting-record` (sem `verified`); intake do `bet-sync`; `idea-triage` (G0) | `ritual betting`, `bet-new` |
| **Bet** | `bet_type`, `appetite`, `hypothesis`, `kill_criteria`, `success_metric`, `cycle_start/end`, `decision_by`, `jira` (Feature), `tier_default`; corpo: problema, para quem, fora de escopo | proposed → active → shipped \| killed \| extended | `bet-new`, `gate G1`, `bet-ship`, `gate G6` | tudo |
| **Bugfix** | `current`, `expected`, `unchanged[]` | draft → approved | `bet-new bugfix`, `gate G1` | `slice-build`, `slice-verify` |
| **Assessment** | `prototypes[] {path, verdict}`, `verdict: go \| needs-clarification \| kill`, `kill_reason?` | sem `state` | `bet-shape --explore` | `ritual betting`, `sweep` |
| **Spec** | `bet?` (ausente no spec vivo do produto), `acceptance[]` (bullets), `verify_how`, `markers_open` (0 para aprovar), `seams[]`, `tier` | bet: draft → approved → frozen; produto: approved → superseded | `bet-spec`, `gate G2`, `bet-ship` (spec vivo) | `bet-plan`, `slice-verify` |
| **Plan** | `bolts[] {id, owner, dod, confidence, slices}`, `checks {simplicity, anti_abstraction, contract, test_first}`, cada um `pass \| exception:<motivo>` | draft → approved | `bet-plan`, `gate G3` | `bet-slice`, Sync de bloqueios |
| **Contract** | `surface: mcp \| cli \| skill \| api`, `version`, `consumers[]`, `breaking_requires: tier-2` | proposed → approved → published → deprecated | `bet-spec`, `bet-plan`, `gate G3`, `bet-ship` | `slice-verify`, squads |
| **Slice** | `bet`, `bolt`, `repo`, `tier: 0\|1\|2`, `acceptance[]`, `verify_how`, `depends_on[]`, `jira` (Story), `pr`, `audit`, `mode?: tutor`, `blocked_by?` | ready → building → in-review → done \| blocked \| conflict | `bet-slice`, `bet-new bugfix`, `bet-sync`, `slice-build`, CI (`gate G4`, `gate G5`) | `slice-build`, `slice-verify`, `digest` |
| **ADR** | `number`, `deciders[]`, `decided_at` | proposed → accepted → superseded \| rejected | `adr-new`, `bet-shape`, `harness-fix`, `meeting-record` (sem `verified`) | agentes em toda sessão |
| **Product** | `stage` (pré-PMF / crescimento / maduro), `adoption_stage: 1\|2\|3`, `eval_owner`, `domain_contacts[]`, `repos[]` | discovery → live → sunset | `pack-setup` (repos), `bet-ship`, `gate G7\|G8`, `sweep` | `bet-shape`, `ritual betting`, AIVA |
| **Eval Suite** | `repo_path`, `regression_size`, `regression_pass`, `capability_size`, `metric: pass@1 \| pass^3`, `last_run` | sem `state` | `eval-run`, `eval-add` | `gate G7\|G8`, Eval Owner |
| **Adoption Report** | `adoption_stage`, `wau`, `target_cohort`, `retention_4w`, `repeat_use`, `verdict` | open → passed \| failed | `bet-ship` (abre), `adoption-report` | `gate G7\|G8`, Demo, Sense & Respond |
| **Ritual** | `cadence`, `duration`, `facilitator`, `participants[]`, `inputs[]`, `outputs[]`, `command`, `cancel_rule`, `recorded: bool` | active \| paused \| retired | humanos via PR no KB | `ritual <slug> open` |
| **Ritual Record** | `ritual`, `date`, `facilitator`, `attended[]`, `decisions[] {text, owner, due}`, `transcript?`, `cancelled?: motivo` | sem `state` | `ritual <slug> close`, `idea-triage`, `handoff --plantao` | `ritual betting`, Harness Retro, auditoria |
| **Transcript** | `ritual`, `redaction` (versão do scanner), `off_record_spans`, `participants[]` (handles) | sem `state` (`stale_after` obrigatório) | `meeting-record` | agentes (contexto), Harness Retro |
| **Cycle Record** | `bets[]`, `archetypes[] {who, primary, secondary, streak, justification?}`, `rotations[]`, `tutor_slices[]` | active → closed | `ritual betting close`, `ritual demo close` | `ritual betting` (regra dos 3 ciclos), métricas |
| **Metric Snapshot** | `period`, `metrics {…}` (§7), `source` | sem `state` | `t0 digest`, `metrics-snapshot`, CI (`trust.md`), `sweep` (`budget.md`) | Demo, AIVA, Sense & Respond, `slice-verify` (trust) |
| **Harness Item** | `pattern`, `occurrences[]` (links), `ladder_step: sensor \| area-rule \| skill \| agents-md`, `pr` | open → fixed \| wontfix | `slice-verify` e `t0 harness record` (ocorrência), `harness-fix` | Harness Retro, `sweep` |
| **PI Outcome** | `outcomes[] {metric, target, product}`, `confidence_vote` | sem `state` | `ritual pi-outcome close` | AIVA, Lead, `ritual betting` |
| **Accountability** | `answers_for`, `term`, `holder` | active \| alumni | humanos via PR no KB | tudo |
| **Rotation**, **Person**, **Role Archetype**, **Principle**, **Practice**, **Policy**, **Playbook**, **Glossary Term**, **Log** | como no profile `t0-team` | idem | humanos, `rotate`, `bet-shape` (glossário) | tudo |

Três detalhes que este método fixa:

- **`log.md` da bet** (`type: Log`, como no exemplo oficial; decide o G13 da pesquisa): todo comando que muda `state` de qualquer artefato da bet grava um registro de passo novo (arquivo com nome único em `steps/`); o `kb-render` é o único escritor do `log.md` e renderiza as linhas `## YYYY-MM-DD` / `**Verbo** por <actor>: o quê (link)`. Gate leva o aprovador. Toda skill do pack termina chamando `t0 log`, para o KB registrar o passo mesmo quando o agente improvisa. Decisões finas de implementação ficam no `.audit/<KEY>.tsv` do PR; no merge, o CI copia para o Slice as linhas de decisão e o link da trilha.
- **Spec congela no ship**: o `spec.md` da bet vira `state: frozen` e `status: stable`, nunca mais editado, e o conteúdo vivo migra para `products/<p>/spec.md`. A bet é spec-first; o produto é spec-anchored.
- **Conformidade**: `kb-check` roda L0 e L1 (bloqueantes no CI do KB) e L2 (avisos no digest), num script Python que segue a semântica do `OKFDocument.parse` de referência.

### 5.5 Espelho Jira: regras

Ordem de escrita: **KB primeiro, sempre.** `bet-sync` chama `t0 jira sync`, que lê o KB, escreve no Jira pela API/MCP do Atlassian e grava a chave de volta no frontmatter. Idempotente: re-rodar sem diff não cria nada.

| Campo | Direção | Regra |
|---|---|---|
| Feature (título, descrição, apetite, link para `bet.md`) | KB → Jira | Jira nunca edita. Edição feita lá é revertida no próximo sync, que comenta na issue "editado fora do KB, revertido; proponha a mudança em <link do PR no KB>" e grava o diff no `log.md` |
| Story (título, descrição, AC em bullets, Tier, link para o slice, label `ready-for-agent`, link **Blocks** por `depends_on`) | KB → Jira | idem |
| Chave Jira (`jira:`) | Jira → KB | Escrita uma vez, no create; nunca muda |
| Status da Story | **duas vias, com fonte declarada** | Transições vindas de Git/CI (G4: PR sai de draft = In Review; G5: merge = Done) escrevem no Jira **e** no slice. Transição humana no Jira (ex.: RTE bloqueia) é lida pelo sync e vira `state: blocked` com `blocked_by: jira:<quem>` + item do digest. Transição que contradiz um gate (Done sem PR mergeado, Story andando antes do G3) é revertida com comentário |
| Comentários | **duas vias, só acréscimo** | Comentário do ART no Jira é importado no `log.md` da bet como "externo". Resumo de merge e decisão de gate vão do KB para o Jira. Ninguém edita comentário importado |
| Issue criada direto no Jira (bug de squad, pedido do ART) | Jira → KB (intake) | Vira Idea `new` ou bet bugfix `proposed` com o link. A partir daí vale a mão única KB → Jira |
| Story points | KB → Jira | Valor fixo 1 por slice, só se o ART exigir; nunca estimado |
| Outcomes do PI | KB → Jira/Confluence | PI Outcome e `cycles/<C>/report.md` geram o texto; o AIVA leva |

**Regra de conflito:** conteúdo (texto, AC, links) é sempre do KB. Status é "última transição com fonte registrada vence"; divergência que o sync não resolve sozinho vira `state: conflict` no slice + item no digest para o Flow Steward. Nunca há sobrescrita silenciosa: toda escrita do sync vai para o `log.md` da bet.

**Quando o sync roda:** a cada comando do pack que escreve no KB, e todo dia num reconcile noturno (`process:t0-sync`, que roda `t0 jira sync --reconcile`). O reconcile produz o **relatório de drift** que o Flow Steward lê no digest. A meta é chegar à Demo com drift zero.

---

## 6. Qualidade e gates

### 6.1 DoR e DoD

**DoR da bet** (checado no G2 e no G3):

- Spec com `markers_open: 0`
- Os 4 checks do Plan (simplicidade, anti-abstração, contrato definido, teste falhando primeiro) com `pass` ou exceção escrita
- Contract `approved` para toda superfície pública nova ou alterada
- Tipo e Tier declarados; Eval Owner nomeado se o produto vai para o degrau 2

**DoR do slice** (`slice-build` checa antes de começar e aborta se falta campo):

- Link para Spec e Plan com `state: approved`. **Bugfix:** link para `bugfix.md` `approved` no G1; sem Spec, sem Plan, sem os 4 checks
- Critérios de aceite em bullets, copiados do spec (bugfix: tirados de `expected` e `unchanged[]`)
- Como verificar (teste, comando, tela)
- Tier 0, 1 ou 2 e `repo` alvo
- Zero `[PRECISA ESCLARECER]` no spec e no plano
- Chave Jira gravada. **Bugfix:** criada pelo `bet-new bugfix` junto com o slice único. Exploratória não tem slice

**DoD do slice** (G5):

- CI verde e agente de review sem pendência (G4)
- Review humano conforme o tier, com primeira resposta em ≤4h úteis
- Teste nas costuras combinadas no spec (`seams[]`); verificação executada (`verify-<app>`); blast-radius com prova executada em Tier 2
- `.audit/<KEY>.tsv` commitado; corpo do PR com antes/depois, porta de mão única ou dupla e blast radius
- Seção "Em minhas palavras" quando exigida (§3.4)
- Slice `state: done` com `verified`; Story transicionada; resumo comentado
- Se o agente errou no caminho, a ocorrência está num Harness Item; se é a segunda, o sensor está no PR ou num PR separado linkado
- Superfície pública alterada: contract tests verdes e `Contract.version` atualizado

**DoD da bet** (G6): todos os slices `done`; `bet-ship` rodado; spec congelado e spec vivo do produto atualizado; Contract `published`; Eval Suite com `regression_pass` registrado se for ferramenta de agente; estado final gravado na Demo. Exploratória: Assessment com veredito e protótipos linkados, nada mergeado em produto. Bugfix: teste de regressão escrito **antes** do fix e `unchanged[]` verificado; a bet fecha no G5.

### 6.2 Tiers de review e graduação de confiança

| Tier | Exemplos | Review mínimo |
|---|---|---|
| **0** | docs, testes, refactor mecânico, limpeza, saída de agente de limpeza, PR de estado no KB | agente de review + CI; 1 humano faz merge em lote, diário |
| **1** | feature em ferramenta interna, slice de bet de entrega | agente de review + 1 humano; júnior não aprova sozinho; preceptor se o autor é júnior |
| **2** | auth, dados de cliente, permissões de agente, contrato público, prompt ou modelo de ferramenta que as squads usam, bet de plataforma por padrão | agente de review + 2 humanos, um deles o Bet Owner (o segundo pode vir de outro pod); blast-radius com prova executada; cadeia de rastreabilidade completa |

Regras de fluxo:

- PR esperando review tem prioridade sobre slice novo.
- No máximo 2 slices em construção por pessoa. Sessões de agente paralelas são ilimitadas; o que é limitado é o que espera humano.
- O revisor humano só lê depois que o agente de review e o CI passaram (G4).
- O agente de review roda num subagente novo, só leitura, contra o spec, pulando estilo. No Verify, quem prova é o blast-radius. Review entre modelos da mesma família fica marcado "same-family".
- PR nasce sempre em draft e nunca tem merge automático fora do Tier 0. Hooks de git e CI bloqueiam force push, `reset --hard`, push em `main` e PR sem draft.

**Graduação de confiança por área (proposta, delta 19):** uma área de código (path) desce de Tier 1 para Tier 0 depois de **20 PRs consecutivos** em que o agente de review não deixou passar defeito escapado. Volta para Tier 1 no primeiro defeito escapado. Tier 2 nunca gradua. O contador fica em `harness/trust.md`, escrito só pelo CI; o `slice-verify` consulta.

### 6.3 Escada do harness (P5)

Na **segunda** ocorrência do mesmo erro de agente, o Harness Item (aberto na primeira por `slice-verify`, que chama `t0 harness record`) sobe a escada, do nível mais alto para o mais baixo:

1. **Sensor computacional:** lint com mensagem de correção escrita para o agente, teste, hook de git ou gate de CI. Funciona igual em qualquer ferramenta.
2. Se impossível: **regra de área**, de uma fonte só em `agents/rules/<area>.md`, gerada por `t0 rules build` para `.claude/rules/`, `.github/instructions/` e steering do Kiro.
3. Se é procedimento longo: **skill** no pack.
4. **`AGENTS.md`**, último recurso, ≤150 linhas.

**Regra sem exceção vai para hook de git ou gate de CI, e nunca para hook de agente.** As três ferramentas têm hooks de agente (Claude Code, Copilot e Kiro), mas cada uma com formato, eventos e semântica próprios: não são portáteis, o Copilot no VS Code ignora matchers, e timeout de hook no Copilot falha aberto. Por isso o que é obrigatório mora em git hook + CI, que valem igual para as três. Hook de agente é acelerador opcional (injeção de contexto, guard local), gerado por ferramenta pelo `pack-setup` a partir de scripts compartilhados. Teto de 20 hooks/deny por repo. O Sweeper reporta linhas, hooks e regras por repo todo ciclo em `harness/budget.md`.

### 6.4 Política de eval para o que o time entrega (P10)

Vale para skills, MCPs, agentes e o próprio pack.

- Toda ferramenta que vai para squads piloto tem **suíte de regressão de 20 a 50 tarefas** tiradas de uso e falhas reais, com casos positivos e negativos, e precisa de **≥95%** para o G7 (proposta). Se uma tarefa dá 0%, a primeira suspeita é a própria tarefa: monta uma solução de referência.
- Duas suítes por produto: **capacidade** (começa baixa, é para subir) e **regressão** (perto de 100%). Eval de capacidade que satura vira regressão.
- Métrica: `pass@1` para ferramenta em que um resultado bom basta; **`pass^3`** para agente que a squad usa sem olhar (consistência). O `product.md` declara qual.
- Grader determinístico sempre que der; juiz LLM por dimensão, com opção "não sei"; humano só em amostra. O que se avalia é o resultado, e não o caminho até ele.
- **Upgrade de modelo, mudança de prompt ou de skill só entra se a regressão fica igual ou melhor.** O Eval Owner assina; `eval-run` registra no Eval Suite.
- **Incidente ou defeito escapado vira caso de eval antes da Harness Retro fechar** (`eval-add`).
- Eval-driven: em bet de plataforma, os primeiros casos de eval são escritos no Shape, antes do código.
- Infra de eval é do pod Agent Platform; tarefas vêm de todo mundo e das squads. O Eval Suite no KB só aponta para `evals/` no repo e carrega o último resultado.
- **O pack:** goldens de spec e slice, fixtures de dry-run do Jira, `kb-check` nos bundles de exemplo e a mesma skill rodando nas três ferramentas. Release do pack passa pela mesma regra de não-regressão.

### 6.5 Pisos de customer zero (todos **PROPOSTA**; `methodology/policies/adoption-floors.md` com `state: proposed`)

"Ativo" = invocou a ferramenta em trabalho real numa semana ISO, medido por telemetria. Login não conta.

| Gate | Critério proposto | Quem confirma |
|---|---|---|
| **G7: degrau 1 → 2** (time → 2 ou 3 squads piloto) | **PROPOSTA:** ≥7 dos 10 do time ativos por semana por 2 semanas seguidas **e** regressão ≥95% (§6.4) | AIVA + Eval Owner |
| **G8: degrau 2 → 3** (piloto → ART) | **PROPOSTA:** ≥40% dos devs-alvo das squads piloto ativos por semana por 3 semanas seguidas **e** ≥50% de retenção em 4 semanas **e** `pass^3` dentro da meta do Eval Owner | AIVA + Lead + Eval Owner; vira outcome do PI |
| **Episódica** (ex.: skill de migração) | **PROPOSTA:** troca uso semanal por uso repetido em ≥2 de 4 semanas, entre quem tinha tarefa elegível | quem confirma o gate correspondente |
| **Sunset** | **PROPOSTA:** <15% de uso semanal no público-alvo, ou <5 usuários ativos absolutos, depois de 8 semanas em piloto → desliga ou funde numa ferramenta geral | Sweeper propõe no Dia de limpeza; Lead confirma |

De onde vêm os números: o time é a coorte mais motivada, então 70% é razoável (o Claude Code foi de 20% a 50% da engenharia da Anthropic em 5 dias, mas isso foi observação, não gate). 40% no piloto fica abaixo do platô de ~60% atribuído à DX (**não verificado**) e passa do pico de novidade de uma semana. A cláusula de retenção copia a forma do gate do time do Claude Code (usuários ativos **e** retenção), cujo número não é público. O gate é nosso, independente dessas fontes. Revisar depois de 3 ferramentas passarem pelo funil.

---

## 7. Métricas e visibilidade

Um painel só, alimentado por Git, CI, Jira, telemetria dos agentes e o próprio KB. Ninguém reporta nada à mão. O time é o primeiro cliente do pipeline que vende para as squads.

| Camada | Métrica | Decisão que ela informa |
|---|---|---|
| **Visibilidade** | Slices por pessoa (construindo / em review / done), bets por pod e `state`, bolt no prazo ou atrasado | Quem destravar no Sync de bloqueios; responde "quem faz o quê" para Lead e RTE |
| **Fluxo** | Cycle time Idea → G1 → produção; cycle time por slice; idade da fila de review e de gates | Onde o trabalho espera |
| **Review (SLOs)** | Mediana até a primeira resposta humana ≤4h úteis (PR e gate); minutos humanos por PR (≤15 em Tier 1); % de problemas achados pelo agente antes do humano; "agente ocioso esperando humano" por sessão | Redistribuir review; graduar área (P6) |
| **Entrega (DORA)** | Frequência de deploy, lead time, taxa de falha de mudança, tempo de recuperação | Pegar o "mais rápido e mais frágil" |
| **Adoção (por ferramenta)** | Uso semanal, retenção em 4 semanas, uso repetido, coortes (nenhum / leve / moderado / pesado), custo por usuário ativo; por squad: tempo economizado (auto-reportado + amostrado) | G7, G8 e sunset; o que o AIVA leva ao Sense & Respond |
| **Uso de IA (eficiência)** | % de PRs de autoria de agente, custo de tokens por slice, sessões por dev/dia (só como piso, para achar quem não está usando e oferecer ajuda) | Custo do AIDLC; revisão mensal de modelo |
| **Harness** | Linhas de `AGENTS.md` por repo, hooks/deny por repo (≤20), taxa de recorrência do mesmo erro, Harness Item abertos e fechados, PRs abertos por agentes de limpeza | Se o time está compondo ganho ou inchando contexto |
| **Evals** | Tamanho e pass rate das suítes por produto, casos adicionados por ciclo | Gates de degrau, troca de modelo |
| **KB** | Concepts com `stale_after` vencido, % de gates com `verified: human:`, drift do Jira, % de rituais com Ritual Record | Se o sistema de registro está vivo |
| **Formação** | % de PRs Tier 1/2 de júnior e Tier 2 com "Em minhas palavras"; slices em modo tutor feitos; plantão em dupla | Saúde da preceptoria (participação, nunca nota) |

**Regra anti-vaidade (sem exceção):**

- **Nenhum ranking de pessoa** por token, PR, linha ou sessão. A visão por pessoa mostra só o que está em andamento e travado, para destravar. A métrica de pessoa é o que ela entregou e destravou (slices done, reviews dentro do SLO, bloqueios resolvidos). Dashboard que mostra pessoa por volume de agente é bug Tier 1.
- **Token é piso e custo, nunca meta.**
- **Toda métrica nomeia a decisão que informa.** Métrica que não informou nenhuma decisão em 2 PIs é removida pelo Sweeper.
- **Métrica que sai do time** (ART, liderança) é só de produto e de fluxo: adoção, retenção, DORA, cycle time. Nunca de atividade.
- **Dado individual de formação** só o preceptor e a própria pessoa veem.

Cadência: `t0 digest` diário gera `cycles/<C>/digests/`; `metrics-snapshot` no close da Demo gera `cycles/<C>/report.md`, que o AIVA leva ao ART.

---

## 8. Interface com o SAFe (AI-Native SAFe, 2026)

Decisão mantida: **SAFe por fora, builder pods por dentro.** O que muda com os fatos verificados do AI-Native SAFe é o argumento: o ART passou a pedir **outcomes** no PI, não features comprometidas, e os nossos degraus de adoção já são outcomes. Com isso a interface fica mais fina.

| SAFe (AI-Native) | Neste modelo | Quem produz | Como chega lá |
|---|---|---|---|
| AI-Native Team (3 a 7 pessoas) | 3 pods de 3 + Lead. Pods de 3 estão no piso da faixa: uma ausência corta pela metade a capacidade de review, por isso o segundo revisor de Tier 2 pode vir de outro pod e o Flow Steward redistribui review | Time | `team/` |
| Epic / tema | Idea promovida e PI Outcome | Lead + PM | `idea-triage`, `ritual pi-outcome` |
| Feature | Bet (com apetite) | Bet Owner; o agente cria no Jira | `bet-sync` |
| Story | Slice | Agente, a partir do spec | `bet-sync` |
| Iteração (2 semanas) | Ciclo: Betting → build → Demo + Harness Retro | Time | `ritual <slug>` |
| **PI Outcome Planning** (1 dia; outcomes + voto de confiança) | Compromisso com degraus de adoção, pisos de eval, SLO de review e DORA por produto. Bets candidatas com apetite e risco aparecem como meio, não como compromisso | Lead + AIVA + Bet Owners | `ritual pi-outcome` → PI Outcome |
| **Sense & Respond** (2h por iteração; substitui System Demo e I&A) | Report do ciclo e Ritual Record da Demo como insumo; decisões do ART voltam como ADR ou Idea | Flow Steward prepara; Lead + AIVA apresentam | `ritual sense-respond` |
| Capacidades do time: Product, Builder, Domain Expert, AI | Product = Bet Owner; Builder = todo dev, em qualquer arquétipo; Domain Expert = contato fixo por produto; AI = agentes com as skills do pack, sob supervisão | Pod | `team/accountabilities/`, `log.md`, `.audit/` |
| AI Value Architect | AIVA do pod Insights & Enablement, **não o Lead** | Fixo por PI | `team/accountabilities/aiva.md`, Adoption Report |
| Align / Sense / Respond | Betting + Mobs / Digest + Demo / Bloqueios + Retro | Time | Ritual Record |
| Capacidade / pontos | Throughput de slices e cycle time; 1 ponto fixo por slice se exigirem | Gerado | `bet-sync` |

**Se o ART ainda roda SAFe clássico:** a Demo alimenta a System Demo, a Harness Retro consolidada alimenta o I&A, e o PI Planning recebe bets candidatas com apetite e risco, além dos outcomes propostos.

Como apresentar ao RTE: piloto de **AI-Native Team** dentro do ART; rastreabilidade intacta (Feature e Story no Jira, mais atualizadas que antes); outcomes de adoção prontos para o PI Outcome Planning; o time exerce a capability de AIVA que o framework acabou de criar.

Quando rever a decisão: mais de 3 pods no mesmo produto; BU exigindo pontos por PI; outros times entregando nos nossos repos; o ART adotando AI-Native SAFe por inteiro e pedindo que o time use a cadência dele por dentro.

---

## 9. Rollout em 90 dias e riscos

O rollout começa com 1 pod e o pack mínimo, prova o modelo em 2 ciclos e depois escala.

**Dias 0 a 30: fundação (1 pod piloto, provavelmente Dev Tooling)**

- Criar o `t0-kb` com `profile.md`, a metodologia, os concepts `Ritual` deste documento, os templates de bet por tipo e `kb-check` (L0 e L1 bloqueantes no CI do KB, L2 aviso).
- Pack v0: `AGENTS.md` modelo + `t0 rules build` para as 3 ferramentas + skills `pack-setup`, `idea-capture`, `idea-triage`, `bet-new`, `gate`, `ritual`, `bet-shape`, `bet-spec`, `bet-plan`, `bet-slice`, `bet-sync`, `slice-build`, `slice-verify`, `digest` + CLI `t0` (`gate`, `ritual`, `log`, `digest`, `jira sync` só KB → Jira com write-back de chave, `kb check`) + hooks de git e gates de CI.
- `docs/agents/issue-tracker.md` nos repos do piloto com o mapeamento Jira (MCP do Atlassian), confirmando os nomes das ferramentas no MCP do banco.
- Digest diário no canal.
- Transcrição em **dry-run** (redige, mas não persiste) até o aval de privacidade/LGPD do banco.
- Rodar 2 bets ponta a ponta (1 entrega, 1 bugfix) com Mob A e Ritual Record.
- **Critério de saída:** 2 bets encerradas no KB com 100% dos gates com `verified`; drift do Jira zero na Demo; `kb-check` verde; o pod achando o ciclo mais leve que antes (pergunta de uma linha na Retro).

**Dias 31 a 60: escala para 3 pods**

- Pods formados; Betting com cobertura de arquétipos e regra dos 3 ciclos no Cycle Record; Rotations de Flow Steward, Sweeper, Plantão e preceptores no KB.
- AIVA, Eval Owners e Domain Experts nomeados.
- `t0 jira sync` completo: status em duas vias, comentários append-only, intake, reconcile noturno com relatório de drift.
- Agente de review obrigatório antes do humano; tiers com SLO; `harness/trust.md` começa a contar.
- Primeira Harness Retro fechando com PRs; Harness Items em uso.
- Primeira suíte de eval (20 casos) para a ferramenta mais usada; primeira ferramenta tentando o G7.
- Painel de fluxo + DORA + adoção do próprio time; `cycles/<C>/report.md` gerado.
- Transcrição ligada se o aval saiu; `ideas/` aberto para as squads.
- **Critério de saída:** 3 pods rodando o ciclo; 1 ferramenta no degrau 2 com números; orçamento síncrono medido contra a §4.3.

**Dias 61 a 90: automação e governança**

- Agentes de limpeza em background abrindo PRs Tier 0 (dívida, docs, candidatos a sunset); `sweep` encolhendo o Dia de limpeza.
- `adoption-floors.md` ainda `proposed`, com dados de 3 ciclos para a primeira revisão.
- Lead + AIVA no Sense & Respond com os reports dos ciclos 1 a 3 como outcomes para o próximo PI Outcome Planning.
- Evals do próprio pack rodando nas três ferramentas; pack v1 empacotado para as squads (templates de KB, skills, CLI, painel), com `THIRD_PARTY_NOTICES.md` (MIT do mattpocock/skills e do pstack).
- **Critério de saída:** Sense & Respond com o time dentro; 1 política de piso virando `in-force` ou revisada com motivo.

**Riscos e mitigações**

| Risco | Mitigação |
|---|---|
| Fila de review vira o novo gargalo | WIP por review pendente, SLO de 4h medido, agente de review antes do humano, PR ≤15 min, graduação de confiança por área |
| Gate assíncrono parado vira fila nova | SLO de gate igual ao de review; PR de gate acima do SLO aparece no digest e no Sync de bloqueios |
| Markdown overload (revisar spec vira pior que revisar código) | Profundidade proporcional (P3): bugfix e Tier 0 sem plano; intent no corpo do `bet.md`; bolt dentro do plano; Mob B assíncrona. Se o cycle time Idea → G1 subir 2 ciclos seguidos, a Retro corta artefato |
| "AI slop" e dívida acumulando | 4 checks do plano, linters com mensagem para o agente, agentes de limpeza, `tech-debt.md` vivo, Sweeper de plantão |
| `AGENTS.md` e KB inchando o contexto | Escada do harness, teto de 150 linhas, P9, proibição de cópia, Sweeper reporta o orçamento todo ciclo |
| Drift Jira ↔ KB | Mestre único por campo, reconcile noturno, relatório no digest, reversão comentada, `state: conflict` |
| Três ferramentas de agente divergem (Copilot, Claude Code, Kiro) | Tudo que é obrigatório mora em git hook, CI e CLI; skills no padrão Agent Skills; regras de área geradas de uma fonte; o pack tem eval que roda a mesma skill nas três |
| Pack vira gargalo (um mantenedor só) | Pack é produto do pod Dev Tooling, com Maintainer e Eval Owner nomeados; fork mínimo do upstream com `metadata.credits`; modo degradado documentado (escrever o concept à mão + `kb-check`) |
| KB vira cemitério de markdown | `stale_after` em tudo que envelhece, `kb-check` L2 no Dia de limpeza, todo comando escreve no KB |
| Privacidade das transcrições (LGPD, banco) | Dry-run até o aval, redação determinística antes do agente, "fora do registro", 1:1 nunca gravado, retenção de 180 dias (proposta) |
| Arquétipo vira cargo | §3.5, com bloqueio da 4ª declaração no `ritual betting close` |
| Atrofia de habilidade, poucos juniores | §3.4; todo mundo passa por Builder e Sweeper; métrica de participação no painel do preceptor |
| Atrito com governança SAFe / PMO | Jira 100% por agente e sempre atualizado, outcomes de adoção prontos para o PI, AIVA no Sense & Respond, enquadramento como AI-Native Team |
| Segurança e compliance (banco) | Permissões versionadas, sem modo sem permissão em repo sensível, `.audit/` por PR, gate como PR no KB com histórico git, Tier 2 em contrato e permissão de agente |
| Custo de token sem controle | Custo por slice e por usuário ativo no painel, revisão mensal de modelos pelo Lead, agentes assíncronos com orçamento |
| Pods de 3 no piso do SAFe | Flow Steward redistribui review entre pods; segundo revisor de Tier 2 de outro pod |

---

## 10. Passo → comando do pack → artefato OKF

Cada comando é uma skill `SKILL.md` no pack, descoberta pelas três ferramentas. A coluna `t0` diz o que roda deterministicamente na CLI (igual nas três); o resto é orquestração do agente. Base upstream indicada quando existe: tudo é fork com `metadata.credits`, nada por composição, porque as skills upstream são quase todas user-invoked.

| Passo, gate ou ritual | Skill | Determinístico via `t0` | Lê (OKF) | Escreve (tipo OKF, caminho) | Base upstream |
|---|---|---|---|---|---|
| Instalar o pack num repo de produto | `pack-setup` | `t0 setup`: gera `AGENTS.md`, ponteiros (CLAUDE.md, copilot-instructions, steering), regras de área, hooks de git, gates de CI, hooks de agente opcionais por ferramenta, `docs/agents/issue-tracker.md` | Profile, `methodology/` | Product (`repos[]`); `harness/budget.md` (Metric Snapshot) | MP setup-matt-pocock-skills |
| Validar o KB | `kb-check` | `t0 kb check`: L0/L1 bloqueiam, L2 avisa | tudo | nada (CI do KB) | local okf-check (Python `-I`) |
| Capturar ideia | `idea-capture` | `t0 idea new` | Glossary Term, Idea (dedup) | Idea `ideas/IDEA-NNNN-slug.md` (`new`) | novo |
| **G0** / **Ritual: Triagem de ideias** | `idea-triage` | `t0 idea triage` + `t0 gate G0` | Idea `new` | Idea `triaged` + `verified` ou `parked\|rejected`; Ritual Record `cycles/<C>/rituals/` | novo |
| Abrir bet (Intent) | `bet-new <tipo> [IDEA]` | `t0 bet new`: pasta + `bet.md` pelo template do tipo | Idea, Product | Bet `products/<p>/bets/BET-NNN/bet.md` (`proposed`, intent no corpo); `log.md`; Idea `promoted` | novo |
| Abrir bet bugfix | `bet-new bugfix` | `t0 bet new --bugfix`: `bugfix.md` + slice único + `t0 jira sync` | Product, Idea ou issue Jira | Bet, Bugfix, Slice `slices/01-fix.md` (`ready`, `jira`), `log.md` | novo |
| Gate genérico (qualquer G0 a G8) | `gate <G> <alvo>` | `t0 gate`: PR no KB mudando `state` + `verified`; no merge, o `kb-render` atualiza o `log.md` e chama `t0 jira sync` | o artefato do gate | o artefato com `state` novo + `verified` | novo |
| **G1** apostar | `ritual betting close` (bugfix: `gate G1 <BET>` pelo Flow Steward) | `t0 gate G1` | Bet `proposed` | Bet `active` + `verified`; Feature no Jira | novo |
| **Ritual: Betting** | `ritual betting open\|close` | `t0 ritual betting`; checa cobertura de arquétipos e bloqueia a 4ª declaração seguida; chama `rotate` | Idea `triaged`, Bet `proposed\|extended`, Assessment, Adoption Report, Cycle Record, report anterior, Rotation | Cycle Record `cycles/<C>/cycle.md`; Bet (G1); Rotation; Idea `parked`; Ritual Record; Transcript | novo |
| Rodízio | `rotate` | `t0 rotate` | Rotation | Rotation `team/rotations/` (atribuição, `stale_after`) | novo |
| Shape (entrega, plataforma) | `bet-shape` | checkpoint obrigatório entre os 2 esboços de arquitetura | Bet, Glossary Term, ADR, Spec vivo, Contract | Spec rascunho (`markers_open`); Glossary Term; ADR `proposed`; `log.md` | MP grilling + domain-modeling; PS architect (texto) |
| Protótipos e Assessment (exploratória) | `bet-shape --explore` | grava protótipos fora do repo de produto | Bet, Product | Assessment `…/assessment.md` (`verdict`) | MP prototype |
| Gravar spec | `bet-spec` | conta `markers_open`; recusa `approved` com marcador | Bet, Assessment, Glossary Term | Spec `…/spec.md`; Contract `products/<p>/contracts/` (`proposed`) | MP to-spec (pt-BR + AC + verificar + tier) |
| Registrar decisão | `adr-new [--supersede <ADR>]` | `t0 adr new`: numera e liga `relations.supersedes` | ADR existentes | ADR `products/<p>/adr/` ou `methodology/adr/` | novo |
| **Ritual: Mob Elaboration A** | `ritual mob-a <BET> open\|close` | `t0 ritual mob-a`; roda `bet-shape` e `bet-spec` ao vivo | Bet, Spec vivo, Glossary Term, ADR, Contract | Spec, Glossary Term, ADR, Ritual Record, Transcript, `log.md` | novo |
| **G2** spec aprovado | `gate G2 <BET>` | `t0 gate G2`: bloqueia com `markers_open > 0`; exige Lead em Tier 2 e preceptor com Bet Owner júnior | Spec | Spec `approved` + `verified` | novo |
| Planejar | `bet-plan` | roda os 4 checks; exige Contract se há `surface` | Spec, Contract | Plan `…/plan.md` (bolts, checks); Contract atualizado | PS architect (esboços); Spec Kit gates |
| Fatiar | `bet-slice` | um arquivo por slice; grafo de dependências | Plan, Spec | Slice `…/slices/NN-slug.md` (`ready`) | MP to-tickets |
| Espelhar no Jira | `bet-sync` | `t0 jira sync`: idempotente, write-back de chave, status em duas vias, comentários append-only, intake | Bet, Slice | `bet.md: jira`, `slices/*: jira`, Idea ou Bet bugfix (intake), `log.md` | MP to-tickets (ramo Jira) + tracker doc |
| Reconcile noturno | (CI agendado) | `t0 jira sync --reconcile` como `process:t0-sync` | Bet, Slice, Jira | relatório de drift no digest; `state: conflict` quando preciso; `log.md` | novo |
| **Ritual: Mob Elaboration B** | `bet-plan` → `bet-slice` → `gate G3`; síncrona: `ritual mob-b <BET> open\|close` | `t0 ritual mob-b` | Spec, Contract, Plan | Plan, Slice, Contract; Ritual Record só se síncrona | novo |
| **Ritual: Mob Construction** | `ritual mob-construction <BET> open\|close` | `t0 ritual mob-construction` | Contract, Plan | Contract `approved`, ADR, Ritual Record, Transcript | novo |
| **G3** pronto para construir | `gate G3 <BET>` | `t0 gate G3`: checa os 4 checks, Contract e chave Jira em cada slice | Plan, Slice, Contract | Plan `approved`, Slice `ready`, Contract `approved`, todos com `verified` | novo |
| Build | `slice-build <KEY>` | checa DoR; branch `bet/BET-NNN/<KEY>-slug`; PR em draft; `.audit/<KEY>.tsv` | Slice, Spec ou Bugfix, Plan, Contract, `AGENTS.md` do repo | Slice `building` + `pr`; `log.md` | MP implement + tdd; PS show-me-your-work |
| Build paralelo (Tier 0/1, contrato aprovado) | `slice-build --parallel` | worktrees; merger; nunca sai do draft | idem | idem | MP implement-spec |
| Diagnosticar bug | `diagnose [--tutor]` | loop vermelho → mínimo → hipótese → fix → regressão | Bugfix, Slice | `log.md` | MP diagnosing-bugs |
| Verify (agente de review) | `slice-verify <KEY>` | review por padrões + aderência ao spec; blast-radius em Tier 2; consulta `harness/trust.md`; `t0 harness record` em erro de agente | Slice, Spec, Contract, `harness/trust.md` | comentário no PR; Harness Item `harness/HI-NNNN.md` (ocorrência) | MP code-review (regex Jira + KB); PS blast-radius |
| **G4** pronto para review | (CI) | `t0 gate G4 <KEY>` depois de CI verde + `slice-verify` limpo | Slice | Slice `in-review` + `verified: process:ci`; Story In Review | hook/CI |
| Verificação ponta a ponta de um app | `verify-<app>` (gerada por repo) | skill local por repo | Spec vivo | evidência no PR | PS create-verification-skill |
| **G5** merge | (humano aprova no PR; CI no merge) | `t0 gate G5 <KEY>`: copia aprovações para `verified`, linhas de decisão do `.audit` para o Slice; fecha bet bugfix | Slice, PR | Slice `done` + `verified`; Bet bugfix `shipped`; Story Done; `log.md`; `harness/trust.md` (contador, por `process:ci`) | hook/CI |
| Ship | `bet-ship <BET>` | congela spec da bet; atualiza spec vivo; publica Contract; notas de release; abre Adoption Report | Bet, Spec, Contract, Product, Eval Suite | Spec `frozen`; `products/<p>/spec.md`; Contract `published`; Adoption Report `products/<p>/adoption/` (`open`); `log.md` | novo |
| **G6** bet encerrada | `ritual demo close` | `t0 gate G6` | Bet, Assessment | Bet `shipped\|killed\|extended` + aprendizado + `verified` | novo |
| **Ritual: Demo** | `ritual demo open\|close` | `t0 ritual demo`; o close chama `metrics-snapshot` e `t0 gate G6` | Bet `active`, Assessment, Adoption Report, digests | Metric Snapshot `cycles/<C>/report.md`; Bet (G6); Cycle Record `closed`; Ritual Record; Transcript | novo |
| Snapshot de ciclo | `metrics-snapshot` | `t0 metrics cycle`: agrega digests + telemetria | Metric Snapshot diários | Metric Snapshot `cycles/<C>/report.md` | novo |
| Medir adoção | `adoption-report <produto>` | `t0 adoption`: lê telemetria e compara com os pisos da §6.5 | Product, Eval Suite, telemetria | Adoption Report (`passed\|failed`) | novo |
| **G7** / **G8** subir degrau | `gate G7\|G8 <produto>` | `t0 gate`: bloqueia sem Adoption Report `passed` e Eval Suite passando | Adoption Report, Eval Suite | Product `adoption_stage` + `verified` | novo |
| Rodar evals | `eval-run <produto>` | executa a suíte; grava pass rate; bloqueia upgrade se piorou | Eval Suite | Eval Suite `products/<p>/evals.md` | novo (guia de evals da Anthropic) |
| Adicionar caso de eval | `eval-add <produto>` | cria caso no `evals/` do repo a partir de incidente ou PR | Eval Suite, Harness Item | caso no repo; Eval Suite (contagem) | novo |
| Erro repetido → sensor | `harness-fix <HI>` | escolhe o degrau da escada; abre PR em draft no repo certo | Harness Item, `.audit/` | Harness Item (`ladder_step`, `pr`, `fixed`) | MP retro + PS correct |
| **Ritual: Harness Retro** | `ritual harness-retro open\|close` | `t0 ritual harness-retro`; o close falha sem PR para cada item aceito | Harness Item, `.audit/`, reviews, `harness/budget.md` | Harness Item; casos de eval; Ritual Record; Transcript | MP retro (escopo workspace) |
| **Ritual: Dia de limpeza** | `ritual limpeza open\|close` (o open roda `sweep`) | `t0 sweep`: candidatos a sunset com números, `stale_after` vencido, drift, contagem de linhas e hooks | Product, Adoption Report, `kb-check` L2, `tech-debt.md` | PRs Tier 0; Product `sunset`; Harness Item; `harness/budget.md`; Ritual Record curto | PS maintain-verification-skill + novo |
| **Ritual: Digest diário** | `digest` (CI agendado) | `t0 digest` | Bet, Slice, Rotation, PRs de gate, `.audit/`, Git/CI/Jira | Metric Snapshot `cycles/<C>/digests/AAAA-MM-DD.md` | novo |
| **Ritual: Sync de bloqueios** | `ritual bloqueios open\|close` | `t0 ritual bloqueios`: pré-preenche do digest e de `t0 review-queue`; propõe cancelamento às 9h05 | Metric Snapshot do dia | Ritual Record | novo |
| **Ritual: Preceptoria 1:1** | `ritual preceptoria open\|close` | `t0 ritual preceptoria`; nunca chama `meeting-record` | explain-backs, Slice `mode: tutor` | Ritual Record mínimo (só ações) | novo |
| **Ritual: Sense & Respond** | `ritual sense-respond open\|close` | `t0 ritual sense-respond`: monta o pacote de entrada | report do ciclo, Adoption Report, Ritual Record da Demo, PI Outcome | Ritual Record; ADR ou Idea; Transcript se o ART permitir | novo |
| **Ritual: PI Outcome Planning** | `ritual pi-outcome open\|close` | `t0 ritual pi-outcome` | Product, Adoption Report, reports, Idea `triaged`, Bet `proposed` | PI Outcome `pi/<PI>/outcomes.md`; Ritual Record | novo |
| Transcrição de reunião | `meeting-record <arquivo>` | `t0 transcript redact`: scanner de segredo + regex de PII antes do agente; respeita "fora do registro" | Ritual | Transcript `cycles/<C>/transcripts/` (`stale_after` 180d, sem `verified`); Idea e ADR candidatos sem `verified` | novo; scanner do handoff |
| Handoff de sessão | `handoff` | scanner de segredo antes de gravar; inclui chaves Jira e ponteiros `.audit/` | Bet, Slice | arquivo em `$TMPDIR` (fora do KB); link no `log.md` | MP handoff |
| Passagem de plantão | `handoff --plantao` | idem, gravando no KB | Rotation, Product | Ritual Record curto `cycles/<C>/rituals/<data>-plantao.md` | MP handoff |
| Rastreabilidade para auditor | (só CLI) | `t0 trace <BET>`: gera o JSON requisito → slice → PR → teste a partir do frontmatter | Bet, Spec, Slice | nada no KB (arquivo entregue ao auditor) | novo |

Comandos que existem só na CLI, sem skill: `t0 jira sync --reconcile`, `t0 review-queue`, `t0 rules build` (gera as regras de área para as três ferramentas), `t0 log` (toda skill termina chamando; grava um registro de passo que o `kb-render` leva ao `log.md`), `t0 kb find` (busca por `uid`, `type`, `tags`, `description`) e `t0 trace`.

Fora do pack, de propósito: poteto-mode (PR pronto, force push, "proceed without asking"), `why`/`recall`/`automate-me`/`reflect` (leem transcrições e varrem todos os MCPs), `make-bot-ui`, `no-comments`, `interrogate` (sem diversidade de família de modelo no banco; o Verify usa blast-radius), `arena`/`swarm` (até o banco aprovar mais de um tier em paralelo).

---

## Apêndice A: os 25 deltas da pesquisa

| # | Delta | Decisão | Motivo |
|---|---|---|---|
| 1 | Separar Lead de AIVA | **Aceito** | O AIVA no SAFe é coaching de adoção em nível de ART, não arquitetura. Fica no pod Insights & Enablement |
| 2 | Capability Product + Domain Expert fixo | **Aceito** | Product fica no Bet Owner; Domain Expert é contato fixo por produto, consultado no G2 |
| 3 | Mistura de arquétipos por estágio | **Aceito** | Regra de cobertura por pod, com declaração individual no Cycle Record para fazer valer a regra dos 3 ciclos |
| 4 | Eval Owner por produto | **Aceito** | Assina upgrade de modelo e co-aprova G7/G8 |
| 5 | Preceptor | **Aceito, ajustado** | A fonte não foi verificada; o 3:1 é decisão nossa, marcado como proposta |
| 6 | Sense & Respond | **Aceito** | Com fallback para SAFe clássico (§8) |
| 7 | Mob em duas etapas + Mob Construction | **Aceito, ajustado** | A é síncrona; B é assíncrona por padrão; Construction é ritual próprio, só para contrato que cruza pods, no lugar da B síncrona |
| 8 | Eval na Retro | **Aceito** | A Harness Retro só fecha com caso de eval para cada incidente |
| 9 | Assessment go / needs-clarification / kill | **Aceito** | É a saída da exploratória e decide o estado no G6 |
| 10 | `bolt-plan.md` | **Ajustado** | Bolt com dono, DoD e hipótese de confiança, mas como seção do Plan; arquivo a mais seria sobrecarga |
| 11 | Contrato por superfície pública | **Aceito** | Contract mora em `products/<p>/contracts/`, contract tests no código |
| 12 | Perfis de bet | **Ajustado** | 4 tipos (o brief fixa quatro). "Regulated" virou a sobreposição Tier 2, que vale para qualquer tipo; plataforma é Tier 2 por padrão. O candidato 2 tinha posto "regulado" só na plataforma; a sobreposição cobre mais casos com a mesma regra |
| 13 | Spec vivo do produto | **Aceito, ajustado** | Nada sai do KB: o spec da bet congela no ship e o conteúdo vivo migra para `products/<p>/spec.md`. Spec-first na bet, spec-anchored no produto |
| 14 | Orçamento de contexto | **Aceito** | `AGENTS.md` canônico ≤150 linhas, hooks/deny ≤20 por repo, P9 |
| 15 | `traceability.json` | **Rejeitado como arquivo** | Seria um segundo sistema de registro que ninguém mantém. A cadeia sai do frontmatter (`relations`, `jira`, `pr`) e do histórico git dos gates; `t0 trace` gera o JSON para auditor sob demanda. O candidato 1 propunha uma chave `traceability` no Slice em Tier 2; ficou como exigência de cadeia completa checada pelo `kb-check`, sem chave nova |
| 16 | Escada do harness | **Aceito** | É o P5 e a §6.3, com Harness Item por erro recorrente |
| 17 | DoR com marcadores + gates do plano | **Aceito** | `markers_open: 0` no G2 e os 4 checks no G3 |
| 18 | Gate de eval | **Aceito** | Regressão ≥95% no G7; não-regressão para upgrade de modelo |
| 19 | Graduação de confiança por área | **Aceito como proposta** | O número 20 precisa de calibração; Tier 2 nunca gradua |
| 20 | Pisos de adoção | **Aceito como proposta** | Rotulados PROPOSTA; Policy entra `proposed` |
| 21 | Tríade utilização / impacto / custo | **Aceito** | Camadas de adoção e de uso de IA no painel |
| 22 | SLOs de review | **Aceito, ampliado** | 4h úteis vale também para PR de gate |
| 23 | Saúde do harness | **Aceito, ampliado** | Inclui saúde do KB (stale, `verified`, drift, rituais com record) |
| 24 | Métricas de habilidade | **Ajustado** | Modo tutor obrigatório só para júnior; para todo mundo custaria review demais. É o primeiro corte se a capacidade apertar |
| 25 | Correção de fontes | **Aceito** | Customer zero continua como gate nosso, sem depender da fonte não verificada |

Do inventário de skills também entram: o `interrogate` sai do Verify e entra o blast-radius; o `tasks.md` vira um arquivo por slice; o `tdd` do pstack sai em favor do do mattpocock; o guard de git é um fork que **não** bloqueia todo `git push`; poteto-mode, `recall` e `automate-me` não são adotados.
