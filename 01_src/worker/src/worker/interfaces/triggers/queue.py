from __future__ import annotations

from typing import Any

from contracts.worker_message import WorkerMessage
from worker.interfaces.triggers.base import Trigger


class QueueTrigger(Trigger):
    """
    Adaptador para mensajes de cola (Azure Storage Queue, Service Bus, etc.).

    Implementar `parse_event` para mapear el mensaje de cola al envelope WorkerMessage.
    """

    def parse_event(self, raw_event: Any) -> WorkerMessage:
        raise NotImplementedError("Implementa el mapeo desde el mensaje de cola.")
