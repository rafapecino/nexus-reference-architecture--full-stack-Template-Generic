from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Asigna un trace_id a cada request y lo expone en headers y request.state."""

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id") or str(uuid4())
        request.state.trace_id = trace_id

        response: Response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
