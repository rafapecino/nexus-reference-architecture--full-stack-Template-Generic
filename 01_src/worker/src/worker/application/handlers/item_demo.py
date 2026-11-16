from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from common.logging import get_logger
from contracts.worker_message import WorkerMessage
from data.repositories import ItemRepository
from worker.application.handlers import StepHandler, StepResult, register_handler
from worker.domain.item_payload import ItemPayload

log = get_logger(__name__)


@register_handler("item_demo", "validate_item")
class ValidateItemStep(StepHandler):
    """Valida y normaliza el payload antes de persistirlo."""

    def handle(self, *, message: WorkerMessage, session: Session) -> StepResult:
        payload = ItemPayload.model_validate(message.payload)
        normalized = payload.normalized()
        log.info(
            "Payload validado para item_demo",
            extra={
                "extra": {
                    "process_id": str(message.process_id),
                    "correlation_id": str(message.correlation_id),
                    "name": normalized["name"],
                }
            },
        )
        return StepResult(next_step="persist_item", next_payload=normalized)


@register_handler("item_demo", "persist_item")
class PersistItemStep(StepHandler):
    """Ejemplo de persistencia idempotente de Item."""

    def __init__(
        self,
        repo_factory: Callable[[Session], ItemRepository] | None = None,
    ) -> None:
        self.repo_factory = repo_factory or ItemRepository

    def handle(self, *, message: WorkerMessage, session: Session) -> StepResult:
        payload = ItemPayload.model_validate(message.payload)
        repository = self.repo_factory(session)
        item, created = repository.upsert_by_name(
            name=payload.name,
            description=payload.description,
        )

        log.info(
            "Item persistido/actualizado en item_demo",
            extra={
                "extra": {
                    "process_id": str(message.process_id),
                    "correlation_id": str(message.correlation_id),
                    "item_id": getattr(item, "id", None),
                    "created": created,
                }
            },
        )
        return StepResult(
            output_data={"item_id": getattr(item, "id", None), "created": created},
        )
