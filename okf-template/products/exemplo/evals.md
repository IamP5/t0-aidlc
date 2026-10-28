---
type: Eval Suite
title: "Evals do exemplo"
description: "Suíte de regressão do bot de status e o último resultado."
uid: evals-exemplo
owner: team:exemplo
tags: [eval, exemplo, fixture]
generated: { by: process:kb-render, at: 2026-10-24T18:00:00-03:00 }
repo: status-bot
repo_path: evals/
metric: "pass@1"
regression_size: 24
regression_pass: "0.96"
last_run: 2026-10-24T17:55:00-03:00
---

# Evals do exemplo

A regressão tem 24 casos tirados de status reais, com casos positivos e negativos (dia sem merge, fim de semana, horário de verão). A última rodada passou 23 de 24. O caso que falha é o de feriado, que fica para uma bet futura. Regra na Policy [eval-gate](/methodology/policies/eval-gate.md).
