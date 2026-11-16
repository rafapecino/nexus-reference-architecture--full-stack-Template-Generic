"""Interfaces para nodos/herramientas del grafo."""

from __future__ import annotations

from typing import Any, Protocol

from .state import GraphState


class ToolContext(Protocol):
    """Contexto mínimo que un handler puede necesitar (llamadas externas, storage, etc.)."""

    def log(self, message: str, *, extra: dict[str, Any] | None = None) -> None: ...


class ToolHandler(Protocol):
    """Contrato simple para nodos o tools usadas en LangGraph."""

    name: str

    def __call__(self, state: GraphState, *, ctx: ToolContext | None = None) -> GraphState: ...
