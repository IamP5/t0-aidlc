# Workspace

Um produto tem vários repos, e o agente precisa do KB (a base de conhecimento do time, o repo `t0-kb`) em toda sessão. O workspace resolve os dois problemas. Ele é uma pasta por produto, com o KB e os repos clonados lado a lado. Na raiz dessa pasta fica um `AGENTS.md` gerado, que entrega a qualquer ferramenta o contexto da bet ativa (a aposta em andamento, um trabalho de até 2 semanas).

## A ideia

O KB continua sendo um repo próprio, que o time inteiro consegue ler, e guarda um manifesto por produto. Cada dev mantém um workspace de longa duração por produto, em `~/ws/<produto>/`, com os repos do produto como clones normais. O KB tem um clone só por máquina, em `~/kb`, e o `kb/` de cada workspace é um link para ele. O card de contexto fica na raiz. Claude Code, Copilot e Kiro leem nativamente um `AGENTS.md` de raiz. Por isso, o piso do padrão não depende de plugin, de servidor nem de multi-root. Plugin, hooks e o MCP local só mantêm o card atualizado e acrescentam ferramentas. No dia um não existe serviço hospedado.

O KB não usa git submodules, por causa destes problemas: HEAD destacado (o agente commita e perde o commit), bump de ponteiro todo dia, código velho, KB preso ao repo menos legível e um token de CI que lê todos os repos. Android, Zephyr e Chromium usam manifesto com clones irmãos, e o t0 faz o mesmo.

## O layout

```
~/ws/<produto>/                 pasta que toda ferramenta abre; não é repo git
  AGENTS.md                     gerado: o card de contexto
  .t0/
    workspace.json              gerado: repos clonados e ausentes
    bet.json                    gerado: bet ativa
    context.md                  gerado: delta de frescor do card
    env.sh                      gerado: exports para o Copilot CLI
  .vscode/  .kiro/              gerados por ferramenta
  kb -> ~/kb                    link para o clone único do KB
  api/  web/  ...               clones normais dos repos do produto

~/ws/<produto>@BET-NNN/         opcional: workspace isolado de uma bet, com worktrees
~/kb/                           clone único do t0-kb; fica sempre no main
~/kb.wt/<branch>/               um worktree por branch de conhecimento (bet/BET-NNN/<handle>, kb/<handle>/<tema>)
~/.t0/
  config.yaml                   handle, `kb:` (o caminho do clone), remote do KB, raiz dos workspaces
  spool/                        registros esperando push
  inbox/                        gravações cruas; nenhum agente lê
```

Regras:

- Abra sempre a pasta do workspace como pasta única, nunca como multi-root.
- Cada clone de repo de produto tem um agente só. Um segundo agente em paralelo vai para um workspace isolado.
- O clone do KB é a exceção: várias sessões usam o mesmo. O `t0` nunca troca a branch dele. Cada escrita de conhecimento vai para o worktree da sua branch.
- Um repo sem acesso fica marcado `absent` no `.t0/workspace.json`, e o card informa isso. Assim o agente nunca supõe que o repo está vazio.
- Nada do que é gerado no workspace vai para commit.

## O manifesto

Cada produto tem um manifesto no KB, em `products/<p>/workspace.md`. O manifesto é um concept (um arquivo Markdown do KB com frontmatter) com `type: Workspace`. Ele lista os repos, o papel de cada um, o tier padrão (o nível de review: 0, 1 ou 2) e os `depends_on`. O manifesto só muda por PR revisado. Este é um trecho real do exemplo:

```yaml
type: Workspace
uid: ws-exemplo
workspace:
  schema: 1
  product: exemplo
  jira_project: EXE
  forge: github
  default_branch: main
  repos:
    - name: status-bot
      url: git@github.example.bank:t0/status-bot.git
      role: "Bot que monta e publica o status antes da daily do time"
      kind: worker
      optional: false
      tier: 1
      depends_on: []
```

O manifesto não fixa revisão: a bet sempre parte da branch padrão de cada repo. Token e credencial nunca entram no manifesto.

## Montando o workspace

Na primeira vez, clone o repo do t0 e rode o instalador com o remote do KB:

```
git clone git@github.example.bank:t0/t0-aidlc.git && cd t0-aidlc
./install.sh --kb git@github.example.bank:t0/t0-kb.git
```

O `install.sh` precisa de `python3` 3.11 ou mais novo e de `git`. Ele instala a CLI com `uv` ou `pipx` e chama o `t0 install`. O `t0 install` faz o resto, nesta ordem:

- grava `~/.t0/config.yaml` com `handle`, `kb`, `kb_remote` e `ws_root`, todos em caminho absoluto, e mantém as outras chaves. Com o `gh` no PATH e sem `forge` no config, grava também `forge: github:<dono>/<repo>` a partir do remote do KB;
- clona o KB em `~/kb`, se ainda não houver um KB no `kb` do config;
- instala o plugin no Claude Code (`claude plugin marketplace add` e `claude plugin install t0@t0-aidlc`), se o `claude` estiver no PATH;
- junta em `~/.claude/settings.json` os `additionalDirectories` de `~/ws`, `~/kb` e `~/kb.wt` e o `instructionFiles`, sem mexer nas outras chaves;
- roda o `t0 ws init` para cada produto dos `pods` do seu arquivo em `team/people/<handle>.md`, ou para cada `--product` que você passar.

Rodar de novo não muda nada. O `t0 install --check` mostra o que falta e sai com 1 se houver pendência.

Para montar o workspace de outro produto depois:

```
t0 ws init exemplo
```

O comando lê o manifesto e cria `~/ws/exemplo/`. Ele liga `kb` ao clone do config e clona cada repo como irmão. Um repo que falha no clone, por exemplo com 403, entra em `absent` no `.t0/workspace.json`, e os outros seguem. Depois ele gera o `AGENTS.md` e o `.t0/env.sh`. Rodar de novo só clona o que falta e atualiza os arquivos gerados. O comando não roda o `t0 setup` nos repos, porque isso é um commit no repo. Ele lista os repos sem o bloco t0 no `AGENTS.md`.

Se precisar montar à mão:

```
git clone git@github.example.bank:t0/t0-kb.git ~/kb
echo "kb: $HOME/kb" >> ~/.t0/config.yaml
mkdir -p ~/ws/exemplo && cd ~/ws/exemplo
ln -s ~/kb kb
git clone git@github.example.bank:t0/status-bot.git status-bot
t0 context --kb kb --format agents > AGENTS.md
```

A URL de cada repo está no manifesto. O `t0 doctor` avisa quando o `kb/` do workspace aponta para outro clone que não o do `config.yaml`. Para trocar a bet ativa, use `t0 bet use BET-002`. Para conferir qual bet a sessão enxerga, use `t0 bet detect`.

## Várias iniciativas

Quem está em mais de um pod trabalha com um KB e um workspace por produto. Para trocar de produto, abra outra janela no workspace do outro produto. As duas sessões podem rodar ao mesmo tempo.

- O WIP de 2 slices em construção conta somando todos os produtos.
- `t0 bet use` recusa bet de outro produto e diz qual workspace abrir.
- O hook de prompt avisa numa linha quando você cita a chave de outra bet, com a bet e o produto dela.
- Cada branch de conhecimento vive no seu worktree, em `~/kb.wt/<branch>`. O `t0 new`, o `t0 gate`, o `t0 ritual close` e os outros comandos de conhecimento escrevem lá e imprimem o caminho. O clone `~/kb` fica no main.
- Edite à mão no worktree que o `t0` imprimiu. O `t0 kb propose` commita o worktree onde você está. Fora de um worktree, ele usa o único worktree com mudanças. Com mudanças no `~/kb`, ele as leva para uma branch nova. Se a branch já existe, ele recusa e diz para onde mover.
- O `t0 gate` recusa quando o `~/kb` tem mudanças sem commit na pasta da bet, porque elas ficariam fora do PR.
- A reserva de número (IDEA, BET, ADR, HI) roda uma de cada vez: a segunda sessão espera a primeira gravar o commit.
- O push dos registros roda um de cada vez. Se outra sessão está empurrando, o hook de fim pula e tenta na próxima.
- No Claude Code, `permissions.additionalDirectories` em `~/.claude/settings.json` precisa de caminhos absolutos (sem `~`) que cubram `~/ws`, `~/kb` e `~/kb.wt`. O `t0 doctor` confere e mostra a entrada exata.

## O card de contexto (AGENTS.md)

O card é o `AGENTS.md` da raiz do workspace, e o `t0 context` é quem o gera. O card tem teto duro de 8.000 caracteres e 150 linhas. Quando passa do teto, o renderer corta de baixo para cima e sempre mantém as três primeiras seções.

O card traz, nesta ordem:

1. Cabeçalho: o que é o KB, onde ele mora (`./kb`), as três raias (os caminhos de escrita no KB: registros, conhecimento e derivados), a frase "spec é o contrato; pergunte antes de desviar" e o carimbo `<!-- t0:card kb=<sha> at=... rule=... -->`.
2. Bet ativa: título, estado, apetite e dias restantes, o problema, a Story ativa com os critérios de aceite e links para spec, slices e ADRs.
3. Repos: nome, papel, branch e posição no merge. Os repos da bet e os `absent` aparecem marcados.
4. Change set da bet (os PRs dos slices nos vários repos): PRs, estado, `depends_on`.
5. Outros slices abertos, só com o título.
6. Mapa do KB: seções do `index.md` raiz e verbetes do glossário do produto.
7. Ponteiros de skill.

O resto chega sob demanda, pelo `index.md` e pelo MCP. O renderer lê o KB de `origin/main` via `git show`. Por isso, a branch em que o `kb/` está não muda o card.

### Card velho

Só um comando reescreve o card (`t0 bet use`, comandos de ritual, sync do workspace). No início de cada sessão, o hook roda `t0 context --format delta`. Esse comando compara o carimbo do card com o último commit de `origin/main` que toca a bet ou o manifesto. Se nada mudou, ele imprime uma linha ("card em dia"). Se algo mudou, ele injeta só o delta, com até 3.000 caracteres. Offline, o card mostra a idade em vez de travar.

### Orçamento de contexto

| Camada | Teto (caracteres) | Quando carrega |
|---|---|---|
| Card no `AGENTS.md` da raiz | 8.000, até 150 linhas | sempre |
| Delta | 3.000, normalmente uma linha | só com card velho |
| Instruções do MCP `t0-kb` | 1.500 | sempre |
| Bloco t0 no `AGENTS.md` de cada repo tocado | 1.200 por repo, até 15 linhas | quando o agente mexe no repo |
| Listagem de skills do plugin | até 300 por skill | sempre |
| Card de subagente | 1.500 | em cada subagente |
| Corpo do spec, ADRs, metodologia | sob demanda | leitura, `kb_get`, skills |

## Como a sessão sabe a bet ativa

O `t0 bet detect` procura a bet ativa nesta ordem, e o primeiro acerto vence:

1. a variável `T0_BET` (CI, execução scriptada, override);
2. a branch do repo no diretório atual;
3. o `.t0/bet.json`, subindo a partir do diretório atual;
4. uma chave Jira no texto da tarefa ou da issue, resolvida pelo `jira:` dos slices no KB (é o caso do cloud agent);
5. nenhuma: o card mostra o mapa do KB e pede a bet.

Skills que geram código se recusam a escrever código sem bet resolvida. Skills de ritual funcionam sem bet. Se a branch aponta uma bet diferente da que está no `bet.json`, o hook avisa numa linha.

## O MCP `t0-kb`

O `t0 mcp` sobe o servidor `t0-kb` por stdio. É um processo local, sem porta e sem serviço hospedado. O plugin já registra o servidor. O servidor oferece estas ferramentas:

| Ferramenta | O que faz |
|---|---|
| `kb_find` | busca concepts por texto, tipo e produto |
| `kb_get` | lê um concept pelo id, `uid` ou caminho |
| `kb_context` | devolve o card de uma bet ou chave |
| `bet_detect` | resolve a bet ativa a partir do diretório |
| `kb_check` | roda o `kb check` num nível |
| `kb_record` | grava um registro de passo no spool (a única escrita) |

Com `--read-only`, o `kb_record` fica de fora. Em cloud agent e CI, o job faz checkout só leitura do `t0-kb` em `.kb/` e roda `t0 mcp --kb .kb --read-only`. Sem KB, o agente para e avisa "KB indisponível".

## O que cada repo de produto commita

Rodado na raiz de um repo de produto, o `t0 setup` escreve:

- o bloco t0 no `AGENTS.md` do repo, com até 15 linhas, entre `<!-- t0:begin -->` e `<!-- t0:end -->`. O bloco informa o produto, onde achar o KB (`../kb`, `.kb/` ou o MCP), a convenção de branch e de PR e a regra "nunca copie spec para este repo; referencie pela chave";
- os ponteiros: `CLAUDE.md`, `.github/copilot-instructions.md` e `.kiro/steering/` só apontam para o `AGENTS.md`, que é o arquivo canônico;
- os hooks de cada ferramenta;
- os links da skill `verify-<app>`, de `.t0/skills/verify-<app>/` para cada ferramenta.

O `t0 setup` não copia nenhuma skill para o repo. A fiação mora no workspace e no plugin.

## Suporte por ferramenta

O contexto chega em três camadas. A primeira, sozinha, já garante que o agente receba o contexto correto. As outras duas trazem frescor e ferramentas.

1. Arquivo: o `AGENTS.md` da raiz, igual nas três ferramentas.
2. Hooks: avisam quando o card está velho, reinjetam o card depois de compactação, dão card aos subagentes e aplicam as travas.
3. MCP: o `t0-kb`, igual nas três.

### Claude Code

- O `AGENTS.md` da raiz carrega como arquivo ancestral, mesmo quando a sessão abre dentro de `api/`. Os repos têm `CLAUDE.md` ponteiro, e um `CLAUDE.md` desliga a leitura de `AGENTS.md`. Por isso, a config de usuário precisa de `instructionFiles: claude-md-and-agents-md`. O `t0 install` grava essa config em `~/.claude/settings.json`, e o `t0 doctor` confere.
- Hooks do plugin: SessionStart (`startup`, `resume`, `clear`, `compact`) roda o delta. SubagentStart dá o card de subagente, porque o subagente nasce sem memória. UserPromptSubmit avisa quando você cita a chave de outra bet. PreToolUse aplica as travas. Stop empurra os registros pendentes.
- As skills do plugin aparecem como `/t0:<nome>`.

### GitHub Copilot

- VS Code (agent mode): abra `~/ws/<produto>` como pasta única. O `AGENTS.md` da raiz carrega por padrão (`chat.useAgentsMdFile`). Uma task de abertura de pasta roda o sync antes do chat (não verificado). O hook de início de sessão roda com os matchers ignorados (não verificado).
- Copilot CLI: rode `source ~/ws/<produto>/.t0/env.sh` antes de abrir. O script exporta `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` para que o `AGENTS.md` da raiz carregue mesmo dentro de um repo. O plugin entra por `copilot plugin install`, que lê o formato Claude. Ainda falta confirmar se o stdout do hook vira contexto (não verificado). De qualquer jeito, o card chega pelo arquivo.
- Cloud agent: não tem workspace. O `AGENTS.md` commitado no repo traz o bloco t0, e os setup steps fazem checkout só leitura do KB em `.kb/` (não verificado: setup steps liberados no GHE do banco). O agente pega a chave Jira da issue e chama `kb_context`.

### Kiro

- Abra `~/ws/<produto>` como pasta, no IDE ou no `kiro-cli chat`. O `AGENTS.md` entra sempre.
- O recurso de specs do Kiro fica desligado, porque o spec mora no KB.
- `.kiro/hooks/t0.json`: Session Start roda o delta, Agent Stop empurra os registros e Pre Tool Use roda as travas. O steering `t0.md` com `inclusion: always` inclui `.t0/context.md`, então o delta entra sem duplicar o card. Ainda falta confirmar se o include resolve depois do hook de Session Start (não verificado).
- Skills e MCP vêm do plugin, empacotado como power. Os custom agents do Kiro ficam de fora, porque não carregam steering nem skills.

## Bet paralela

Às vezes um agente já está rodando num repo e chega outra bet para o mesmo repo. Nesse caso, use um workspace isolado ao lado do principal, `~/ws/<produto>@BET-NNN/`, com worktrees só dos repos da bet e card próprio. O workspace isolado fica ao lado do principal, nunca dentro dele. Se ficasse dentro, o `AGENTS.md` do principal viraria ancestral, e a sessão carregaria dois cards.

## O que falta verificar antes do rollout

- auto-merge da raia de registros sob a proteção de branch do banco (até lá, vale o modo `batch`);
- setup steps e MCP stdio no cloud agent do Copilot;
- stdout de hook virando contexto no Copilot CLI e no Kiro;
- `verify-<app>` ligado pelo `t0 setup` no Copilot e no Kiro (não verificado).
