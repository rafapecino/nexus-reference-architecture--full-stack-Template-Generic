from __future__ import annotations

from typing import Any

from contracts.worker_message import WorkerMessage
from worker.interfaces.triggers.base import Trigger


class TimerTrigger(Trigger):
    """
    Adaptador para ejecuciones programadas (cron/intervalo).

    Implementar `parse_event` según los metadatos del scheduler usado.
    """

    def parse_event(self, raw_event: Any) -> WorkerMessage:
        raise NotImplementedError("Implementa el mapeo desde el evento del scheduler.")
