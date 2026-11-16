from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from contracts import ErrorResponse


def _trace_id_from_request(request: Request) -> str:
    trace_id = getattr(request.state, "trace_id", None)
    return trace_id or "unknown"


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    trace_id = _trace_id_from_request(request)
    payload = ErrorResponse(
        code=str(exc.status_code),
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error",
        trace_id=trace_id,
        detail=exc.detail if not isinstance(exc.detail, str) else None,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    trace_id = _trace_id_from_request(request)
    payload = ErrorResponse(
        code="validation_error",
        message="Request validation error",
        trace_id=trace_id,
        detail=exc.errors(),
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=payload.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = _trace_id_from_request(request)
    payload = ErrorResponse(
        code="internal_error",
        message="Internal server error",
        trace_id=trace_id,
        detail=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump()
    )
