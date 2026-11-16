from typing import Any

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    task_type: str
    input_ref: str | None = None
    payload: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    callback_url: str | None = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
