from application.services import ItemService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.database import get_xchg_db
from data.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_xchg_db)):
    service = ItemService(db)
    return service.list_items()


@router.post("/", response_model=ItemRead)
def create_item(item: ItemCreate, db: Session = Depends(get_xchg_db)):
    service = ItemService(db)
    return service.create_item(item)


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: Session = Depends(get_xchg_db)):
    service = ItemService(db)
    return service.get_item(item_id)


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_xchg_db)):
    service = ItemService(db)
    return service.update_item(item_id, item)


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_xchg_db)):
    service = ItemService(db)
    return service.delete_item(item_id)
