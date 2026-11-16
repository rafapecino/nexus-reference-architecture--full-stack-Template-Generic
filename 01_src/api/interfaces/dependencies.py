from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, Request


def _extract_trace_id(request: Request) -> str:
    trace_id = getattr(request.state, "trace_id", None)
    if not trace_id:
        trace_id = str(uuid4())
        request.state.trace_id = trace_id
    return trace_id


async def get_trace_id(request: Request) -> str:
    """Devuelve el trace_id asociado a la peticion (middleware o generado aqui)."""
    return _extract_trace_id(request)


TraceIdDep = Depends(get_trace_id)
