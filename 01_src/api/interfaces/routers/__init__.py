from .db import router as db_router
from .health import router as health_router
from .item import router as item_router
from .messages import router as message_router
from .version import router as version_router

__all__ = ["db_router", "health_router", "item_router", "message_router", "version_router"]
