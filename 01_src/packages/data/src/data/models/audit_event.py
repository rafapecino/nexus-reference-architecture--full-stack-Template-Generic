from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from data.database import Base
from data.models.mixins import UUIDMixin


class AuditEvent(UUIDMixin, Base):
    """Evento genérico de auditoría para acciones de usuario/sistema."""

    __tablename__ = "audit_events"

    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    process_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    step: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
