# Ferramentas

A skill `t0` e os playbooks falam em subagente, lista de tarefas, pergunta ao usuário e skill. Leia este arquivo uma vez por sessão e traduza cada nome para a ferramenta em que você está rodando. Campo sem linha aqui fica de fora, e você diz isso. Passe só campos e valores que o schema da ferramenta aceita.

Fontes de cada coluna:

- Claude Code: o schema das tools numa sessão local e o adapter `docs/harness/claude-code.md` do pstack 0.15.25.
- Copilot CLI: `copilot help` e `copilot skill --help` na versão 1.0.105, um `copilot -p` local que chamou a skill `bet-spec`, e `research/multi-agent-compat.md` (marcado "docs").
- Kiro: só `research/multi-agent-compat.md` (marcado "docs"), sem teste local.

O que não tem fonte está marcado "(não verificado)". Antes de depender de um item assim, teste na sessão e diga o resultado.

## Skills

| t0 | Claude Code | Copilot CLI | Kiro |
|---|---|---|---|
| Chamar uma skill de passo | tool `Skill` com o nome; skill de plugin vai como `t0:<nome>` | tool `skill` com o nome | `/<nome>` (docs); tool para o agente chamar (não verificado) |
| Pastas de projeto | `.claude/skills/` | `.github/skills/`, `.agents/skills/`, `.claude/skills/` | `.kiro/skills/` (docs) |
| Pastas pessoais | `~/.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` | `~/.kiro/skills/` (docs) |
| Plugin | `.claude-plugin/plugin.json`; o humano digita `/t0:<nome>` | plugin no formato Claude e Agent Plugins 1.0 (docs) | power no formato Agent Plugins 1.0 (docs) |
| `verify-<app>` do repo | link de `.t0/skills/verify-<app>/` pelo `t0 setup` (não verificado) | idem (não verificado) | idem (não verificado) |

## Subagentes

| t0 | Claude Code | Copilot CLI | Kiro |
|---|---|---|---|
| Lançar um subagente | tool `Agent` | subagente embutido General-purpose; nome da tool (não verificado); `--fleet` orquestra subagentes em paralelo | tool de spawn (não verificado) |
| `t0-agent` e os revisores | `subagent_type: "t0:t0-agent"` (inferido do padrão `<plugin>:<agente>`), idem para `spec-reviewer`, `standards-reviewer` e `verifier` | agente custom em `.github/agents/<nome>.agent.md` (docs); `--agent <nome>` na linha de comando | `.kiro/agents/<nome>.json` ou `.md` (docs), com `skill://.kiro/skills/*/SKILL.md` em `resources`, senão o agente não carrega as skills (docs) |
| Só leitura | `subagent_type: "Explore"` ou um dos revisores. O Explore mantém `Bash`, então o brief diz "não edite arquivos" e você confere `git status` depois | campo `tools` do agente custom (docs) | campo `tools` do agente (docs) |
| Isolamento | `isolation: "worktree"`; diga a branch ou o commit | (não verificado); crie a worktree com `git worktree add` e passe o caminho no brief | (não verificado); igual ao Copilot |
| Modelo da Policy `models` | `model` aceita só `opus`, `sonnet`, `haiku` ou `fable`; esforço vai em `effort` | `model` no frontmatter do agente (docs); `--model` e `--reasoning-effort` na sessão; por chamada (não verificado) | `model` na config do agente (docs) |
| Segundo plano | padrão; você é avisado quando termina | (não verificado) | (não verificado) |
| Retomar | lance um subagente novo e cole o resultado anterior no brief | (não verificado); faça igual ao Claude Code | (não verificado); igual |

Modelo da Policy que a ferramenta não aceita: omita o campo, rode no modelo da sessão e diga isso na resposta. A família continua a mesma, então o rótulo `same-family` continua valendo.

Os nomes das tools de arquivo mudam por ferramenta (Claude `Bash` e `Read`, Copilot `shell` e `view`, Kiro `shell` e `read`, pelas docs). Escreva o brief pelo que fazer, sem nome de tool.

## Lista de tarefas

| Claude Code | Copilot CLI | Kiro |
|---|---|---|
| `TodoWrite` quando a sessão oferece (o app desktop pode oferecer outra tool de plano no lugar). Sem tool, a lista vai na resposta e é atualizada a cada fase | tool (não verificado); existe modo plano com `--plan` ou `--mode plan`. Sem tool, lista na resposta | tool (não verificado). Sem tool, lista na resposta |

## Perguntar ao usuário

| Claude Code | Copilot CLI | Kiro |
|---|---|---|
| `AskUserQuestion`. Em `claude -p` ela não existe; pergunte em texto e pare | tool (não verificado). Em `copilot -p`, pergunte em texto e pare | tool (não verificado). Em `kiro-cli chat --no-interactive`, pergunte em texto e pare |

## Sem interface

| Claude Code | Copilot CLI | Kiro |
|---|---|---|
| `claude -p` | `copilot -p -s` | `kiro-cli chat --no-interactive` (docs; precisa de `KIRO_API_KEY`, plano pago) |

## Travas

O mesmo `t0 hook <evento> --tool claude|copilot|kiro` roda nas três. O bloqueio volta como erro do hook (exit 2). Trate como resposta final e mude de caminho. Num `copilot -p` local, um hook com erro negou também leituras comuns; se tudo vier negado, mostre a mensagem e rode `t0 doctor`.
