from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from contracts.worker_message import WorkerMessage
from worker.application.handlers.base import StepResult
from worker.runner import Runner


class Trigger(ABC):
    """Interfaz mínima para adaptar runtimes concretos (cola, timer, evento)."""

    def __init__(self, runner: Runner | None = None) -> None:
        self.runner = runner or Runner()

    @abstractmethod
    def parse_event(self, raw_event: Any) -> WorkerMessage:
        """Convierte el evento del runtime en un WorkerMessage validado."""
        raise NotImplementedError

    def handle(self, raw_event: Any) -> StepResult:
        """Parsea y delega la ejecución en el runner."""
        message = self.parse_event(raw_event)
        return self.runner.run(message)
