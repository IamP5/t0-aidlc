---
type: Workspace
title: "Workspace do exemplo"
description: "Repos, papéis e dependências do produto exemplo; entrada do t0 ws."
uid: ws-exemplo
owner: team:exemplo
tags: [workspace, exemplo, fixture]
generated: { by: human:ana-exemplo, at: 2026-10-13T09:00:00-03:00 }
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
  groups: {}
---

# Workspace do exemplo

Um repo só. O `t0 ws init exemplo` monta `~/ws/exemplo/` com `kb/` e `status-bot/`. Ver o [produto](/products/exemplo/product.md).
