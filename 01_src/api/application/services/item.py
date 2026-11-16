from sqlalchemy.orm import Session

from data.models import Item

from .base import BaseService


class ItemService(BaseService):
    """Caso de uso simple para CRUD de Item."""

    def __init__(self, db: Session):
        super().__init__(db=db, model=Item)
