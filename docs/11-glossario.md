# Glossário

Os termos que o time usa, em ordem alfabética. Quando o termo tem nome em inglês, ele aparece entre parênteses. O glossário vivo mora no KB, em `glossary/`, um arquivo por termo, com `aliases` e `avoid`. A skill `grill` grava termo novo ali.

| Termo | O que é |
|---|---|
| ADR (Architecture Decision Record) | registro de uma decisão difícil de desfazer, surpreendente sem contexto e fruto de trade-off real. Mora em `methodology/adr/` ou `products/<p>/adr/` |
| Adoption Report | relatório semanal de adoção de um produto, com uso semanal, retenção e veredito do degrau |
| agente de review | o subagente que revisa o PR antes do humano, contra o spec; no t0, a skill `slice-verify` |
| apetite (appetite) | quanto tempo o time aceita gastar numa bet, em duração ISO: `P1D`, `P1W`, `P2W`. Máximo de 1 dia na rápida e 2 semanas na bet |
| aposta (bet) | trabalho com apetite de até 2 semanas que o Bet Owner decidiu fazer depois de um protótipo. Também nomeia a decisão em si (`gate aposta`). No Jira, vira Feature. Evite: projeto, épico, feature |
| ART (Agile Release Train) | o trem do SAFe de que o time faz parte; a Demo segue a iteração dele |
| `.audit/<KEY>.tsv` | trilha de decisões de um slice, uma linha por decisão, commitada no PR |
| bet | ver aposta. Também nomeia a trilha completa, em oposição à rápida |
| Bet Owner | sênior que facilita a daily do pod, decide o que vira bet, aprova o spec e responde pelo resultado |
| blast radius (raio de impacto) | a análise, com prova executada, do que uma mudança Tier 2 pode quebrar |
| Builder | todo mundo do time, no papel de quem prototipa, constrói e revisa |
| card de contexto (context card) | o `AGENTS.md` gerado na raiz do workspace, com a bet ativa, os repos e o mapa do KB; até 8.000 caracteres |
| change set | os PRs dos slices de uma bet, nos vários repos, com a ordem de merge |
| CODEOWNERS | o arquivo que diz quem aprova PR em cada caminho do KB, na raia de conhecimento |
| costura (seam) | o ponto do código onde o comportamento é testado. O spec combina as costuras, e o ideal é uma só |
| critério de aceite (acceptance criterion) | afirmação de comportamento observável e verificável, sempre em bullet, nunca em Gherkin |
| customer zero | o time como primeiro cliente das próprias ferramentas, antes das squads |
| daily do pod | ritual diário de 30 a 45 minutos em que o pod prototipa, aposta, especifica e planeja com o agente ao vivo |
| daily do time | ritual diário de 10 minutos só para bloqueios e pedidos de review |
| degrau (adoption rung) | cada passo de adoção de um produto: 1 é o time, 2 são de 2 a 3 squads piloto, 3 é o ART. Quem decide a subida é o Lead/AIVA, com números |
| delta | o pedaço do card que mudou desde que ele foi gerado, injetado no início da sessão; até 3.000 caracteres |
| derivado (derived) | arquivo ou chave que só o `kb-render` escreve: `index.md`, `log.md`, `changeset.md`, estado do slice depois de `ready`, `pr`, `jira`, `verified` |
| digest | o status que o bot imprime na abertura da daily do time: merges, reviews parados há mais de 24h e bloqueios |
| DoR / DoD (Definition of Ready / Done) | o que um slice precisa ter para começar e para terminar |
| Domain Expert | dev de squad que o Bet Owner chama para a daily do pod quando a bet toca o trabalho da squad |
| draft | estado em que todo PR nasce e fica até um humano marcar pronto |
| "Em minhas palavras" | seção do PR, escrita pelo autor humano, com o que muda, por que e o que pode dar errado. Obrigatória em PR de júnior e em todo Tier 2 |
| Eval Suite | as suítes de capacidade e de regressão de um produto, declaradas em `products/<p>/evals.md` |
| Flow Steward | rodízio de 2 semanas: facilita daily do time, Demo e Retro, cuida da fila de review e da coerência entre Jira e KB |
| gate | o check de CI que confere uma decisão humana no PR: `aposta`, `spec` e, previsto, `degrau` |
| harness | tudo o que cerca o agente para ele errar menos: `AGENTS.md`, regras, skills, linters, testes, hooks e CI |
| Harness Health | ritual semanal de 20 minutos em que erros repetidos do agente sobem a escada do harness |
| Harness Item | registro de uma classe de erro de agente, com as ocorrências e o degrau da escada escolhido |
| Harness Keeper | rodízio de 2 semanas que cuida do harness, do KB e facilita o Harness Health |
| Idea | a ideia registrada no KB, com problema, para quem, sinal e o veredito do protótipo |
| kb-render | o workflow do KB que escreve os arquivos e as chaves derivados, serializado |
| KB (knowledge base) | o repositório OKF do time, `t0-kb`, sistema de registro de tudo o que foi decidido |
| kill | matar uma ideia ou bet. Na Idea, é o veredito `mata`; na Bet, `t0 log kill`. Conta como resultado |
| Lead / AIVA (AI Value Architect) | o Chapter Lead, que escolhe bets com PM e RTE, faz a interface com o ART e decide os degraus |
| manifesto | o `products/<p>/workspace.md`, que lista os repos de um produto |
| MCP `t0-kb` | o servidor MCP local, por stdio, que deixa o agente buscar, ler e registrar no KB |
| mob | trabalho em grupo com o agente ao vivo, como na daily do pod |
| OKF | o formato do bundle de conhecimento: Markdown com frontmatter, `index.md` por pasta, `log.md` e um profile de tipos |
| piloto (pilot squads) | as 2 ou 3 squads do degrau 2 |
| pod | grupo do time dono de um produto: Dev Tooling, PACO, Portal do time e Métricas |
| Policy | regra do time que vive no KB e muda por PR sem release do toolkit: WIP, modelos, retenção, pisos |
| `[PRECISA ESCLARECER]` | marcador de decisão em aberto no spec. Com marcador aberto, o `gate spec` recusa |
| profile `t0-team` | a definição dos tipos, chaves e estados do KB, gerada em `profile.md` |
| PROPOSTA | marca de número ou piso que ainda não está valendo (`state: proposed`) |
| protótipo (prototype) | código descartável, fora do main, que responde a pergunta de uma ideia e termina num veredito |
| raia (write lane) | cada um dos três caminhos de escrita no KB: registros, conhecimento e derivados |
| rápida, trilha (fast track) | trilha para ajuste, bugfix ou melhoria que cabe em 1 dia, sem spec, com um slice que já nasce com "atual, esperado, o que não muda" e um teste |
| registro de passo (Step) | arquivo novo e de nome único em `steps/`, gravado por `t0 log` ou por evento de PR |
| Ritual Record | o registro de uma sessão de ritual, com decisões e donos, gravado pelo `t0 ritual close` |
| rodízio (rotation) | a troca de Harness Keeper e Flow Steward a cada 2 semanas, gravada no fechamento da Demo |
| same-family | rótulo de saída de review ou comparação em que todos os modelos são da mesma família; a concordância vale menos |
| slice | fatia vertical de uma bet: um repo, um PR, revisável em até 15 minutos. No Jira, vira Story |
| spec | o contrato de uma bet: histórias, critérios de aceite, como verificar, tier e, quando precisa, Design. Congela no ship |
| spec vivo (living spec) | a seção do `product.md` com o comportamento atual do produto e os contratos das superfícies |
| spool | a pasta local `~/.t0/spool/`, onde os registros esperam o push |
| sunset | desligar uma ferramenta ou skill que não pegou |
| Tier | o nível de review de um PR: 0, 1 ou 2 |
| trailer | linha no corpo do PR ou do commit que liga ao KB: `Bet:`, `Story:`, `Jira-Feature:`, `Depends-on:`, `KB-Context:` |
| Transcript | a transcrição redigida de um ritual, com `stale_after` obrigatório |
| `verified` | a chave que diz qual humano confirmou e quando. Em decisão de PR, vem das aprovações |
| veredito (verdict) | o resultado do protótipo: `segue`, `ajusta` ou `mata` |
| `verify-<app>` | a skill local de cada repo de produto que sobe, dirige e prova o app real |
| WIP (work in progress) | no máximo 2 slices em construção por pessoa |
| workspace | a pasta `~/ws/<produto>/` com o KB e os repos do produto clonados lado a lado |
