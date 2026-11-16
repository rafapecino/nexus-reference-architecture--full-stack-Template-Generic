import os
from collections.abc import Generator

import pytest
from data.database import get_xchg_db
from fastapi.testclient import TestClient
from main import app
from data.database import BaseXchg
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.sqlite"

engine_xchg = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_xchg)


@pytest.fixture(scope="session")
def setup_database() -> Generator[None, None, None]:
    """Creates the local SQLite database before tests and removes it after."""
    BaseXchg.metadata.create_all(bind=engine_xchg)
    yield
    BaseXchg.metadata.drop_all(bind=engine_xchg)
    db_path: str = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provides a fresh database session for each test."""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def override_get_db(db_session: Session) -> Generator:
    """Replaces the get_xchg_db() dependency with the file-based SQLite session."""

    def _get_db() -> Generator[Session, None, None]:
        yield db_session

    return _get_db


@pytest.fixture(scope="function")
def client(setup_database: None, override_get_db: Generator) -> Generator[TestClient, None, None]:
    """Creates a test client with the configured SQLite database."""
    app.dependency_overrides[get_xchg_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
