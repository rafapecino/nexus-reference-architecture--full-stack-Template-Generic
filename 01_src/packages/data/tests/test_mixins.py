from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from data.database import BaseXchg
from data.models import AuditLogMixin, DirtyFieldsMixin, SoftDeleteMixin, StatusWorkflowMixin


class WorkflowEntity(StatusWorkflowMixin, BaseXchg):
    __tablename__ = "workflow_entities"
    __allowed_statuses__ = {"draft", "published", "archived"}
    __allowed_transitions__ = {"draft": ("published",), "published": ("archived",)}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


class SoftEntity(SoftDeleteMixin, BaseXchg):
    __tablename__ = "soft_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


class AuditedEntity(DirtyFieldsMixin, AuditLogMixin, BaseXchg):
    __tablename__ = "audited_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


def test_status_workflow_transitions(db_session) -> None:
    """Valida transiciones permitidas y bloquea las invalidas."""
    entity = WorkflowEntity(name="doc")
    db_session.add(entity)
    db_session.commit()

    entity.transition_to("published")
    assert entity.status == "published"

    with pytest.raises(ValueError):
        entity.transition_to("draft")


def test_soft_delete_marks_fields(db_session) -> None:
    """Comprueba flags y metadatos del borrado logico."""
    entity = SoftEntity(name="to-delete")
    db_session.add(entity)
    db_session.commit()

    entity.soft_delete(actor="tester@example.com")

    assert entity.is_deleted is True
    assert entity.deleted_by == "tester@example.com"
    assert isinstance(entity.deleted_at, datetime)


def test_audit_log_collects_dirty_fields(db_session) -> None:
    """Genera un log de cambios con valores old/new."""
    entity = AuditedEntity(name="old")
    db_session.add(entity)
    db_session.commit()

    entity.name = "new"
    entry = entity.build_audit_log_entry(actor="tester", action="update")

    assert entry["actor"] == "tester"
    assert entry["action"] == "update"
    assert "name" in entry["changes"]
    assert entry["changes"]["name"]["old"] == "old"
    assert entry["changes"]["name"]["new"] == "new"
