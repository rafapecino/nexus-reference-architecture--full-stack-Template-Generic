from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from data.database import get_xchg_db

router = APIRouter()


@router.get("/db/ping")
def db_ping(db: Session = Depends(get_xchg_db)) -> dict[str, str]:
    """Ejecuta SELECT 1 para validar conectividad a BD."""
    db.execute(text("SELECT 1"))
    return {"db": "ok"}
