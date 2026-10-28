import json
import sys

import anyio
from mcp.client.client import Client
from mcp.client.stdio import StdioServerParameters

from t0.context import MCP_INSTRUCTIONS_BUDGET
from t0.mcp_server import INSTRUCTIONS, build_server

ALL = {"kb_find", "kb_get", "kb_context", "bet_detect", "kb_check", "kb_record"}


def run(coro_fn):
    return anyio.run(coro_fn)


def test_instructions_within_budget():
    assert len(INSTRUCTIONS) <= MCP_INSTRUCTIONS_BUDGET


def test_lists_six_tools_in_process():
    async def go():
        async with Client(build_server()) as c:
            return {t.name for t in (await c.list_tools()).tools}, c.instructions
    names, instructions = run(go)
    assert names == ALL
    assert instructions == INSTRUCTIONS


def test_read_only_over_stdio_drops_kb_record():
    params = StdioServerParameters(command=sys.executable, args=["-m", "t0.mcp_server", "--read-only"])

    async def go():
        async with Client(params) as c:
            return {t.name for t in (await c.list_tools()).tools}
    assert run(go) == ALL - {"kb_record"}


def test_kb_record_refuses_secret_before_touching_kb():
    async def go():
        async with Client(build_server()) as c:
            return await c.call_tool("kb_record", {"kind": "progress", "text": "cpf 529.982.247-25 senha: abc12345"})
    result = run(go)
    assert result.is_error
    text = result.content[0].text
    assert "recusado" in text and "cpf" in text and "secret" in text and "529" not in text


def test_bet_detect_reads_marker(tmp_path, monkeypatch):
    monkeypatch.delenv("T0_BET", raising=False)
    (tmp_path / ".t0").mkdir()
    (tmp_path / ".t0/bet.json").write_text(json.dumps({"bet": "BET-042", "product": "payments"}))

    async def go():
        async with Client(build_server()) as c:
            return await c.call_tool("bet_detect", {"cwd": str(tmp_path)})
    result = run(go)
    assert not result.is_error
    assert json.loads(result.content[0].text) == {"bet": "BET-042", "story": None, "rule": "bet.json", "product": "payments"}
