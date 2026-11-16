from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from common.logging import get_logger

# from worker.application.handlers.base import StepResult
from contracts.worker_message import WorkerMessage
from data.models.process_instance import ProcessInstance, ProcessStatus

log = get_logger(__name__)


class ProcessService:
    """Puerta de acceso a BD para instancias de proceso."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, process_id: UUID) -> ProcessInstance | None:
        return self.session.get(ProcessInstance, process_id)

    def get_or_create_from_message(self, message: WorkerMessage) -> ProcessInstance:
        instance = self.get(message.process_id)
        if instance:
            return instance

        instance = ProcessInstance(
            id=message.process_id,
            process_type=message.process_type,
            status=ProcessStatus.PENDING,
            current_step=None,
            input_data=message.payload,
        )
        self.session.add(instance)
        self.session.flush()
        return instance

    def mark_running(self, instance: ProcessInstance, *, step: str) -> None:
        instance.transition_to(ProcessStatus.RUNNING)
        instance.current_step = step
        self.session.flush()
        log.info(
            "Proceso en ejecución",
            extra={
                "extra": {
                    "process_id": str(instance.id),
                    "process_type": instance.process_type,
                    "step": step,
                    "status": instance.status.value,
                }
            },
        )

    def mark_next_step(self, instance: ProcessInstance, *, next_step: str) -> None:
        instance.status = ProcessStatus.RUNNING
        instance.current_step = next_step
        self.session.flush()

    def mark_completed(
        self,
        instance: ProcessInstance,
        *,
        output_data: dict[str, Any] | None = None,
    ) -> None:
        instance.transition_to(ProcessStatus.COMPLETED)
        instance.current_step = None
        if output_data:
            instance.output_data = output_data
        self.session.flush()
        log.info(
            "Proceso completado",
            extra={
                "extra": {
                    "process_id": str(instance.id),
                    "process_type": instance.process_type,
                    "status": instance.status.value,
                }
            },
        )

    def mark_failed(self, instance: ProcessInstance, *, error: str) -> None:
        instance.transition_to(ProcessStatus.FAILED)
        instance.set_error(error)
        self.session.flush()
        log.error(
            "Proceso marcado como FAILED",
            extra={
                "extra": {
                    "process_id": str(instance.id),
                    "process_type": instance.process_type,
                    "status": instance.status.value,
                    "error": instance.error,
                }
            },
        )

    def mark_dead_letter(self, instance: ProcessInstance, *, error: str) -> None:
        instance.transition_to(ProcessStatus.DEAD_LETTER)
        instance.set_error(error)
        self.session.flush()

    def mark_cancelled(self, instance: ProcessInstance, *, reason: str) -> None:
        instance.transition_to(ProcessStatus.CANCELLED)
        instance.set_error(reason)
        self.session.flush()
