from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Endpoint de salud básico."""
    return {"status": "ok"}
