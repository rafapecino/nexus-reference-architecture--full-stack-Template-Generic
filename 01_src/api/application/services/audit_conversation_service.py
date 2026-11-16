from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from contracts import ConversationMessage, LlmRun
from data.models import (
    Conversation,
    ConversationMessage as ConversationMessageORM,
    LlmRun as LlmRunORM,
)


class AuditConversationService:
    """
    Servicio sencillo para registrar conversaciones, mensajes y ejecuciones LLM.

    Nota: es un esqueleto base; cada proyecto puede enriquecer campos y validaciones.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_conversation(self, conversation_id: UUID | None) -> Conversation:
        if conversation_id:
            existing = self.session.get(Conversation, conversation_id)
            if existing:
                return existing
        conv = Conversation()
        self.session.add(conv)
        self.session.flush()
        return conv

    def log_message(
        self, message: ConversationMessage, *, trace_id: str | None = None
    ) -> ConversationMessageORM:
        conv = self.get_or_create_conversation(message.conversation_id)
        msg = ConversationMessageORM(
            id=message.id,
            conversation_id=conv.id,
            role=message.role,
            content=message.content,
            trace_id=trace_id or message.trace_id,
            input_tokens=message.input_tokens,
            output_tokens=message.output_tokens,
            latency_ms=message.latency_ms,
            tool_calls=message.tool_calls,
            retrieval_metadata=message.retrieval_metadata,
            created_at=message.created_at,
        )
        self.session.add(msg)
        return msg

    def log_llm_run(self, run: LlmRun, *, trace_id: str | None = None) -> LlmRunORM:
        conv_id = run.conversation_id
        conv = self.get_or_create_conversation(conv_id) if conv_id else None
        llm_run = LlmRunORM(
            id=run.id,
            conversation_id=conv.id if conv else None,
            trace_id=trace_id or run.trace_id,
            model=run.model,
            prompt_version=run.prompt_version,
            prompt_hash=run.prompt_hash,
            input_tokens=run.input_tokens,
            output_tokens=run.output_tokens,
            latency_ms=run.latency_ms,
            error=run.error,
            created_at=run.created_at,
        )
        self.session.add(llm_run)
        return llm_run
