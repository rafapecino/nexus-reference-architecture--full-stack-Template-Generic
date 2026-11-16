import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from interfaces.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from interfaces.middleware.trace import TraceIdMiddleware
from interfaces.routers import db_router, health_router, item_router, message_router, version_router
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.config.settings import get_settings
from common.logging.logger import get_logger, setup_logging
from data.database import BaseXchg, engine_xchg

load_dotenv()
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI Template Starter"),
    version=os.getenv("APP_VERSION", "1.0"),
    description="BaseUE monorepo API starter",
    docs_url="/docs",
)

app.add_middleware(TraceIdMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

if settings.app.environment in {"local", "dev"}:
    BaseXchg.metadata.create_all(bind=engine_xchg)
    logger.info("Database tables ensured (auto-create enabled for local/dev).")

app.include_router(health_router, tags=["health"])
app.include_router(version_router, tags=["meta"])
app.include_router(db_router, tags=["db"])
app.include_router(item_router, tags=["items"])
app.include_router(message_router, tags=["messages"])
logger.info("API routers registered.")


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """Redirects to the interactive documentation."""
    logger.info("Redirecting to /docs")
    return RedirectResponse(url="/docs")
