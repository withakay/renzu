"""Integration tests for OpenAI embedder.

These tests are skipped unless OpenAI credentials are configured.
"""

from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.indexing.embedder import OpenAIEmbedder


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_embedder_returns_expected_dimensions() -> None:
    settings = get_settings()
    if not settings.openai_api_key and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not configured")

    embedder = OpenAIEmbedder()
    vectors = await embedder.embed(["hello"])

    assert len(vectors) == 1
    expected_size = settings.embedding_vector_size or settings.qdrant_vector_size
    assert len(vectors[0]) == expected_size
