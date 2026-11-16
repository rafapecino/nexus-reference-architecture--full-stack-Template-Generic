from application.services.message_service import MessageService
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from contracts import ErrorResponse, MessageAcceptedResponse, MessageRequest, MessageResponse
from data.database import get_xchg_db

from ..dependencies import get_trace_id

router = APIRouter(prefix="/messages", tags=["messages"])
service = MessageService()


@router.post(
    "/",
    response_model=MessageResponse | MessageAcceptedResponse,
    responses={
        202: {
            "description": "Accepted for async processing",
            "model": MessageAcceptedResponse,
        },
        400: {"description": "Validation error", "model": ErrorResponse},
        404: {"description": "Resource not found", "model": ErrorResponse},
        500: {"description": "Internal error", "model": ErrorResponse},
    },
)
async def post_message(
    request: MessageRequest,
    trace_id: str = Depends(get_trace_id),
    async_mode: bool = False,
    db: Session | None = Depends(get_xchg_db),
):
    """
    Main endpoint for the AI runtime.

    - 200: synchronous processing (response generated).
    - 202: accepted if delegated to async processing (queue stub).
    """
    result, status = await service.process(request, trace_id=trace_id, async_mode=async_mode, db=db)
    return JSONResponse(status_code=status, content=result.model_dump(mode="json"))
