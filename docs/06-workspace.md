# Workspace

Um produto tem vários repos, e o agente precisa do KB em toda sessão. O workspace resolve as duas coisas: uma pasta por produto, com o KB e os repos clonados lado a lado, e um `AGENTS.md` gerado na raiz que entrega o contexto da bet ativa para qualquer ferramenta.

## A ideia

O KB continua um repo próprio, legível pelo time inteiro, e guarda um manifesto por produto. Cada dev tem um workspace de longa duração por produto, `~/ws/<produto>/`, com o KB e os repos do produto como clones normais. Na raiz mora o card de contexto. Claude Code, Copilot e Kiro leem um `AGENTS.md` de raiz nativamente, então o piso do padrão não depende de plugin, de servidor nem de multi-root. Plugin, hooks e o MCP local só deixam o card fresco e somam ferramentas. No dia um não existe serviço hospedado.

O KB não usa git submodules. Submodule dá HEAD destacado (o agente commita e perde o commit), bump de ponteiro diário, código velho, KB preso ao repo menos legível e um token de CI que lê todos os repos. Android, Zephyr e Chromium usam manifesto mais clones irmãos, e o t0 faz igual.

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
  kb/                           clone normal do t0-kb
  api/  web/  ...               clones normais dos repos do produto

~/ws/<produto>@BET-NNN/         opcional: workspace isolado de uma bet, com worktrees
~/.t0/
  config.yaml                   handle, remote do KB, raiz dos workspaces
  spool/                        registros esperando push
  inbox/                        gravações cruas; nenhum agente lê
```

Regras:

- Abra sempre a pasta do workspace como pasta única. Nunca multi-root.
- Cada clone tem um agente só. Segundo agente em paralelo vai para um workspace isolado.
- Repo sem acesso fica marcado `absent` no `.t0/workspace.json`, e o card diz isso. Assim o agente nunca acha que o repo está vazio.
- Nada gerado no workspace é commitado.

## O manifesto

Cada produto tem um manifesto no KB, em `products/<p>/workspace.md`, um concept `type: Workspace`. Ele lista os repos, o papel de cada um, o tier padrão e os `depends_on`. Muda por PR revisado. Trecho real do exemplo:

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

O manifesto não fixa revisão. A bet sempre parte da branch padrão de cada repo. Token e credencial nunca aparecem ali.

## Montando o workspace

O padrão prevê `t0 ws init <produto>`, que lê o manifesto, clona o KB e os repos como irmãos, pula o que der 403 e gera o `AGENTS.md`. O clone automático ainda não está na CLI atual: depende de detalhes do GHE do banco. Até lá, monte à mão:

```
mkdir -p ~/ws/exemplo && cd ~/ws/exemplo
git clone git@github.example.bank:t0/t0-kb.git kb
git clone git@github.example.bank:t0/status-bot.git status-bot
t0 context --kb kb --format agents > AGENTS.md
```

A URL de cada repo está no manifesto. Para trocar a bet ativa, `t0 bet use BET-002`. Para conferir qual bet a sessão enxerga, `t0 bet detect`.

## O card de contexto (AGENTS.md)

O card é o `AGENTS.md` da raiz do workspace, gerado pelo `t0 context`. Teto duro de 8.000 caracteres e 150 linhas. Quando estoura, o renderer corta de baixo para cima e mantém sempre as três primeiras seções.

Conteúdo, em ordem:

1. Cabeçalho: o que é o KB, onde mora (`./kb`), as três raias, "spec é o contrato; pergunte antes de desviar" e o carimbo `<!-- t0:card kb=<sha> at=... rule=... -->`.
2. Bet ativa: título, estado, apetite e dias restantes, o problema, a Story ativa com os critérios de aceite, links para spec, slices e ADRs.
3. Repos: nome, papel, branch, posição no merge; os da bet marcados, os `absent` marcados.
4. Change set da bet: PRs, estado, `depends_on`.
5. Outros slices abertos, só o título.
6. Mapa do KB: seções do `index.md` raiz e verbetes do glossário do produto.
7. Ponteiros de skill.

O resto chega sob demanda, pelo `index.md` e pelo MCP. O renderer lê o KB de `origin/main` via `git show`, então a branch em que o `kb/` está não muda o card.

### Card velho

O card só é reescrito por comando (`t0 bet use`, comandos de ritual, sync do workspace). No início de cada sessão, o hook roda `t0 context --format delta`. Ele compara o carimbo do card com o último commit de `origin/main` que toca a bet ou o manifesto. Se nada mudou, imprime uma linha ("card em dia"). Se mudou, injeta só o delta, com até 3.000 caracteres. Offline, o card mostra a idade em vez de travar.

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

`t0 bet detect` resolve nesta ordem, e o primeiro acerto vence:

1. variável `T0_BET` (CI, execução scriptada, override);
2. branch do repo no diretório atual;
3. `.t0/bet.json`, subindo a partir do diretório atual;
4. uma chave Jira no texto da tarefa ou da issue, resolvida pelo `jira:` dos slices no KB (é o caso do cloud agent);
5. nenhuma: o card mostra o mapa do KB e pede a bet.

Skills que geram código se recusam a escrever código sem bet resolvida. Skills de ritual funcionam sem bet. Se a branch aponta uma bet diferente da do `bet.json`, o hook avisa numa linha.

## O MCP `t0-kb`

`t0 mcp` sobe o servidor `t0-kb` por stdio: um processo local, sem porta e sem serviço hospedado. O plugin já registra o servidor. As ferramentas:

| Ferramenta | O que faz |
|---|---|
| `kb_find` | busca concepts por texto, tipo e produto |
| `kb_get` | lê um concept pelo id, `uid` ou caminho |
| `kb_context` | devolve o card de uma bet ou chave |
| `bet_detect` | resolve a bet ativa a partir do diretório |
| `kb_check` | roda o `kb check` num nível |
| `kb_record` | grava um registro de passo no spool (a única escrita) |

Com `--read-only`, o `kb_record` sai. Em cloud agent e CI, o job faz checkout só leitura do `t0-kb` em `.kb/` e roda `t0 mcp --kb .kb --read-only`. Sem KB, o agente para e avisa "KB indisponível".

## O que cada repo de produto commita

O `t0 setup`, rodado na raiz de um repo de produto, escreve:

- o bloco t0 no `AGENTS.md` do repo, com até 15 linhas, entre `<!-- t0:begin -->` e `<!-- t0:end -->`: o produto, onde achar o KB (`../kb`, `.kb/` ou o MCP), a convenção de branch e de PR e a regra "nunca copie spec para este repo; referencie pela chave";
- ponteiros: `CLAUDE.md`, `.github/copilot-instructions.md` e `.kiro/steering/` só apontam para o `AGENTS.md`, que é o canônico;
- os hooks por ferramenta;
- os links da skill `verify-<app>` de `.t0/skills/verify-<app>/` para cada ferramenta.

Nenhuma skill é copiada para o repo. A fiação mora no workspace e no plugin.

## Suporte por ferramenta

O contexto chega em três camadas. A primeira sozinha já garante correção. As outras trazem frescor e ferramentas.

1. Arquivo: o `AGENTS.md` da raiz, igual para as três.
2. Hooks: avisam card velho, reinjetam depois de compactação, dão card aos subagentes e guardam as travas.
3. MCP: o `t0-kb`, igual nas três.

### Claude Code

- O `AGENTS.md` da raiz carrega como ancestral, mesmo abrindo a sessão dentro de `api/`. Como os repos têm `CLAUDE.md` ponteiro, e `CLAUDE.md` desliga a leitura de `AGENTS.md`, a config de usuário precisa de `instructionFiles: claude-md-and-agents-md`. O `t0 doctor` confere.
- Hooks do plugin: SessionStart (`startup`, `resume`, `clear`, `compact`) roda o delta; SubagentStart dá o card de subagente, porque subagente nasce sem memória; UserPromptSubmit avisa quando você cita chave de outra bet; PreToolUse aplica as travas; Stop empurra registros pendentes.
- Skills do plugin aparecem como `/t0:<nome>`.

### GitHub Copilot

- VS Code (agent mode): abra `~/ws/<produto>` como pasta única. O `AGENTS.md` da raiz carrega por padrão (`chat.useAgentsMdFile`). Uma task de abertura de pasta roda o sync antes do chat (não verificado). O hook de início de sessão roda com matchers ignorados (não verificado).
- Copilot CLI: `source ~/ws/<produto>/.t0/env.sh` antes de abrir. O script exporta `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` para o `AGENTS.md` da raiz carregar mesmo dentro de um repo. O plugin entra por `copilot plugin install`, que lê o formato Claude. Se o stdout do hook vira contexto ainda está para confirmar (não verificado); o card chega pelo arquivo de qualquer jeito.
- Cloud agent: não tem workspace. O `AGENTS.md` commitado do repo traz o bloco t0, e os setup steps fazem checkout só leitura do KB em `.kb/` (não verificado: setup steps liberados no GHE do banco). O agente pega a chave Jira da issue e chama `kb_context`.

### Kiro

- Abra `~/ws/<produto>` como pasta, no IDE ou no `kiro-cli chat`. O `AGENTS.md` entra sempre.
- O recurso de specs do Kiro fica desligado. Spec mora no KB.
- `.kiro/hooks/t0.json`: Session Start roda o delta, Agent Stop empurra registros, Pre Tool Use roda as travas. O steering `t0.md` com `inclusion: always` inclui `.t0/context.md`, então o delta entra sem duplicar o card. Se o include resolve depois do hook de Session Start ainda falta confirmar (não verificado).
- Skills e MCP vêm do plugin empacotado como power. Custom agents do Kiro ficam de fora, porque não carregam steering nem skills.

## Bet paralela

Quando já tem um agente rodando num repo e cai outra bet no mesmo repo, use um workspace isolado ao lado do principal, `~/ws/<produto>@BET-NNN/`, com worktrees só dos repos da bet e card próprio. Ele fica ao lado, nunca dentro: dentro, o `AGENTS.md` do principal viraria ancestral e a sessão carregaria dois cards.

## O que falta verificar antes do rollout

- auto-merge da raia de registros sob a proteção de branch do banco (até lá, modo `batch`);
- setup steps e MCP stdio no cloud agent do Copilot;
- stdout de hook virando contexto no Copilot CLI e no Kiro;
- `verify-<app>` ligado pelo `t0 setup` no Copilot e no Kiro (não verificado).
