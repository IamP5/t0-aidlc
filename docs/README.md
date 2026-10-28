# t0: como o time vai da ideia à produção com agentes

O t0 é a metodologia do time de Inovação em IA. Ela cobre o caminho inteiro: a ideia vira protótipo, o protótipo vira aposta, a aposta vira spec e slices, os slices viram PRs e o que vai pro ar sobe os degraus de adoção até as squads do ART.

Por baixo, três peças sustentam o dia a dia:

- o KB do time (`t0-kb`), um repositório no formato OKF que guarda ideias, bets, specs, decisões, rituais e o harness;
- o plugin `t0`, com 15 skills em pt-BR, subagentes, hooks e o MCP `t0-kb`, que roda igual no Claude Code, no GitHub Copilot e no Kiro;
- a CLI `t0`, que faz a parte determinística: cria arquivos no KB, confere gates, abre e fecha rituais, redige transcrições e gera o contexto de cada sessão.

## Para quem

- Gente do time, nos três pods, que usa o fluxo todo dia.
- Gente de squad que entra numa daily do pod como Domain Expert ou que vai adotar uma ferramenta do time.
- Quem precisa auditar uma decisão. O histórico git do KB é a trilha de auditoria que o banco pede.

## A regra

> Um passo de processo só entra quando protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado. Se não protege nem ensina, sai.

Toda página daqui passa por essa régua. A Retro mensal aplica a régua de novo e corta o que não pagou o próprio custo.

## Em 1 minuto

A ideia vira protótipo na hora, em minutos ou horas, e o pod decide na daily seguinte se ela vira bet. Bet tem apetite de até 2 semanas e passa por spec e slices. Ajuste que cabe em um dia vai pela trilha rápida, sem spec.

Só três decisões humanas ficam registradas: aposta, spec e degrau de adoção. O resto é review de PR ou automação.

Por dentro não tem sprint. A Demo a cada 2 semanas segue a iteração do ART, o Harness Health é semanal e a Retro é mensal. O WIP é limitado por review pendente: no máximo 2 slices em construção por pessoa.

São seis rituais, com cerca de 3h20 de cerimônia pura por pessoa a cada 2 semanas. Todo comando do `t0` grava o passo no KB, e ninguém escreve ata à mão. O Jira é espelho gerado do KB. O código mora nos repos de produto.

Erro de agente que se repete vira sensor: lint, teste, hook de git ou gate de CI. Contexto é orçamento, e o que não pegou é desligado.

## Como ler estas páginas

| Página | O que tem | Leia se |
|---|---|---|
| [Princípios](01-principios.md) | a régua enxuta e os oito princípios | você quer entender o porquê de cada regra |
| [Papéis e pods](02-papeis-e-pods.md) | os 5 papéis, os 3 pods, rodízios e práticas de júnior | você está chegando ao time |
| [Fluxo](03-fluxo.md) | da ideia aos degraus de adoção, trilhas, decisões, WIP | você vai propor, apostar ou construir algo |
| [Rituais](04-rituais.md) | os seis rituais, a conta de tempo e as transcrições | você facilita ou participa de um ritual |
| [KB em OKF](05-kb-okf.md) | o bundle, os tipos, as raias de escrita e o Jira | você vai ler ou escrever no KB |
| [Workspace](06-workspace.md) | o workspace multi-repo, o card de contexto e o MCP | você vai configurar a máquina |
| [Plugin e skills](07-plugin-e-skills.md) | instalação, `/t0` e as 15 skills | você vai trabalhar com o agente |
| [Guia prático](08-guia-pratico.md) | passo a passo com os comandos | você quer fazer agora |
| [CLI](09-cli.md) | referência dos comandos `t0` | você precisa de um comando específico |
| [Harness e qualidade](10-harness-e-qualidade.md) | escada do harness, tiers, evals, pisos de adoção e métricas | você é Harness Keeper ou revisa PR |
| [Glossário](11-glossario.md) | os termos do time, em pt-BR e inglês | você travou numa palavra |

Três caminhos curtos:

- chegando no time: esta página, [Princípios](01-principios.md), [Fluxo](03-fluxo.md) e [Guia prático](08-guia-pratico.md);
- configurando a máquina: [Workspace](06-workspace.md) e [Plugin e skills](07-plugin-e-skills.md);
- facilitando ritual: [Papéis e pods](02-papeis-e-pods.md) e [Rituais](04-rituais.md).

## Convenções destas páginas

- KB é o repositório OKF do time, `t0-kb`, no OKF v0.2 com o profile `t0-team`.
- Skill aparece grafada como `bet-spec` e é chamada pelo nome em qualquer ferramenta. No Claude Code, com o plugin, o nome digitado é `/t0:bet-spec`.
- Comando da CLI aparece como `t0 <subcomando>`.
- `PROPOSTA` marca número ou piso que ainda não está valendo. Ele entra no profile com `state: proposed` e só vira `in-force` depois de 3 ferramentas passarem pelo funil.
- `(não verificado)` marca afirmação que a pesquisa não confirmou ou mecanismo que precisa de teste antes do rollout.
- Os termos bet, slice, spec, Tier, Bet Owner, Harness Keeper e Flow Steward ficam em inglês, como o time fala.
