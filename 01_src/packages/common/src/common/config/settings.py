"""Application configuration: general parameters, DB, storage and OpenAI.

Typical usage:

    from common.config.settings import get_settings
    settings = get_settings()
    print(settings.db_staging.url)
    print(settings.openai.chat_model)
    print(settings.openai.embedding_model)

Cache reset:

    from common.config.settings import get_settings
    get_settings.cache_clear()
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value


def _str_to_bool(value: str | None, *, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


class AppSettings(BaseModel):
    """General application parameters."""

    environment: str = Field(default="local", description="Current environment: local/dev/pre/pro")


class DatabaseSettings(BaseModel):
    """Database access configuration."""

    url: str = Field(description="SQLAlchemy database URL")

    @classmethod
    def from_env(cls, prefix: str = "POSTGRES") -> DatabaseSettings:
        user = _require_env(f"{prefix}_USER")
        password = _require_env(f"{prefix}_PASSWORD")
        host = _require_env(f"{prefix}_HOST")
        port = _require_env(f"{prefix}_PORT")
        name = _require_env(f"{prefix}_DB")
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
        return cls(url=url)


class StorageSettings(BaseModel):
    """Azure Storage / Azurite configuration."""

    connection_string: str = Field(description="Azure Storage / Azurite connection string")
    auto_create_containers: bool = Field(default=True)

    @classmethod
    def from_env(cls) -> StorageSettings:
        conn = _require_env("AZURE_STORAGE_CONNECTION_STRING")
        auto_create = _str_to_bool(os.getenv("STORAGE_AUTO_CREATE_CONTAINERS"), default=True)
        return cls(connection_string=conn, auto_create_containers=auto_create)


class OpenAISettings(BaseModel):
    """OpenAI client configuration (chat + embeddings)."""

    api_key: str | None = Field(default=None, description="OpenAI API key")

    # ── Chat model ────────────────────────────────────────────────────────────
    chat_model: str = Field(
        default="gpt-4.1",
        description="Chat completion model — gpt-4.1 (large) | gpt-4.1-mini | gpt-4.1-nano",
    )
    max_tokens: int = Field(
        default=2048,
        description="Maximum tokens in the chat completion response",
    )
    temperature: float = Field(
        default=0.6,
        description="Sampling temperature (0.0 = deterministic, 1.0 = creative)",
    )

    # ── Embedding model ───────────────────────────────────────────────────────
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="Embedding model to use",
    )
    embedding_dimensions: int = Field(
        default=3072,
        description="Embedding vector dimensions — must match Vector(N) in the ORM model",
    )

    # ── Search ────────────────────────────────────────────────────────────────
    search_default_limit: int = Field(
        default=5,
        description="Default number of Structure Sheets returned by the search endpoint",
    )
    search_max_limit: int = Field(
        default=20,
        description="Maximum number of Structure Sheets the client can request",
    )
    mock_embeddings: bool = Field(
        default=False,
        description="If True, return random vectors instead of calling OpenAI (for local dev/testing)",
    )

    @classmethod
    def from_env(cls) -> OpenAISettings:
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2048")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.6")),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            embedding_dimensions=int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "3072")),
            search_default_limit=int(os.getenv("SEARCH_DEFAULT_LIMIT", "5")),
            search_max_limit=int(os.getenv("SEARCH_MAX_LIMIT", "20")),
            mock_embeddings=_str_to_bool(os.getenv("MOCK_EMBEDDINGS"), default=False),
        )


class Settings(BaseModel):
    """Settings aggregator."""

    app: AppSettings
    db_staging: DatabaseSettings  # Datalake — historical, consistent
    db_work: DatabaseSettings      # Working DB — drafts, in-progress jobs
    storage: StorageSettings
    openai: OpenAISettings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Factory with cache: one instance per process."""
    return Settings(
        app=AppSettings(),
        db_staging=DatabaseSettings.from_env(prefix="STAGING_POSTGRES"),
        db_work=DatabaseSettings.from_env(prefix="POSTGRES"),
        storage=StorageSettings.from_env(),
        openai=OpenAISettings.from_env(),
    )
