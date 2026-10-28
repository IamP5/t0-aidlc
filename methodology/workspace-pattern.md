---
type: Playbook
title: "Workspace multi-repo com o KB como contexto"
description: "Como montar o workspace de um produto com 5 ou 6 repos, levar o KB t0-kb para toda sessão de agente (Claude Code, Copilot, Kiro e CI) e gravar de volta no KB sem conflito entre 10 pessoas."
uid: workspace-pattern
owner: role:lead
tags: [workspace, kb, agentes, multi-repo, t0, okf]
status: draft
trigger: "Dev novo no time, produto novo no KB, ou bet que vai mexer em mais de um repo."
steps_owner: role:lead
stale_after: 2027-01-27T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-27T23:10:00-03:00 }
---

# Workspace multi-repo com o KB como contexto

Este playbook define o ADR-0002. Fontes: `research/workspace-topology.md`, `research/workspace-agent-mechanics.md` e `research/multi-agent-compat.md`. Todo mecanismo que essas pesquisas não confirmam vem marcado **(verificar)** e precisa de teste antes do rollout. A seção 8 junta a lista.

**A ideia num parágrafo.** O KB (`t0-kb`) continua sendo um repo próprio, legível pelo time todo, e guarda um manifesto por produto. Cada dev tem um workspace de longa duração por produto, `~/ws/<produto>/`, com o KB e os repos do produto clonados lado a lado. Na raiz desse workspace mora um `AGENTS.md` gerado, o **card de contexto**: mapa do KB, bet ativa, papel de cada repo. As três ferramentas leem um `AGENTS.md` de raiz nativamente, então o piso do padrão não depende de plugin, de servidor nem de multi-root. Plugin, hooks e um MCP local (stdio) só deixam o card fresco e somam ferramentas. A escrita no KB tem três raias. Registros entram como arquivo novo, com nome único. Conhecimento entra por PR revisado. Arquivos derivados têm um único escritor, um workflow no próprio KB. No dia um não existe serviço hospedado.

---

## 1. Dá pra ter o repo OKF com os repos de produto como git submodules?

Funciona, mas a recomendação é não usar. A estratégia melhor é um manifesto no KB mais clones irmãos num workspace gerado. Android (`repo`), Zephyr (`west`) e Chromium (`gclient`) escolheram esse mesmo modelo, e nenhum usa submodule para isso (workspace-topology §8).

O que dá errado com submodule, no nosso dia a dia:

| Falha | O que acontece com a gente |
|---|---|
| HEAD destacado depois de `git submodule update` | O agente commita onde o HEAD estiver. O próximo `update` larga esses commits sem avisar. E commitar em HEAD solto é o comportamento padrão do agente. |
| Bump de ponteiro | Para alguém ver código novo, o KB precisa commitar um bump de gitlink. O histórico do KB vira "bump api", e conflito de gitlink não faz auto-merge. Com 10 pessoas isso é diário. |
| Código velho | O KB fixa o código de quando alguém deu o último bump. O agente raciocina sobre o `api/` da semana passada achando que é o de hoje. |
| Esqueceu `--recurse-submodules` | Diretório vazio, e o agente conclui "esse repo está vazio" e começa a scaffoldar do zero. Também quebra todo fluxo de worktree, porque worktree novo nasce com submodule não inicializado. |
| Controle de acesso invertido | O `.gitmodules` mostra a URL de todo repo de produto para quem lê o KB. Quem não tem acesso a um repo toma erro no init. O KB, que tem que ser o artefato mais legível do time, fica preso ao repo menos legível. |
| Credencial de CI | O CI do KB que faz checkout dos submodules precisa de um token que lê **todos** os repos de produto. Isso não passa na revisão de segurança do banco. |
| Dono errado | O KB passaria a versionar código que não é dele. O produto dependeria de um "release" do KB para ver o próprio código. |

O inverso também não serve. Se cada repo de produto embute o KB como submodule ou subtree, são seis versões fixadas do spec, todo write-back vira bump em três passos, e o agente continua sem enxergar os repos irmãos que a bet toca.

Quando faz sentido outra coisa: se os repos de um produto têm o mesmo dono, o mesmo pipeline e a mesma população de acesso, e as bets mexem em 3 ou mais deles quase sempre, vale avaliar um monorepo daquele produto depois de 2 ou 3 bets (workspace-topology §10). O KB continua separado mesmo assim, e este padrão segue valendo com 2 repos no workspace em vez de 7.

---

## 2. O padrão

### 2.1 Topologia

```
GitHub (GHE do banco)
  t0-kb                              KB. OKF v0.2 + profile t0-team. Legível pelo time todo.
  payments-{ledger,api,web,gateway,batch,admin}   repos de produto. ACL por repo, sem mudança.
  t0-toolkit                         CLI t0, plugin t0 (o pack t0-method empacotado), workflows reutilizáveis.

Máquina do dev
~/ws/payments/                       WORKSPACE DO PRODUTO (padrão). Não é repo git. Pasta que toda ferramenta abre.
  AGENTS.md                          GERADO: o card de contexto (2.6)
  .t0/
    workspace.json                   GERADO: sha do manifesto, repos clonados e ausentes (403)
    bet.json                         GERADO: bet ativa (t0 bet start|use)
    context.md                       GERADO: delta de frescor do card (2.4). Normalmente uma linha.
    env.sh                           GERADO: exports para o Copilot CLI
  .vscode/settings.json, .vscode/tasks.json     GERADO (Copilot no VS Code)
  .kiro/steering/t0.md, .kiro/hooks/t0.json     GERADO (Kiro)
  kb/                                clone normal do t0-kb
  ledger/ api/ web/ gateway/ batch/ admin/      clones normais, branches normais

~/ws/payments@BET-042/               OPCIONAL: workspace isolado de uma bet (t0 bet start BET-042 --isolate)
  AGENTS.md, .t0/ ...                mesmos arquivos gerados, bet fixa
  kb/ ledger/ api/ web/              git worktrees dos clones de ~/ws/payments/, só os repos da bet

~/.t0/
  config.yaml                        handle, remote do KB, raiz dos workspaces (caminho absoluto)
  spool/                             registros esperando push (seção 4)
```

Regras:

- O padrão é um workspace por produto, de longa duração, com clones normais, branches normais e um `t0 ws sync` de vez em quando. É o que o dev já faz hoje, só que organizado.
- Isolamento é opt-in. `t0 bet start <BET> --isolate` cria `~/ws/<produto>@<BET>/` com worktrees só dos repos da bet. Serve para duas bets em paralelo ou dois agentes na mesma bet. Fica **ao lado** do workspace principal e não dentro dele. Dentro, o `AGENTS.md` do principal viraria ancestral e a sessão carregaria dois cards, estourando o orçamento. O `slice-build --parallel` da metodologia usa o mesmo mecanismo.
- Cada clone tem um agente só. Ninguém troca branch embaixo de um agente rodando, e um segundo agente em paralelo vai para um workspace isolado.
- A raiz não é repo git, de propósito: cada subpasta é um repo. O VS Code acha os repos aninhados com `git.repositoryScanMaxDepth: 1` **(verificar)**.
- Repo sem acesso é pulado com um aviso e marcado `absent` em `.t0/workspace.json`. O card diz isso, então o agente nunca acha que o repo está vazio.

### 2.2 Arquivos que definem o workspace

| Caminho | Dono | Para quê |
|---|---|---|
| `t0-kb/products/<p>/workspace.md` | KB, raia de conhecimento (CODEOWNERS = lead do produto) | **O manifesto.** Concept OKF `type: Workspace`, indexado, linkável a partir das bets. |
| `t0-kb/products/<p>/product.md` | KB, raia de conhecimento | `repos[]` só com os nomes. `kb-check` exige que bata com o manifesto. |
| `t0-kb/products/<p>/bets/BET-NNN/bet.md` | KB, raia de conhecimento | A bet. Pasta = id KB-nativo, sem slug. Título no frontmatter. Chave da Feature no Jira em `jira:`. |
| `t0-kb/products/<p>/bets/BET-NNN/slices/NN-slug.md` | KB, raia de conhecimento | Um slice por arquivo, com `repo`, `depends_on[]` e `jira:` (Story). |
| `~/ws/<p>/.t0/workspace.json` | local, gerado | O que foi clonado, o que ficou `absent`, sha do manifesto. |
| `~/ws/<p>/.t0/bet.json` | local, gerado | Bet ativa. |
| `~/ws/<p>/AGENTS.md` + adaptadores | local, gerado | Card e fiação das ferramentas. Nunca commitado. |
| `~/.t0/config.yaml` | local, `t0 install` | Handle, remote do KB, raiz dos workspaces. |

**Manifesto** (`/products/payments/workspace.md`):

```yaml
---
type: Workspace
title: "Workspace do payments"
description: "Repos, papéis e dependências do produto payments; entrada do t0 ws."
uid: ws-payments
owner: team:payments
tags: [workspace, payments]
generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }
workspace:
  schema: 1
  product: payments                 # == /products/payments/
  jira_project: PAY                 # Feature e Story usam esse prefixo
  forge: github                     # escolhe o adaptador de PR e de checks
  default_branch: main
  repos:                            # ordem = ordem de merge padrão (provedores primeiro)
    - name: ledger                  # nome da pasta; [a-z0-9-]+, único
      url: git@github.example.bank:t0/payments-ledger.git
      role: "Ledger de partidas dobradas; guarda saldos e limites"   # uma linha, vai pro card
      kind: service                 # service | web | worker | lib | infra | mobile
      optional: false               # false = avisa alto se não der pra ler
      tier: 2                       # tier de review padrão para slices neste repo
      depends_on: []
    - name: api
      url: git@github.example.bank:t0/payments-api.git
      role: "API REST pública; valida e aplica limites"
      kind: service
      optional: false
      tier: 2
      depends_on: [ledger]
    - name: web
      url: git@github.example.bank:t0/payments-web.git
      role: "App web do cliente (Angular)"
      kind: web
      optional: false
      tier: 1
      depends_on: [api]
    - name: admin
      url: git@github.example.bank:t0/payments-admin.git
      role: "Backoffice; população de leitura restrita"
      kind: web
      optional: true                # true = pula quieto no 403
      tier: 2
      depends_on: [api]
    # gateway, batch ...
  groups:
    backend: [ledger, api, gateway, batch]   # t0 ws init payments --group backend
---
Notas humanas: quem cuida de quê, cadência de release, link para [product.md](./product.md).
```

O manifesto não fixa revisão. A bet sempre parte da branch padrão de cada repo, e o conjunto de SHAs testado junto fica no change set (seção 3). URL de repo não é segredo, porque quem garante o acesso é o forge. Token e credencial nunca aparecem no manifesto.

**Bet** (`bet.md`, chaves do profile mais `jira`):

```yaml
type: Bet
title: "Limites diários de transferência"
description: "Cliente define e o sistema aplica um limite diário de transferência."
uid: bet-042
owner: human:ana
bet_type: entrega
state: active
jira: PAY-123                       # Feature; escrita uma vez pelo t0 jira sync (seção 4)
appetite: P2W
cycle_end: 2026-11-07T23:59:00-03:00
stale_after: 2026-11-07T23:59:00-03:00
generated: { by: human:ana, at: 2026-10-27T10:00:00-03:00 }
```

**Slice** (`slices/02-api-limits.md`): `repo: api`, `depends_on: [01-ledger-limits]`, `jira: PAY-131`, critérios de aceite em bullets. Um slice é um repo e um PR. Uma Story que precisaria de dois repos vira dois slices ligados por `depends_on`. As chaves `state`, `pr` e `audit` do slice são derivadas (seção 4), e ninguém edita essas chaves na mão.

**Marcador da bet ativa** (`~/ws/payments/.t0/bet.json`):

```json
{ "schema": 1, "product": "payments", "bet": "BET-042", "jira": "PAY-123",
  "kb_path": "/products/payments/bets/BET-042",
  "repos": ["ledger", "api", "web"], "active_story": "PAY-130",
  "card": { "kb_sha": "9f3c1e2", "rendered_at": "2026-10-27T13:02:11-03:00", "chars": 6120 } }
```

`repos` vem do `repo` dos slices (ou de `--repos` antes de fatiar).

### 2.3 Comandos

```
t0 install --user                 uma vez por máquina: plugin t0 no Claude Code, Copilot e Kiro (2.4);
                                  sem plugin, copia as skills para os diretórios de usuário;
                                  grava as configs de usuário com caminhos absolutos
t0 ws init payments [--group backend]
                                  clona o KB se faltar, lê /products/payments/workspace.md,
                                  clona os repos como irmãos, pula 403, gera AGENTS.md e adaptadores
t0 ws sync [--quick]              fetch + ff-only nas branches padrão limpas e no kb/;
                                  re-renderiza AGENTS.md; avisa árvore suja ou divergente
t0 ws status                      por repo: branch, sujo, ahead/behind, PRs; frescor do card; spool
t0 bet start BET-042 [--isolate] [--repos a,b]
                                  marca a bet ativa e re-renderiza o card; com --isolate cria
                                  ~/ws/payments@BET-042/ com worktrees
t0 bet use BET-042|PAY-123        troca a bet ativa sem criar nada (chave Jira resolve por lookup)
t0 bet detect                     imprime a bet resolvida e a regra que disparou (2.5)
t0 slice start PAY-131            cria ou troca para bet/BET-042/PAY-131-<slug> no repo do slice;
                                  recusa árvore suja
t0 context [--format agents|delta|hook|subagent|json] [--write] [--kb <dir>]
                                  renderiza o card ou o delta
t0 pr [--draft] [--verify]        abre ou atualiza o PR do slice com trailers (seção 3)
t0 pr check                       CI: trailers, bet ativa, depends_on mergeado segundo o KB
t0 kb record | push | status      raia de registros (seção 4)
t0 jira sync <BET>                cria Feature e Stories, emite o registro com as chaves
t0 bet close                      depois do merge: tira worktrees, esvazia o spool da bet
t0 mcp [--kb <dir>]               servidor MCP stdio t0-kb
t0 setup                          num repo de produto: bloco t0 no AGENTS.md, workflows (2.7)
t0 doctor [--repo]                roda as detecções da seção 7
```

`t0 ws sync`, `t0 bet start|use` e os comandos de ritual re-renderizam o `AGENTS.md` da raiz. O início de sessão **não** reescreve o card (2.4). Fetch usa timeout de 3 s. Offline, o card mostra a idade em vez de travar.

O renderer lê o conteúdo do KB de `origin/main` via `git show`, e não da árvore de trabalho. Por isso a branch em que o `kb/` está (por exemplo, a branch de shaping da bet) não muda o card.

### 2.4 Como cada ferramenta recebe o contexto do KB

O contexto chega em três camadas. A camada 1 sozinha já garante correção; as outras duas trazem frescor e ferramentas.

1. **Arquivo, igual para todo mundo.** É o `~/ws/<p>/AGENTS.md`. As três ferramentas leem um `AGENTS.md` de raiz nativamente (multi-agent-compat §2.1). Abrir o workspace como **pasta única** evita a descoberta multi-root, que não é documentada no Copilot do VS Code e que no Kiro limita o `fileMatch` por raiz.
2. **Hooks, por ferramenta.** Avisam quando o card está velho, re-injetam depois de compactação, dão contexto aos subagentes e guardam a bet.
3. **MCP, igual nas três.** `t0 mcp` é o servidor **stdio** `t0-kb`. É um processo local, sem porta e sem serviço hospedado. Ferramentas: `kb_context(bet?)`, `kb_search(query, scope?)`, `kb_get(path|uid)`, `bet_get(id|jira_key)`, `changeset_get(bet)`, `kb_record(kind, body, bet?, story?)`. As instruções do servidor (≤1.500 chars, sempre carregadas, teto do Claude Code é 4.096) dizem: "KB = t0-kb. Sem card t0 no contexto, chame kb_context primeiro. Nunca edite index.md, log.md nem changeset.md do KB." O servidor acha o workspace subindo a partir do cwd até `.t0/workspace.json`, ou recebe `--kb`.

**Card velho sem carregar dois cards.** O `AGENTS.md` só muda por `t0 ws sync`, `t0 bet start|use` e comandos de ritual. No início de sessão o hook roda `t0 context --format delta`. Ele compara o carimbo do card (`kb=<sha>`) com o último commit de `origin/main` que toca `/products/<p>/bets/<BET>/` ou `/products/<p>/workspace.md`. Se nada mudou, imprime uma linha ("card em dia"). Se mudou, escreve em `.t0/context.md` e injeta só o **delta**, no máximo 3.000 chars, com as seções do card que mudaram (bet ativa, change set) e a linha "isto substitui as seções 2 e 4 do AGENTS.md; rode `t0 ws sync`". A sessão nunca leva dois cards inteiros.

| Superfície | Sempre ligado | Frescor, compactação, subagentes | Ferramentas | Fallback |
|---|---|---|---|---|
| **Claude Code** (CLI, IDE, Desktop) | `AGENTS.md` da raiz, carregado como ancestral mesmo lançando dentro de `api/`. Os repos de produto têm `CLAUDE.md` ponteiro (metodologia §5.1), e CLAUDE.md desliga a leitura de AGENTS.md. Por isso o `t0 install` grava `instructionFiles: claude-md-and-agents-md` nas configs de usuário. | Plugin `t0` exigido por managed settings (`enabledPlugins`). **SessionStart** `startup\|resume\|clear\|compact` roda `t0 context --format delta`. **SubagentStart** injeta um card de subagente (≤3.000 chars), porque Explore e Plan nascem sem memória. **UserPromptSubmit** avisa numa linha quando o prompt cita uma chave Jira de outra bet. Se ainda assim existir `CLAUDE*.md` acima do cwd sem o `instructionFiles`, o hook injeta o card inteiro (≤8.000) no lugar do delta, porque aí o AGENTS.md não carregou. | `.mcp.json` do plugin → `t0 mcp`; skills do plugin | Acesso aos irmãos e ao `kb/`: `permissions.additionalDirectories` de **usuário** com caminho **absoluto** (`/Users/ana/ws/payments`), escrito pelo `t0 ws init`. Escopo de projeto espera trust do workspace e é ignorado em `-p` (mechanics §1.1). Expansão de `~` nessa chave não está verificada, então ele nunca grava `~`. |
| **Copilot no VS Code** (agent mode) | Abrir `~/ws/payments` como **pasta única** (não multi-root). `AGENTS.md` da raiz (`chat.useAgentsMdFile`, ligado por padrão). `.vscode/settings.json` gerado liga `chat.useNestedAgentsMdFiles` para carregar o AGENTS.md dos repos (experimental). | Task `t0: sync` com `runOptions.runOn: folderOpen` roda `t0 ws sync --quick` antes do chat **(verificar)**. Plugin instalado como Agent Plugin. O hook de sessionStart dele roda no VS Code com matchers ignorados **(verificar)**. | MCP do plugin | O card manda: "se `.t0/context.md` for mais novo que este card, leia ele primeiro". Fallback para quem abre um repo sozinho: o bloco t0 commitado no `AGENTS.md` de cada repo (2.7). |
| **Copilot CLI** | `source ~/ws/payments/.t0/env.sh` exporta `COPILOT_CUSTOM_INSTRUCTIONS_DIRS=/Users/ana/ws/payments`, então o AGENTS.md da raiz carrega mesmo lançando dentro de `api/`. O CLI por padrão só sobe até a raiz do repo. | Plugin via `copilot plugin install` (lê o formato Claude). O CLI também lê os hooks do plugin e de `.claude/settings.json`. Se o stdout do hook vira contexto **(verificar)**. O design não depende disso: o card já chega pelo arquivo. | MCP do plugin, ou `~/.copilot/mcp-config.json` | Mesma linha do card sobre `.t0/context.md`. |
| **Copilot cloud agent** | Sem workspace. O `AGENTS.md` commitado do repo de produto traz o bloco t0. `.github/workflows/copilot-setup-steps.yml` faz checkout read-only do `t0-kb` em `.kb/` (gitignored) e instala o `t0` **(verificar: setup steps liberados no GHE do banco)**. | n/a (uma tarefa por execução) | Repo Settings → Copilot → MCP: stdio `t0 mcp --kb .kb`, allowlist `kb_context`, `kb_search`, `kb_get`, `bet_get`. Servidor stdio disponível depois dos setup steps **(verificar)**. | O bloco manda: pegue a chave Jira da issue, chame `kb_context(<chave>)` ou rode `t0 context <chave> --kb .kb`. Se nada funcionar, pare e diga "KB indisponível". O `t0 pr check` avisa PR sem trailer `KB-Context`. |
| **Kiro** (IDE e kiro-cli) | Abrir `~/ws/payments` como pasta. `AGENTS.md` é sempre incluído. | `.kiro/hooks/t0.json`: Session Start roda `t0 context --format delta --write`, Agent Stop roda `t0 kb push --if-due`, Pre Tool Use roda o guard. `.kiro/steering/t0.md` com `inclusion: always` contém `#[[file:.t0/context.md]]`, então o delta entra igual ao do Claude e o card nunca entra duas vezes. Se o include é resolvido depois do hook de Session Start **(verificar)**. Custom agents do Kiro ficam de fora, porque não carregam steering nem skills. | Skills e MCP pelo power `t0` (formato Agent Plugins). O Kiro carregar um power que também tem `.claude-plugin/` e `hooks/` **(verificar)**. Sem power: `t0 install --user` copia para `~/.kiro/skills` e `~/.kiro/settings/mcp.json`. | `~/.kiro/steering/t0.md` (`inclusion: always`, 6 linhas) com a mesma regra do fallback. |
| **CI sem agente** | n/a | n/a | `t0 pr check` | Workflow reutilizável faz checkout read-only do KB. |
| **CI com agente** (claude-code-action, `copilot -p`, `kiro-cli --no-interactive`) | Mesmo checkout em `.kb/` + `t0 context <chave> --kb .kb --format agents > card.md`, passado como primeiro arquivo do prompt | n/a | `t0 mcp --kb .kb` | "KB indisponível → pare." |

**Por que AGENTS.md e não CLAUDE.md na raiz.** O Copilot CLI lê os dois e carregaria o conteúdo duas vezes. O Claude lê AGENTS.md quando não há CLAUDE.md, e o `instructionFiles` cobre os ponteiros dos repos.

**Por que não `@../kb/...`.** Em `-p`, em CI e em máquina nova, import externo é pulado em silêncio até alguém aprovar por projeto (mechanics §1.2).

### 2.5 Como a sessão sabe a bet ativa

`t0 bet detect` resolve nesta ordem. O primeiro acerto vence, e o card imprime qual regra disparou.

1. Variável `T0_BET` (CI, execução scriptada, override explícito).
2. Branch do repo no cwd, casando `^bet/(BET-\d+)/([A-Z][A-Z0-9]+-\d+)-` (bet e Story).
3. `.t0/bet.json`, subindo a partir do cwd (sessão na raiz ou no `kb/`).
4. Uma chave Jira no texto da tarefa ou da issue. Ela resolve por lookup no frontmatter `jira:` de `bet.md` e `slices/*.md` (e nos registros `jira-linked` ainda não renderizados). É o caso do cloud agent.
5. Nenhuma: o card mostra o mapa do KB e "pergunte qual bet, ou rode `/bet-use`". Skills de ritual funcionam nesse modo. **Skills que geram código se recusam a escrever código sem bet resolvida.**

Se a branch (regra 2) aponta uma bet diferente do `bet.json` (regra 3), o hook de SessionStart diz numa linha: "branch é BET-051, card é BET-042: rode `t0 bet use BET-051`".

### 2.6 Orçamento de contexto

Conta de 4 chars por token (inferido, mechanics §2.1).

| Camada | Teto (chars) | Quando carrega |
|---|---|---|
| Card no `AGENTS.md` da raiz | **8.000**, ≤150 linhas. Teto duro no renderer, testado no CI do KB | Sempre |
| Delta (`.t0/context.md` ou saída do hook) | 3.000. Normalmente uma linha | Só com card velho |
| Instruções do MCP `t0-kb` | 1.500 | Sempre (ferramentas são diferidas) |
| Bloco t0 no `AGENTS.md` de cada repo tocado | 1.200 por repo (≤15 linhas) | Quando o agente mexe no repo |
| Listagem de skills do pack | ≤25 skills × ≤300 chars = 7.500 | Sempre |
| **Pior caso na sessão principal, bet de 3 repos + kb** | 8.000 + 3.000 + 1.500 + 4 × 1.200 + 7.500 = **24.800 (~6,2k tokens)** | |
| Card de subagente | 3.000 | Contexto separado, em cada subagente do Claude |
| Resto (corpo do spec, plan, ADRs, metodologia, transcrições) | sob demanda | `Read`, `kb_get`, skills |

Cada valor injetado por hook fica abaixo do teto de 10.000 chars do Claude Code (mechanics §1.4). No fallback em que o hook injeta o card inteiro, o `AGENTS.md` não carregou, então o pior caso continua o mesmo.

**Conteúdo do card, em ordem.** Quando estoura, o renderer corta de baixo para cima e sempre mantém as seções 1 a 3.

1. Cabeçalho (≤12 linhas): o que é o KB, onde mora (`./kb`), as três raias, "spec é o contrato; pergunte antes de desviar", a regra do `.t0/context.md` e o carimbo `<!-- t0:card kb=9f3c1e2 at=… rule=bet.json -->`.
2. Bet ativa (≤40 linhas): título, `state`, apetite e dias restantes, problema do intent (≤5 linhas), a Story ativa e seus critérios de aceite (≤15 bullets), links para `kb/products/<p>/bets/BET-NNN/{spec,plan}.md`, `slices/` e `adr/`.
3. Repos (≤10 linhas): nome, papel, branch, posição no merge. Os da bet marcados; os `absent` marcados.
4. Change set da bet (≤10 linhas): PRs, estado, depends_on.
5. Outros slices abertos (≤10 linhas), só título.
6. Mapa do KB (≤25 linhas): seções do `index.md` raiz e verbetes do glossário do produto.
7. Ponteiros de skill (≤8 linhas).

Nada além disso entra inline. Documento inteiro chega por disclosure progressiva (`index.md` → concept).

### 2.7 O que cada repo de produto commita

O `t0 setup` (skill `pack-setup`) gera, e o CI confere com `t0 setup --check`:

- **Bloco t0 no `AGENTS.md`** (≤15 linhas, entre `<!-- t0:begin -->` e `<!-- t0:end -->`): nome do produto, onde achar o KB (`../kb`, `../../kb`, `.kb/`, senão MCP `kb_context`, senão pare), convenção de branch e de PR, e "nunca copie spec para este repo; referencie pela chave". `CLAUDE.md`, `.github/copilot-instructions.md` e `.kiro/steering/` só apontam para o AGENTS.md (metodologia §5.1).
- `.gitignore` com `.kb/`.
- `.github/workflows/t0.yml`, que chama os workflows reutilizáveis `t0-pr-check` e `t0-kb-sync` do `t0-toolkit` num SHA fixo.
- `.github/workflows/copilot-setup-steps.yml` (checkout read-only do KB + `t0`), só onde o cloud agent está ligado.
- Nenhum `.mcp.json` e nenhuma skill copiada. A fiação mora no workspace e no plugin de usuário, em vez de se repetir em 6×N repos.

---

## 3. Fluxo de uma bet em vários repos

**IDs.** A bet nasce no KB (`bet-new`) como `BET-042`. O `t0 jira sync` cria a Feature (`PAY-123`) e uma Story por slice (`PAY-130`, `PAY-131`, `PAY-132`), e as chaves voltam pro KB (seção 4). O G3 exige chave Jira em todo slice, então toda branch de código já nasce com a chave da Story. O conteúdo pertence ao KB, e o status segue as regras de espelho da metodologia §5.5.

**Branches.**

- Repo de produto: `bet/BET-042/PAY-131-api-limits`. O mesmo formato em todo repo, então uma regex dá a bet e a Story. Git não aceita `bet/BET-042` e `bet/BET-042/x` juntos, então a bet nunca ganha branch própria.
- KB, edição de conhecimento: `bet/BET-042/<handle>` (por exemplo `bet/BET-042/ana`) ou `kb/<handle>/<tema>`.
- KB, registros: `rec/<handle>/<utc-ts>` e `rec/bot/<repo>/<pr>-<utc-ts>`, só criados por ferramenta.
- Branches do cloud agent (`copilot/…`) são aceitas. Para autor bot, o check lê as chaves do corpo do PR.

**Change set = os PRs dos slices de uma bet.** Um slice é um repo e um PR. Uma Story que atravessa `api` e `web` vira dois slices com `depends_on`.

**Linkagem de PR.** O `t0 pr` (ou a skill `slice-build`) abre o PR em draft e escreve os trailers no corpo:

```
Bet: BET-042
Story: PAY-131
Jira-Feature: PAY-123
Depends-on: t0/payments-ledger#88
Merge-order: 2/3
KB-Context: 9f3c1e2
```

`KB-Context` é o sha do KB que o agente usou. O título do PR começa com `PAY-131:`, para a integração entre GitHub e Jira linkar **(verificar: integração ativa no GHE do banco)**. Commits levam os trailers `Bet:` e `Story:`, que a skill coloca.

**Ordem de merge.**

1. Por padrão vale a ordem topológica dos `depends_on` do manifesto, provedores primeiro (ledger → api → web). O `depends_on` de cada slice manda quando o `plan.md` diz outra coisa.
2. Todo PR tem que ser deployável sozinho, com expand → migrate → contract, porque não existe merge atômico entre repos. A ordem serve de rede de segurança e não substitui compatibilidade.
3. Quem garante a ordem é o `t0 pr check`, que posta o status obrigatório `t0/merge-order`. Ele lê o estado do change set **no KB** (`changeset.md` em `main` e os registros bot ainda pendentes em `rec/bot/*`) com um token só de leitura do KB. Nunca consulta a API de outro repo de produto. Re-execução: um workflow agendado no próprio repo (a cada 15 min, só para PRs com `t0/merge-order` vermelho) re-posta o status com o `GITHUB_TOKEN` do repo, e `workflow_dispatch` deixa o dev re-checar na hora **(verificar: status de commit vindo de workflow agendado conta como check obrigatório no ruleset)**. Nenhum `repository_dispatch` entre repos.
4. O teste integrado é opcional. Se o `plan.md` define `integration: "<comando rodado da raiz do workspace>"`, o `t0 pr --verify` roda e emite um registro `integration` com os SHAs testados.

**Change set no KB.** `/products/<p>/bets/BET-NNN/changeset.md` é **derivado**. O `kb-render` gera o arquivo a partir dos registros `pr-*` e `integration`, e ninguém edita na mão:

```yaml
---
type: Changeset
title: "Change set da BET-042"
description: "PRs, ordem de merge e SHAs testados juntos da BET-042."
uid: cs-bet-042
owner: human:ana
generated: { by: process:kb-render, at: 2026-10-28T16:02:00-03:00 }
changes:
  - { repo: ledger, story: PAY-130, pr: "t0/payments-ledger#88", order: 1, state: merged,    sha: 3f2a9c1 }
  - { repo: api,    story: PAY-131, pr: "t0/payments-api#412",   order: 2, state: in-review, sha: 9b0e7d2 }
  - { repo: web,    story: PAY-132, pr: "t0/payments-web#977",   order: 3, state: open,      sha: 51c4aa0 }
tested_together: { ledger: 3f2a9c1, api: 9b0e7d2, web: 51c4aa0 }   # última execução integrada verde
---
```

Os registros vêm de duas fontes:

- O `t0 pr` emite `pr-opened` pela raia de registros do dev.
- O `t0-kb-sync`, workflow reutilizável em cada repo de produto, dispara em `pull_request: [opened, ready_for_review, synchronize, closed]`. Ele escreve registros `pr-*` (e as linhas de decisão do `.audit/<KEY>.tsv` no merge) na raia de registros usando o **GitHub App KB-writer**. É **a única credencial que atravessa repos** no design. Fica instalado só no `t0-kb`. O workflow pede tokens de instalação com permissão reduzida: `contents:read` para checks e setup steps, `contents:write` + `pull_requests:write` só no job de escrita **(verificar: token de App com permissões reduzidas na versão do GHE)**. Ele não enxerga código de produto.

**Transições no Jira.** O `kb-render`, rodando no KB, aplica as transições de estado do slice a partir dos registros: PR saiu de draft → In Review; merge → Done. "Done" da Feature só quando o change set inteiro mergeou. O token do Jira mora só no KB.

---

## 4. Write-back no KB

**Princípio: agente adiciona arquivo, humano revisa conhecimento, um bot escreve o derivado.** Nenhuma raia concorrente tem arquivo compartilhado editado à mão.

| Raia | O quê | Caminho | Como entra | Revisão |
|---|---|---|---|---|
| **Registros** | Passos (`t0 log`), decisão em voo, bloqueio, handoff, eventos de PR, linhas de `.audit`, chaves Jira criadas, resumo de sessão | `/products/<p>/bets/BET-NNN/steps/<utc-ts>-<handle>-<repo>-<rand4>.md` (`type: Step`); fora de bet, `/steps/<utc-ts>-<handle>-<rand4>.md` | `kb_record` / `t0 kb record` / `t0 log` escrevem em `~/.t0/spool/`. `t0 kb push` monta **um commit por sessão** sobre `origin/main` com índice temporário (plumbing, não toca árvore de trabalho), empurra `rec/<handle>/<ts>`, abre PR e liga auto-merge **(verificar: auto-merge com a proteção de branch do banco)** | Nenhuma humana. Check obrigatório `kb-check --lane records`: só adições, caminho no padrão, frontmatter OKF + profile válido, `generated.by` coerente com o autor, secret scan limpo, ≤20 KB por arquivo |
| **Conhecimento** | `bet.md`, spec, plan, slices, ADRs, `workspace.md`, metodologia, rituais, glossário, **records de reunião e transcrições redigidas** (`/rituals/`, `/transcripts/`), mudanças de `state` por `t0 gate` | todo o resto | Branch `bet/BET-NNN/<handle>` (ou `kb/<handle>/<tema>`) no `kb/` → PR | CODEOWNERS: dono da bet na pasta da bet, steward da metodologia em `/methodology/`, facilitador em `/cycles/*/rituals/`. Transcrição sempre com revisor humano confirmando a redação |
| **Derivado** | Todo `index.md`, o `log.md` de cada bet (renderizado de `steps/`), `changeset.md`, as chaves derivadas dos slices (`state` depois de `ready`, `pr`, `audit`), e as chaves `jira:` escritas uma vez a partir dos registros `jira-linked` | gerado | Workflow `kb-render` no push para `main`, `concurrency: kb-render` (serializado), commitando como o App KB-writer, que é ator de bypass do ruleset **(verificar)** | O check de PR rejeita qualquer edição humana ou de agente nesses arquivos e chaves. O hook PreToolUse do plugin bloqueia localmente também |

O `t0 log` da metodologia ("toda skill termina chamando") emite um registro `Step`, e o `log.md` da bet é a renderização desses registros. Assim 10 pessoas registram passo ao mesmo tempo sem disputar o mesmo arquivo.

**Por que não commit direto em `main`.** Commit direto é auditável mas não passa por check, e a proteção de branch já proíbe. PR de registro com zero aprovação ainda dá trilha com check, assinatura e autor.

**Por que não um MCP hospedado que escreve.** Ele seria um serviço, com revisão de segurança, uptime e uma identidade escrevendo por todo mundo. `kb_record` local mais spool dá a mesma ergonomia com a credencial do próprio dev.

**Ruleset do `main` do `t0-kb`:**

- PR obrigatório, checks obrigatórios `kb-check`, review de code owner.
- Aprovações exigidas no nível do ruleset: 0. Aprovação vem **só** pelo CODEOWNERS nos caminhos de conhecimento.
- `**/steps/**` não tem code owner. É isso que deixa o PR de registro fazer auto-merge **(verificar com o admin do GHE)**.
- **Fallback** se a política do banco exigir ≥1 aprovação em todo PR: o `t0 kb push` só empurra a branch `rec/*`, sem PR. Um workflow agendado do KB junta as branches `rec/*` da última hora num PR `rec/batch/<data>-<hora>`, aprovado pelo rodízio do Flow Steward com um clique. Isso cabe na revisão que o papel já faz ("o Jira gerado está coerente?"). Nesse modo o `t0 pr check` continua lendo os registros bot pendentes em `rec/bot/*`, então a ordem de merge não espera a aprovação do lote.

**Cloud agent e CI não empurram para o KB.** O token deles é só de leitura. Eles põem registros no corpo do PR de produto (bloco YAML `<!-- t0:records … -->`), e o `t0-kb-sync` colhe para a raia de registros com `generated.by: copilot-cloud/<versão>` e `on_behalf_of` do dono da issue, sem `verified`.

**10 pessoas escrevendo ao mesmo tempo:**

- Registros: o nome é único por construção e o PR só adiciona, então entra em qualquer `main` sem conflito. Corrida de push se resolve rebaseando o commit único (3 tentativas).
- Derivados: um escritor serializado, então também não há conflito.
- Conhecimento: conflito real é possível e desejado, porque duas pessoas mudando o mesmo spec precisam conversar. Mitigações: um dono por pasta de bet, arquivos pequenos (um ADR, um slice, um record de reunião por arquivo), slice sem status editável à mão, e o `kb-check` avisa quando um PR de conhecimento está aberto há mais de 48 h e o alvo mudou.
- Jira: `t0 jira sync` é idempotente e chaveado pelo `uid` do slice. Duas execuções convergem. A chave volta como registro `jira-linked` e só o `kb-render` grava `jira:`.

**Registro de passo** (`type: Step`):

```yaml
type: Step
title: "PAY-130: limite em int64 de unidades menores"
description: "Limite guardado como int64 em unidades menores, igual ao ledger."
uid: step-20261027T141502Z-ana-ledger-k3f9
kind: decision            # progress|decision|blocker|handoff|pr-opened|pr-merged|pr-closed|jira-linked|integration|session
bet: BET-042
story: PAY-130
repo: ledger
refs: [t0/payments-ledger@4be1a90]
generated: { by: claude-code/opus-5.5, at: 2026-10-27T11:15:02-03:00 }
on_behalf_of: human:ana
```

Corpo com ≤20 linhas. Um `decision` que muda o contrato (spec, API, modelo de dados) tem que virar ADR na raia de conhecimento. A skill `kb-record` puxa isso, e a Harness Retro revisa decisões não promovidas.

---

## 5. Um dia na vida

Ana é Bet Owner da **BET-042 "limites diários de transferência"** no `payments` (6 repos). A daily do pod já mergeou `bet.md`, `spec.md`, `plan.md` e três slices: `01-ledger-limits` (PAY-130, ledger), `02-api-limits` (PAY-131, api, depende do 01) e `03-web-limit-errors` (PAY-132, web, depende do 02). A Feature é PAY-123. No primeiro dia ela rodou `t0 install --user` e `t0 ws init payments`.

**Começo comum, qualquer ferramenta:**

```
$ cd ~/ws/payments && t0 bet start BET-042
  sync: kb 9f3c1e2 (ff 4), ledger/api/web ff, gateway/batch ff, admin absent (403)
  bet ativa: BET-042 (PAY-123), repos: ledger api web
  card: 6.120 chars -> ~/ws/payments/AGENTS.md
$ t0 slice start PAY-130
  ledger: bet/BET-042/PAY-130-ledger-limits
```

### Claude Code

1. `cd ~/ws/payments/ledger && claude`. O AGENTS.md da raiz carrega como ancestral, e o `instructionFiles` garante que o `CLAUDE.md` ponteiro do ledger não o desliga. O SessionStart imprime "card em dia (kb 9f3c1e2, rule=branch)". Ela pede "planeja o PAY-130". O Plan Mode lê `../kb/products/payments/bets/BET-042/spec.md` e `plan.md` sob demanda, liberado pelo `additionalDirectories` absoluto.
2. O Claude dispara um subagente Explore em `ledger/`. O SubagentStart dá a ele o card de subagente com os critérios de aceite e o verbete do glossário sobre tipo monetário.
3. No meio, o Claude escolhe int64 em unidades menores. `/kb-record decision …` grava um passo no spool. Como mexe no modelo de dados, a skill também rascunha `kb/products/payments/adr/ADR-0004-tipo-do-limite.md` na branch `bet/BET-042/ana` (raia de conhecimento).
4. Ela escreve "o PAY-131 vai precisar disso?". O UserPromptSubmit vê que PAY-131 é da mesma bet e fica quieto. Se fosse uma chave de outra bet, avisaria numa linha.
5. `/slice-build` termina com `t0 pr`: abre o ledger #88 com os trailers e emite `pr-opened`. No fim da sessão, o hook Stop roda `t0 kb push --if-due`. O PR de registro faz auto-merge em uns 2 minutos, e o `kb-render` atualiza `log.md` e `changeset.md`.
6. Depois de compactar numa sessão longa, o SessionStart `compact` re-checa o card. O `AGENTS.md` continua na memória.

### GitHub Copilot

- **VS Code:** `code ~/ws/payments`. A task de folderOpen roda `t0 ws sync --quick` antes do chat. O agent mode lê o AGENTS.md da raiz e, com o AGENTS.md aninhado ligado, o `api/AGENTS.md` quando entra no `api/`. Ela roda `/slice-build PAY-131`, que chama `t0 slice start PAY-131` (`api` em `bet/BET-042/PAY-131-api-limits`). O Copilot implementa e chama `kb_get` no ADR da manhã. O `t0 pr` abre o api #412 com `Depends-on: t0/payments-ledger#88`. O `t0/merge-order` fica vermelho até o `changeset.md` (ou o registro bot pendente) mostrar o #88 mergeado. Aí o workflow agendado deixa verde em até 15 min, ou ela roda `gh workflow run t0-pr-check` na hora.
- **Copilot CLI**, mesma máquina: `source ~/ws/payments/.t0/env.sh && cd api && copilot`. O env faz o AGENTS.md da raiz carregar de dentro do `api/`. Skills e MCP vêm do plugin. Mesmo fluxo.
- **Cloud agent:** ela atribui ao Copilot a issue "PAY-132: mostrar erros de limite" no `payments-web`. Os setup steps põem o `t0-kb` em `.kb/`. O agente lê o bloco t0, chama `kb_context("PAY-132")`, que resolve pelo `jira:` do slice para a BET-042, e recebe o card da bet com a Story PAY-132. O PR sai com os trailers e um bloco `t0:records`. O `t0-kb-sync` colhe os dois para o KB.

### Kiro

`kiro ~/ws/payments` (IDE) ou `kiro-cli chat` na mesma pasta. O AGENTS.md entra sempre. O Session Start re-calcula o delta, e o steering `t0.md` inclui `.t0/context.md` ("card em dia"). As skills vêm do power: `/slice-build PAY-132`, implementa em `web/`, `t0 pr`. O web #977 sai com `Depends-on: t0/payments-api#412` e `Merge-order: 3/3`. Ela pergunta "como a gente nomeou erro de limite na bet do gateway?", e o `kb_search` responde. O Agent Stop empurra os registros. Nenhum `.kiro/specs` é criado, porque a bet no KB é o único spec.

**Bet paralela.** No meio da tarde cai a bugfix BET-051 no `api`. Como já tem um agente rodando no `api/` da BET-042, ela roda `t0 bet start BET-051 --isolate` e trabalha em `~/ws/payments@BET-051/`, com card próprio e worktrees próprias.

**Fim da bet.** Com os três slices mergeados, o change set inteiro fecha e o `kb-render` move a Feature PAY-123 para Done. A Ana abre o PR de conhecimento do `bet-ship`, e `t0 bet close` limpa worktrees e spool.

---

## 6. O que o toolkit (`t0-toolkit`) implementa

**CLI `t0`.** É um pacote só, sem daemon, fixado e instalado pelo registry interno do banco.

1. `install --user`: plugin nas três ferramentas (marketplace do Claude, `copilot plugin install`, power do Kiro) ou cópia das skills para os diretórios de usuário; configs de usuário com caminhos absolutos (`instructionFiles`, `permissions.additionalDirectories`, `~/.copilot/instructions/t0.instructions.md`, `~/.kiro/steering/t0.md`, configs MCP de usuário quando não há plugin).
2. `ws init|sync|status`: leitor do manifesto (`workspace:` de `workspace.md`), clone com pulo de 403, sync ff-only, geração de `AGENTS.md`, `.t0/*`, `.vscode/*`, `.kiro/*`.
3. `bet start|use|detect|close` e `slice start`: cadeia de resolução (2.5), workspaces isolados com worktrees, nomes de branch, lookup de chave Jira.
4. `context`: renderer com tetos duros (2.6), formatos `agents|delta|hook|subagent|json`, carimbo de frescor, leitura de `origin/main` via `git show`.
5. `pr` e `pr check`: PR em draft com trailers, `--verify`, `pr-opened`; check que lê o change set só no KB e posta `t0/merge-order`.
6. `kb record|push|status` e `log`: spool, commit por plumbing sobre `origin/main`, PR + auto-merge ou só branch no modo lote, retentativa.
7. `jira sync`: Feature e Stories a partir do KB, chaves devolvidas como registro `jira-linked`.
8. `setup [--check]`: bloco t0 no AGENTS.md do repo de produto, ponteiros, workflows, `.gitignore`.
9. `mcp`: servidor stdio `t0-kb` com `kb_context`, `kb_search` (ripgrep + filtro de frontmatter, sem embeddings), `kb_get`, `bet_get`, `changeset_get`, `kb_record`; instruções ≤1.500 chars.
10. `doctor`: todas as detecções da seção 7.

**Plugin `t0`** (o pack `t0-method` empacotado), com manifesto duplo: `.claude-plugin/plugin.json` e `plugin.json` Agent Plugins 1.0.

- Skills da metodologia §10 (frontmatter portátil, descrição ≤300 chars), mais `kb-record`, `kb-search` e `bet-use`. Skills que geram código checam `t0 bet detect` e se recusam sem bet. Skills de ritual não exigem bet.
- Hooks num só conjunto de scripts (`scripts/hooks/*.sh`, JSON no stdin, exit 2 bloqueia), com registros gerados para Claude, Copilot e Kiro:
  - SessionStart (`startup|resume|clear|compact`): delta de frescor; card inteiro se o AGENTS.md não carregou; aviso de bet divergente.
  - SubagentStart: card de subagente.
  - UserPromptSubmit: aviso de chave Jira de outra bet.
  - Stop: `kb push --if-due`.
  - PreToolUse Edit/Write: bloqueia arquivos e chaves derivados do KB, edição de `steps/*` existente, escrita em repo `absent`.
  - PreToolUse Bash: bloqueia force-push e push direto em `main` do KB.
- MCP: `t0 mcp`.

**Gerado por workspace (nunca commitado):** `AGENTS.md`, `.t0/{workspace.json,bet.json,context.md,env.sh}`, `.vscode/{settings,tasks}.json`, `.kiro/steering/t0.md`, `.kiro/hooks/t0.json`.

**KB (`t0-kb`):**

- Workflows: `kb-check` (L0/L1 do profile em Python com SafeLoader, regras de raia, guarda de derivados, secret scan, teste de tamanho do card de toda bet ativa); `kb-render` (índices, `log.md`, `changeset.md`, chaves derivadas, transições Jira, serializado); `kb-batch` (só no modo fallback, lote horário); `t0 jira sync --reconcile` noturno.
- CODEOWNERS e ruleset (seção 4).
- Profile: tipos `Workspace`, `Step` e `Changeset`; chave `jira` em Bet e Slice; `workspace:` como bloco de dados do `Workspace`.
- `/products/<p>/workspace.md` por produto.

**Repos de produto:** workflows reutilizáveis `t0-pr-check` (obrigatório, com gatilho agendado e `workflow_dispatch`) e `t0-kb-sync`, `copilot-setup-steps.yml` onde o cloud agent está ligado, e o bloco t0 no AGENTS.md.

**Org/admin:**

- Managed settings: `enabledPlugins` + `strictKnownMarketplaces` no Claude Code e no `managed-settings.json` do Copilot.
- O GitHub App KB-writer, instalado só no `t0-kb`. É a única credencial que cruza repos.
- Token do Jira só nos secrets do `t0-kb`.

---

## 7. Modos de falha e detecção

| # | Falha | Detecção | Resposta |
|---|---|---|---|
| 1 | KB do workspace velho (dias sem sync) | Carimbo `kb=<sha> at=<hora>` no card. O SessionStart, o Session Start do Kiro e a task de folderOpen comparam com o `origin/main` buscado (timeout de 3 s) | Delta injetado. Offline, a primeira linha diz "snapshot do KB de 3 dias" |
| 2 | Card velho numa ferramenta sem hook funcionando | `t0 doctor` e `ws status` mostram a idade. `t0 pr` recusa carimbar card com mais de 24 h sem `--force` | `t0 ws sync` |
| 3 | AGENTS.md desligado no Claude (`CLAUDE.md` ponteiro ou `CLAUDE.local.md` sem `instructionFiles`) | O hook varre os ancestrais. O doctor checa `instructionFiles` | Hook injeta o card inteiro. Corrigir a config |
| 4 | Agente trabalhou sem bet, ou com a bet errada | Skill de código recusa sem bet. Hook avisa branch ≠ `bet.json`. `t0 pr check` falha sem `Story`, avisa sem `KB-Context` ou com mais de 7 dias | Refazer com contexto. A Harness Retro revisa os avisos |
| 5 | Dois agentes no mesmo clone | `t0 slice start` recusa árvore suja. `ws status` lista branches trocadas com mudança pendente | `t0 bet start --isolate` |
| 6 | Bet precisa de repo fora do workspace isolado | `ws status` compara o `repo` dos slices com as worktrees. `t0 pr` recusa repo fora da bet | `t0 bet start --isolate --repos …` de novo, ou trabalhar no workspace principal |
| 7 | Sem acesso a um repo que a bet precisa | `ws init` grava o 403. O card marca `absent`. O hook bloqueia escrita em repo `absent` | Parear ou pedir acesso ao dono |
| 8 | Change set meio mergeado (ledger entrou, web travou) | `changeset.md` com estado misto. O digest diário lista change sets mistos há mais de 24 h. A Feature só vai a Done com tudo mergeado | Flow Steward cobra. Expand/contract segura produção |
| 9 | Merge fora de ordem | Status obrigatório `t0/merge-order` | Bloqueado até a dependência mergear |
| 10 | Merge-order verde atrasado | Workflow agendado de 15 min; `workflow_dispatch` | Esperar o próximo ciclo ou disparar na mão |
| 11 | Registros nunca empurrados (spool esquecido no notebook) | `kb status` e o spool no `ws status`. Os hooks de Stop empurram. `bet close` recusa com spool da bet | `t0 kb push` |
| 12 | PR de registro falha (segredo, frontmatter, edição em vez de adição) | `kb-check --lane records` falha. O PR fica aberto e atribuído ao autor | Corrigir e re-empurrar. Segredo = rotação pelo processo do banco |
| 13 | Auto-merge negado pela política do banco | PRs `rec/*` parados. O doctor checa o ruleset | Ligar o modo lote horário com o Flow Steward |
| 14 | Duas pessoas editam o mesmo spec | Conflito git normal no PR de conhecimento. O `kb-check` avisa alvo que mudou com PR aberto há mais de 48 h | O dono resolve; esse conflito é desejado |
| 15 | Alguém edita arquivo ou chave derivada | Hook PreToolUse (local) e `kb-check` (servidor) | Rejeitado. O `kb-render` regenera |
| 16 | Jira diverge do KB | Reconcile noturno → relatório de drift no digest | Re-sync, porque o conteúdo é do KB |
| 17 | Manifesto diverge da realidade (repo novo não listado, repo arquivado) | O `t0-pr-check` de cada repo confere se o próprio remote está em algum `workspace.md`. `ws sync` avisa remote arquivado ou renomeado. `kb-check` compara `product.md` com o manifesto | PR de conhecimento no `workspace.md` |
| 18 | Card estoura o orçamento | O renderer corta de baixo e mantém 1 a 3. O `kb-check` renderiza o card de toda bet ativa e falha acima de 8.000 chars | Dividir os critérios de aceite ou encurtar o intent |
| 19 | Cloud agent rodou sem KB (setup steps desligados, MCP ausente) | Instrução "pare e diga KB indisponível". `t0 pr check` avisa sem `KB-Context` | Corrigir a config do repo. Conferir com `t0 doctor --repo` |
| 20 | Conteúdo sensível no KB (transcrição sem redação) | Transcrição só pela raia de conhecimento com revisão humana. Secret scan do `kb-check`. Push protection do GitHub **(verificar)** | Revert e purga pelo processo do banco |
| 21 | Workspaces isolados acumulando | `ws status` lista os de bets `shipped` ou `killed` | `t0 bet close` |
| 22 | Plugin ausente ou desligado numa máquina | Managed settings tornam obrigatório. Sem ele, o AGENTS.md ainda entrega o card (camada 1), e o doctor aponta | `t0 install --user` |

---

## 8. O que precisa ser verificado antes do rollout

Cada item tem dono e um teste de meia hora numa máquina ou no GHE do banco. Nenhum é premissa de correção: se falhar, a camada 1 (o `AGENTS.md`) continua entregando o card.

- Copilot cloud agent: `copilot-setup-steps.yml` liberado no GHE e MCP stdio `t0 mcp --kb .kb` disponível depois dos setup steps.
- Copilot CLI e Kiro: se o stdout do hook de início de sessão vira contexto.
- Copilot no VS Code: hooks de plugin rodando, task `folderOpen`, `git.repositoryScanMaxDepth`.
- Kiro: `#[[file:.t0/context.md]]` resolvido depois do hook de Session Start; power com `.claude-plugin/` e `hooks/` carregando.
- GHE: auto-merge de PR de registro com 0 aprovações e CODEOWNERS só nos caminhos de conhecimento; App KB-writer como bypass do ruleset para o `kb-render`; token de App com permissões reduzidas; status de workflow agendado valendo como check obrigatório; integração entre GitHub e Jira; push protection.
- `~` em `permissions.additionalDirectories`: não verificado, por isso o `t0` grava sempre caminho absoluto.
