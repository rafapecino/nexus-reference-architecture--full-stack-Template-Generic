from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from common.logging import get_logger, setup_logging
from contracts.worker_message import WorkerMessage
from worker.application.handlers import item_demo as _item_demo  # noqa: F401
from worker.runner import Runner

log = get_logger(__name__)


def handle_message(message: WorkerMessage | dict[str, Any]) -> None:
    """
    Punto de entrada genérico que puede invocar cualquier trigger.

    Cada trigger debe construir el WorkerMessage y llamar a esta función.
    """
    runner = Runner()
    runner.run(message)


def bootstrap() -> None:
    """Inicializa logging y deja listo el worker para que el runtime monte triggers."""
    setup_logging()
    log.info("Worker skeleton inicializado; conecta un trigger para procesar mensajes.")


def _parse_payload(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - se captura para CLI manual
        raise SystemExit(f"Payload JSON invalido: {exc}") from exc


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta un job del worker de forma directa.")
    parser.add_argument("--process-type", required=False, help="Tipo de proceso a ejecutar.")
    parser.add_argument("--step", required=False, help="Paso a ejecutar.")
    parser.add_argument(
        "--payload",
        default="{}",
        help='Payload JSON para el paso (ej. \'{"index_version":"v1","sources":["docs/"]}\').',
    )
    args = parser.parse_args()

    if not args.process_type or not args.step:
        log.info("Sin --process-type/--step no se ejecuta ningun handler.")
        return

    message = WorkerMessage(
        process_id=uuid4(),
        process_type=args.process_type,
        step=args.step,
        payload=_parse_payload(args.payload),
        correlation_id=uuid4(),
        retry=0,
        created_at=datetime.now(tz=UTC),
    )
    handle_message(message)


if __name__ == "__main__":
    bootstrap()
    run_cli()
