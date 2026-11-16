from __future__ import annotations

import os

from application.services.audit_conversation_service import AuditConversationService
from application.services.message_engine import MessageEngine
from sqlalchemy.orm import Session

from contracts import MessageAcceptedResponse, MessageRequest, MessageResponse
from contracts.audit_conversation import ConversationMessage, LlmRun
from data.database import xchg_session_scope


class MessageService:
    """Orquesta el flujo de /messages delegando en el motor y la auditoría."""

    def __init__(self, engine_staging: MessageEngine | None = None) -> None:
        self.engine_staging = engine_staging or MessageEngine()

    async def process(
        self,
        request: MessageRequest,
        *,
        trace_id: str,
        async_mode: bool = False,
        db: Session | None = None,
    ) -> tuple[MessageResponse | MessageAcceptedResponse, int]:
        if async_mode:
            accepted = self.engine_staging.enqueue(request, trace_id=trace_id)
            return accepted, 202

        audit_enabled = os.getenv("AUDIT_ENABLED", "false").lower() in {"1", "true", "yes"}

        result = await self.engine_staging.process(request, trace_id=trace_id)
        if isinstance(result, tuple):
            response, audit_message, audit_run = result
        else:
            response = result
            audit_message = audit_run = None

        if audit_enabled:
            session = db
            if session is None:
                with xchg_session_scope() as scoped:
                    self._run_audit(scoped, audit_message, audit_run, trace_id)
            else:
                self._run_audit(session, audit_message, audit_run, trace_id)

        return response, 200

    def _run_audit(
        self,
        session: Session,
        audit_message: ConversationMessage | None,
        audit_run: LlmRun | None,
        trace_id: str,
    ) -> None:
        audit = AuditConversationService(session)
        if isinstance(audit_message, ConversationMessage):
            audit.log_message(audit_message, trace_id=trace_id)
        if isinstance(audit_run, LlmRun):
            audit.log_llm_run(audit_run, trace_id=trace_id)
        session.commit()
