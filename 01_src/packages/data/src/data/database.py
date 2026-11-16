"""Configuración de la capa de datos (SQLAlchemy + sesiones compartidas).

Dos bases de datos:
  - Xchg      → histórico final, consistente. Variables STAGING_POSTGRES_*.
               Base: BaseXchg · Sesión: get_xchg_db() / xchg_session_scope()
  - Work      → borradores y trabajos intermedios y finales. Variables POSTGRES_*.
               Base: Base · Sesión: get_db() / session_scope()
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from common.config.settings import get_settings

settings = get_settings()

# ── Datalake ──────────────────────────────────────────────────────────────────

engine_xchg = create_engine(settings.db_staging.url)

SessionXchg = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_xchg,
    expire_on_commit=False,
)

BaseXchg = declarative_base()


def get_xchg_db() -> Generator[Session, None, None]:
    """FastAPI dependency: staging session."""
    db: Session = SessionXchg()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def xchg_session_scope() -> Iterator[Session]:
    """Context manager for scripts/workers using the staging."""
    session: Session = SessionXchg()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ── Work DB ───────────────────────────────────────────────────────────────────

engine = create_engine(settings.db_work.url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: work (staging) session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager for scripts/workers using the work DB."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
