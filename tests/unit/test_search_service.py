"""Unit tests for semantic search service."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.retrieval.search import SearchService


def _payload(
    *,
    repo_id: str = "repo-1",
    path: str = "src/app/main.py",
    language: str = "python",
    chunk_type: str = "ts:function",
    start_line: int = 1,
    end_line: int = 3,
    text: str = "def f(): pass",
) -> dict[str, object]:
    return {
        "repo_id": repo_id,
        "path": path,
        "language": language,
        "chunk_type": chunk_type,
        "start_line": start_line,
        "end_line": end_line,
        "text": text,
        "content_hash": "hash123",
        "symbol_scip": None,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_embeds_query_forwards_filters_and_builds_citations() -> None:
    embedder = AsyncMock()
    embedder.embed.return_value = [[0.1, 0.2, 0.3]]

    qdrant = AsyncMock()
    qdrant.search.return_value = [
        SimpleNamespace(payload=_payload(), score=0.91),
    ]

    service = SearchService(qdrant=qdrant, embedder=embedder)
    results = await service.search(
        " find f ",
        top_k=1,
        repo_id="repo-1",
        path_prefix="src/app",
        language="python",
        chunk_type="ts:function",
    )

    embedder.embed.assert_awaited_once_with(["find f"])
    qdrant.search.assert_awaited_once()
    search_kwargs = qdrant.search.await_args.kwargs
    assert search_kwargs["repo_id"] == "repo-1"
    assert search_kwargs["path_prefix"] == "src/app"
    assert search_kwargs["language"] == "python"
    assert search_kwargs["chunk_type"] == "ts:function"

    assert len(results) == 1
    result = results[0]
    assert result.text == "def f(): pass"
    assert result.citation.repo_id == "repo-1"
    assert result.citation.path == "src/app/main.py"
    assert result.citation.start_line == 1
    assert result.citation.end_line == 3
    assert result.citation.chunk_type == "ts:function"
    assert abs(result.citation.score - 0.91) < 1e-9


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_enforces_path_prefix_after_qdrant_response() -> None:
    embedder = AsyncMock()
    embedder.embed.return_value = [[0.0, 0.0, 0.0]]

    qdrant = AsyncMock()
    qdrant.search.return_value = [
        SimpleNamespace(payload=_payload(path="other/main.py"), score=0.99),
        SimpleNamespace(payload=_payload(path="src/app/ok.py", text="ok"), score=0.5),
    ]

    service = SearchService(qdrant=qdrant, embedder=embedder)
    results = await service.search("q", top_k=1, path_prefix="src/app")

    assert len(results) == 1
    assert results[0].citation.path == "src/app/ok.py"
