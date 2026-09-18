"""Standard MCP discovery and bounded tool calls.

This module deliberately delegates transport and protocol handling to the
official MCP Python SDK.  Film OS adds only configuration scope checks,
input-schema validation, bounded output receipts, and an optional external
capability/receipt directory.  It does not implement a Blender connector or a
second wire protocol.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator


class MCPUnavailableError(RuntimeError):
    """Raised when the optional official MCP SDK is not installed."""


def _load_sdk() -> tuple[Any, Any]:
    try:
        from mcp import Client
        from mcp.client.stdio import StdioServerParameters
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise MCPUnavailableError(
            "standard MCP runtime is optional; install the 'runtime' extra (mcp)"
        ) from exc
    return Client, StdioServerParameters


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return _plain(model_dump(by_alias=True, exclude_none=True))
        except TypeError:
            return _plain(model_dump())
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    return str(value)


def _json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    try:
        result = json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field} must be JSON serializable: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"{field} must be an object")
    return result


def _config(config: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(config, Mapping):
        raise ValueError("MCP config must be an object")
    transport = config.get("transport")
    if not isinstance(transport, str) or not transport:
        raise ValueError("MCP transport must be a non-empty string")
    if transport not in {"stdio", "streamable-http", "sse", "fake"}:
        raise ValueError("MCP transport must be stdio, streamable-http, or sse")
    allowed = config.get("allowed_tools", [])
    required = config.get("required_tools", allowed)
    for field, value in (("allowed_tools", allowed), ("required_tools", required)):
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"MCP {field} must be an array of names")
        if len(value) != len(set(value)):
            raise ValueError(f"MCP {field} must not contain duplicate names")
    if not set(required).issubset(set(allowed)):
        raise ValueError("MCP required_tools must be a subset of allowed_tools")
    timeout = config.get("timeout_seconds", 30.0)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("MCP timeout_seconds must be positive")
    max_output = config.get("max_output_bytes", 65536)
    if isinstance(max_output, bool) or not isinstance(max_output, int) or max_output <= 0:
        raise ValueError("MCP max_output_bytes must be a positive integer")
    result = dict(config)
    result["allowed_tools"] = list(allowed)
    result["required_tools"] = list(required)
    result["timeout_seconds"] = float(timeout)
    result["max_output_bytes"] = max_output
    return result


def _state_dir(config: Mapping[str, Any]) -> Path | None:
    value = config.get("state_dir")
    if value is None:
        return None
    if not isinstance(value, (str, os.PathLike)):
        raise ValueError("MCP state_dir must be a path")
    path = Path(value)
    if path.exists() and path.is_symlink():
        raise ValueError("MCP state_dir must not be a symlink")
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValueError("MCP state_dir must be a directory")
    return path.resolve()


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _receipt_path(config: Mapping[str, Any], operation_id: str) -> Path | None:
    directory = _state_dir(config)
    if directory is None:
        return None
    receipt_dir = directory / "mcp-receipts"
    if receipt_dir.exists() and receipt_dir.is_symlink():
        raise ValueError("MCP receipt directory must not be a symlink")
    receipt_dir.mkdir(parents=True, exist_ok=True)
    if not receipt_dir.is_dir():
        raise ValueError("MCP receipt path must be a directory")
    digest = hashlib.sha256(operation_id.encode("utf-8")).hexdigest()
    return receipt_dir / f"{digest}.json"


def _arguments_digest(arguments: Mapping[str, Any]) -> str:
    encoded = json.dumps(arguments, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _load_receipt(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _tool_value(tool: Any, name: str, alias: str | None = None) -> Any:
    value = getattr(tool, name, None)
    if value is None and alias is not None:
        value = getattr(tool, alias, None)
    if value is None and isinstance(tool, Mapping):
        value = tool.get(name, tool.get(alias) if alias else None)
    return value


def _tool_record(tool: Any) -> dict[str, Any]:
    name = _tool_value(tool, "name")
    if not isinstance(name, str) or not name:
        raise ValueError("MCP server returned a tool without a name")
    description = _tool_value(tool, "description")
    schema = _tool_value(tool, "input_schema", "inputSchema")
    if not isinstance(schema, Mapping):
        raise ValueError(f"MCP tool {name} returned no input schema")
    return {
        "name": name,
        "description": description if isinstance(description, str) else None,
        "input_schema": _json_object(schema, f"input schema for {name}"),
    }


async def _discover(client: Any, config: Mapping[str, Any]) -> dict[str, Any]:
    await client.send_ping()
    tools: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(100):
        result = await client.list_tools(cursor=cursor)
        page = getattr(result, "tools", None)
        if page is None and isinstance(result, Mapping):
            page = result.get("tools")
        if not isinstance(page, list):
            raise ValueError("MCP tools/list returned no tools array")
        tools.extend(_tool_record(tool) for tool in page)
        cursor = getattr(result, "next_cursor", None)
        if cursor is None and isinstance(result, Mapping):
            cursor = result.get("nextCursor", result.get("next_cursor"))
        if cursor is None:
            break
    else:
        raise ValueError("MCP tools/list exceeded the pagination limit")
    required = set(config["required_tools"])
    missing = sorted(required.difference(tool["name"] for tool in tools))
    filtered = [tool for tool in tools if not required or tool["name"] in required]
    return {
        "status": "blocked" if missing else "ready",
        "server": _plain(getattr(client, "server_info", None)),
        "protocol_version": _plain(getattr(client, "protocol_version", None)),
        "capabilities": _plain(getattr(client, "server_capabilities", None)),
        "available_tool_names": sorted(tool["name"] for tool in tools),
        "tools": filtered,
        "missing_required_tools": missing,
    }


@asynccontextmanager
async def _client_context(config: Mapping[str, Any]) -> AsyncIterator[Any]:
    factory = config.get("_client_factory")
    if factory is not None:
        if config["transport"] != "fake":
            raise ValueError("MCP _client_factory is test-only and requires fake transport")
        if not callable(factory):
            raise ValueError("MCP _client_factory must be callable")
        client = factory()
        async with client as active:
            yield active
        return

    Client, StdioServerParameters = _load_sdk()
    transport = config["transport"]
    if transport == "streamable-http":
        url = config.get("url")
        if not isinstance(url, str) or urlparse(url).scheme not in {"http", "https"}:
            raise ValueError("streamable-http MCP config requires an http(s) url")
        client = Client(url, read_timeout_seconds=config["timeout_seconds"], mode=config.get("mode", "auto"))
    elif transport == "sse":
        url = config.get("url")
        if not isinstance(url, str) or urlparse(url).scheme not in {"http", "https"}:
            raise ValueError("sse MCP config requires an http(s) url")
        from mcp.client.sse import sse_client

        client = Client(
            sse_client(url, timeout=config["timeout_seconds"], sse_read_timeout=config["timeout_seconds"]),
            read_timeout_seconds=config["timeout_seconds"],
            mode=config.get("mode", "auto"),
        )
    elif transport == "stdio":
        command = config.get("command")
        if not isinstance(command, str) or not command:
            raise ValueError("stdio MCP config requires a command")
        args = config.get("args", [])
        if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
            raise ValueError("stdio MCP args must be an array of strings")
        env = config.get("env")
        if env is not None and (
            not isinstance(env, Mapping)
            or not all(isinstance(key, str) and isinstance(value, str) for key, value in env.items())
        ):
            raise ValueError("stdio MCP env must map strings to strings")
        client = Client(
            StdioServerParameters(
                command=command,
                args=list(args),
                env=dict(env) if isinstance(env, Mapping) else None,
                cwd=config.get("cwd"),
            ),
            read_timeout_seconds=config["timeout_seconds"],
            mode=config.get("mode", "auto"),
        )
    else:
        raise ValueError("fake MCP transport requires _client_factory and is test-only")
    async with client as active:
        yield active


def _failure(status: str, operation_id: str | None, reason: str, **extra: Any) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "operation_id": operation_id,
        "status": status,
        "reason": reason,
    }
    receipt.update(extra)
    return {"status": status, "receipt": receipt, "error": {"type": reason}}


def _write_inventory(config: Mapping[str, Any], inventory: Mapping[str, Any]) -> None:
    directory = _state_dir(config)
    if directory is not None:
        _atomic_json(directory / "mcp-capabilities.json", inventory)


async def inspect_server(config: Mapping[str, Any]) -> dict[str, Any]:
    """Negotiate with a configured server and persist a filtered capability inventory."""

    prepared = _config(config)
    try:
        async with asyncio.timeout(prepared["timeout_seconds"]):
            async with _client_context(prepared) as client:
                inventory = await _discover(client, prepared)
    except MCPUnavailableError:
        raise
    except Exception as exc:
        return {
            "status": "failed",
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
    _write_inventory(prepared, inventory)
    return inventory


def _bounded_result(value: Any, max_output_bytes: int) -> tuple[Any, str, int]:
    plain = _plain(value)
    encoded = json.dumps(plain, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    if len(encoded) > max_output_bytes:
        return {"truncated": True, "bytes": len(encoded), "sha256": digest}, digest, len(encoded)
    return plain, digest, len(encoded)


async def call_tool(
    config: Mapping[str, Any], tool_name: str, arguments: Mapping[str, Any], operation_id: str
) -> dict[str, Any]:
    """Call one allowlisted MCP tool and return a bounded receipt on every outcome."""

    prepared = _config(config)
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("MCP tool_name must be a non-empty string")
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("MCP operation_id must be a non-empty string")
    args = _json_object(arguments, "MCP arguments")
    args_digest = _arguments_digest(args)
    receipt_path = _receipt_path(prepared, operation_id)
    if receipt_path is not None and receipt_path.exists() and receipt_path.is_symlink():
        return _failure(
            "blocked",
            operation_id,
            "receipt-path-symlink",
            tool_name=tool_name,
            arguments_sha256=args_digest,
        )
    existing = _load_receipt(receipt_path)
    if receipt_path is not None and receipt_path.exists() and existing is None:
        return _failure(
            "blocked",
            operation_id,
            "receipt-corrupt",
            tool_name=tool_name,
            arguments_sha256=args_digest,
        )
    if existing is not None:
        if existing.get("tool_name") != tool_name or existing.get("arguments_sha256") != args_digest:
            return _failure("blocked", operation_id, "operation-id-conflict")
        return {"status": "reused-receipt", "receipt": existing, "result": existing.get("result")}
    if tool_name not in prepared["allowed_tools"]:
        result = _failure(
            "blocked",
            operation_id,
            "tool-not-allowlisted",
            tool_name=tool_name,
            arguments_sha256=args_digest,
        )
        if receipt_path is not None:
            _atomic_json(receipt_path, result["receipt"])
        return result

    started = perf_counter()
    try:
        async with asyncio.timeout(prepared["timeout_seconds"]):
            async with _client_context(prepared) as client:
                inventory = await _discover(client, prepared)
                if inventory["status"] != "ready":
                    result = _failure(
                        "blocked",
                        operation_id,
                        "required-tool-missing",
                        tool_name=tool_name,
                        arguments_sha256=args_digest,
                        missing_required_tools=inventory["missing_required_tools"],
                    )
                    if receipt_path is not None:
                        _atomic_json(receipt_path, result["receipt"])
                    return result
                record = next((tool for tool in inventory["tools"] if tool["name"] == tool_name), None)
                if record is None:
                    return _failure(
                        "blocked",
                        operation_id,
                        "tool-not-required",
                        tool_name=tool_name,
                        arguments_sha256=args_digest,
                    )
                schema_errors = sorted(
                    error.message for error in Draft202012Validator(record["input_schema"]).iter_errors(args)
                )
                if schema_errors:
                    result = _failure(
                        "blocked",
                        operation_id,
                        "argument-schema-invalid",
                        tool_name=tool_name,
                        arguments_sha256=args_digest,
                        schema_errors=schema_errors,
                    )
                    if receipt_path is not None:
                        _atomic_json(receipt_path, result["receipt"])
                    return result
                response = await client.call_tool(
                    tool_name,
                    args,
                    read_timeout_seconds=prepared["timeout_seconds"],
                )
                bounded, output_digest, output_bytes = _bounded_result(response, prepared["max_output_bytes"])
                is_error = bool(getattr(response, "is_error", False))
                receipt = {
                    "operation_id": operation_id,
                    "tool_name": tool_name,
                    "arguments_sha256": args_digest,
                    "status": "failed" if is_error else "ok",
                    "server": inventory.get("server"),
                    "protocol_version": inventory.get("protocol_version"),
                    "output_sha256": output_digest,
                    "output_bytes": output_bytes,
                    "duration_ms": (perf_counter() - started) * 1000,
                    "result": bounded,
                }
                if is_error:
                    receipt["reason"] = "server-returned-error"
                result = {
                    "status": receipt["status"],
                    "result": bounded,
                    "receipt": receipt,
                }
    except MCPUnavailableError:
        raise
    except Exception as exc:
        receipt = {
            "operation_id": operation_id,
            "tool_name": tool_name,
            "arguments_sha256": args_digest,
            "status": "failed",
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "duration_ms": (perf_counter() - started) * 1000,
        }
        result = {"status": "failed", "receipt": receipt, "error": receipt["error"]}
    if receipt_path is not None:
        _atomic_json(receipt_path, result["receipt"])
    return result


__all__ = ["MCPUnavailableError", "call_tool", "inspect_server"]
