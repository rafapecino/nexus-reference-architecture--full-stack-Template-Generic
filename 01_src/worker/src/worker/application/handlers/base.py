from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from contracts.worker_message import WorkerMessage


@dataclass
class StepResult:
    """
    Resultado de un paso.

    - next_step/next_payload permiten continuar el pipeline publicando otro mensaje.
    - output_data se puede persistir como resultado final del proceso.
    """

    next_step: str | None = None
    next_payload: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None

    @property
    def has_next(self) -> bool:
        return bool(self.next_step)


class StepHandler(ABC):
    """Interfaz base para cualquier paso de proceso."""

    @abstractmethod
    def handle(self, *, message: WorkerMessage, session: Session) -> StepResult:
        """
        Ejecuta el paso con el mensaje validado y una sesión de BD gestionada externamente.

        Debe ser idempotente y evitar efectos colaterales irreversibles.
        """
        raise NotImplementedError
