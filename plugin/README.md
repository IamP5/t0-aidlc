# t0

Plugin do fluxo t0 (AIDLC do time) para Claude Code, GitHub Copilot e Kiro. Traz as 15 skills em pt-BR (`/t0` é a porta de entrada), os subagentes `t0-agent`, `spec-reviewer`, `standards-reviewer` e `verifier`, o MCP `t0-kb` para ler o KB e os hooks que mantêm todo PR em draft e bloqueiam force push, edição de chave derivada e leitura de transcrição crua.

Requisito: o comando `t0` no PATH (pacote `t0` do `toolkit/`). Hooks e MCP chamam `t0 hook` e `t0 mcp`.

Num repo de produto, rode `t0 setup` para escrever o ponteiro no `AGENTS.md`, os hooks por ferramenta e os links das skills `verify-<app>`.

Fontes escritas à mão: `skills/`, `agents/`, `evals/`, `.mcp.json`, `README.md` e `THIRD_PARTY_NOTICES.md`. O resto é gerado por `t0 gen`; não edite.
