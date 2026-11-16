"""AI message engine: routes user messages through the GPT-4.1 pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from time import monotonic
from uuid import uuid4

from openai import OpenAI

from contracts import MessageAcceptedResponse, MessageRequest, MessageResponse
from contracts.audit_conversation import ConversationMessage, LlmRun
from common.config.settings import get_settings
from common.logging.logger import get_logger
from common.prompts.loader import load_prompt

logger = get_logger(__name__)

_PROMPT_NAME = "message_engine"
_PROMPT_VERSION = "v1.0.0"

_system_prompt, _prompt_version, _prompt_hash = load_prompt(_PROMPT_NAME, _PROMPT_VERSION)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Singleton OpenAI client (lazy initialization)."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=get_settings().openai.api_key)
    return _client


class MessageEngine:
    """Engine: synchronous GPT-4.1 completion with full audit trail."""

    async def process(
        self, request: MessageRequest, *, trace_id: str
    ) -> tuple[MessageResponse, ConversationMessage, LlmRun]:
        settings = get_settings().openai
        conversation_id = request.conversation_id or uuid4()

        logger.info(
            "Calling GPT-4.1",
            extra={"extra": {
                "model": settings.chat_model,
                "prompt_version": _prompt_version,
                "trace_id": trace_id,
            }},
        )

        start = monotonic()
        error_msg: str | None = None
        reply: str = ""
        input_tokens: int | None = None
        output_tokens: int | None = None

        try:
            completion = _get_client().chat.completions.create(
                model=settings.chat_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=[
                    {"role": "system", "content": _system_prompt},
                    {"role": "user",   "content": request.message},
                ],
            )
            reply = completion.choices[0].message.content or ""
            input_tokens = completion.usage.prompt_tokens if completion.usage else None
            output_tokens = completion.usage.completion_tokens if completion.usage else None

        except Exception as exc:
            error_msg = str(exc)
            logger.error("GPT-4.1 call failed", extra={"extra": {"error": error_msg, "trace_id": trace_id}})
            reply = "An error occurred while processing your request."

        latency_ms = int((monotonic() - start) * 1000)

        response = MessageResponse(
            conversation_id=conversation_id,
            message=reply,
            trace_id=trace_id,
            usage={"input_tokens": input_tokens, "output_tokens": output_tokens, "latency_ms": latency_ms},
        )
        audit_message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content=reply,
            trace_id=trace_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            tool_calls=None,
            retrieval_metadata=None,
            created_at=datetime.now(tz=UTC),
        )
        audit_run = LlmRun(
            id=uuid4(),
            conversation_id=conversation_id,
            trace_id=trace_id,
            model=settings.chat_model,
            prompt_version=_prompt_version,
            prompt_hash=_prompt_hash,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            error=error_msg,
            created_at=datetime.now(tz=UTC),
        )
        return response, audit_message, audit_run

    def enqueue(self, request: MessageRequest, *, trace_id: str) -> MessageAcceptedResponse:
        # Queue stub — publish to queue/worker here.
        return MessageAcceptedResponse(trace_id=trace_id)
