from typing import Any

from pydantic import BaseModel


class TaskCompleted(BaseModel):
    task_id: str
    output_ref: str | None = None
    result: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    schema_version: str = "v1"
