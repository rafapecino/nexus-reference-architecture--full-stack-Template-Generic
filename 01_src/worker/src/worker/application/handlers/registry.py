from __future__ import annotations

from contracts.worker_message import WorkerMessage
from worker.application.handlers.base import StepHandler


class HandlerNotFoundError(LookupError):
    """No existe handler registrado para el proceso/paso solicitado."""


class HandlerRegistry:
    """Registro de procesos y pasos disponibles."""

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, type[StepHandler]]] = {}

    def register(self, process_type: str, step: str, handler_cls: type[StepHandler]) -> None:
        process_key = process_type.strip()
        step_key = step.strip()
        self._registry.setdefault(process_key, {})[step_key] = handler_cls

    def resolve(self, message: WorkerMessage) -> StepHandler:
        process_handlers = self._registry.get(message.process_type)
        if not process_handlers:
            raise HandlerNotFoundError(f"No hay handlers para el proceso '{message.process_type}'.")

        handler_cls = process_handlers.get(message.step)
        if not handler_cls:
            raise HandlerNotFoundError(
                f"No hay handler para el paso '{message.step}' del proceso '{message.process_type}'."
            )

        return handler_cls()


registry = HandlerRegistry()


def register_handler(process_type: str, step: str):
    """Decorator para registrar handlers sin acoplar al runner."""

    def decorator(handler_cls: type[StepHandler]) -> type[StepHandler]:
        registry.register(process_type, step, handler_cls)
        return handler_cls

    return decorator
