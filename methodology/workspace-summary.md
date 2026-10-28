**Workspace pattern em 20 linhas** (detalhe em `methodology/workspace-pattern.md`, ADR-0002):

- **Submodules no KB? Não.** Funciona, mas dá HEAD destacado (agente perde commit), bump de ponteiro diário, código velho, KB preso ao repo menos legível e token de CI que lê todos os repos. Android, Zephyr e Chromium usam manifesto + clones irmãos. A gente também.
- **Manifesto no KB:** `/products/<p>/workspace.md`, concept `type: Workspace` com os repos, papéis, `depends_on` e grupos. Muda por PR revisado.
- **Workspace por produto:** `t0 ws init <p>` monta `~/ws/<p>/` com `kb/` e os repos como clones normais. Repo sem acesso fica `absent`. Para bet paralela, `t0 bet start BET-NNN --isolate` cria `~/ws/<p>@BET-NNN/` com worktrees.
- **Contexto em toda sessão:** a raiz do workspace tem um `AGENTS.md` gerado, o card (≤8.000 chars), com bet ativa, critérios de aceite, repos e mapa do KB. Claude Code, Copilot e Kiro leem AGENTS.md de raiz nativamente. Abra sempre a pasta do workspace, nunca multi-root.
- **Por cima do card:** plugin `t0` com hooks (card velho vira delta de ≤3.000 chars, subagente ganha card, aviso de bet trocada) e o MCP local `t0-kb` (stdio, sem serviço hospedado). Copilot CLI: `source .t0/env.sh`. Kiro: steering `t0.md`.
- **Cloud agent e CI:** checkout read-only do `t0-kb` em `.kb/` e `t0 mcp --kb .kb`. Sem KB, o agente para e avisa.
- **Bet ativa:** `T0_BET`, depois a branch `bet/BET-NNN/<STORY>-<slug>`, depois `.t0/bet.json`, depois chave Jira por lookup. Sem bet, skill de código não escreve código.
- **Cross-repo:** um slice = um repo = um PR. Trailers `Bet:`, `Story:`, `Jira-Feature:`, `Depends-on:`, `KB-Context:`. O status obrigatório `t0/merge-order` lê o change set no KB, nunca a API de outro repo. Todo PR é deployável sozinho (expand → migrate → contract).
- **Escrita no KB, três raias:**
  - Registros (`t0 log`, decisões, eventos de PR): arquivo novo com nome único em `steps/`, PR com auto-merge. Zero conflito.
  - Conhecimento (spec, plan, slices, ADR, rituais, transcrições redigidas): PR com CODEOWNERS.
  - Derivados (`index.md`, `log.md`, `changeset.md`, chaves `jira:` e `state`): só o workflow `kb-render`, serializado.
- **Uma credencial cruza repos:** o GitHub App KB-writer, instalado só no `t0-kb`.
- **A verificar antes do rollout:** auto-merge sob a proteção do banco (fallback: lote horário aprovado pelo Flow Steward), setup steps e MCP stdio no cloud agent, stdout de hook no Copilot CLI e no Kiro.
