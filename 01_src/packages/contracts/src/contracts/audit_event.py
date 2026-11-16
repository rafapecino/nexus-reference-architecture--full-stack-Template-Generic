from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditEvent(BaseModel):
    """Evento genérico de auditoría (acciones de usuario/sistema)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor: str | None = Field(default=None, description="Usuario o sistema que realizó la acción")
    action: str = Field(
        description="Acción realizada (crear, actualizar, eliminar, ejecutar_tarea, etc.)"
    )
    entity: str | None = Field(default=None, description="Entidad o recurso afectado")
    entity_id: str | None = Field(default=None, description="Identificador del recurso afectado")
    metadata: dict[str, Any] | None = Field(default=None, description="Metadatos adicionales")
    trace_id: str | None = Field(default=None, description="Correlación/trace asociada")
    process_id: UUID | None = Field(default=None, description="Process_id si viene de un worker")
    step: str | None = Field(default=None, description="Paso del worker si aplica")
    created_at: datetime
