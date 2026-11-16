from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Conversation(BaseModel):
    """Auditoría de conversaciones (contexto LLM/tool-calling)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None


class ConversationMessage(BaseModel):
    """Mensaje individual dentro de una conversación auditada."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str = Field(description="user/assistant/system")
    content: str
    trace_id: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    tool_calls: dict[str, Any] | None = None
    retrieval_metadata: dict[str, Any] | None = None
    created_at: datetime


class LlmRun(BaseModel):
    """Ejecución de un modelo LLM asociada (prompt, tokens, error)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID | None = None
    trace_id: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    prompt_hash: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: datetime
