# AIDLC Operating Model — Time de Inovação em IA

2026-10-27 · @Tuba

## TL;DR

A proposta: **humanos definem a intenção e verificam; agentes executam e também mantêm o Jira**. O time roda em fluxo contínuo, com ciclos de 2 semanas alinhados às iterações do ART. O spec mora no repositório, e o Jira vira um espelho gerado por agentes via MCP.

- **Unidade de trabalho:** uma Bet (≈ Feature SAFe) com apetite fixo, quebrada em Slices (≈ Stories) que o próprio agente gera a partir do spec. Cada slice vira um PR pequeno.
- **Onde o humano gasta tempo:** shaping (Mob Elaboration), revisão por risco e melhoria do harness (CLAUDE.md, skills, linters, CI). Ninguém digita história no Jira.
- **Visibilidade:** vem de telemetria (PRs, sessões de agente, DORA, cycle time) publicada automaticamente, não de cerimônia.
- **Estrutura:** 3 builder pods de 3 devs, um por linha de produto. No lugar de cargos, os 5 arquétipos do time do Claude Code: Prototyper, Builder, Grower, Sweeper e Maintainer. O Sweeper e o Flow Steward rodam em rodízio a cada ciclo.
- **SAFe:** por fora, não por dentro. Internamente o time roda como builder pods com gate de customer zero, no modelo do time do Claude Code. Para o ART, só expõe Features e Stories espelhadas no Jira e bets no PI.
- **Skills:** o toolkit vem de forks internos do mattpocock/skills (grill, spec, tickets, review) e do pstack (prova, review adversário, trilha de decisões), adaptados para Jira, pt-BR e compliance.

## Decisão: SAFe por fora, builder pods por dentro

**Recomendação:** não usar o AI-Native SAFe como sistema operacional interno do time. Por dentro, o time roda como builder pods, no modelo do time do Claude Code. Para o ART, expõe só uma interface fina compatível com SAFe: Features e Stories espelhadas no Jira por agente e presença no PI com bets. Sair do SAFe não é decisão do time, porque a BU e o portfólio rodam nele. Mas trazer o framework inteiro para dentro de um time de 10 custa mais do que entrega.

**Como o time do Claude Code trabalha** (Product School, out/2026; entrevista com Meaghan Choi):

- Pods de 3 a 5 pessoas, em qualquer mistura de engenheiros, designers e AI PMs. Todos fazem deploy em produção.
- O título diz a especialidade, não o limite do que a pessoa contribui. Designer sobe código e engenheiro desenha.
- A decisão de qualidade saiu do PRD e do mockup e foi para o código funcionando. Code review, CI e testes protegem a produção.
- Customer zero: a feature precisa atingir um número mínimo de usuários internos ativos por dia antes de ir para fora. O produto passou cerca de 3 meses em uso interno antes do lançamento.
- O que mede sucesso é adoção, retenção e receita. Consumo de tokens serve só como piso, para achar quem não está usando IA, nunca como meta.
- Sem PRD: o time constrói primeiro. O Agent Teams passou por centenas de versões antes de uma sobreviver, e o Cowork ficou perto da versão final em cerca de 10 dias. Esse ritmo não cabe num compromisso de Feature fechado no PI, e é mais um motivo para o SAFe ficar só na interface.

| Critério | AI-Native SAFe dentro do time | Builder pods + interface SAFe |
| Custo de processo | Papéis, eventos e trilha de certificação próprios | 3 papéis leves e cerca de 3h de ritual a cada 2 semanas |
| Onde se decide | Feature priorizada e comprometida no PI | Protótipo funcionando e uso real pelas squads |
| Ciclo de feedback | Ritmo do PI | Dias (bolts) e 2 semanas (bets) |
| Visibilidade para governança | Nativa | A mesma, via espelho automático no Jira |
| Risco político | Baixo | Médio, mitigado pelo espelho e pelo enquadramento como piloto |
| Maturidade | Framework lançado em jun/2026, guidance e cursos ainda saindo | Práticas já em produção na Anthropic e na OpenAI |

**Por que encaixa ainda melhor no caso de vocês:** os clientes são internos (as 130+ squads), então o gate de customer zero sai quase de graça. Toda ferramenta passa por 3 degraus: (1) o próprio time usa; (2) 2 ou 3 squads piloto usam; (3) rollout no ART. O degrau 3 só abre quando o uso semanal do piloto bater um número que vocês definirem. Adoção vira a métrica de produto do time, e é exatamente o que a liderança quer ver.

**Quando eu revisaria a decisão:** se o time passar de uns 3 pods trabalhando no mesmo produto, se a BU exigir compromisso em pontos por PI, ou se outros times começarem a entregar no mesmo repositório. Aí a sincronia que o SAFe oferece começa a pagar o custo.

## O que as big techs estão fazendo

Ninguém publicou um "Scrum para agentes". O padrão comum é outro: o gargalo saiu da escrita de código e foi para a **especificação, a revisão e o contexto que o agente recebe**. Os processos estão sendo redesenhados em volta disso.

| Empresa / fonte | O que mudou no processo | O que levamos para o time |
| OpenAI — Harness engineering | Princípio "humans steer, agents execute". AGENTS.md de ~100 linhas como índice, com docs/ versionado como sistema de registro. Planos de execução (ativos, concluídos, dívida técnica) ficam no repo. Review majoritariamente agente-a-agente. Time de 3 a 7 engenheiros fez ~1.500 PRs (~3,5 PRs/eng/dia). Agentes de "garbage collection" abrem PRs de refatoração continuamente. | Repo como fonte da verdade; erro do agente vira melhoria do harness; limpeza contínua automatizada. |
| Anthropic — time do Claude Code | Sessões paralelas em worktrees. A maioria das sessões começa em Plan Mode. Um CLAUDE.md compartilhado no git recebe uma regra nova sempre que o agente erra, e o time atualiza o arquivo direto no PR. O foco humano fica em review e direção. | Plan Mode como "refinamento"; CLAUDE.md/skills/permissões como ativo do time, versionado. |
| Anthropic — estudo de emprego (out/2026) | ~80% do tempo de sessão interativa é o agente esperando input humano. "Meta-trabalho" (skills, specs, reviews, dashboards) foi de 10% para 22% das sessões. Tempo em reunião subiu ~20%: alinhamento presencial ficou mais importante. O estudo desencoraja trabalho privado e não registrado. | Atenção humana é o recurso escasso. Ritual de alinhamento curto e bom vale mais que cerimônia longa. Decisões ficam registradas. |
| Google | 75% do código novo é gerado por IA e aprovado por engenheiros. Uma migração complexa saiu 6x mais rápida com agentes + humanos. | Review humano continua como ponto de controle; migrações e refactors são o primeiro alvo de agentes assíncronos. |
| AWS — AI-DLC | Três fases (Inception, Construction, Operations). Sprints viram bolts de horas ou dias. Mob Elaboration: o time inteiro valida as perguntas e propostas da IA antes de construir. | Mob Elaboration como ritual de shaping; ciclos curtos dentro da iteração. |
| GitHub — Spec Kit | Spec-driven development: constitution → specify → plan → tasks → implement, tudo em markdown no repo. | Template de bet (intent/spec/plan/tasks) e uma "constitution" do time. |
| DORA 2025 — AI Capabilities Model | IA é amplificador: aumenta throughput, mas também a instabilidade de entrega. Sete capacidades amplificam o ganho, entre elas postura clara sobre IA, dados internos acessíveis à IA, lotes pequenos e plataforma interna de qualidade. | Lotes pequenos e plataforma interna (nossos MCPs/skills) são pré-requisito, não luxo. |
| Scaled Agile — AI-Native SAFe | Lançado em junho/2026. Times AI-Native rodam em fluxo contínuo, sem intervalos rígidos de reunião, organizados em Align / Sense / Respond. Capacidades do time: Product, Builder, Domain Expert e AI. Novo papel: AI Value Architect. | Cobertura oficial dentro do SAFe para o que estamos propondo. |
| Atlassian — Rovo MCP | Mais de 5 milhões de chamadas de ferramenta por dia: agentes já criam, editam e transicionam issues. | O Jira pode ser mantido por agentes, não por pessoas. |

## Princípios do modelo

Oito regras decidem os casos que o processo não cobre.

- **Humanos guiam, agentes executam.** O dev é dono da intenção, dos critérios de aceite e da verificação. Não é dono da digitação.
- **O repo é o sistema de registro.** Spec, plano, decisões e dívida técnica ficam versionados em markdown. O Jira espelha isso e é gerado por agente.
- **Spec antes de código.** Todo slice nasce de um plano revisado (Plan Mode ou /plan). O refinamento acontece no spec, não numa reunião de grooming.
- **Lotes pequenos.** 1 slice = 1 PR revisável em até ~15 min. Bet grande demais vira duas bets.
- **Todo erro do agente melhora o harness.** Errou uma vez → regra no CLAUDE.md, skill, linter ou teste. Corrigir "no prompt" não conta.
- **A atenção humana é o gargalo.** O WIP é limitado por review pendente, não por tarefas abertas.
- **Visibilidade por telemetria.** Se alguém precisa perguntar o status, falta automação, não reunião.
- **Decisão registrada ou não existe.** ADR curto no repo ou thread no canal do time, nunca só na cabeça de alguém. O agente também precisa desse contexto.
- **Geral antes de específico.** É a bitter lesson, que o time do Claude Code mantém emoldurada na parede. Antes de criar mais uma skill de nicho, melhore o contexto geral (MCPs, CLAUDE.md, skills genéricas). O Sweeper desliga as específicas que não pegaram.

## Estrutura do time e papéis

Com 10 devs, a proposta são 3 builder pods de 3 pessoas, um por linha de produto, mais o lead. Como no time do Claude Code, o título diz a especialidade (front, plataforma, dados), não o limite do que a pessoa faz. Cada pod tem dono claro e conversa pouco com os outros, o que mantém a coordenação barata.

| Pod | Escopo | Exemplos de bets |
| **Dev Tooling** | Coding agents, skills, MCPs, CLIs, templates de harness para as squads | Skill de migração Angular, MCP de catálogo de APIs, CLI de bootstrap de repo |
| **Agent Platform** | Orquestração e plataforma de agentes, execução assíncrona, guardrails | Runner de agentes em background, políticas de permissão, observabilidade de sessões |
| **Insights & Enablement** | DORA, AI usage, dashboards das squads, capacitação | Pipeline de telemetria, painel por ART, trilhas e office hours |

**Papéis****: os 5 arquétipos do time do Claude Code.** Boris Cherny descreve cinco modos de contribuir que se formam no time, e nenhum deles é cargo (Aakash Gupta). A mesma pessoa prototipa na segunda e faz limpeza na sexta: o arquétipo segue o trabalho. A tabela adapta os cinco ao portfólio de vocês (skills, MCPs, CLIs, plataforma, painéis).

| Arquétipo | O que faz aqui | Estágio do produto | Sinal de que está faltando |
| Prototyper | Faz 3 a 5 versões de ~30 min por ideia e mata a maioria; alimenta o Shape | Ideia | Bet entra em build sem nenhuma alternativa testada (o autor aponta isso como o buraco típico de times enterprise) |
| Builder | Leva o protótipo que sobreviveu até produção: testes, permissões, segurança, telemetria | Protótipo → squads piloto | Protótipo bom que nunca sai do time |
| Grower | Acompanha o uso nas squads piloto, conversa com usuários e itera toda semana até o gate de adoção | Piloto → ART | Ferramenta lançada que ninguém usa duas vezes |
| Sweeper | Simplifica e desliga: skills e MCPs abaixo do piso de adoção, código morto, regras velhas do CLAUDE.md. Cuida também do harness | Contínuo | Catálogo de skills crescendo mais rápido que o uso |
| Maintainer | Mantém rápido e confiável o que as squads já usam: plataforma de agentes, pipeline de telemetria, MCPs críticos | Maduro | Incidente e chamado de suporte repetidos |

**Como alocar:** no Betting, cada pessoa declara seu arquétipo principal na quinzena, conforme o estágio das bets e dos produtos. Duas regras fixas:

- Todo ciclo tem pelo menos 1 Sweeper, em rodízio. Ele absorve o antigo papel de Harness Keeper.
- Todo produto que as squads já usam tem um Maintainer nomeado.

Três responsabilidades continuam existindo, mas não são arquétipos:

- **Lead / AI Value Architect (você):** escolhe as bets, cuida da arquitetura transversal e da interface com o ART. Com protótipo morrendo em horas, o gargalo passa a ser quem avalia. Saber olhar 15 protótipos e apontar os 3 que valem escalar vira o trabalho mais importante do papel.
- **Bet Owner:** responde pelo resultado de uma bet e conduz a Mob Elaboration.
- **Flow Steward (rotativo):** olha a fila de review, garante que o Jira gerado está coerente e prepara a demo.

## Ciclo de trabalho: Intent → Shape → Slice → Build → Verify → Ship

Uma bet tem apetite de 1 a 2 semanas e anda em bolts de horas a dias. O humano atua no Intent, no Shape e no Verify. Todo erro pego no Verify volta para o harness, e a próxima sessão já começa sabendo.

Em bet exploratória, o Shape começa com protótipo, não com spec. O Prototyper faz de 3 a 5 versões de ~30 min, o pod mata a maioria e só a sobrevivente vira spec.md. O spec documenta o que o protótipo provou. No time do Claude Code, cerca de 80% das 50 a 100 iterações da animação de carregamento nunca foram lançadas, e esse descarte faz parte do trabalho.

[embed {'id': '.16032', 'rev': '12', 'h': '82c69b30', 'caption': 'ciclo de uma bet · 6 etapas + loop do harness', 'ref': 'node/44fa2b66-7a28'}]

**Definition of Ready de um slice** (o agente checa antes de começar):

- Link para spec.md e plan.md aprovados
- Critérios de aceite em bullets
- Como verificar (testes, comando, tela)
- Tier de risco (0, 1 ou 2)

**Definition of Done:**

- CI verde e agente de review sem pendências
- Review humano conforme o tier
- Docs e tasks.md atualizados pelo agente; Story transicionada
- Se o agente errou algo no caminho, a regra ou o teste novo está no PR

## Toolkit de skills: o que pegar de mattpocock/skills e pstack

Os dois repositórios se completam. O mattpocock/skills cobre bem a parte de cima do ciclo: entrevista, spec e tickets. O pstack cobre a de baixo: prova de que funciona, review adversário e trilha de decisões. Os dois são MIT. A proposta é manter um fork interno fixado com a nossa versão de cada skill, em vez de instalar os plugins direto.

| Etapa | mattpocock/skills | pstack | Nossa versão |
| Shape | grill-with-docs (entrevista em rodadas, atualiza GLOSSARY.md e ADRs), prototype, to-questionnaire | architect (tipos e assinaturas a partir de 2+ alternativas), in-your-own-words | /bet-shape: grill-with-docs + architect, saída em pt-BR em docs/bets/ |
| Spec | to-spec (antigo to-prd) | Sem skill de planejamento, de propósito: o autor defende que o código é o melhor spec | /bet-spec: template do to-spec traduzido, grava spec.md |
| Slice | to-tickets (antigo to-issues): fatias verticais tracer bullet com dependências | — | /bet-sync: to-tickets + mapeamento para o MCP do Atlassian |
| Build | implement, tdd, implement-spec (subagentes em worktrees + merger) | tdd, swarm/arena, typescript-best-practices | implement + tdd como padrão; implement-spec só em Tier 0/1 |
| Verify | code-review (2 subagentes: padrões do repo e aderência ao spec), diagnosing-bugs | interrogate (só mantém achados provados por execução), create-verification-skill, blast-radius | code-review como agente de review obrigatório + uma skill de verificação por repo |
| Evidência | pr (antes/depois, porta de mão única ou dupla, blast radius) | show-me-your-work (TSV de decisões + seção Attention), ketchup | .audit/<CHAVE-JIRA>.tsv no PR + corpo de PR no formato do pr |
| Harness | retro, writing-for-agents | reflect, correct, biblioteca de principle-* | Harness Retro roda retro + correct |
| Handoff | handoff | recall | handoff com varredura de segredos |

**Show-me-your-work como mecanismo de visibilidade.** O agente mantém um TSV só de acréscimo, uma linha por decisão. As colunas são momento, fase, decisão, porquê, evidência (SHA, PR, arquivo:linha) e resultado. Linha errada nunca é editada; uma nova a substitui. Commitado por PR e lido pelo painel, ele substitui o "qual o status?": dá para ver decisões por PR, taxa de inconclusivos e cobertura de evidência. Falta uma coluna de ticket, então pomos a chave do Jira no nome do arquivo.

**Adaptações obrigatórias antes de usar:**

- **Jira:** o mattpocock deixa Jira fora de escopo de propósito. Escrevemos o docs/agents/issue-tracker.md mapeando cada operação (criar, ler, JQL, comentar, transicionar, link de bloqueio, Epic) para o MCP do Atlassian. Também ajustamos o code-review para achar o spec pela chave PROJ-123, e não por #123.
- **pt-BR:** templates de spec, ticket e brief traduzidos, mais uma regra no CLAUDE.md fixando a saída em português. O GLOSSARY.md fica bilíngue, com termos de negócio em PT.
- **Autonomia:** o pstack abre PR pronto (não draft) e segue sem perguntar em trabalho reversível. No fork: PR em draft, sem merge automático fora do Tier 0, e um hook bloqueando push forçado e reset destrutivo, no estilo do git-guardrails do mattpocock.
- **Modelos:** o pstack manda código para o Grok e julgamento para o Opus. No Claude Code, os reviews entre famílias de modelo viram da mesma família, o que enfraquece o interrogate. Mapear só para os modelos aprovados pelo banco.
- **Dados e rede:** automate-me, recall e reflect leem transcrições locais e precisam de revisão de privacidade. research e improve-codebase-architecture dependem de web e CDN. O wizard grava segredo em .env; trocar pelo cofre do banco.
- **Não adotar:** no-comments (conflita com padrão de código do banco), make-bot-ui (só funciona no Cursor), as skills de verificação formal por enquanto, e os skills ainda em construção do mattpocock.

Observação: as cópias de to-prd e to-issues que eu tenho aqui são a versão anterior. No upstream elas viraram to-spec e to-tickets, e o CONTEXT.md virou GLOSSARY.md.

## Repo como sistema de registro, Jira como espelho

O dev escreve no repo, onde o agente lê. O Jira é atualizado por agente, e a governança do ART continua vendo tudo.

**Layout padrão de um repositório do time** (adaptado do harness da OpenAI e do Spec Kit):

[codeBlock] AGENTS.md / CLAUDE.md      # ~100 linhas: mapa, não manual
constitution.md            # princípios, gates de qualidade, o que nunca fazer
docs/
  architecture.md
  bets/
    BET-042-mcp-catalogo/
      intent.md            # problema, apetite, fora de escopo
      spec.md              # comportamento + critérios de aceite (bullets)
      plan.md              # plano técnico gerado em Plan Mode e revisado
      tasks.md             # slices; cada um vira Story no Jira
      decisions/           # ADRs curtos
  exec-plans/active|completed/
  tech-debt.md
.claude/
  skills/  commands/  agents/  settings.json   # permissões compartilhadas

**Como o Jira se mantém sozinho:**

- Uma skill /bet-sync lê intent.md e tasks.md e cria ou atualiza a Feature e as Stories via MCP do Atlassian. Os critérios de aceite vão em bullets, copiados do spec.
- Cada branch/PR leva a chave da Story (BET-042/S3). Smart commits ou um job de CI transicionam o status: PR aberto = In Review, merge = Done.
- No merge, o agente comenta na Story um resumo do PR e o link da execução.
- Story points: não estimamos. Se o ART exigir número, usamos valor fixo por slice (ex.: 1) e reportamos throughput e cycle time, que são mais honestos com agentes.
- Bug, dúvida ou dívida descoberta no meio do caminho: o agente abre a issue, linka na bet e registra em tech-debt.md.

Resultado esperado: o dev não abre o Jira para escrever, só para consultar. A Feature e as Stories continuam rastreáveis para o PI.

## Cadência e rituais

Somando tudo, dá cerca de 3h por pessoa a cada 2 semanas de ritual síncrono. O resto é assíncrono e gerado por bot. Os rituais seguem o Align / Sense / Respond do AI-Native SAFe.

| Ritual | Tipo | Quando | Duração | Saída |
| Digest diário | Sense, assíncrono | Todo dia, 9h, no canal do time | 0 min (bot) | Agente publica o que mergeou, o que está em review há mais de 24h e o que travou, por pessoa |
| Sync de bloqueios | Respond | Seg, qua e sex | 15 min | Só bloqueios e pedidos de review; cancela se o digest estiver limpo |
| Mob Elaboration | Align | Sob demanda, por bet (~2 por semana no time) | 60–90 min | Pod + domain expert + agente ao vivo: intent → spec → plano aprovado → slices |
| Betting | Align | Início do ciclo (dia 1 da iteração) | 45 min | Bets escolhidas por pod, com apetite; o resto volta pra pilha, sem backlog infinito |
| Demo | Sense | Fim do ciclo | 45 min | Demo ao vivo + painel de métricas do ciclo; vira insumo pra System Demo |
| Harness Retro | Respond | Fim do ciclo | 30 min | Top 5 erros dos agentes → regra, skill, linter ou teste. A retro só fecha com PRs abertos |
| Dia de limpeza | Respond | 1 dia por ciclo (no começo) | 1 dia | Dívida técnica e doc gardening. A meta é automatizar isso com agentes de limpeza até o dia sumir |

Três regras de review mantêm o fluxo andando:

- PR aguardando review tem prioridade sobre começar slice novo.
- No máximo 2 slices em construção por pessoa. Sessões de agente paralelas são ilimitadas; o que é limitado é o que espera revisão humana.
- O revisor usa um agente de review antes de ler. O humano só lê depois que o agente de review e o CI passam.

## Métricas e visibilidade

Um painel único, alimentado por Git, CI, Jira e telemetria dos agentes, responde "quem está fazendo o quê" sem ninguém reportar. É o mesmo pipeline que vocês já constroem para as squads: o time vira o primeiro cliente do próprio produto.

| Camada | Métrica | Para que serve |
| Visibilidade | Slices por pessoa (em construção / em review / done), bets por pod | Responde "quem faz o quê" para o lead e o RTE |
| Fluxo | Cycle time intent → produção, cycle time por slice, idade da fila de review | Mostra onde o trabalho espera |
| Entrega (DORA) | Frequência de deploy, lead time de mudança, taxa de falha de mudança, tempo de recuperação | Pega o "mais rápido, mas mais frágil" que o DORA 2025 aponta |
| Uso de IA | % de PRs de autoria de agente, sessões por dev/dia, custo de tokens por slice, tempo humano de review por PR | Mostra eficiência e custo do AIDLC |
| Harness | Regras/skills adicionadas por ciclo, reincidência do mesmo erro de agente, PRs abertos pelos agentes de limpeza | Mede se o time está compondo ganho |

Regra anti-vaidade: nada de ranking de dev por tokens ou por PRs. A métrica de pessoa é o que ela entregou e destravou, não o volume que o agente gerou.

## Encaixe com SAFe / ART

Esta é a interface do time com o ART, não o processo interno (veja a Decisão lá em cima). Os artefatos SAFe continuam existindo, o que muda é quem os produz. A Scaled Agile lançou o AI-Native SAFe em junho de 2026 com times AI-Native em fluxo contínuo, então a proposta pode ser apresentada como piloto de AI-Native Team dentro do ART.

| SAFe | Neste modelo | Quem produz |
| Epic / tema | Intent | Lead + PM |
| Feature | Bet (com apetite) | Bet Owner; o agente cria no Jira |
| Story | Slice (tasks.md) | Agente, a partir do spec |
| Iteração (2 sem) | Ciclo: Betting → build → Demo + Harness Retro | Time |
| PI Planning | Bets candidatas com apetite e risco, em vez de stories estimadas | Lead + Bet Owners |
| System Demo | Demo do ciclo + painel de métricas | Flow Steward |
| Inspect & Adapt | Harness Retro consolidada + tendências DORA/AI usage | Time |
| Capacidade / pontos | Throughput de slices e cycle time (ponto fixo por slice, se exigido) | Gerado |

Como vender para o RTE: o ART não perde rastreabilidade (Feature e Story seguem no Jira, até mais atualizadas). Ganha um caso real de AI-Native SAFe para levar às outras 130+ squads. E vocês fazem o papel de AI Value Architect que o próprio framework criou.

## Rollout em 90 dias e riscos

A ideia é começar com 1 pod e o harness mínimo, provar em 2 ciclos e só então escalar para os 3 pods e apresentar ao ART.

**Dias 0–30: fundação (1 pod piloto)**

- Escrever constitution.md do time e o template de bet (intent/spec/plan/tasks)
- CLAUDE.md compartilhado + .claude/settings.json com permissões do time em todos os repos
- Skill /bet-sync (Jira via MCP) e transição de status por PR/CI
- Digest diário por bot no canal do time
- Rodar 2 bets do piloto ponta a ponta, com Mob Elaboration

**Dias 31–60: escala para 3 pods**

- Pods formados, arquétipos declarados no Betting, Sweeper e Flow Steward rodando, piso de adoção para desligar ferramenta definido
- Agente de review obrigatório antes do humano; tiers de review por risco
- Painel de fluxo + DORA + AI usage do próprio time
- Primeira Harness Retro com PRs de regra/skill/linter

**Dias 61–90: automação e governança**

- Agentes de limpeza em background (dívida, docs desatualizadas) para encolher o dia de limpeza
- Apresentar ao RTE como piloto AI-Native Team, com números de 3 ciclos
- Empacotar o modelo (templates, skills, painel) como produto para as squads

**Tiers de review por risco** (ajustar com segurança e compliance do banco):

| Tier | Exemplos | Review |
| 0 | Docs, testes, refactor mecânico, limpeza | Agente de review + CI; merge por 1 humano em lote |
| 1 | Feature em ferramenta interna | Agente de review + 1 humano |
| 2 | Auth, dados de cliente, permissões de agente, algo exposto às squads | Agente de review + 2 humanos, um deles o Bet Owner |

**Riscos e mitigação:**

| Risco | Mitigação |
| Fila de review vira o novo gargalo | WIP limitado por review pendente, agente de review antes do humano, PRs pequenos |
| "AI slop" e dívida acumulando | Constitution + linters com mensagem de correção para o agente, agentes de limpeza, tech-debt.md vivo |
| Atrofia de habilidade (citada no estudo interno da Anthropic) | Mob Elaboration e review em par, todo mundo passa por Builder e Sweeper, slices "feitos à mão" por escolha |
| Atrito com a governança SAFe / PMO | Jira 100% atualizado por agente, mapeamento explícito para artefatos SAFe, enquadrar como AI-Native SAFe |
| Segurança e compliance (banco) | Permissões versionadas, sem modo sem permissão em repos sensíveis, trilha de auditoria das sessões, Tier 2 obrigatório |
| Custo de tokens sem controle | Custo por slice no painel, revisão mensal de modelos e de onde rodar agentes assíncronos |

## Fontes

- Harness engineering: leveraging Codex in an agent-first world — OpenAI (fev/2026)
- How employment is changing at Anthropic — Anthropic (out/2026)
- How AI is transforming work at Anthropic — Anthropic (dez/2025)
- Claude Code creator workflow — InfoQ (jan/2026)
- Google says 75% of its new code is written by AI — The Decoder (abr/2026)
- AI-Driven Development Life Cycle — AWS DevOps Blog e workflows open source do AI-DLC
- Spec-driven development with Spec Kit — Microsoft Developer Blog
- DORA AI Capabilities Model — Google Cloud Blog (set/2025)
- AI-Native SAFe Session 3: Teams, Roles, and ARTs — Scaled Agile
- Atlassian Rovo MCP enhancements — Atlassian e docs do Rovo MCP Server
- How Anthropic's Claude Code AI-native team actually ships — Product School (out/2026)
- Meaghan Choi (Anthropic) sobre a evolução do Claude Code — The Product Podcast
- mattpocock/skills — GitHub
- pstack: show-me-your-work — cursor/plugins

