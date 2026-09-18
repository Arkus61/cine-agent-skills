"""Disposable result reuse backed by the community DiskCache library."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from diskcache import Cache


def _json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"cache value must be JSON serializable: {exc}") from exc


def _key_part(value: Any) -> bytes:
    return _json_bytes(value)


def result_key(manifest: dict[str, Any], execution: dict[str, Any]) -> str:
    """Build a content-addressed key from all declared inputs and policy."""

    if not isinstance(manifest, Mapping) or not isinstance(execution, Mapping):
        raise ValueError("manifest and execution must be objects")
    payload = b"film-os-result-v1\x00" + _key_part(manifest) + b"\x00" + _key_part(execution)
    return hashlib.sha256(payload).hexdigest()


def _validate_key(key: str) -> str:
    if not isinstance(key, str) or len(key) != 64 or any(char not in "0123456789abcdef" for char in key):
        raise ValueError("cache key must be a lowercase SHA-256 digest")
    return key


def _envelope(result: dict[str, Any]) -> bytes:
    if not isinstance(result, Mapping):
        raise ValueError("cache result must be an object")
    result_bytes = _json_bytes(result)
    envelope = {
        "format": "film-os-result-v1",
        "payload_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "result": json.loads(result_bytes),
    }
    return _json_bytes(envelope)


def store_result(
    cache_dir: Path, key: str, result: dict[str, Any], *, expire: float | None = None
) -> None:
    """Store only JSON bytes; authoritative project state is elsewhere."""

    _validate_key(key)
    payload = _envelope(result)
    try:
        with Cache(str(Path(cache_dir))) as cache:
            cache.set(key, payload, expire=expire)
    except (OSError, TypeError, ValueError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"unable to store cache result: {exc}") from exc


def lookup_result(cache_dir: Path, key: str) -> dict[str, Any] | None:
    """Return a verified JSON result or ``None`` for misses/corruption."""

    _validate_key(key)
    try:
        with Cache(str(Path(cache_dir))) as cache:
            payload = cache.get(key, default=None)
    except (OSError, TypeError, ValueError):
        return None
    if not isinstance(payload, (bytes, bytearray)):
        return None
    try:
        envelope = json.loads(bytes(payload).decode("utf-8"))
        if not isinstance(envelope, Mapping) or envelope.get("format") != "film-os-result-v1":
            return None
        result = envelope.get("result")
        expected = envelope.get("payload_sha256")
        actual = hashlib.sha256(_json_bytes(result)).hexdigest()
        if not isinstance(result, dict) or expected != actual:
            return None
        return result
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None
