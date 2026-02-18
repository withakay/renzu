"""Integration tests for Qdrant client against a real Qdrant instance."""

from __future__ import annotations

import os
import uuid

import pytest

from app.indexing.qdrant import ChunkPayload, ChunkPoint, QdrantClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_qdrant_round_trip() -> None:
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection_name=f"it_chunks_{uuid.uuid4().hex[:8]}",
        vector_size=4,
    )

    if not await client.health_check():
        pytest.skip("Qdrant is not reachable at QDRANT_URL")

    await client.ensure_collection()

    payload = ChunkPayload(
        repo_id="repo-integration",
        path="src/example.py",
        language="python",
        chunk_type="function",
        start_line=10,
        end_line=20,
        text="def integration(): return True",
        content_hash="integration-hash",
    )

    await client.upsert_points(
        repo_id="repo-integration",
        points=[ChunkPoint(id="p-1", vector=[0.1, 0.2, 0.3, 0.4], payload=payload)],
    )

    results = await client.search(
        query_vector=[0.1, 0.2, 0.3, 0.4], repo_id="repo-integration", limit=3
    )
    assert len(results) >= 1

    await client.delete_by_repo("repo-integration")
