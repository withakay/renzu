"""Integration tests for Ollama embedder.

These tests are skipped unless a local Ollama instance is reachable.
"""

from __future__ import annotations

import pytest

from app.config import get_settings
from app.indexing.embedder import OllamaEmbedder


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_embedder_returns_a_vector() -> None:
    settings = get_settings()

    embedder = OllamaEmbedder(base_url=settings.ollama_url)

    try:
        await embedder.health_check()
    except RuntimeError:
        pytest.skip("Ollama is not reachable")

    try:
        vectors = await embedder.embed(["hello"])
    except RuntimeError as exc:
        if "ollama pull" in str(exc).lower():
            pytest.skip("Ollama embedding model is not installed")
        raise

    assert len(vectors) == 1
    assert len(vectors[0]) > 0
