from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.database import Base
from data.models.mixins import TimestampMixin, UUIDMixin


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    messages: Mapped[list[ConversationMessage]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
    runs: Mapped[list[LlmRun]] = relationship(
        "LlmRun", back_populates="conversation", cascade="all, delete-orphan"
    )


class ConversationMessage(UUIDMixin, Base):
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True
    )
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")

    role: Mapped[str] = mapped_column(String(20), default="user")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tool_calls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    retrieval_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LlmRun(UUIDMixin, Base):
    __tablename__ = "llm_runs"

    conversation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True, index=True
    )
    conversation: Mapped[Conversation | None] = relationship("Conversation", back_populates="runs")

    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
