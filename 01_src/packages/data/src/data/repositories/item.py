from __future__ import annotations

from sqlalchemy.orm import Session

from data.models import Item

from .base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repositorio concreto para Item con upsert idempotente por nombre."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Item)

    def upsert_by_name(self, *, name: str, description: str | None = None) -> tuple[Item, bool]:
        existing = self.session.query(Item).filter(Item.name == name).first()
        if existing:
            existing.description = description
            self.session.flush([existing])
            return existing, False

        item = Item(name=name, description=description)
        self.session.add(item)
        self.session.flush([item])
        return item, True
