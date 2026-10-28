---
type: Policy
title: "Política de eval"
description: "Toda ferramenta de agente só sai com suíte de regressão, e mudança de modelo, prompt ou skill só entra se a regressão fica igual ou melhor."
uid: policy-eval-gate
owner: role:lead
tags: [policy, eval, regressao, qualidade]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
thresholds:
  suite_min_tasks: 20
  suite_max_tasks: 50
  regression_min_pass: 0.95
  regression_may_drop: false
---

# Política de eval

Vale para skills, MCPs, agentes e o próprio toolkit. Os números são PROPOSTA. Fonte: [metodologia §7.4](/methodology/methodology.md).

## Regras

- Ferramenta que vai para squads piloto tem suíte de regressão de 20 a 50 tarefas, tiradas de uso e de falhas reais, com casos positivos e negativos.
- O degrau 1 para 2 pede pelo menos 95% na regressão (PROPOSTA). Tarefa com 0% é suspeita: monte uma solução de referência antes de culpar o agente.
- Cada produto tem duas suítes, capacidade (começa baixa) e regressão (perto de 100%). Capacidade que satura vira regressão.
- `pass@1` quando um resultado bom basta, `pass^3` para agente que a squad usa sem olhar. O `evals.md` do produto declara qual.
- Grader determinístico sempre que der. Juiz LLM por dimensão, com a opção "não sei". Humano só em amostra. Avalia-se o resultado, nunca o caminho.
- Upgrade de modelo, mudança de prompt ou de skill só entra se a regressão fica igual ou melhor. O Bet Owner do pod dono do produto assina.
- Incidente ou defeito escapado vira caso de eval no Harness Health seguinte. Em superfície pública, os primeiros casos saem junto com o spec.

## Quem cuida

A infra de eval fica com o pod PACO. O Eval Suite de cada produto (`products/<pod>/evals.md`) aponta para `evals/` no repo e guarda o último resultado.
