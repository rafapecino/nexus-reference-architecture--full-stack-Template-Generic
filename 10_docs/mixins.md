# Mixins base disponibles

Este documento resume los mixins listos para reutilizar en el monorepo, agrupados por capa. Todos están implementados en español y pensados para combinarse sin acoplar dominio e infraestructura.

## Modelos (SQLAlchemy) — `packages/data/src/data/models/mixins.py`
- `UUIDMixin`: clave primaria UUID (`uuid4`) para evitar IDs secuenciales.
- `TimestampMixin`: `created_at` y `updated_at` con `func.now()`.
- `UserAuditMixin`: `created_by`/`updated_by` y helpers `touch_*`.
- `OptimisticLockMixin`: columna `version` integrada en el control de concurrencia de SQLAlchemy.
- `SoftDeleteMixin`: borrado lógico (`is_deleted`, `deleted_at`, `deleted_by`) con `soft_delete`/`restore`.
- `BlobReferenceMixin`: metadatos lógicos de blobs (`blob_container`, `blob_path`, `blob_version`, `mime`, `checksum`, `size`), alineado con `BlobLocation` del paquete común.
- `TenantScopeMixin`: `tenant_id`, `country_code`, `scope` con `CheckConstraint` para país.
- `StatusWorkflowMixin`: `status` y validación de transiciones mediante `__allowed_statuses__`/`__allowed_transitions__`.
- `VersionedEntityMixin`: `schema_version`, `data_version`, `source_version`, `payload_version`, `metadata_json`.
- `DirtyFieldsMixin`: detección de cambios `{campo: {old, new}}` usando el estado de SQLAlchemy.
- `AuditLogMixin`: genera entradas de auditoría a partir de cambios y actor.
- `GeoMixin`: coordenadas `latitude`, `longitude`, `altitude` con validaciones de rango.
- `FileAssetMixin`: metadatos de ficheros (`file_name`, `file_path`, `mime_type`, `file_size_bytes`, `checksum`).

## API (FastAPI) — `apps/api/services/mixins.py`
- `PaginationMixin`: normaliza `limit/offset`, calcula `total` y devuelve `{"data": ..., "meta": ...}`.
- `ResponseMetadataMixin`: arma envelopes de respuesta con `meta` y `warnings`.
- `AuthContextMixin`: extrae `user` y `permissions` desde `request.state`.
- `ValidationMixin`: valida diccionarios con esquemas Pydantic (lanza `ValidationError`).
- `BackgroundTasksMixin`: helper ligero para encolar tareas de fondo.

## Operaciones y mantenimiento
Se apoyan en los mixins de modelos: usa `DirtyFieldsMixin` + `AuditLogMixin` para logging de cambios y `VersionedEntityMixin` para versionar payloads. Combina `GeoMixin`, `FileAssetMixin` y `BlobReferenceMixin` cuando el dominio requiera localizar recursos o adjuntar ficheros.

## Ejemplo rápido
```python
from data.models import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StatusWorkflowMixin,
    VersionedEntityMixin,
)
from data.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Article(UUIDMixin, TimestampMixin, SoftDeleteMixin, StatusWorkflowMixin, VersionedEntityMixin, Base):
    __tablename__ = "articles"
    __allowed_statuses__ = {"draft", "published", "archived"}

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)

    def publish(self) -> None:
        self.transition_to("published")
        self.bump_data_version()
```
