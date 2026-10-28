# CLI

A CLI `t0` faz a parte determinística do fluxo. As skills chamam a CLI, e você também pode chamá-la direto. Ela é um único pacote Python (`t0-toolkit`), sem daemon.

Todo comando aceita `--kb <pasta>` para apontar o KB (a base de conhecimento do time). Sem a flag, o padrão é `T0_KB`, o workspace ou o KB onde você está. Todo comando que muda alguma coisa segue três regras:

- monta um plano, imprime o plano e só depois aplica;
- aceita `--dry-run`, que mostra o plano sem aplicar;
- tem efeito limitado a um registro no spool (a pasta local onde os registros esperam o push), a um PR de conhecimento em draft (ou a branch e commit locais, quando não há forge configurado) ou a nada.

Cada branch de conhecimento tem um worktree próprio, em `<kb>.wt/<branch>` (por exemplo `~/kb.wt/bet/BET-012/ana`). O comando escreve lá e imprime o caminho. O clone do KB fica no main, então duas sessões no mesmo clone não escrevem uma na branch da outra. Um ref que ainda não entrou no main (uma bet recém-criada, por exemplo) é procurado também nos worktrees. O `t0 kb find` lê só o main e o spool.

Nos comandos que aceitam `--format`, o relatório sai em `text`, `github` ou `json`. Em qualquer comando, o código de saída 3 quer dizer KB indisponível.

## Configurar

| Comando | O que faz |
|---|---|
| `t0 install [--kb URL\|PASTA] [--handle H] [--root DIR] [--product P ...] [--plugin-source S] [--check]` | uma vez por máquina: grava `~/.t0/config.yaml`, clona o KB, instala o plugin no Claude Code, junta `additionalDirectories` e `instructionFiles` em `~/.claude/settings.json` e roda o `ws init` dos seus produtos; rodar de novo não muda nada |
| `t0 ws init <produto> [--root DIR] [--check]` | monta `~/ws/<produto>`: link `kb`, um clone por repo do manifesto (o que falha vai para `absent`), `AGENTS.md`, `.t0/workspace.json` e `.t0/env.sh`; lista os repos sem o bloco t0 |
| `t0 setup [--repo R] [--check]` | num repo de produto, escreve o bloco t0 no `AGENTS.md`, os ponteiros por ferramenta, os hooks e os links das skills `verify-<app>` |
| `t0 doctor` | confere a instalação: `t0` no PATH, config das ferramentas, hooks e se o KB está alcançável; avisa quando o `kb/` do workspace não é o clone do `config.yaml`, quando o Claude Code não tem `additionalDirectories` absolutos para `~/ws`, `~/kb` e `~/kb.wt` e quando o `instructionFiles` não é `claude-md-and-agents-md` |
| `t0 gen [--check] [--scope plugin\|kb] [--src S] [--out O]` | regenera os arquivos gerados do plugin ou do KB (como o `profile.md`); com `--check`, só aponta as diferenças |

## Ler o KB

| Comando | O que faz |
|---|---|
| `t0 kb find [--type T] [--text X] [--state S] [--product P] [--bet B]` | busca concepts (os arquivos do KB) por texto e por frontmatter |
| `t0 kb get <ref>` | lê um concept pelo `uid`, caminho, chave Jira, `BET-NNN` ou `IDEA-NNNN` |
| `t0 kb check [--level L0\|L1\|L2] [--format text\|github\|json] [--changed-from REF]` | confere a conformidade com o OKF e o profile; com `--changed-from main`, olha só o que mudou |
| `t0 context [ref] [--format agents\|delta\|subagent\|json]` | gera o card de contexto, o delta de frescor ou o card de subagente |
| `t0 mcp [--kb DIR] [--read-only]` | sobe o servidor MCP `t0-kb` por stdio |

## Escrever no KB

| Comando | O que faz |
|---|---|
| `t0 new idea\|bet\|spec\|slice\|adr\|harness` | cria um concept a partir do Template e abre o PR em draft; para reservar o número, olha o `main` e as branches abertas |
| `t0 new bet --track rapida\|bet <IDEA>` | abre o PR da aposta; na trilha rápida, o PR já vem com o slice |
| `t0 idea prototype <IDEA> --verdict segue\|ajusta\|mata [--ref R]` | grava na Idea o veredito do protótipo |
| `t0 log progress\|decision\|blocker\|kill "<texto>" [--bet B] [--story K]` | grava um registro de passo pela raia de registros |
| `t0 kb propose -m MSG` | abre um PR de conhecimento em draft com as edições à mão: as do worktree onde você está; fora de um, as do único worktree com mudanças; com mudanças no clone do KB, leva-as para uma branch nova (recusa se a branch já existe) |
| `t0 kb push [--if-due]` | empurra para o KB os registros do spool; se outra sessão já está empurrando, pula com "push em andamento em outra sessão" |
| `t0 adr accept <ADR>` | prepara a mudança do ADR para `accepted` num PR em draft, para quem decide |
| `t0 kb init <dir>` | cria um KB novo a partir do `okf-template` |
| `t0 kb render` | regenera índices, `log.md` e chaves derivadas; quem roda é o workflow `kb-render`, não uma pessoa |

## Decidir

| Comando | O que faz |
|---|---|
| `t0 gate aposta <ref> [--ci]` | confere a decisão de aposta no PR: campos completos, slice completo na trilha rápida e o Lead quando a bet cruza pods, é Tier 2 ou passa de 1 semana |
| `t0 gate spec <ref> [--ci]` | confere a decisão de spec: bet ativa, zero `[PRECISA ESCLARECER]`, critérios em bullets, como verificar, slices prontos e o Lead em Tier 2 |

O gate grava `state` e `status` no PR de decisão e nunca grava `verified` (a chave que diz qual humano confirmou e quando). O `verified` vem das aprovações do PR, no merge.

## Construir

| Comando | O que faz |
|---|---|
| `t0 bet detect` | imprime a bet ativa e a regra que a resolveu |
| `t0 bet use <BET\|KEY>` | troca a bet ativa; uma chave Jira é resolvida por lookup; recusa bet de outro produto e diz qual workspace abrir |
| `t0 slice dor <KEY>` | confere o DoR do slice (o que ele precisa ter para começar) e o WIP de 2 por pessoa |
| `t0 slice start <KEY>` | cria a branch `<KEY>-<slug>` no repo do slice, ou troca para ela; recusa se a árvore estiver suja |

## CI e espelho

| Comando | O que faz |
|---|---|
| `t0 ci <KEY\|ref> --pr P --state draft\|ready\|merged [--approval A]` | grava os registros de estado do PR para o `kb-render`; no merge de um PR de decisão, grava as aprovações que viram `verified` |
| `t0 bet ship` | no último merge, congela o spec da bet, atualiza o spec vivo e move a Bet para `shipped` |
| `t0 jira sync [--apply] [--tracker file:<dir>]` | espelha no Jira as bets e os slices do KB; sem `--apply`, só mostra o que faria |

## Rituais e transcrição

| Comando | O que faz |
|---|---|
| `t0 ritual <slug> open` | monta a pauta a partir do KB; na `daily-time`, imprime o digest |
| `t0 ritual <slug> close [--decisions FILE] [--transcript F]` | grava o Ritual Record e abre os PRs de decisão; no `harness-health`, recusa fechar se algum item aceito não tiver PR; na `demo`, grava o rodízio |
| `t0 transcript redact <arquivo> [--dry-run]` | faz a redação determinística do arquivo, com scanner de segredo, CPF, conta, e-mail e telefone |

Slugs: `daily-time`, `daily-pod`, `harness-health`, `demo`, `retro`, `pi`.

## Hooks

| Comando | O que faz |
|---|---|
| `t0 hook <evento> [--tool claude\|copilot\|kiro]` | entrada única dos hooks das três ferramentas; lê JSON no stdin, e o código de saída 2 bloqueia |

Eventos: `session-start`, `subagent-start`, `prompt-submit`, `pre-tool` e o de fim de sessão.

## Previstos, ainda fora da CLI atual

| Comando | Para quê | Depende de |
|---|---|---|
| `t0 gate degrau <produto>`, `t0 adoption`, `t0 eval run`, `t0 eval add` | decidir o degrau contra os pisos e a regressão de eval; adicionar caso de eval novo | primeiro produto chegando às squads piloto |
| `t0 ws sync\|status` | sincronizar o workspace (fetch e ff-only) e mostrar o estado de cada repo | detalhes do GHE do banco |
| `t0 pr check` | status obrigatório `t0/merge-order` entre repos | aprovação do GitHub App |
| `t0 jira sync --reconcile` | reconciliação noturna, com relatório de drift | integração com o Jira do banco |
| `t0 trace <BET>` | gerar para o auditor um JSON que liga requisito, slice, PR e teste | demanda |
| `t0 rules build` | gerar regras de área para as três ferramentas | demanda |
