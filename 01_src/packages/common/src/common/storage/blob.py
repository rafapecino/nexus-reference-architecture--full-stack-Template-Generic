from __future__ import annotations

import json
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient, ContentSettings

from common.config.settings import get_settings
from common.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BlobLocation:
    """
    Representa la ubicación lógica de un blob.

    Es lo que SI queremos guardar en BD:
      - container
      - name (path relativo dentro del container)
      - version_id (opcional, si el storage tiene versionado)
    """

    container: str
    name: str
    version_id: str | None = None


# ---------- Factories básicos ----------


def _get_blob_service_client() -> BlobServiceClient:
    """
    Crea un BlobServiceClient a partir de la connection string de settings.
    """
    conn_str = get_settings().storage.connection_string
    return BlobServiceClient.from_connection_string(conn_str)


def get_container_client(container: str) -> ContainerClient:
    """
    Devuelve un ContainerClient y, opcionalmente, crea el contenedor si no existe.

    El comportamiento se controla por StorageSettings.auto_create_containers:
      - True  -> intenta crear el contenedor (útil en local/Azurite).
      - False -> asume que el contenedor ya existe; si no, fallará al usarlo.
    """
    service = _get_blob_service_client()
    container_client = service.get_container_client(container)

    settings = get_settings().storage
    if settings.auto_create_containers:
        with suppress(ResourceExistsError):
            container_client.create_container()

    return container_client


def get_blob_client(container: str, blob_name: str, version_id: str | None = None) -> BlobClient:
    """
    Devuelve un BlobClient para (container, blob_name).

    Si se proporciona version_id, apunta a una versión concreta del blob
    (útil cuando el storage account tiene versionado activado).
    Si version_id es None, se usa la versión "actual" del blob.
    """
    container_client = get_container_client(container)
    return container_client.get_blob_client(blob_name, version_id=version_id)


# ---------- Helpers de contenido ----------


def upload_text(
    container: str,
    blob_name: str,
    content: str,
    content_type: str = "text/plain; charset=utf-8",
) -> BlobLocation:
    """
    Sube texto como blob.

    Devuelve un BlobLocation con:
      - container
      - blob_name
      - version_id (si el storage tiene versionado activo; si no, None)
    """
    blob_client = get_blob_client(container, blob_name)
    logger.info(
        "Uploading text blob",
        extra={"container": container, "blob": blob_name},
    )

    result = blob_client.upload_blob(
        content.encode("utf-8"),
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )

    # En cuentas sin versionado, result.version_id suele ser None
    version_id = getattr(result, "version_id", None)

    return BlobLocation(container=container, name=blob_name, version_id=version_id)


def download_text(
    container: str,
    blob_name: str,
    encoding: str = "utf-8",
    version_id: str | None = None,
) -> str:
    """
    Descarga un blob como texto UTF-8 (u otro encoding) usando el SDK de Azure.

    Esta es la función "base" de lectura de texto. Cualquier helper que reciba
    URIs externas o formatos alternativos debería terminar llamando aquí.

    Si version_id no es None, descarga esa versión concreta del blob.
    """
    blob_client = get_blob_client(container, blob_name, version_id=version_id)
    data = blob_client.download_blob().readall()
    text = data.decode(encoding, errors="ignore")

    logger.info(
        "Downloaded text blob",
        extra={
            "container": container,
            "blob": blob_name,
            "length": len(text),
            "version_id": version_id,
        },
    )
    return text


def download_text_from_uri(
    uri: str,
    encoding: str = "utf-8",
    version_id: str | None = None,
) -> str:
    """
    Descarga un blob como texto a partir de una URI externa.

    NOTA IMPORTANTE:
    - Esta función solo se encarga de "normalizar" la URI (parsearla)
      y convertirla a (container, blob_name).
    - La lógica real de acceso al blob la hace SIEMPRE `download_text`.

    De este modo hay un único camino de lectura real, y si mañana cambias
    cómo descargas blobs solo tocas `download_text`.
    """
    container, blob_path = parse_blob_uri(uri)
    return download_text(container, blob_path, encoding=encoding, version_id=version_id)


def upload_json(
    container: str,
    blob_name: str,
    data: Any,
) -> BlobLocation:
    """
    Serializa un objeto Python a JSON y lo sube como blob.

    Devuelve un BlobLocation (container, name, version_id).
    """
    content = json.dumps(data, ensure_ascii=False, indent=2)
    return upload_text(
        container=container,
        blob_name=blob_name,
        content=content,
        content_type="application/json; charset=utf-8",
    )


def download_json(
    container: str,
    blob_name: str,
    version_id: str | None = None,
) -> Any:
    """
    Descarga un blob y lo parsea como JSON.

    Esta es la función base para leer JSON desde blobs. Helpers que trabajen
    con URIs deberían acabar llamando aquí (vía download_text_from_uri o
    directamente).

    Si version_id no es None, descarga esa versión concreta del blob.
    """
    text = download_text(container, blob_name, version_id=version_id)
    try:
        return json.loads(text)
    except json.JSONDecodeError as ex:
        logger.error(
            "Failed to parse JSON blob",
            extra={
                "container": container,
                "blob": blob_name,
                "version_id": version_id,
                "error": str(ex),
            },
        )
        raise


def download_json_from_uri(uri: str, version_id: str | None = None) -> Any:
    """
    Descarga un blob como JSON a partir de una URI externa.

    Igual que con texto:
    - Primero normalizamos la URI → (container, blob_path)
    - Luego delegamos toda la lógica en `download_json`.
    """
    container, blob_path = parse_blob_uri(uri)
    return download_json(container, blob_path, version_id=version_id)


def upload_bytes(
    container: str,
    blob_name: str,
    data: bytes,
    content_type: str | None = None,
) -> BlobLocation:
    """
    Sube bytes directamente. Ideal para PDFs, binarios, etc.

    Devuelve un BlobLocation (container, name, version_id).
    """
    blob_client = get_blob_client(container, blob_name)
    logger.info(
        "Uploading bytes blob",
        extra={"container": container, "blob": blob_name, "size": len(data)},
    )

    if content_type:
        result = blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
    else:
        result = blob_client.upload_blob(
            data,
            overwrite=True,
        )

    version_id = getattr(result, "version_id", None)
    return BlobLocation(container=container, name=blob_name, version_id=version_id)


def upload_file(
    container: str,
    file_path: str | Path,
    blob_name: str | None = None,
    content_type: str | None = None,
) -> BlobLocation:
    """
    Sube un fichero del sistema local como blob.

    Si no se pasa blob_name, se usa el nombre del fichero.
    Devuelve un BlobLocation (container, name, version_id).
    """
    file_path = Path(file_path)
    if blob_name is None:
        blob_name = file_path.name

    with file_path.open("rb") as f:
        data = f.read()

    return upload_bytes(
        container=container,
        blob_name=blob_name,
        data=data,
        content_type=content_type,
    )


def download_to_file(
    container: str,
    blob_name: str,
    dest_path: str | Path,
    chunk_size: int = 1024 * 1024,
    version_id: str | None = None,
) -> str:
    """
    Descarga un blob a un fichero local en chunks.

    Esta es la función base para descargas binarias a fichero.
    """
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    blob_client = get_blob_client(container, blob_name, version_id=version_id)
    stream = blob_client.download_blob()

    with dest_path.open("wb") as out:
        for chunk in stream.chunks(chunk_size=chunk_size):
            out.write(chunk)

    logger.info(
        "Downloaded blob to file",
        extra={
            "container": container,
            "blob": blob_name,
            "dest_path": str(dest_path),
            "version_id": version_id,
        },
    )
    return str(dest_path)


def download_file_from_uri(
    uri: str,
    dest_path: str | Path,
    chunk_size: int = 1024 * 1024,
    version_id: str | None = None,
) -> str:
    """
    Descarga un blob de una URI a un fichero local.

    Siguiendo el mismo patrón:
    - Esta función solo parsea la URI y llama a la función base
      `download_to_file`, que es la que sabe realmente descargar.
    """
    container, blob_path = parse_blob_uri(uri)
    return download_to_file(
        container, blob_path, dest_path, chunk_size=chunk_size, version_id=version_id
    )


def exists(container: str, blob_name: str, version_id: str | None = None) -> bool:
    blob_client = get_blob_client(container, blob_name, version_id=version_id)
    try:
        blob_client.get_blob_properties()
        return True
    except ResourceNotFoundError:
        return False


def get_properties(container: str, blob_name: str, version_id: str | None = None):
    blob_client = get_blob_client(container, blob_name, version_id=version_id)
    return blob_client.get_blob_properties()


# ---------- Helpers basados en URI ----------


def parse_blob_uri(uri: str) -> tuple[str, str]:
    """
    Extrae (container, blob_path) de una URI de Azure Blob.

    Soporta:
      - https://account.blob.core.windows.net/container/path/to/blob
      - wasbs://container@account.blob.core.windows.net/path/to/blob
      - abfs://container@account.blob.core.windows.net/path/to/blob
    """
    from urllib.parse import urlparse

    parsed = urlparse(uri)
    scheme = (parsed.scheme or "").lower()

    if scheme == "blob":
        # blob://container/path/to/blob
        container = parsed.netloc
        blob_path = parsed.path.lstrip("/")
        if not container or not blob_path:
            raise ValueError(f"Invalid blob:// URI: {uri}")
        return container, blob_path

    if scheme in ("https", "http"):
        # https://account.blob.core.windows.net/container/path/to/blob
        path = parsed.path.lstrip("/")  # 'container/path/to/blob'
        parts = path.split("/", 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid blob URI (no blob path): {uri}")
        return parts[0], parts[1]

    if scheme in ("wasbs", "abfs"):
        # wasbs://container@account.blob.core.windows.net/path/to/blob
        host = parsed.netloc  # 'container@account.blob.core.windows.net'
        if "@" not in host:
            raise ValueError(f"Invalid wasbs/abfs URI (missing '@'): {uri}")
        container, _account_host = host.split("@", 1)
        blob_path = parsed.path.lstrip("/")  # 'path/to/blob'
        return container, blob_path

    raise ValueError(f"Unsupported blob URI scheme: {scheme}")


def make_blob_uri(container: str, blob_name: str) -> str:
    """
    Construye una URI interna estándar para identificar un blob, sin SAS y sin dominio.
    Esta URI NO debe usarse para acceso directo (para eso está el SDK).

    Formato recomendado (independiente del storage account):
        blob://<container>/<path/to/blob>

    Esto permite guardar identificadores estables en BD sin acoplar a un hostname real.
    """
    container = container.strip("/")
    blob_name = blob_name.lstrip("/")
    return f"blob://{container}/{blob_name}"
