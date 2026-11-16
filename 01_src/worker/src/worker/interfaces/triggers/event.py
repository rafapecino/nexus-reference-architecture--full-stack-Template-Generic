from __future__ import annotations

from typing import Any

from contracts.worker_message import WorkerMessage
from worker.interfaces.triggers.base import Trigger


class EventTrigger(Trigger):
    """
    Adaptador para eventos externos (webhook, evento de dominio, etc.).

    Implementar `parse_event` para extraer el payload y construir WorkerMessage.
    """

    def parse_event(self, raw_event: Any) -> WorkerMessage:
        raise NotImplementedError("Implementa el mapeo desde el evento externo.")
