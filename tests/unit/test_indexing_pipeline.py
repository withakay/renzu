"""Unit tests for indexing pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from app.indexing.embedder import EmbeddingProvider
from app.indexing.pipeline import IndexingPipeline

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from app.indexing.qdrant import ChunkPoint


class StubQdrant:
    def __init__(self) -> None:
        self.ensure_calls = 0
        self.delete_calls: list[str] = []
        self.upsert_calls: list[tuple[str, list[ChunkPoint]]] = []

    async def ensure_collection(self) -> None:
        self.ensure_calls += 1

    async def delete_by_repo(self, repo_id: str) -> None:
        self.delete_calls.append(repo_id)

    async def upsert_points(self, repo_id: str, points: Sequence[ChunkPoint]) -> None:
        self.upsert_calls.append((repo_id, list(points)))


@dataclass(slots=True)
class FakeEmbedder(EmbeddingProvider):
    calls: int = 0

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return [[float(len(text)), 0.0, 1.0] for text in texts]


@pytest.mark.unit
@pytest.mark.asyncio
class TestIndexingPipeline:
    async def test_indexes_only_matching_languages(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
        (tmp_path / "src" / "main.js").write_text("function alpha() {}\n", encoding="utf-8")
        (tmp_path / "notes.txt").write_text("hello\n", encoding="utf-8")

        qdrant = StubQdrant()
        embedder = FakeEmbedder()
        pipeline = IndexingPipeline(qdrant=qdrant, embedder=embedder, delete_existing=True)

        result = await pipeline.index_repo(
            "repo-1",
            tmp_path,
            globs=["**/*"],
            languages=["python"],
        )

        assert qdrant.ensure_calls == 1
        assert qdrant.delete_calls == ["repo-1"]
        assert result.indexed_files == 1
        assert result.indexed_chunks >= 1
        assert sum(len(points) for _, points in qdrant.upsert_calls) == result.indexed_chunks
        assert embedder.calls >= 1

    async def test_dedupes_chunks_by_content_hash(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
        (tmp_path / "b.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

        qdrant = StubQdrant()
        pipeline = IndexingPipeline(
            qdrant=qdrant, embedder=FakeEmbedder(), dedupe_by_content_hash=True
        )

        result = await pipeline.index_repo(
            "repo-1", tmp_path, globs=["**/*.py"], languages=["python"]
        )

        assert result.discovered_files == 2
        assert result.indexed_chunks == 1
        assert result.skipped_chunks == 1

    async def test_per_file_decode_error_does_not_stop_other_files(self, tmp_path: Path) -> None:
        (tmp_path / "good.py").write_text("print('ok')\n", encoding="utf-8")
        (tmp_path / "bad.py").write_bytes(b"\xff\xfe\xfd")

        qdrant = StubQdrant()
        pipeline = IndexingPipeline(qdrant=qdrant, embedder=FakeEmbedder())

        result = await pipeline.index_repo(
            "repo-1", tmp_path, globs=["**/*.py"], languages=["python"]
        )

        assert result.indexed_files == 1
        assert any(error.relative_path == "bad.py" for error in result.errors)
