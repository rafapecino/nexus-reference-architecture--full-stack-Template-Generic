"""Hooks sencillos de trazabilidad para LangGraph."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("ai.langgraph")


def log_graph_event(
    event: str, *, state: Any | None = None, extra: dict[str, Any] | None = None
) -> None:
    """Log estructurado para eventos del grafo (nodo ejecutado, transición, error)."""
    payload = {
        "event": event,
        "state_keys": list(state.keys()) if isinstance(state, dict) else None,
    }
    if extra:
        payload.update(extra)
    logger.info("langgraph_event", extra={"extra": payload})
