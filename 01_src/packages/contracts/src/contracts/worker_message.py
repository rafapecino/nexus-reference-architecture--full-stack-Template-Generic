from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, conint, field_validator


class WorkerMessage(BaseModel):
    """
    Envelope compartido para procesos encolados y triggers.

    Fuente unica de verdad para productores (API, scripts, otros servicios) y consumidores (workers).
    """

    process_id: UUID
    process_type: str
    step: str
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: UUID
    retry: conint(ge=0) = 0  # type: ignore[call-arg]
    created_at: datetime

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True,
    )

    @field_validator("process_type", "step")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("El campo no puede estar vacio")
        return value
