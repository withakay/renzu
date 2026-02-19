"""Unit tests for Qdrant client wrapper."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.indexing.qdrant import ChunkPayload, ChunkPoint, QdrantClient


@pytest.mark.unit
@pytest.mark.asyncio
class TestQdrantClient:
    async def test_ensure_collection_creates_when_missing(self) -> None:
        fake_client = AsyncMock()
        fake_client.get_collections.return_value = SimpleNamespace(collections=[])

        client = QdrantClient(client=fake_client, vector_size=8)
        await client.ensure_collection()

        fake_client.create_collection.assert_awaited_once()

    async def test_ensure_collection_skips_when_present(self) -> None:
        fake_client = AsyncMock()
        fake_client.get_collections.return_value = SimpleNamespace(
            collections=[SimpleNamespace(name="code_chunks")]
        )

        client = QdrantClient(client=fake_client)
        await client.ensure_collection()

        fake_client.create_collection.assert_not_awaited()

    async def test_upsert_points_applies_repo_id_to_payload(self) -> None:
        fake_client = AsyncMock()
        client = QdrantClient(client=fake_client)
        payload = ChunkPayload(
            repo_id="ignored",
            path="src/main.py",
            language="python",
            chunk_type="function",
            start_line=1,
            end_line=5,
            text="def f(): pass",
            content_hash="abc123",
        )
        point = ChunkPoint(id="p1", vector=[0.1, 0.2, 0.3], payload=payload)

        await client.upsert_points(repo_id="repo-1", points=[point])

        fake_client.upsert.assert_awaited_once()
        upsert_call = fake_client.upsert.await_args.kwargs
        assert upsert_call["collection_name"] == "code_chunks"
        assert upsert_call["points"][0].payload["repo_id"] == "repo-1"

    async def test_delete_by_repo_uses_repo_filter(self) -> None:
        fake_client = AsyncMock()
        client = QdrantClient(client=fake_client)

        await client.delete_by_repo("repo-1")

        fake_client.delete.assert_awaited_once()
        delete_call = fake_client.delete.await_args.kwargs
        selector = delete_call["points_selector"]
        condition = selector.filter.must[0]
        assert condition.key == "repo_id"
        assert condition.match.value == "repo-1"

    async def test_search_passes_filter_arguments(self) -> None:
        fake_client = AsyncMock()
        fake_client.search.return_value = []
        client = QdrantClient(client=fake_client)

        await client.search(
            query_vector=[0.1, 0.2, 0.3],
            repo_id="repo-1",
            path_prefix="src/",
            language="python",
            chunk_type="ts:function",
            limit=3,
        )

        fake_client.search.assert_awaited_once()
        search_call = fake_client.search.await_args.kwargs
        assert search_call["limit"] == 3
        assert search_call["query_filter"] is not None
        assert len(search_call["query_filter"].must) == 4

    async def test_health_check_returns_true_when_qdrant_reachable(self) -> None:
        fake_client = AsyncMock()
        fake_client.get_collections.return_value = SimpleNamespace(collections=[])
        client = QdrantClient(client=fake_client)

        assert await client.health_check() is True

    async def test_health_check_returns_false_on_error(self) -> None:
        fake_client = AsyncMock()
        fake_client.get_collections.side_effect = RuntimeError("boom")
        client = QdrantClient(client=fake_client)

        assert await client.health_check() is False


@pytest.mark.unit
def test_chunk_payload_requires_expected_fields() -> None:
    payload = ChunkPayload(
        repo_id="repo-1",
        path="src/main.py",
        language="python",
        chunk_type="function",
        start_line=1,
        end_line=3,
        text="def f(): pass",
        content_hash="hash123",
    )

    assert payload.repo_id == "repo-1"
