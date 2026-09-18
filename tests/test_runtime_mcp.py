from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest


pytest.importorskip("mcp")


@dataclass
class FakeTool:
    name: str
    description: str
    inputSchema: dict


class FakeResult:
    def __init__(self, *, tools=None, structured_content=None, content=None, is_error=False, next_cursor=None):
        self.tools = tools or []
        self.structured_content = structured_content
        self.content = content or []
        self.is_error = is_error
        self.next_cursor = next_cursor


class FakeClient:
    def __init__(self, *, fail: Exception | None = None, oversized: bool = False):
        self.fail = fail
        self.oversized = oversized
        self.calls: list[tuple[str, dict]] = []
        self.server_info = SimpleNamespace(name="fake-blender", version="9.1")
        self.protocol_version = "2026-07-28"
        self.server_capabilities = SimpleNamespace(tools=SimpleNamespace(list_changed=False))

    async def __aenter__(self):
        if self.fail is not None:
            raise self.fail
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def send_ping(self):
        return FakeResult()

    async def list_tools(self, *, cursor=None):
        return FakeResult(
            tools=[
                FakeTool("scene.read", "Read the disposable scene", {"type": "object", "properties": {}, "additionalProperties": False}),
                FakeTool("scene.write", "Modify the scene", {"type": "object", "required": ["scene_id"], "properties": {"scene_id": {"type": "string"}}, "additionalProperties": False}),
            ]
        )

    async def call_tool(self, name: str, arguments: dict, **kwargs):
        self.calls.append((name, arguments))
        if self.oversized:
            return FakeResult(structured_content={"payload": "x" * 500})
        return FakeResult(structured_content={"tool": name, "arguments": arguments})


def _config(tmp_path: Path, client: FakeClient, **extra) -> dict:
    allowed_tools = extra.pop("allowed_tools", ["scene.read", "scene.write"])
    required_tools = extra.pop("required_tools", allowed_tools)
    return {
        "transport": "fake",
        "allowed_tools": allowed_tools,
        "required_tools": required_tools,
        "state_dir": str(tmp_path / "state"),
        "_client_factory": lambda: client,
        **extra,
    }


def test_inspect_server_filters_tools_and_writes_capability_inventory(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import inspect_server

    client = FakeClient()
    result = asyncio.run(inspect_server(_config(tmp_path, client, required_tools=["scene.read"])))

    assert result["status"] == "ready"
    assert result["server"]["name"] == "fake-blender"
    assert result["protocol_version"] == "2026-07-28"
    assert [tool["name"] for tool in result["tools"]] == ["scene.read"]
    inventory = json.loads(
        (tmp_path / "state" / "mcp-capabilities.json").read_text(encoding="utf-8")
    )
    assert inventory["tools"][0]["name"] == "scene.read"


def test_call_tool_validates_scope_schema_and_reuses_receipt(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import call_tool

    client = FakeClient()
    config = _config(tmp_path, client)
    first = asyncio.run(call_tool(config, "scene.read", {}, "op-1"))
    second = asyncio.run(call_tool(config, "scene.read", {}, "op-1"))

    assert first["status"] == "ok"
    assert first["receipt"]["operation_id"] == "op-1"
    assert second["status"] == "reused-receipt"
    assert second["result"] == first["result"]
    assert len(client.calls) == 1

    blocked = asyncio.run(call_tool(config, "scene.write", {}, "op-2"))
    assert blocked["status"] == "blocked"
    assert blocked["receipt"]["reason"] == "argument-schema-invalid"
    assert len(client.calls) == 1

    out_of_scope = asyncio.run(
        call_tool(_config(tmp_path, client, allowed_tools=["scene.read"]), "scene.write", {"scene_id": "S01"}, "op-3")
    )
    assert out_of_scope["status"] == "blocked"
    assert out_of_scope["receipt"]["reason"] == "tool-not-allowlisted"


def test_call_tool_returns_failure_receipt_for_disconnect(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import call_tool

    result = asyncio.run(
        call_tool(
            _config(tmp_path, FakeClient(fail=ConnectionError("server offline"))),
            "scene.read",
            {},
            "op-offline",
        )
    )

    assert result["status"] == "failed"
    assert result["receipt"]["operation_id"] == "op-offline"
    assert "server offline" in result["receipt"]["error"]["message"]


def test_call_tool_truncates_oversized_output_and_keeps_digest(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import call_tool

    result = asyncio.run(
        call_tool(_config(tmp_path, FakeClient(oversized=True), max_output_bytes=64), "scene.read", {}, "op-big")
    )

    assert result["status"] == "ok"
    assert result["result"]["truncated"] is True
    assert result["result"]["bytes"] > 64
    assert len(result["result"]["sha256"]) == 64


def test_corrupt_receipt_blocks_replay(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import call_tool

    client = FakeClient()
    config = _config(tmp_path, client)
    first = asyncio.run(call_tool(config, "scene.read", {}, "op-corrupt"))
    assert first["status"] == "ok"

    receipt_path = next((tmp_path / "state" / "mcp-receipts").glob("*.json"))
    receipt_path.write_text("{not-json", encoding="utf-8")

    replay = asyncio.run(call_tool(config, "scene.read", {}, "op-corrupt"))

    assert replay["status"] == "blocked"
    assert replay["receipt"]["reason"] == "receipt-corrupt"
    assert len(client.calls) == 1


def test_client_factory_cannot_bypass_standard_transport(tmp_path: Path) -> None:
    from cine_skills.runtime.mcp_client import inspect_server

    config = {
        "transport": "streamable-http",
        "url": "http://127.0.0.1:8000/mcp",
        "allowed_tools": ["scene.read"],
        "required_tools": ["scene.read"],
        "_client_factory": lambda: FakeClient(),
        "state_dir": str(tmp_path / "state"),
    }

    result = asyncio.run(inspect_server(config))

    assert result["status"] == "failed"
    assert "test-only" in result["error"]["message"]
