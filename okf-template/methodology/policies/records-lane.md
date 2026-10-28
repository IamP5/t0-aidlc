---
type: Policy
title: "Raia de registros"
description: "Como os registros de passo entram no main do KB: em lote diário aprovado pelo Flow Steward, até a segurança liberar o auto-merge."
uid: policy-records-lane
owner: role:flow-steward
tags: [policy, raias, registros, kb]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
mode: batch
batch:
  schedule: "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8;BYMINUTE=45"
  before_ritual: ritual-daily-time
  branch: "rec/batch/<data>"
  approver: role:flow-steward
auto:
  requires: "aval da segurança de que a proteção de branch do banco aceita auto-merge sem aprovação"
  security_signoff: null
---

# Raia de registros

Os registros de passo (`type: Step`) são arquivos novos com nome único em `steps/`, então nunca dão conflito. O que esta Policy decide é como eles chegam ao `main`. Fonte: [workspace pattern §4](/methodology/workspace-pattern.md).

## Modo atual: batch

- O `t0 kb push` empurra só a branch `rec/<handle>/<ts>`, sem abrir PR.
- Uma vez por dia, antes da daily do time, um workflow junta as branches `rec/*` num PR `rec/batch/<data>`.
- O Flow Steward aprova o lote com um clique. Isso cabe na revisão que o papel já faz.
- O `t0 pr check` lê os registros pendentes em `rec/bot/*`, então a ordem de merge dos slices não espera o lote.

## Modo futuro: auto

Cada push de registro abre o próprio PR com auto-merge e sem aprovação humana. Esse modo só liga quando a segurança confirmar que a proteção de branch do banco aceita isso. Aí o PR desta Policy preenche `auto.security_signoff` e troca `mode` para `auto`.
