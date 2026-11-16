from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from contracts import AuditEvent
from data.models import AuditEvent as AuditEventORM


class AuditEventService:
    """Servicio genérico de auditoría para acciones de usuario/sistema."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def log_event(
        self,
        *,
        actor: str | None,
        action: str,
        entity: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        trace_id: str | None = None,
        process_id: UUID | None = None,
        step: str | None = None,
        created_at: datetime | None = None,
    ) -> AuditEventORM:
        event = AuditEvent(
            id=uuid4(),
            actor=actor,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata=metadata,
            trace_id=trace_id,
            process_id=process_id,
            step=step,
            created_at=created_at or datetime.now(tz=UTC),
        )
        orm = AuditEventORM(
            id=event.id,
            actor=event.actor,
            action=event.action,
            entity=event.entity,
            entity_id=event.entity_id,
            metadata_json=event.metadata,
            trace_id=event.trace_id,
            process_id=str(event.process_id) if event.process_id else None,
            step=event.step,
            created_at=event.created_at,
        )
        self.session.add(orm)
        return orm
