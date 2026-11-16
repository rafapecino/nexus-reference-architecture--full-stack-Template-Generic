from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from data.database import BaseXchg

# SQLite en memoria para tests unitarios ligeros.
TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine_xchg = create_engine(
    TEST_DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine_xchg, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Crea tablas en limpio y expone una sesion aislada por test."""
    BaseXchg.metadata.drop_all(bind=engine_xchg)
    BaseXchg.metadata.create_all(bind=engine_xchg)
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
