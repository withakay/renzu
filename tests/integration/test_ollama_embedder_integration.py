"""Integration tests for Ollama embedder.

These tests are skipped unless a local Ollama instance is reachable.
"""

from __future__ import annotations

import httpx
import pytest

from app.config import get_settings
from app.indexing.embedder import OllamaEmbedder


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_embedder_returns_a_vector() -> None:
    settings = get_settings()

    try:
        async with httpx.AsyncClient(base_url=settings.ollama_url, timeout=2.0) as client:
            response = await client.get("/api/version")
            response.raise_for_status()
    except httpx.HTTPError:
        pytest.skip("Ollama is not reachable")

    embedder = OllamaEmbedder()
    vectors = await embedder.embed(["hello"])

    assert len(vectors) == 1
    assert len(vectors[0]) > 0
