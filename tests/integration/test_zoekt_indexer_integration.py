"""Integration tests for ZoektIndexer behavior with real file walking."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.zoekt.indexer import ZoektIndexer

if TYPE_CHECKING:
    from pathlib import Path


class RecordingZoektClient:
    def __init__(self) -> None:
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_indexer_detects_incremental_file_changes(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    target = tmp_path / "src" / "main.py"
    target.write_text("print('a')\n", encoding="utf-8")

    client = RecordingZoektClient()
    indexer = ZoektIndexer(zoekt_client=client)

    first = await indexer.index_repo(repo_id="repo-1", path=tmp_path)
    assert first.state == "complete"
    assert first.changed_files == 1
    assert client.calls[0]["incremental"] is False
    assert client.calls[0]["changed_files"] == ["src/main.py"]

    target.write_text("print('b')\n", encoding="utf-8")
    second = await indexer.index_repo(repo_id="repo-1", path=tmp_path)

    assert second.state == "complete"
    assert second.changed_files == 1
    assert client.calls[1]["incremental"] is True
    assert client.calls[1]["changed_files"] == ["src/main.py"]
