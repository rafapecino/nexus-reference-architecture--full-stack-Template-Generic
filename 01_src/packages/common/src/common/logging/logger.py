"""

Uso típico en cualquier sitio (API, worker, script):

from common.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

logger.info("Servicio arrancado")

"""

from __future__ import annotations

import json
import logging
import os
from logging.handlers import RotatingFileHandler

_LOGGING_CONFIGURED = False


class JsonConsoleFormatter(logging.Formatter):
    """
    Formateador JSON para logs en consola.

    Controlado por la variable de entorno:
      - APP_LOG_JSON=true/false
    """

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Campos opcionales útiles
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        return json.dumps(log_record, ensure_ascii=False)


def _parse_bool_env(var_name: str, default: bool = False) -> bool:
    val = os.getenv(var_name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y"}


def setup_root_logging(
    level: str = "INFO",
    json_console: bool = False,
    root_log_file: str | None = None,
) -> None:
    """
    Configura el logger raíz de la aplicación:

    - Nivel (APP_LOG_LEVEL)
    - Consola (texto o JSON)
    - Fichero rotativo opcional (APP_LOG_ROOT_FILE + APP_LOG_DIR)
    """
    global _LOGGING_CONFIGURED

    root_logger = logging.getLogger()
    # Evitamos duplicar handlers si se llama varias veces
    if _LOGGING_CONFIGURED:
        return

    # Limpiar handlers previos
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Nivel
    root_logger.setLevel(level.upper())

    # Handler para consola
    console_handler = logging.StreamHandler()

    if json_console:
        formatter: logging.Formatter = JsonConsoleFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler opcional para fichero rotativo
    if root_log_file:
        log_dir = os.getenv("APP_LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, root_log_file)

        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Integración con Uvicorn / FastAPI
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.setLevel(level.upper())
        uvicorn_logger.propagate = True

    _LOGGING_CONFIGURED = True


def get_namespace_logger(
    namespace: str,
    log_file_name: str | None = None,
) -> logging.Logger:
    """
    Crea/obtiene un logger de 'namespace' con su propio fichero opcional.

    Ejemplo:
      namespace = "gestion_contenidos"
      log_file_name = "gestion_contenidos.log"
    """
    logger = logging.getLogger(namespace)

    # Si ya tiene handlers, asumimos que está configurado
    if logger.handlers:
        return logger

    logger.setLevel(logging.getLogger().level)
    logger.propagate = True  # pasa por el root (consola + root file)

    if log_file_name:
        log_dir = os.getenv("APP_LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, log_file_name)

        # Usamos el mismo formato que el root (primer handler del root)
        root = logging.getLogger()
        formatter = (
            root.handlers[0].formatter
            if root.handlers
            else logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_logging() -> None:
    """
    Punto de entrada único para configurar logging en cualquier app (API, worker, script).

    Variables de entorno soportadas:

      - APP_LOG_LEVEL          (por defecto: INFO)
      - APP_LOG_JSON           (true/false, por defecto: false)
      - APP_LOG_ROOT_FILE      (nombre de fichero para el root logger, opcional)
      - APP_LOG_DIR            (directorio de logs, por defecto: logs)

      - APP_LOG_NAMESPACE      (por defecto: "app")
      - APP_LOG_NAMESPACE_FILE (por defecto: "<namespace>.log")
    """
    level = os.getenv("APP_LOG_LEVEL", "INFO")
    json_console = _parse_bool_env("APP_LOG_JSON", default=False)
    root_log_file = os.getenv("APP_LOG_ROOT_FILE", None)

    setup_root_logging(
        level=level,
        json_console=json_console,
        root_log_file=root_log_file,
    )

    namespace = os.getenv("APP_LOG_NAMESPACE", "app")
    namespace_file = os.getenv(
        "APP_LOG_NAMESPACE_FILE",
        f"{namespace}.log",
    )

    get_namespace_logger(namespace, log_file_name=namespace_file)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Devuelve un logger hijo del namespace configurado.

    Si APP_LOG_NAMESPACE = "gestion_contenidos" y haces:

        logger = get_logger(__name__)

    obtendrás algo como:
        "gestion_contenidos.apps.api.main"
    """
    # Aseguramos que el logging está configurado al primer uso
    if not _LOGGING_CONFIGURED:
        setup_logging()

    namespace = os.getenv("APP_LOG_NAMESPACE", "app")
    full_name = namespace if name in (None, "", "__main__") else f"{namespace}.{name}"
    return logging.getLogger(full_name)


if __name__ == "__main__":
    # Pequeña prueba manual
    setup_logging()
    log = get_logger(__name__)
    log.info("Logger de prueba funcionando")
