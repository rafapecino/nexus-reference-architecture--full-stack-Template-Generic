from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from common.logging.logger import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class BaseService:
    """Servicio generico para operaciones CRUD sencillas sobre un modelo ORM."""

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model
        self.pk_name = self._get_primary_key_name()
        logger.info(
            "Service initialized",
            extra={"extra": {"model": self.model.__name__, "pk": self.pk_name}},
        )

    def _get_primary_key_name(self) -> str:
        mapper = inspect(self.model)
        pk_columns = [key.name for key in mapper.primary_key]
        if not pk_columns:
            raise ValueError(f"Model {self.model.__name__} has no primary key defined")
        return pk_columns[0]

    def create_item(self, item_data: BaseModel) -> ModelType:
        item = self.model(**item_data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        pk_value = getattr(item, self.pk_name)
        logger.info(
            "Created entity", extra={"extra": {"model": self.model.__name__, "id": pk_value}}
        )
        return item

    def list_items(self, order_by: str | None = None) -> list[ModelType]:
        order_by_clause = text(self.pk_name) if order_by is None else text(order_by)
        items = self.db.query(self.model).order_by(order_by_clause).all()
        logger.info(
            "Listed entities", extra={"extra": {"model": self.model.__name__, "count": len(items)}}
        )
        return items

    def get_item(self, item_id: int) -> ModelType:
        primary_key_field = getattr(self.model, self.pk_name)
        item = self.db.query(self.model).filter(primary_key_field == item_id).first()
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with ID {item_id} not found",
            )
        logger.info(
            "Fetched entity", extra={"extra": {"model": self.model.__name__, "id": item_id}}
        )
        return item

    def update_item(self, item_id: int, item_data: BaseModel) -> ModelType:
        primary_key_field = getattr(self.model, self.pk_name)
        item = self.db.query(self.model).filter(primary_key_field == item_id).first()
        if not item:
            logger.warning(
                "Entity not found for update",
                extra={"extra": {"model": self.model.__name__, "id": item_id}},
            )
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with ID {item_id} not found",
            )

        for key, value in item_data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        logger.info(
            "Updated entity", extra={"extra": {"model": self.model.__name__, "id": item_id}}
        )
        return item

    def delete_item(self, item_id: int) -> dict[str, str]:
        primary_key_field = getattr(self.model, self.pk_name)
        item = self.db.query(self.model).filter(primary_key_field == item_id).first()
        if not item:
            logger.warning(
                "Entity not found for deletion",
                extra={"extra": {"model": self.model.__name__, "id": item_id}},
            )
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with ID {item_id} not found",
            )

        self.db.delete(item)
        self.db.commit()
        logger.info(
            "Deleted entity", extra={"extra": {"model": self.model.__name__, "id": item_id}}
        )
        return {"message": f"{self.model.__name__} with ID {item_id} deleted successfully"}
