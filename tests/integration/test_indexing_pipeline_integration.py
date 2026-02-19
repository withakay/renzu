"""Integration-style tests for the indexing pipeline.

These tests exercise the default FileWalker + Chunker + IndexingPipeline wiring
without requiring external services.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from app.indexing.pipeline import IndexingPipeline

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from app.indexing.qdrant import ChunkPoint


class MemoryQdrant:
    def __init__(self) -> None:
        self.ensure_calls = 0
        self.deleted: list[str] = []
        self.upserts: list[tuple[str, list[ChunkPoint]]] = []

    async def ensure_collection(self) -> None:
        self.ensure_calls += 1

    async def delete_by_repo(self, repo_id: str) -> None:
        self.deleted.append(repo_id)

    async def upsert_points(self, repo_id: str, points: Sequence[ChunkPoint]) -> None:
        self.upserts.append((repo_id, list(points)))


@dataclass(slots=True)
class FlakyEmbedder:
    fail_first: bool = True
    calls: int = 0

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        if self.fail_first:
            self.fail_first = False
            raise RuntimeError("temporary embedding failure")
        return [[float(len(text)), 0.0, 1.0] for text in texts]


@pytest.mark.integration
@pytest.mark.unit
@pytest.mark.asyncio
async def test_indexes_repo_end_to_end_with_retry_and_dedupe(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (tmp_path / "src" / "b.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    qdrant = MemoryQdrant()
    embedder = FlakyEmbedder()
    pipeline = IndexingPipeline(
        qdrant=qdrant,
        embedder=embedder,
        delete_existing=True,
        embed_retries=2,
        embed_retry_delay_seconds=0.0,
        dedupe_by_content_hash=True,
    )

    result = await pipeline.index_repo(
        "repo-1",
        tmp_path,
        globs=["**/*.py"],
        languages=["python"],
    )

    assert qdrant.ensure_calls == 1
    assert qdrant.deleted == ["repo-1"]
    assert embedder.calls == 2

    assert result.discovered_files == 2
    assert result.indexed_chunks == 1
    assert result.skipped_chunks == 1
    assert result.errors == ()
