from __future__ import annotations

from pydantic import BaseModel, field_validator


class ItemPayload(BaseModel):
    """Payload base para procesos de Item en el worker."""

    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El nombre de item no puede estar vacio")
        return cleaned

    def normalized(self) -> dict[str, str | None]:
        return {"name": self.name.strip(), "description": self.description}
