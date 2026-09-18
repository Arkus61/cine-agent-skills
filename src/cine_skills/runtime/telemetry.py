"""Small, provider-neutral usage records and optional span hooks.

This module deliberately does not infer missing provider counters. A value
that was not returned by a provider remains ``None`` so reports cannot turn
unknown usage into a false zero-cost claim.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
import json
from pathlib import Path
from time import perf_counter
from typing import Any


def _counter(usage: Mapping[str, Any], *names: str) -> int | None:
    for name in names:
        value = usage.get(name)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"usage counter {name} must be a non-negative integer")
        return value
    return None


def _cost(usage: Mapping[str, Any]) -> float | None:
    value = usage.get("cost", usage.get("total_cost"))
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError("usage cost must be a non-negative number")
    return float(value)


def record_usage(
    run_id: str, task_id: str, usage: Mapping[str, Any], source: str
) -> dict[str, Any]:
    """Normalize provider or estimate usage without inventing counters."""

    if source not in {"provider", "estimate"}:
        raise ValueError("source must be 'provider' or 'estimate'")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run_id must be a non-empty string")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(usage, Mapping):
        raise ValueError("usage must be a mapping")
    return {
        "run_id": run_id,
        "task_id": task_id,
        "source": source,
        "input_tokens": _counter(usage, "input_tokens", "prompt_tokens", "prompt"),
        "output_tokens": _counter(usage, "output_tokens", "completion_tokens", "completion"),
        "cached_input_tokens": _counter(
            usage, "cached_input_tokens", "cached_tokens", "cache_read_input_tokens"
        ),
        "reasoning_output_tokens": _counter(
            usage, "reasoning_output_tokens", "reasoning_tokens"
        ),
        "cost": _cost(usage),
    }


@dataclass
class Span:
    """An in-process span record that can be exported to OpenTelemetry later."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    duration_ms: float | None = None


def _public_attributes(attributes: Mapping[str, Any], *, include_sensitive: bool) -> dict[str, Any]:
    """Keep local exports useful without writing prompts or project prose."""

    sensitive_names = {
        "prompt",
        "text",
        "content",
        "raw_output",
        "source_text",
        "project_text",
    }
    result: dict[str, Any] = {}
    for key, value in attributes.items():
        if not isinstance(key, str):
            continue
        if not include_sensitive and key.lower() in sensitive_names:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            result[key] = value
    return result


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[Span]:
    """Record a local span without requiring an observability SDK."""

    if not name:
        raise ValueError("span name must be non-empty")
    item = Span(name=name, attributes=dict(attributes))
    started = perf_counter()
    try:
        yield item
    finally:
        item.duration_ms = (perf_counter() - started) * 1000


@dataclass
class TelemetryRecorder:
    """Collect local spans and optionally mirror them to OpenTelemetry.

    The OpenTelemetry API is optional.  When installed, the recorder creates
    standard spans through ``trace.get_tracer``; the JSONL export remains a
    deterministic local evidence file and strips raw content by default.
    """

    include_sensitive: bool = False
    spans: list[Span] = field(default_factory=list)

    def _otel_context(self, name: str, attributes: Mapping[str, Any]):
        try:
            from opentelemetry import trace
        except ImportError:  # pragma: no cover - depends on optional extra
            return nullcontext(None)
        tracer = trace.get_tracer("cine-agent-skills")
        context = tracer.start_as_current_span(name)
        return context

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[Span]:
        public = _public_attributes(attributes, include_sensitive=self.include_sensitive)
        item: Span | None = None
        try:
            with self._otel_context(name, public) as otel_span:
                if otel_span is not None:
                    for key, value in public.items():
                        try:
                            otel_span.set_attribute(key, value)
                        except (TypeError, ValueError):
                            continue
                try:
                    with span(name, **dict(attributes)) as recorded:
                        item = recorded
                        yield recorded
                finally:
                    if otel_span is not None and item is not None and item.duration_ms is not None:
                        try:
                            otel_span.set_attribute("duration_ms", item.duration_ms)
                        except (TypeError, ValueError):
                            pass
        finally:
            if item is not None:
                self.spans.append(item)

    def export_jsonl(self, path: Path) -> int:
        """Write deterministic local spans and return the number exported."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for item in self.spans:
                payload = {
                    "name": item.name,
                    "attributes": _public_attributes(
                        item.attributes, include_sensitive=self.include_sensitive
                    ),
                    "duration_ms": item.duration_ms,
                }
                handle.write(
                    json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    + "\n"
                )
        return len(self.spans)


__all__ = ["Span", "TelemetryRecorder", "record_usage", "span"]
