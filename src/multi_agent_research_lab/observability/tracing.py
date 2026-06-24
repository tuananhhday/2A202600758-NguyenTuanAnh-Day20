"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Generator
from contextlib import contextmanager
from time import perf_counter
from typing import Any


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Generator[dict[str, Any], None, None]:
    """Minimal span context used by the skeleton.

    Optionally integrations for LangSmith/Langfuse can be plugged here.
    """

    import logging
    logger = logging.getLogger("multi_agent_research_lab.observability.tracing")

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        logger.info(f"Span '{name}' completed in {span['duration_seconds']:.4f}s. Attributes: {span['attributes']}")

