from __future__ import annotations

from typing import Any

from sqlalchemy.exc import SQLAlchemyError, StaleDataError

from common.logging import get_logger
from contracts.worker_message import WorkerMessage
from data.database import xchg_session_scope
from worker.application.handlers.base import StepResult
from worker.application.handlers.registry import HandlerNotFoundError, HandlerRegistry, registry
from worker.infrastructure.services.process_service import ProcessService

log = get_logger(__name__)


class Runner:
    """
    Orquestador principal del worker.

    - Valida el mensaje.
    - Carga/crea la instancia de proceso.
    - Marca estado RUNNING y ejecuta el handler.
    - Actualiza estado final o siguiente paso.
    """

    def __init__(self, handler_registry: HandlerRegistry | None = None) -> None:
        self.registry = handler_registry or registry

    def run(self, message: WorkerMessage | dict[str, Any]) -> StepResult:
        message_model = message if isinstance(message, WorkerMessage) else WorkerMessage(**message)
        ctx = {
            "process_id": str(message_model.process_id),
            "process_type": message_model.process_type,
            "step": message_model.step,
            "correlation_id": str(message_model.correlation_id),
            "retry": message_model.retry,
        }

        log.info("Procesando mensaje de worker", extra={"extra": ctx})

        with xchg_session_scope() as session:
            service = ProcessService(session)
            instance = service.get_or_create_from_message(message_model)

            try:
                handler = self.registry.resolve(message_model)
            except HandlerNotFoundError as exc:
                service.mark_dead_letter(instance, error=str(exc))
                log.error("Handler not found", extra={"extra": ctx}, exc_info=exc)
                raise

            try:
                service.mark_running(instance, step=message_model.step)
                result = handler.handle(message=message_model, session=session)
            except StaleDataError as exc:
                # Conflicto de versionado optimista: dejamos que el invocador reintente.
                log.error(
                    "Conflicto de versión al actualizar el proceso",
                    extra={"extra": ctx},
                    exc_info=exc,
                )
                raise
            except SQLAlchemyError as exc:
                log.error("Database error", extra={"extra": ctx}, exc_info=exc)
                service.mark_failed(instance, error="Database error")
                raise
            except Exception as exc:  # noqa: BLE001
                service.mark_failed(instance, error=str(exc))
                log.error("Error executing handler", extra={"extra": ctx}, exc_info=exc)
                raise

            if result.has_next and result.next_step:
                service.mark_next_step(instance, next_step=result.next_step)
                log.info(
                    "Paso completado, se agenda el siguiente",
                    extra={"extra": {**ctx, "next_step": result.next_step}},
                )
            else:
                service.mark_completed(instance, output_data=result.output_data)
                log.info("Proceso finalizado", extra={"extra": ctx})

            return result
