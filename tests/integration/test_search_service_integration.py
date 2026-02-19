"""Integration tests for SearchService against Qdrant."""

from __future__ import annotations

import os
import uuid

import pytest

from app.indexing.qdrant import ChunkPayload, ChunkPoint, QdrantClient
from app.retrieval.search import SearchService


class StaticEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_service_filters_and_citations_round_trip() -> None:
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=f"it_search_{uuid.uuid4().hex[:8]}",
        vector_size=4,
    )

    if not await client.health_check():
        pytest.skip("Qdrant is not reachable at QDRANT_URL")

    await client.ensure_collection()

    payload_ok = ChunkPayload(
        repo_id="repo-integration",
        path="src/app/ok.py",
        language="python",
        chunk_type="ts:function",
        start_line=1,
        end_line=2,
        text="def ok(): return True",
        content_hash="h1",
    )
    payload_other = ChunkPayload(
        repo_id="repo-integration",
        path="other/nope.py",
        language="python",
        chunk_type="ts:class",
        start_line=10,
        end_line=20,
        text="class Nope: pass",
        content_hash="h2",
    )

    await client.upsert_points(
        repo_id="repo-integration",
        points=[
            ChunkPoint(id="p1", vector=[0.1, 0.2, 0.3, 0.4], payload=payload_ok),
            ChunkPoint(id="p2", vector=[0.1, 0.2, 0.3, 0.4], payload=payload_other),
        ],
    )

    service = SearchService(qdrant=client, embedder=StaticEmbedder())
    results = await service.search(
        "any query",
        repo_id="repo-integration",
        top_k=10,
        path_prefix="src/app",
        chunk_type="ts:function",
    )

    assert len(results) == 1
    assert results[0].citation.repo_id == "repo-integration"
    assert results[0].citation.path == "src/app/ok.py"
    assert results[0].citation.start_line == 1
    assert results[0].citation.end_line == 2
    assert results[0].citation.chunk_type == "ts:function"
    assert results[0].citation.score >= 0.0

    await client.delete_by_repo("repo-integration")
