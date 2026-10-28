# Glossário

Estes são os termos que o time usa, em ordem alfabética. Quando o termo tem nome em inglês, ele aparece entre parênteses. O glossário vivo fica no KB, na pasta `glossary/`, com um arquivo por termo e as chaves `aliases` e `avoid`. A skill `grill` grava ali os termos novos.

| Termo | O que é |
|---|---|
| ADR (Architecture Decision Record) | registro de uma decisão que é difícil de desfazer, surpreende quem não tem o contexto e resulta de um trade-off real. Fica em `methodology/adr/` ou `products/<p>/adr/` |
| Adoption Report | relatório semanal de adoção de um produto. Traz o uso semanal, a retenção e o veredito do degrau |
| agente de review | subagente que revisa o PR contra o spec antes do revisor humano. No t0, é a skill `slice-verify` |
| apetite (appetite) | tempo que o time aceita gastar numa bet, escrito em duração ISO: `P1D`, `P1W`, `P2W`. O máximo é 1 dia na trilha rápida e 2 semanas na bet |
| aposta (bet) | trabalho com apetite de até 2 semanas que o Bet Owner decidiu fazer depois de um protótipo. No Jira, vira Feature. A palavra também nomeia a própria decisão (`gate aposta`). Evite: projeto, épico, feature |
| ART (Agile Release Train) | o trem do SAFe de que o time faz parte. A Demo segue a iteração do ART |
| `.audit/<KEY>.tsv` | trilha das decisões de um slice, com uma linha por decisão, commitada no PR |
| bet | o mesmo que aposta. Também nomeia a trilha completa, em oposição à trilha rápida |
| Bet Owner | sênior que decide o que vira bet, aprova o spec e responde pelo resultado. Também facilita a daily do pod |
| blast radius (raio de impacto) | análise do que uma mudança Tier 2 pode quebrar, com prova executada |
| Builder | papel de todo mundo do time: quem prototipa, constrói e revisa |
| card de contexto (context card) | o `AGENTS.md` gerado na raiz do workspace. Traz a bet ativa, os repos e o mapa do KB, em até 8.000 caracteres |
| change set | conjunto dos PRs dos slices de uma bet, nos vários repos, com a ordem de merge |
| CODEOWNERS | arquivo que define quem aprova PR em cada caminho do KB, na raia de conhecimento |
| costura (seam) | ponto do código onde o comportamento é testado. O spec combina quais são as costuras, e o ideal é uma só |
| critério de aceite (acceptance criterion) | afirmação sobre um comportamento observável e verificável. É escrito sempre em bullet, nunca em Gherkin |
| customer zero | o próprio time como primeiro cliente das suas ferramentas, antes das squads |
| daily do pod | ritual diário de 30 a 45 minutos em que o pod prototipa, aposta, especifica e planeja com o agente ao vivo |
| daily do time | ritual diário de 10 minutos, só para bloqueios e pedidos de review |
| degrau (adoption rung) | cada passo na adoção de um produto: 1 é o time, 2 são de 2 a 3 squads piloto e 3 é o ART. O Lead/AIVA decide a subida, com números |
| delta | a parte do card que mudou desde que ele foi gerado. Entra no início da sessão, com até 3.000 caracteres |
| derivado (derived) | arquivo ou chave que só o `kb-render` escreve: `index.md`, `log.md`, `changeset.md`, estado do slice depois de `ready`, `pr`, `jira`, `verified` |
| digest | status que o bot imprime na abertura da daily do time: merges, reviews parados há mais de 24h, bloqueios abertos e bloqueios sem dono |
| DoR / DoD (Definition of Ready / Done) | o que um slice precisa ter para começar (DoR) e para terminar (DoD) |
| Domain Expert | dev de uma squad que o Bet Owner chama para a daily do pod quando a bet toca o trabalho dessa squad |
| draft | estado em que todo PR nasce. O PR fica em draft até um humano marcar como pronto |
| "Em minhas palavras" | seção do PR em que o autor humano escreve o que muda, por que muda e o que pode dar errado. É obrigatória em PR de júnior e em todo Tier 2 |
| Eval Suite | conjunto das suítes de capacidade e de regressão de um produto, declaradas em `products/<p>/evals.md` |
| Flow Steward | papel em rodízio de 2 semanas. Quem está no papel facilita a daily do time, a Demo e a Retro, cuida da fila de review e da coerência entre Jira e KB |
| forge | servidor git com PR (GitHub). Sem forge, o PR em draft é a branch local, com o corpo em `.t0/pr/<branch>.md`, e ninguém faz push |
| gate | check de CI que confere uma decisão humana no PR. Existem o `aposta` e o `spec`; o `degrau` está previsto |
| harness | tudo o que cerca o agente para ele errar menos: `AGENTS.md`, regras, skills, linters, testes, hooks e CI |
| Harness Health | ritual semanal de 20 minutos em que os erros repetidos do agente sobem a escada do harness |
| Harness Item | registro de uma classe de erro do agente, com as ocorrências e o degrau da escada escolhido |
| Harness Keeper | papel em rodízio de 2 semanas que cuida do harness e do KB e facilita o Harness Health |
| Idea | ideia registrada no KB, com o problema, para quem é, o sinal e o veredito do protótipo |
| kb-render | workflow do KB que escreve os arquivos e as chaves derivados. Roda serializado, uma execução por vez |
| KB (knowledge base) | o repositório OKF do time, `t0-kb`. É o sistema de registro de tudo o que foi decidido |
| kill | matar uma ideia ou uma bet. Na Idea, é o veredito `mata`; na Bet, é o `t0 log kill`. Matar conta como resultado |
| Lead / AIVA (AI Value Architect) | o Chapter Lead. Escolhe as bets com PM e RTE, faz a interface com o ART e decide os degraus |
| manifesto | o arquivo `products/<p>/workspace.md`, que lista os repos de um produto |
| MCP `t0-kb` | servidor MCP local, por stdio, que deixa o agente buscar, ler e registrar no KB |
| mob | trabalho em grupo com o agente ao vivo, como na daily do pod |
| OKF | formato do bundle de conhecimento: Markdown com frontmatter, um `index.md` por pasta, `log.md` e um profile de tipos |
| piloto (pilot squads) | as 2 ou 3 squads do degrau 2 |
| pod | grupo do time que é dono de um produto. Os pods são Dev Tooling, PACO, Portal do time e Métricas |
| Policy | regra do time que vive no KB e muda por PR, sem release do toolkit: WIP, modelos, retenção, pisos |
| `[PRECISA ESCLARECER]` | marcador de decisão em aberto no spec. Enquanto houver marcador aberto, o `gate spec` recusa |
| profile `t0-team` | definição dos tipos, das chaves e dos estados do KB, gerada em `profile.md` |
| PROPOSTA | marca de um número ou piso que ainda não está valendo (`state: proposed`) |
| protótipo (prototype) | código descartável, fora do main, que responde à pergunta de uma ideia e termina num veredito |
| raia (write lane) | cada um dos três caminhos de escrita no KB: registros, conhecimento e derivados |
| rápida, trilha (fast track) | trilha para ajuste, bugfix ou melhoria que cabe em 1 dia. Não tem spec. Tem um slice que já nasce com "atual, esperado, o que não muda" e um teste |
| registro de passo (Step) | arquivo novo, de nome único, em `steps/`. É gravado pelo `t0 log` ou por evento de PR |
| Ritual Record | registro de uma sessão de ritual, com as decisões e os donos, gravado pelo `t0 ritual close` |
| rodízio (rotation) | troca de Harness Keeper e de Flow Steward a cada 2 semanas, gravada no fechamento da Demo |
| same-family | rótulo na saída de um review ou de uma comparação em que todos os modelos são da mesma família. Nesse caso, a concordância entre eles vale menos |
| slice | fatia vertical de uma bet: um repo, um PR, revisável em até 15 minutos. No Jira, vira Story |
| spec | contrato de uma bet: histórias, critérios de aceite, como verificar, tier e, quando precisa, Design. O spec congela no ship |
| spec vivo (living spec) | seção do `product.md` com o comportamento atual do produto e os contratos das superfícies |
| spool | pasta local `~/.t0/spool/`, onde os registros esperam o push |
| sunset | desligar uma ferramenta ou skill que não pegou |
| Tier | nível de review de um PR: 0, 1 ou 2 |
| trailer | linha no corpo do PR ou do commit que faz a ligação com o KB: `Bet:`, `Story:`, `Jira-Feature:`, `Depends-on:`, `KB-Context:` |
| Transcript | transcrição redigida de um ritual, com `stale_after` obrigatório |
| `verified` | chave que diz qual humano confirmou e quando. Numa decisão de PR, ela vem das aprovações |
| veredito (verdict) | resultado do protótipo: `segue`, `ajusta` ou `mata` |
| `verify-<app>` | skill local de cada repo de produto que sobe, dirige e prova o app real |
| WIP (work in progress) | limite de trabalho em andamento: no máximo 2 slices em construção por pessoa |
| workspace | a pasta `~/ws/<produto>/` com o KB e os repos do produto clonados lado a lado |
