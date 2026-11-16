from __future__ import annotations

from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column

from data.database import Base
from data.models.mixins import OptimisticLockMixin, TimestampMixin, UUIDMixin


class ProcessStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DEAD_LETTER = "DEAD_LETTER"


class ProcessInstance(UUIDMixin, TimestampMixin, OptimisticLockMixin, Base):
    """
    Estado técnico de un proceso multi-paso.

    No contiene lógica de negocio; controla flujo técnico e idempotencia.
    """

    __tablename__ = "process_instances"

    process_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[ProcessStatus] = mapped_column(
        PG_ENUM(ProcessStatus, name="process_status"),
        nullable=False,
        default=ProcessStatus.PENDING,
        index=True,
    )
    current_step: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    def transition_to(self, status: ProcessStatus) -> None:
        """Transiciona de estado validando reglas básicas."""
        allowed = {
            ProcessStatus.PENDING: {ProcessStatus.RUNNING, ProcessStatus.CANCELLED},
            ProcessStatus.RUNNING: {
                ProcessStatus.COMPLETED,
                ProcessStatus.FAILED,
                ProcessStatus.CANCELLED,
                ProcessStatus.DEAD_LETTER,
            },
            ProcessStatus.FAILED: {ProcessStatus.DEAD_LETTER},
        }
        if status == self.status:
            return
        allowed_targets = allowed.get(self.status, set())
        if allowed_targets and status not in allowed_targets:
            raise ValueError(f"Transition not allowed: {self.status} -> {status}")
        self.status = status

    def is_terminal(self) -> bool:
        return self.status in {
            ProcessStatus.COMPLETED,
            ProcessStatus.FAILED,
            ProcessStatus.CANCELLED,
            ProcessStatus.DEAD_LETTER,
        }

    def set_error(self, error: str) -> None:
        self.error = error[:1024]
