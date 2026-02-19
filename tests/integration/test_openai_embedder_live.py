"""Live OpenAI integration test for embeddings.

Skipped by default to avoid network and billing in CI.
"""

from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.indexing.embedder import OpenAIEmbedder


@pytest.mark.live_api
@pytest.mark.asyncio
async def test_openai_embedder_returns_expected_dimensionality() -> None:
    if os.environ.get("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_API_TESTS=1 to enable live API tests")

    settings = get_settings()
    if not settings.openai_api_key:
        pytest.skip("OPENAI_API_KEY is not configured")

    expected_size = settings.embedding_vector_size or settings.qdrant_vector_size

    embedder = OpenAIEmbedder(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_embedding_model,
        vector_size=expected_size,
        send_dimensions=settings.embedding_vector_size is not None,
        max_batch_size=16,
        requests_per_second=1.0,
    )

    vectors = await embedder.embed(["hello world"])
    assert len(vectors) == 1
    assert len(vectors[0]) == expected_size
