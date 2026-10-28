"""stdio MCP server `t0-kb` (official `mcp` SDK 2.x, MCPServer). Local process, no port, no service.

Six tools, each a thin call over the KB facade (bet_detect needs only ws). Inputs are parsed into
domain types here; outputs are text or small JSON objects (no View/Concept crosses the wire).
The write surface is exactly one tool, kb_record (records lane -> spool); --read-only drops it.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .redact import scan

INSTRUCTIONS = (
    "KB = t0-kb (OKF). Sem card t0 no contexto, chame kb_context primeiro (com a chave Jira da tarefa, "
    "se houver). Se o KB estiver indisponível, pare e diga 'KB indisponível'. "
    "Nunca edite index.md, log.md, changeset.md nem chaves derivadas (state, status, verified, jira, pr): "
    "estado muda por gate (skill `gate`), o resto o kb-render deriva. "
    "Para registrar progresso, decisão, bloqueio ou handoff use kb_record; texto com segredo ou dado "
    "pessoal é recusado. Mudança de conhecimento (spec, plan, ADR) é PR revisado: edite no clone do KB e "
    "rode `t0 kb propose`. Use kb_find e kb_get para ler; bet_detect diz qual bet está ativa e por qual regra. "
    "Skills que geram código se recusam sem bet resolvida."
)
RecordKind = Literal["progress", "decision", "blocker", "handoff", "session"]


def _kb(kb_dir: Path | None) -> Any:
    from .kb import KB, KBUnavailable

    try:
        return KB.open(kb_dir)
    except KBUnavailable as e:
        raise ToolError(str(e)) from e


def build_server(kb_dir: Path | None = None, *, read_only: bool = False) -> MCPServer:
    server = MCPServer(name="t0-kb", instructions=INSTRUCTIONS)

    @server.tool()
    def kb_find(text: str | None = None, type: str | None = None, product: str | None = None,
                state: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Busca no KB por texto e frontmatter (tipo, produto, estado). Retorna uid, caminho, título, estado."""
        from .kb import Query

        hits = _kb(kb_dir).find(Query(text=text, type=type, product=product, state=state, limit=limit))
        return [{"uid": h.uid, "path": h.path, "type": h.type, "title": h.title, "state": h.state,
                 "description": h.description, "snippet": h.snippet} for h in hits]

    @server.tool()
    def kb_get(ref: str) -> dict[str, Any]:
        """Lê um concept por uid, caminho, chave Jira ou id do KB (BET-042, ADR-0004). Chaves derivadas incluídas."""
        from .view import Ref

        c = _kb(kb_dir).get(Ref(ref))
        if c is None:
            raise ToolError(f"{ref} não encontrado no KB")
        return {"path": c.doc.path.value, "frontmatter": {**dict(c.doc.frontmatter), **dict(c.derived)},
                "derived": sorted(c.derived), "body": c.doc.body}

    @server.tool()
    def kb_context(ref: str | None = None) -> str:
        """Card de contexto (até 8000 chars) da bet, slice ou chave Jira; sem ref, da bet ativa."""
        from .context import CardFormat
        from .view import Ref

        card = _kb(kb_dir).context(Ref(ref) if ref else None, CardFormat.AGENTS)
        return card.text if card else "card em dia"

    @server.tool()
    def bet_detect(cwd: str | None = None) -> dict[str, Any]:
        """Qual bet está ativa e qual regra decidiu (env, branch, bet.json ou none)."""
        from .ws import detect

        d = detect(Path(cwd) if cwd else Path.cwd())
        return {"bet": d.bet, "story": d.story, "rule": d.rule, "product": d.product}

    @server.tool()
    def kb_check(level: Literal["L0", "L1", "L2"] = "L1") -> str:
        """Conformidade do KB (OKF + profile t0-team) no nível pedido; retorna o relatório em JSON."""
        from .check import Level

        return _kb(kb_dir).check(Level[level]).format("json")

    if not read_only:
        @server.tool()
        def kb_record(kind: RecordKind, text: str, bet: str | None = None, story: str | None = None,
                      refs: list[str] | None = None) -> dict[str, Any]:
            """Registra progresso, decisão, bloqueio, handoff ou sessão na raia de registros (spool local)."""
            findings = scan(text)
            if findings:
                kinds = sorted({f.kind.value for f in findings})
                raise ToolError(f"recusado: texto contém {', '.join(kinds)}; remova e tente de novo")
            from .profile.spec import EventKind
            from .view import Ref

            kb = _kb(kb_dir)
            plan = kb.record(EventKind(kind), text, bet=Ref(bet) if bet else None, story=story, refs=tuple(refs or ()))
            applied = kb.apply(plan)
            return {"spooled": [str(p) for p in applied.spooled], "push": "pending"}

    return server


def serve(kb_dir: Path | None, *, read_only: bool = False) -> None:
    """`t0 mcp [--kb DIR] [--read-only]`."""
    build_server(kb_dir, read_only=read_only).run("stdio")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kb_dir = Path(args[args.index("--kb") + 1]) if "--kb" in args else None
    serve(kb_dir, read_only="--read-only" in args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
