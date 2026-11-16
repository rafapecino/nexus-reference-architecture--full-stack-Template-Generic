from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any, TypeVar

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from data.database import BaseXchg

T = TypeVar("T", bound=BaseXchg)


class BaseRepository[T]:
    """Repositorio generico con CRUD minimo y helpers de consulta."""

    def __init__(self, session: Session, model: type[T]) -> None:
        self.session = session
        self.model = model
        mapper = inspect(model)
        pk_columns = [col.name for col in mapper.primary_key]
        self.pk_name: str = pk_columns[0] if pk_columns else "id"

    def get(self, obj_id: Any) -> T | None:
        """Recupera una entidad por su PK."""
        return self.session.get(self.model, obj_id)

    def list(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[T]:
        """Listado simple con filtros por igualdad y paginacion basica."""
        query = self.session.query(self.model)
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field)
                query = query.filter(column == value)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def add(self, entity: T, *, flush: bool = False) -> T:
        """Anade una entidad y opcionalmente hace flush inmediato."""
        self.session.add(entity)
        if flush:
            self.session.flush([entity])
        return entity

    def delete(self, entity: T) -> None:
        """Elimina la entidad (usa soft-delete en la capa superior si aplica)."""
        self.session.delete(entity)

    def get_or_create(
        self,
        defaults: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> tuple[T, bool]:
        """
        Devuelve (instancia, creado). Si existe un registro que cumple kwargs, lo retorna.
        Si no existe, lo crea aplicando defaults.
        """
        instance = self.session.query(self.model).filter_by(**kwargs).limit(1).first()
        if instance:
            return instance, False

        params: MutableMapping[str, Any] = dict(kwargs)
        if defaults:
            params.update(defaults)
        instance = self.model(**params)  # type: ignore[arg-type]
        self.session.add(instance)
        return instance, True
