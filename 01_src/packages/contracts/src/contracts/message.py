from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    """Contrato base de entrada para /messages."""

    message: str = Field(..., description="Contenido del mensaje o prompt del usuario.")
    conversation_id: UUID | None = Field(
        default=None,
        description="Identificador de conversacion si se quiere mantener contexto.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Metadatos opcionales (canal, usuario, idioma, etc.)."
    )


class MessageResponse(BaseModel):
    """Respuesta sincrona (200)."""

    conversation_id: UUID | None = Field(
        default=None,
        description="Conversacion asociada (puede crearse en la primera llamada).",
    )
    message: str = Field(..., description="Generated response.")
    trace_id: str = Field(..., description="Identificador de traza para correlacion.")
    usage: dict[str, Any] | None = Field(
        default=None,
        description="Metricas opcionales (tokens, latencia, steps).",
    )


class MessageAcceptedResponse(BaseModel):
    """Respuesta asincrona (202)."""

    request_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Identificador del request."
    )
    status: str = Field(default="accepted", description="Processing status.")
    trace_id: str = Field(..., description="Identificador de traza para correlacion.")


class ErrorResponse(BaseModel):
    """Contrato estandar de error."""

    code: str = Field(..., description="Codigo de error interno o clasificacion.")
    message: str = Field(..., description="Mensaje de error legible.")
    trace_id: str = Field(..., description="Identificador de traza para correlacion.")
    detail: Any | None = Field(default=None, description="Detalle opcional (stack, campos, etc.).")
