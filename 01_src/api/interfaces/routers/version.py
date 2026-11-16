import os

from fastapi import APIRouter

router = APIRouter(prefix="/version")


@router.get("/", tags=["meta"])
@router.get("", tags=["meta"])
def version() -> dict[str, str]:
    """Devuelve metadatos básicos de la aplicación."""
    return {
        "app": os.getenv("APP_NAME", "starter-api"),
        "env": os.getenv("APP_ENV", "local"),
        "version": os.getenv("APP_VERSION", "0.0.0"),
    }
