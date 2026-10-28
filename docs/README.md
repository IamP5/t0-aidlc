# t0: como o time vai da ideia à produção com agentes

O t0 é a metodologia do time de Inovação em IA. Ela cobre o caminho inteiro, em etapas:

1. a ideia vira protótipo;
2. o protótipo vira aposta (bet: trabalho de até 2 semanas que o time decidiu fazer);
3. a aposta vira spec (o contrato da bet) e slices (fatias de um repo e um PR cada);
4. os slices viram PRs;
5. o que vai pro ar sobe os degraus de adoção: primeiro o time, depois squads piloto e por fim as squads do ART.

Três peças sustentam o dia a dia:

- o KB do time (`t0-kb`), um repositório no formato OKF que guarda ideias, bets, specs, decisões, rituais e o harness (tudo o que cerca o agente para ele errar menos);
- o plugin `t0`, com 15 skills em pt-BR, subagentes, hooks e o MCP `t0-kb`. O plugin roda igual no Claude Code, no GitHub Copilot e no Kiro;
- a CLI `t0`, que faz a parte determinística: cria arquivos no KB, confere gates (os checks de CI que conferem uma decisão humana), abre e fecha rituais, redige transcrições e gera o contexto de cada sessão.

## Para quem

- Gente do time, nos três pods, que usa o fluxo todo dia.
- Gente de squad que entra numa daily do pod como Domain Expert ou que vai adotar uma ferramenta do time.
- Quem precisa auditar uma decisão. O histórico git do KB é a trilha de auditoria que o banco pede.

## A regra

> Um passo de processo só entra quando protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado. Se não protege nem ensina, sai.

Toda página daqui segue essa régua. A Retro mensal aplica a régua de novo e corta o que não pagou o próprio custo.

## Em 1 minuto

A ideia vira protótipo na hora, em minutos ou horas. Na daily seguinte, o pod decide se ela vira bet. A bet tem apetite de até 2 semanas e passa por spec e slices. Um ajuste que cabe em um dia vai pela trilha rápida, sem spec.

O time registra só três decisões humanas: aposta, spec e degrau de adoção. O resto é review de PR ou automação.

Dentro do time não existe sprint. A Demo acontece a cada 2 semanas e segue a iteração do ART. O Harness Health é semanal e a Retro é mensal. O review pendente limita o WIP: cada pessoa tem no máximo 2 slices em construção.

São seis rituais, com cerca de 3h20 de cerimônia pura por pessoa a cada 2 semanas. Cada comando do `t0` grava o passo no KB, então ninguém escreve ata à mão. O Jira é um espelho gerado a partir do KB. O código fica nos repos de produto.

Quando um erro de agente se repete, ele vira sensor: lint, teste, hook de git ou gate de CI. O contexto é tratado como orçamento, e o time desliga o que não pegou.

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

- se você está chegando no time: esta página, [Princípios](01-principios.md), [Fluxo](03-fluxo.md) e [Guia prático](08-guia-pratico.md);
- se vai configurar a máquina: [Workspace](06-workspace.md) e [Plugin e skills](07-plugin-e-skills.md);
- se vai facilitar um ritual: [Papéis e pods](02-papeis-e-pods.md) e [Rituais](04-rituais.md).

## Convenções destas páginas

- KB é o repositório OKF do time, `t0-kb`, no OKF v0.2 com o profile `t0-team`.
- O nome de uma skill aparece grafado como `bet-spec`, e você chama a skill por esse nome em qualquer ferramenta. No Claude Code, com o plugin, você digita `/t0:bet-spec`.
- Um comando da CLI aparece como `t0 <subcomando>`.
- `PROPOSTA` marca número ou piso que ainda não está valendo. O número entra no profile com `state: proposed` e só vira `in-force` depois que 3 ferramentas passarem pelo funil.
- `(não verificado)` marca afirmação que a pesquisa não confirmou ou mecanismo que precisa de teste antes do rollout.
- Os termos bet, slice, spec, Tier, Bet Owner, Harness Keeper e Flow Steward ficam em inglês, como o time fala.
