"""Esqueleto minimo de grafo LangGraph compartible entre API y workers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .state import GraphState
from .tools import ToolHandler
from .tracing import log_graph_event


class GraphBuilder:
    """Crea un grafo simple con soporte de checkpointer y registro de tools."""

    def __init__(
        self,
        *,
        tools: Mapping[str, ToolHandler] | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> None:
        self.tools = tools or {}
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = StateGraph(GraphState)
        self._register_nodes()

    def _register_nodes(self) -> None:
        self.graph.add_node("entry", self._entry)

        for name, tool in self.tools.items():
            self.graph.add_node(name, self._wrap_tool(name, tool))

        self.graph.add_edge(START, "entry")
        if self.tools:
            for name in self.tools:
                self.graph.add_edge("entry", name)
                self.graph.add_edge(name, END)
        else:
            self.graph.add_edge("entry", END)

    def _entry(self, state: GraphState) -> GraphState:
        """Nodo inicial: se puede enriquecer con guardrails/validaciones."""
        log_graph_event("entry", state=state)
        return state

    def _wrap_tool(self, name: str, tool: ToolHandler):
        def _run(state: GraphState) -> GraphState:
            log_graph_event("node_start", state=state, extra={"node": name})
            next_state = tool(state, ctx=None)
            log_graph_event("node_end", state=next_state, extra={"node": name})
            return next_state

        _run.__name__ = f"tool_{name}"
        return _run

    def compile(self) -> Any:
        """Devuelve el grafo compilado listo para ejecutar (sync o async)."""
        return self.graph.compile(checkpointer=self.checkpointer)
