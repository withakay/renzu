"""Zoekt repository index orchestration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from app.config import get_settings
from app.indexing.walker import FileWalker


@dataclass(frozen=True, slots=True)
class IndexStatus:
    repo_id: str
    state: str
    indexed_files: int = 0
    changed_files: int = 0
    error: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


class ZoektIndexClient(Protocol):
    async def index_repo(
        self,
        *,
        repo_id: str,
        root: Path,
        changed_files: list[str],
        incremental: bool,
    ) -> None: ...


class QdrantIndexPipeline(Protocol):
    async def index_repo(self, repo_id: str, path: Path | str) -> object: ...


class ZoektIndexer:
    def __init__(
        self,
        *,
        zoekt_client: ZoektIndexClient | None,
        walker: FileWalker | None = None,
        qdrant_pipeline: QdrantIndexPipeline | None = None,
        enabled: bool = True,
    ) -> None:
        self._zoekt_client = zoekt_client
        self._walker = walker or FileWalker(include=["**/*"], exclude=[".git/**", ".venv/**"])
        self._qdrant_pipeline = qdrant_pipeline
        self._enabled = enabled
        self._status_by_repo: dict[str, IndexStatus] = {}
        self._snapshot_by_repo: dict[str, dict[str, datetime]] = {}

    async def index_repo(
        self,
        *,
        repo_id: str,
        path: Path | str,
        parallel: bool = False,
    ) -> IndexStatus:
        if not self._enabled or self._zoekt_client is None:
            status = IndexStatus(
                repo_id=repo_id,
                state="complete",
                indexed_files=0,
                changed_files=0,
                error=None,
            )
            self._status_by_repo[repo_id] = status
            return status

        root = Path(path).expanduser().resolve()
        self._status_by_repo[repo_id] = IndexStatus(repo_id=repo_id, state="pending")

        try:
            current_snapshot = self._scan_snapshot(root)
            previous_snapshot = self._snapshot_by_repo.get(repo_id, {})

            changed_files: list[str] = []
            for relative_path, modified_at in current_snapshot.items():
                previous_modified = previous_snapshot.get(relative_path)
                if previous_modified != modified_at:
                    changed_files.append(relative_path)

            incremental = bool(previous_snapshot)
            await self._run_indexing(
                repo_id=repo_id,
                root=root,
                changed_files=changed_files,
                incremental=incremental,
                parallel=parallel,
            )

            self._snapshot_by_repo[repo_id] = current_snapshot
            status = IndexStatus(
                repo_id=repo_id,
                state="complete",
                indexed_files=len(current_snapshot),
                changed_files=len(changed_files),
            )
            self._status_by_repo[repo_id] = status
            return status
        except Exception as exc:
            status = IndexStatus(repo_id=repo_id, state="error", error=str(exc))
            self._status_by_repo[repo_id] = status
            return status

    def index_status(self, repo_id: str) -> IndexStatus:
        return self._status_by_repo.get(repo_id, IndexStatus(repo_id=repo_id, state="pending"))

    def _scan_snapshot(self, root: Path) -> dict[str, datetime]:
        snapshot: dict[str, datetime] = {}
        for file_info in self._walker.walk(root):
            snapshot[file_info.relative_path] = file_info.modified_at
        return snapshot

    async def _run_indexing(
        self,
        *,
        repo_id: str,
        root: Path,
        changed_files: list[str],
        incremental: bool,
        parallel: bool,
    ) -> None:
        if self._zoekt_client is None:
            return

        client = self._zoekt_client
        zoekt_task = client.index_repo(
            repo_id=repo_id,
            root=root,
            changed_files=changed_files,
            incremental=incremental,
        )

        if parallel and self._qdrant_pipeline is not None:
            await asyncio.gather(
                zoekt_task,
                self._qdrant_pipeline.index_repo(repo_id, root),
            )
            return

        await zoekt_task


def get_zoekt_indexer() -> ZoektIndexer:
    from app.zoekt.client import get_zoekt_client

    settings = get_settings()
    return ZoektIndexer(
        zoekt_client=get_zoekt_client(),
        enabled=settings.zoekt_enabled,
    )
