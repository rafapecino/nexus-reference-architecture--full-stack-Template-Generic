from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from interfaces.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from interfaces.middleware.trace import TraceIdMiddleware
from interfaces.routers.messages import router as messages_router
from starlette.exceptions import HTTPException as StarletteHTTPException


def _build_app() -> TestClient:
    app = FastAPI()
    app.add_middleware(TraceIdMiddleware)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.include_router(messages_router)
    return TestClient(app)


def _fake_completion(reply: str) -> MagicMock:
    """Builds a minimal OpenAI completion mock."""
    choice = MagicMock()
    choice.message.content = reply
    completion = MagicMock()
    completion.choices = [choice]
    completion.usage.prompt_tokens = 10
    completion.usage.completion_tokens = 5
    return completion


@pytest.mark.unit
@patch(
    "application.services.message_engine.MessageEngine.process",
    new_callable=AsyncMock,
)
def test_post_messages_sync_returns_200_with_trace_id(mock_process):
    from contracts import MessageResponse
    from uuid import uuid4

    fake_response = MessageResponse(
        conversation_id=uuid4(),
        message="Hello from GPT",
        trace_id="trace-test",
        usage={"input_tokens": 10, "output_tokens": 5, "latency_ms": 120},
    )
    mock_process.return_value = (fake_response, MagicMock(), MagicMock())

    client = _build_app()
    response = client.post("/messages/", json={"message": "hola"})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello from GPT"
    assert "trace_id" in body
    assert response.headers.get("X-Trace-Id") is not None
    assert body["conversation_id"] is not None


@pytest.mark.unit
def test_post_messages_async_returns_202_with_request_id_and_trace():
    client = _build_app()
    response = client.post("/messages/?async_mode=true", json={"message": "hola"})

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert "request_id" in body
    assert "trace_id" in body
    assert response.headers.get("X-Trace-Id") == body["trace_id"]


@pytest.mark.unit
def test_post_messages_validation_error_returns_400_with_error_contract():
    client = _build_app()
    response = client.post("/messages/", json={})

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "validation_error"
    assert body["message"] == "Request validation error"
    assert "trace_id" in body
