from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Proporciona una clave primaria UUID para evitar IDs secuenciales."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )


class TimestampMixin:
    """Añade marcas de tiempo de creación y actualización."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        server_onupdate=func.now(),
    )


class UserAuditMixin:
    """Registra el usuario o sistema que creó y actualizó la entidad."""

    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def touch_created_by(self, actor: str) -> None:
        """Asigna el actor creador cuando aún no existe valor."""
        if self.created_by:
            return
        self.created_by = actor
        self.updated_by = actor

    def touch_updated_by(self, actor: str) -> None:
        """Actualiza el actor modificador."""
        self.updated_by = actor


class OptimisticLockMixin:
    """Habilita control de concurrencia optimista por versión."""

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}


class SoftDeleteMixin:
    """Soporta borrado lógico e instantánea de cuándo ocurrió."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def soft_delete(self, actor: str | None = None) -> None:
        """Marca la entidad como eliminada sin borrar el registro."""
        self.is_deleted = True
        self.deleted_at = datetime.now(tz=UTC)
        self.deleted_by = actor

    def restore(self) -> None:
        """Revierte el borrado lógico."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class BlobReferenceMixin:
    """Mantiene metadatos de blobs desacoplados de la URI pública."""

    blob_container: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blob_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    blob_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    blob_checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    blob_mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blob_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def set_blob_reference(
        self,
        *,
        container: str,
        path: str,
        version: str | None = None,
        checksum: str | None = None,
        mime_type: str | None = None,
        size_bytes: int | None = None,
    ) -> None:
        """
        Actualiza los metadatos del blob enlazado.

        Usa identificadores lógicos (container, path, version) alineados con BlobLocation
        y evita persistir URIs dependientes del storage account.
        """
        self.blob_container = container.strip("/")
        self.blob_path = path.lstrip("/")
        self.blob_version = version
        self.blob_checksum = checksum
        self.blob_mime_type = mime_type
        self.blob_size_bytes = size_bytes

    def as_blob_reference(self) -> dict[str, str | None] | None:
        """Devuelve un dict básico con container, path y version si está completo."""
        if not self.blob_container or not self.blob_path:
            return None
        return {
            "container": self.blob_container,
            "name": self.blob_path,
            "version_id": self.blob_version,
        }


class TenantScopeMixin:
    """Campos de aislamiento multi-tenant y ámbito (país/área)."""

    tenant_id: Mapped[str | None] = mapped_column(String(64), index=True)
    country_code: Mapped[str | None] = mapped_column(String(2), index=True)
    scope: Mapped[str | None] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "country_code IS NULL OR char_length(country_code) = 2",
            name="ck_country_code_len",
        ),
    )


class StatusWorkflowMixin:
    """Define un estado y comprueba transiciones válidas si se configuran."""

    status: Mapped[str] = mapped_column(String(64), default="draft", index=True)
    __allowed_statuses__: Iterable[str] | None = None
    __allowed_transitions__: Mapping[str, Iterable[str]] | None = None

    def transition_to(self, new_status: str) -> None:
        """Cambia de estado validando el flujo si hay reglas definidas."""
        if self.__allowed_statuses__ and new_status not in self.__allowed_statuses__:
            raise ValueError(f"Status not allowed: {new_status}")

        if self.__allowed_transitions__:
            current = getattr(self, "status", None)
            allowed = self.__allowed_transitions__.get(current or "", [])
            if new_status not in allowed:
                raise ValueError(f"Transition not allowed: {current} -> {new_status}")

        self.status = new_status


class VersionedEntityMixin:
    """Versionado múltiple para distinguir esquema, datos y origen."""

    schema_version: Mapped[str] = mapped_column(String(32), default="v1")
    data_version: Mapped[int] = mapped_column(Integer, default=1)
    source_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def bump_data_version(self) -> None:
        """Incrementa la versión de datos para reflejar cambios de negocio."""
        self.data_version += 1


class DirtyFieldsMixin:
    """Detecta campos sucios usando el estado de SQLAlchemy."""

    __dirty_exclude__: tuple[str, ...] = ("updated_at",)

    def get_dirty_fields(self) -> dict[str, dict[str, Any]]:
        """
        Devuelve un diccionario {campo: {old, new}} con cambios pendientes.
        Excluye los campos definidos en __dirty_exclude__.
        """
        state = inspect(self)
        dirty: dict[str, dict[str, Any]] = {}
        for attr in state.attrs:
            if attr.key in self.__dirty_exclude__:
                continue
            history = attr.history
            if not history.has_changes():
                continue
            dirty[attr.key] = {
                "old": history.deleted[0] if history.deleted else None,
                "new": history.added[0] if history.added else None,
            }
        return dirty


class AuditLogMixin:
    """
    Construye entradas de auditoría a partir de cambios detectados.
    Combina bien con DirtyFieldsMixin y UserAuditMixin.
    """

    __audit_exclude__: tuple[str, ...] = ("updated_at", "version")

    def build_audit_log_entry(
        self,
        *,
        actor: str | None = None,
        action: str = "update",
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Genera una entrada lista para persistir en un log o tabla de auditoría."""
        changes: MutableMapping[str, Any] = {}
        if hasattr(self, "get_dirty_fields"):
            changes = {
                key: value
                for key, value in self.get_dirty_fields().items()
                if key not in self.__audit_exclude__
            }
        entry = {
            "entity": self.__class__.__name__,
            "action": action,
            "actor": actor,
            "changes": changes,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }
        if extra:
            entry["extra"] = dict(extra)
        return entry


class GeoMixin:
    """Campos para coordenadas geográficas básicas."""

    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    altitude: Mapped[float | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint("(latitude IS NULL) OR (latitude BETWEEN -90 AND 90)", name="ck_latitude"),
        CheckConstraint(
            "(longitude IS NULL) OR (longitude BETWEEN -180 AND 180)",
            name="ck_longitude",
        ),
    )


class FileAssetMixin:
    """Metadatos mínimos para ficheros almacenados externamente."""

    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)

    def set_file_asset(
        self,
        *,
        name: str,
        path: str,
        mime_type: str | None = None,
        size_bytes: int | None = None,
        checksum: str | None = None,
    ) -> None:
        """Actualiza los metadatos asociados a un fichero."""
        self.file_name = name
        self.file_path = path
        self.mime_type = mime_type
        self.file_size_bytes = size_bytes
        self.checksum = checksum
