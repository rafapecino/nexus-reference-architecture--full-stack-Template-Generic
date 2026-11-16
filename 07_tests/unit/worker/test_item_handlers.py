from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from contracts.worker_message import WorkerMessage
from worker.application.handlers.item_demo import PersistItemStep, ValidateItemStep

pytestmark = pytest.mark.unit


def _message(payload: dict[str, str | None], step: str) -> WorkerMessage:
    return WorkerMessage(
        process_id=uuid4(),
        process_type="item_demo",
        step=step,
        payload=payload,
        correlation_id=uuid4(),
        retry=0,
        created_at=datetime.now(tz=UTC),
    )


def test_validate_item_returns_next_step_and_normalized_payload():
    handler = ValidateItemStep()
    message = _message({"name": "  Demo ", "description": "desc"}, step="validate_item")

    result = handler.handle(message=message, session=None)

    assert result.next_step == "persist_item"
    assert result.next_payload == {"name": "Demo", "description": "desc"}


class FakeItemRepository:
    def __init__(self) -> None:
        self.items: dict[str, SimpleNamespace] = {}
        self.counter = 0

    def upsert_by_name(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> tuple[SimpleNamespace, bool]:
        if name in self.items:
            item = self.items[name]
            item.description = description
            return item, False

        self.counter += 1
        item = SimpleNamespace(id=self.counter, name=name, description=description)
        self.items[name] = item
        return item, True


def test_persist_item_step_upserts_and_returns_output_data():
    repo = FakeItemRepository()
    handler = PersistItemStep(repo_factory=lambda _session: repo)
    message = _message({"name": "Demo", "description": "desc"}, step="persist_item")

    result_first = handler.handle(message=message, session=SimpleNamespace())
    assert result_first.output_data == {"item_id": 1, "created": True}

    message.payload["description"] = "nueva"
    result_second = handler.handle(message=message, session=SimpleNamespace())

    assert result_second.output_data == {"item_id": 1, "created": False}
    assert repo.items["Demo"].description == "nueva"
