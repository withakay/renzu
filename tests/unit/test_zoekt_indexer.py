"""Unit tests for ZoektIndexer."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.zoekt.indexer import ZoektIndexer


class StubZoektClient:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict[str, object]] = []

    async def index_repo(
        self,
        *,
        repo_id: str,
        root: Path,
        changed_files: list[str],
        incremental: bool,
    ) -> None:
        self.calls.append(
            {
                "repo_id": repo_id,
                "root": root,
                "changed_files": list(changed_files),
                "incremental": incremental,
            }
        )
        if self.fail:
            raise RuntimeError("index failed")


class StubQdrantPipeline:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Path]] = []

    async def index_repo(self, repo_id: str, path: Path | str) -> object:
        self.calls.append((repo_id, Path(path)))
        return object()


@pytest.mark.unit
@pytest.mark.asyncio
class TestZoektIndexer:
    async def test_disabled_indexer_is_no_op(self, tmp_path: Path) -> None:
        client = StubZoektClient()
        indexer = ZoektIndexer(zoekt_client=client, enabled=False)

        status = await indexer.index_repo(repo_id="repo-1", path=tmp_path)

        assert status.state == "complete"
        assert status.indexed_files == 0
        assert status.changed_files == 0
        assert client.calls == []

    async def test_indexes_repo_and_tracks_incremental_changes(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("print('a')\n", encoding="utf-8")
        client = StubZoektClient()
        indexer = ZoektIndexer(zoekt_client=client)

        first_status = await indexer.index_repo(repo_id="repo-1", path=tmp_path)

        assert first_status.state == "complete"
        assert first_status.indexed_files == 1
        assert first_status.changed_files == 1
        assert client.calls[0]["incremental"] is False
        assert client.calls[0]["changed_files"] == ["a.py"]

        second_status = await indexer.index_repo(repo_id="repo-1", path=tmp_path)

        assert second_status.state == "complete"
        assert second_status.changed_files == 0
        assert client.calls[1]["incremental"] is True
        assert client.calls[1]["changed_files"] == []

    async def test_parallel_mode_runs_qdrant_pipeline(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("print('a')\n", encoding="utf-8")
        client = StubZoektClient()
        qdrant = StubQdrantPipeline()
        indexer = ZoektIndexer(zoekt_client=client, qdrant_pipeline=qdrant)

        status = await indexer.index_repo(repo_id="repo-1", path=tmp_path, parallel=True)

        assert status.state == "complete"
        assert len(client.calls) == 1
        assert qdrant.calls == [("repo-1", tmp_path.resolve())]

    async def test_error_state_when_indexing_fails(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("print('a')\n", encoding="utf-8")
        client = StubZoektClient(fail=True)
        indexer = ZoektIndexer(zoekt_client=client)

        status = await indexer.index_repo(repo_id="repo-1", path=tmp_path)

        assert status.state == "error"
        assert status.error is not None
        assert "index failed" in status.error

    async def test_index_status_defaults_pending(self) -> None:
        indexer = ZoektIndexer(zoekt_client=StubZoektClient())

        status = indexer.index_status("repo-unknown")

        assert status.state == "pending"
