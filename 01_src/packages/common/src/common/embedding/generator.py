"""Reusable embedding generation via OpenAI text-embedding models."""

from __future__ import annotations

import random

from openai import OpenAI

from common.config.settings import get_settings
from common.logging.logger import get_logger

logger = get_logger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Singleton OpenAI client (lazy initialization)."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=get_settings().openai.api_key)
    return _client


def generate_embedding(text: str) -> list[float]:
    """Convert text into a semantic vector using the configured OpenAI model.

    Model and dimensions are read from settings:
        OPENAI_EMBEDDING_MODEL       (default: text-embedding-3-large)
        OPENAI_EMBEDDING_DIMENSIONS  (default: 3072)

    Args:
        text: Input text. Newlines are normalized to spaces.

    Returns:
        List of floats representing the semantic vector.

    Raises:
        ValueError: If the text is empty after normalization.
    """
    clean_text = text.replace("\n", " ").strip()
    if not clean_text:
        raise ValueError("Input text cannot be empty.")

    settings = get_settings()
    model = settings.openai.embedding_model
    dimensions = settings.openai.embedding_dimensions

    if settings.openai.mock_embeddings:
        logger.info("Generating mock embedding (MOCK_EMBEDDINGS=true)")
        return [random.uniform(-1.0, 1.0) for _ in range(dimensions)]

    logger.info(
        "Generating embedding",
        extra={"extra": {"model": model, "dimensions": dimensions, "chars": len(clean_text)}},
    )

    response = _get_client().embeddings.create(
        model=model,
        input=clean_text,
        dimensions=dimensions,
    )
    return response.data[0].embedding
