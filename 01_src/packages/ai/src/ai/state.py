"""Definiciones de estado para grafos LangGraph.

Este estado es genérico y sirve como punto de partida; cada proyecto puede extenderlo.
"""

from __future__ import annotations

from typing import Any, TypedDict


class GraphState(TypedDict, total=False):
    """Estado básico compartido entre nodos del grafo."""

    messages: list[Any]  # historial o turnos de conversación/pipeline
    context: dict[str, Any]  # metadatos compartidos (ej. usuario, entorno)
    payload: dict[str, Any]  # datos de trabajo que viajan entre nodos
    result: Any  # salida agregada del grafo
