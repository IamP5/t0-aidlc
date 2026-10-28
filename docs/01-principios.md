# Princípios

A metodologia existe para habilitar o time e deixá-lo mais rápido. Os princípios abaixo explicam por que cada regra do t0 existe. Quando uma regra parecer estranha, procure aqui o princípio que ela protege.

## A régua enxuta

> Um passo de processo só entra quando protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado. Se não protege nem ensina, sai.

Na prática, isso dá quatro consequências:

- O registro continua, mas é automático. Cada comando `t0` grava o passo no KB. Ninguém escreve ata, relatório de status ou resumo de reunião à mão.
- Status quem dá é o bot. A daily do time fala de bloqueio e de pedido de review, e o resto já está no digest.
- Só sobra decisão humana onde ela protege algo: aposta, spec e degrau de adoção. Build, review e merge ficam com o CI e com o review normal de PR.
- A Retro mensal pergunta, toda vez, que passo de processo cortar.

## Os oito princípios

### 1. Passo só entra se protege ou ensina

É a régua acima. Vale para ritual, campo de frontmatter, gate, template e métrica. Métrica que não informou nenhuma decisão em 2 PIs é removida pelo Harness Keeper.

### 2. Humanos decidem e verificam, agentes executam

O dev é dono da intenção, do critério de aceite e da verificação. A digitação e o Jira ficam com o agente. Por isso todo PR nasce em draft e só humano marca pronto ou faz merge.

### 3. O KB é o sistema de registro, e quem grava é o comando

Jira, painel e PR são projeções do KB. Se KB e Jira divergem, vale o KB, com as exceções de status descritas em [KB em OKF](05-kb-okf.md#jira-como-espelho). O histórico git do KB é a trilha de auditoria.

### 4. Protótipo antes de documento

Spec só existe para ideia que sobreviveu a um protótipo. Protótipo leva de minutos a horas, não pede aprovação e fica fora do main.

### 5. Atenção humana é o gargalo, e ela é medida

Um slice vira um PR revisável em até 15 minutos. O WIP é limitado por review pendente. A primeira resposta de review sai em até 4 horas úteis.

### 6. Erro repetido do agente vira sensor

Na segunda ocorrência do mesmo erro, ele sobe a escada do harness: sensor computacional primeiro, `AGENTS.md` por último. Detalhes em [Harness e qualidade](10-harness-e-qualidade.md#escada-do-harness).

### 7. Contexto é orçamento

Link em vez de cópia. O KB é carregado por índice e busca. O `AGENTS.md` tem até 150 linhas. O card de contexto tem teto de 8.000 caracteres. O que não pegou é desligado.

### 8. Ferramenta de agente só sai com eval

Skill, MCP, agente e o próprio toolkit têm suíte de regressão. Incidente vira caso de eval no Harness Health seguinte.

## Onde cada princípio aparece

| Princípio | Onde ele vira regra |
|---|---|
| 1. Protege ou ensina | Retro mensal; sunset de skill e de métrica |
| 2. Humanos decidem | PR sempre em draft; hooks bloqueiam merge, force push e `reset --hard` |
| 3. KB é o registro | `t0 log` em toda skill; `t0 jira sync` só depois do merge no KB |
| 4. Protótipo antes | skill `prototype`; a trilha bet espera veredito `segue` |
| 5. Atenção é gargalo | WIP de 2 slices; tiers de review; digest da daily do time |
| 6. Erro vira sensor | Harness Item; skill `harness-fix`; Harness Health semanal |
| 7. Contexto é orçamento | tetos do card, do delta e do `AGENTS.md`; `harness/budget.md` |
| 8. Eval antes de sair | Policy `eval-gate`; pisos de adoção |

## Princípios de engenharia das skills

As skills do plugin carregam mais 19 princípios curtos de engenharia, em pt-BR, em `skills/t0/references/principios.md`. Eles orientam o agente na hora de escrever código: tirar peso morto antes de acrescentar, provar que funciona contra a coisa real, corrigir a causa raiz, testar comportamento em vez de implementação, operações idempotentes, e assim por diante. Um deles, "nunca travar no humano", vale só para trabalho reversível dentro de um slice. A lista completa está em [Plugin e skills](07-plugin-e-skills.md).
