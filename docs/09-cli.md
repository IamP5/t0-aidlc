# CLI

A CLI `t0` faz a parte determinística do fluxo. As skills chamam a CLI, e você também pode chamar direto. Ela é um pacote Python só (`t0-toolkit`), sem daemon.

Todo comando aceita `--kb <pasta>` para apontar o KB (o padrão é `T0_KB`, o workspace ou o KB onde você está). Três regras valem para todo comando que muda alguma coisa:

- ele monta um plano, imprime e só depois aplica;
- aceita `--dry-run`, que mostra o plano sem aplicar;
- o efeito fica limitado a um registro no spool, um PR de conhecimento em draft (ou branch e commit locais, quando não há forge configurado) ou nada.

Relatórios saem em `text`, `github` ou `json` onde o comando aceita `--format`. Saída 3 em qualquer comando quer dizer KB indisponível.

## Configurar

| Comando | O que faz |
|---|---|
| `t0 setup [--repo R] [--check]` | num repo de produto: bloco t0 no `AGENTS.md`, ponteiros por ferramenta, hooks e links das skills `verify-<app>` |
| `t0 doctor` | confere a instalação: `t0` no PATH, config das ferramentas, hooks, KB alcançável |
| `t0 gen [--check] [--scope plugin\|kb] [--src S] [--out O]` | regenera os arquivos gerados do plugin ou do KB (como o `profile.md`); `--check` só acusa diferença |

## Ler o KB

| Comando | O que faz |
|---|---|
| `t0 kb find [--type T] [--text X] [--state S] [--product P] [--bet B]` | busca concepts por texto e frontmatter |
| `t0 kb get <ref>` | lê um concept pelo `uid`, caminho, chave Jira, `BET-NNN` ou `IDEA-NNNN` |
| `t0 kb check [--level L0\|L1\|L2] [--format text\|github\|json] [--changed-from REF]` | confere conformidade com o OKF e o profile; `--changed-from main` olha só o que mudou |
| `t0 context [ref] [--format agents\|delta\|subagent\|json]` | gera o card de contexto, o delta de frescor ou o card de subagente |
| `t0 mcp [--kb DIR] [--read-only]` | sobe o servidor MCP `t0-kb` por stdio |

## Escrever no KB

| Comando | O que faz |
|---|---|
| `t0 new idea\|bet\|spec\|slice\|adr\|harness` | cria um concept a partir do Template e abre o PR em draft; reserva o número olhando o `main` e as branches abertas |
| `t0 new bet --track rapida\|bet <IDEA>` | abre o PR da aposta; na rápida, com o slice |
| `t0 idea prototype <IDEA> --verdict segue\|ajusta\|mata [--ref R]` | grava o veredito do protótipo na Idea |
| `t0 log progress\|decision\|blocker\|kill "<texto>" [--bet B] [--story K]` | grava um registro de passo pela raia de registros |
| `t0 kb propose -m MSG` | abre PR de conhecimento em draft para a branch atual do clone do KB |
| `t0 kb push [--if-due]` | empurra os registros do spool para o KB |
| `t0 adr accept <ADR>` | prepara a mudança do ADR para `accepted`, num PR em draft para quem decide |
| `t0 kb init <dir>` | cria um KB novo a partir do `okf-template` |
| `t0 kb render` | regenera índices, `log.md` e chaves derivadas; roda no workflow `kb-render`, não na mão |

## Decidir

| Comando | O que faz |
|---|---|
| `t0 gate aposta <ref> [--ci]` | confere a decisão de aposta no PR: campos completos, slice completo na rápida, Lead quando cruza pods, é Tier 2 ou passa de 1 semana |
| `t0 gate spec <ref> [--ci]` | confere a decisão de spec: bet ativa, zero `[PRECISA ESCLARECER]`, critérios em bullets, como verificar, slices prontos, Lead em Tier 2 |

O gate grava `state` e `status` no PR de decisão e nunca grava `verified`. O `verified` vem das aprovações do PR, no merge.

## Construir

| Comando | O que faz |
|---|---|
| `t0 bet detect` | imprime a bet ativa e a regra que a resolveu |
| `t0 bet use <BET\|KEY>` | troca a bet ativa; chave Jira resolve por lookup |
| `t0 slice dor <KEY>` | confere o DoR do slice e o WIP de 2 por pessoa |
| `t0 slice start <KEY>` | cria ou troca para a branch `<KEY>-<slug>` no repo do slice; recusa árvore suja |

## CI e espelho

| Comando | O que faz |
|---|---|
| `t0 ci <KEY\|ref> --pr P --state draft\|ready\|merged [--approval A]` | grava os registros de estado do PR para o `kb-render`; no merge de um PR de decisão, grava as aprovações que viram `verified` |
| `t0 bet ship` | no último merge: congela o spec da bet, atualiza o spec vivo e move a Bet para `shipped` |
| `t0 jira sync [--apply] [--tracker file:<dir>]` | espelha bets e slices no Jira a partir do KB; sem `--apply`, só mostra o que faria |

## Rituais e transcrição

| Comando | O que faz |
|---|---|
| `t0 ritual <slug> open` | monta a pauta a partir do KB; na `daily-time`, imprime o digest |
| `t0 ritual <slug> close [--decisions FILE] [--transcript F]` | grava o Ritual Record e abre os PRs de decisão; `harness-health` recusa sem PR por item aceito; `demo` grava o rodízio |
| `t0 transcript redact <arquivo> [--dry-run]` | redação determinística: scanner de segredo, CPF, conta, e-mail e telefone |

Slugs: `daily-time`, `daily-pod`, `harness-health`, `demo`, `retro`, `pi`.

## Hooks

| Comando | O que faz |
|---|---|
| `t0 hook <evento> [--tool claude\|copilot\|kiro]` | entrada única dos hooks das três ferramentas; lê JSON no stdin, e saída 2 bloqueia |

Eventos: `session-start`, `subagent-start`, `prompt-submit`, `pre-tool` e o de fim de sessão.

## Previstos, ainda fora da CLI atual

| Comando | Para quê | Depende de |
|---|---|---|
| `t0 gate degrau <produto>`, `t0 adoption`, `t0 eval run`, `t0 eval add` | decisão de degrau contra os pisos e a regressão de eval; caso de eval novo | primeiro produto chegando às squads piloto |
| `t0 ws init\|sync\|status` | montar e sincronizar o workspace a partir do manifesto | detalhes do GHE do banco |
| `t0 pr check` | status obrigatório `t0/merge-order` entre repos | aprovação do GitHub App |
| `t0 jira sync --reconcile` | reconcile noturno com relatório de drift | integração com o Jira do banco |
| `t0 trace <BET>` | JSON requisito, slice, PR e teste para o auditor | demanda |
| `t0 rules build` | gerar regras de área para as três ferramentas | demanda |
