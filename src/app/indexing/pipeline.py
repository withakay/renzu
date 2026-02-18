"""Indexing pipeline orchestration.

This module wires together discovery (FileWalker), chunking (Chunker), embedding
(EmbeddingProvider), and storage (QdrantClient).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

from app.indexing.chunker import Chunk, Chunker, TreeSitterChunker
from app.indexing.embedder import EmbeddingProvider, get_embedder
from app.indexing.qdrant import ChunkPayload, ChunkPoint, get_qdrant_client
from app.indexing.walker import FileInfo, FileWalker

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

T = TypeVar("T")

logger = logging.getLogger(__name__)


@runtime_checkable
class QdrantStore(Protocol):
    async def ensure_collection(self) -> None: ...

    async def delete_by_repo(self, repo_id: str) -> None: ...

    async def upsert_points(self, repo_id: str, points: Sequence[ChunkPoint]) -> None: ...


@dataclass(frozen=True, slots=True)
class IndexingFileError:
    relative_path: str
    error: str


@dataclass(frozen=True, slots=True)
class IndexingResult:
    repo_id: str
    root: Path
    discovered_files: int
    indexed_files: int
    indexed_chunks: int
    skipped_files: int
    skipped_chunks: int
    errors: tuple[IndexingFileError, ...]
    duration_seconds: float


class IndexingPipeline:
    """Orchestrate repository indexing.

    Dependencies are injectable for tests.
    """

    def __init__(
        self,
        *,
        qdrant: QdrantStore | None = None,
        embedder: EmbeddingProvider | None = None,
        walker: FileWalker | None = None,
        chunker: Chunker | None = None,
        upsert_batch_size: int = 64,
        delete_existing: bool = True,
        exclude_globs: list[str] | None = None,
        dedupe_by_content_hash: bool = True,
        log_every_files: int = 25,
        embed_retries: int = 3,
        embed_retry_delay_seconds: float = 0.5,
        upsert_retries: int = 3,
        upsert_retry_delay_seconds: float = 0.5,
    ) -> None:
        if upsert_batch_size <= 0:
            raise ValueError("upsert_batch_size must be > 0")
        if log_every_files <= 0:
            raise ValueError("log_every_files must be > 0")
        if embed_retries <= 0:
            raise ValueError("embed_retries must be > 0")
        if embed_retry_delay_seconds < 0:
            raise ValueError("embed_retry_delay_seconds must be >= 0")
        if upsert_retries <= 0:
            raise ValueError("upsert_retries must be > 0")
        if upsert_retry_delay_seconds < 0:
            raise ValueError("upsert_retry_delay_seconds must be >= 0")

        self._qdrant = qdrant or get_qdrant_client()
        self._embedder = embedder or get_embedder()
        self._walker = walker
        self._chunker = chunker or TreeSitterChunker()
        self._upsert_batch_size = upsert_batch_size
        self._delete_existing = delete_existing
        self._exclude_globs = exclude_globs or [
            ".git/**",
            ".venv/**",
            "**/__pycache__/**",
        ]
        self._dedupe_by_content_hash = dedupe_by_content_hash
        self._log_every_files = log_every_files
        self._embed_retries = embed_retries
        self._embed_retry_delay_seconds = embed_retry_delay_seconds
        self._upsert_retries = upsert_retries
        self._upsert_retry_delay_seconds = upsert_retry_delay_seconds

    async def _with_retry(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        retries: int,
        delay_seconds: float,
        context: str,
    ) -> T:
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                return await operation()
            except Exception as exc:
                last_error = exc
                if attempt >= retries:
                    raise
                logger.warning(
                    "Retrying operation context=%s attempt=%d/%d error=%s",
                    context,
                    attempt,
                    retries,
                    str(exc),
                )
                if delay_seconds:
                    await asyncio.sleep(delay_seconds)

        raise RuntimeError("Retry loop ended unexpectedly") from last_error

    def _build_walker(self, *, globs: list[str] | None) -> FileWalker:
        if self._walker is not None:
            return self._walker
        include = globs or ["**/*"]
        return FileWalker(include=include, exclude=self._exclude_globs)

    def _point_id(self, *, info: FileInfo, chunk_hash: str, start_line: int, end_line: int) -> str:
        return f"{info.relative_path}:{start_line}:{end_line}:{chunk_hash}"

    async def index_repo(
        self,
        repo_id: str,
        path: Path | str,
        globs: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> IndexingResult:
        """Index a repository directory.

        Args:
            repo_id: Logical repository identifier.
            path: Root directory to walk.
            globs: Include globs for files (defaults to **/*).
            languages: Optional allowlist of detected languages.
        """

        start = time.monotonic()

        root = Path(path).expanduser().resolve()
        walker = self._build_walker(globs=globs)

        allowlist: set[str] | None = None
        if languages is not None:
            normalized = [language.strip().lower() for language in languages if language.strip()]
            allowlist = set(normalized)

        await self._qdrant.ensure_collection()
        if self._delete_existing:
            await self._qdrant.delete_by_repo(repo_id)

        discovered_files = 0
        indexed_files = 0
        indexed_chunks = 0
        skipped_files = 0
        skipped_chunks = 0
        errors: list[IndexingFileError] = []

        seen_hashes: set[str] = set()
        buffer: list[ChunkPoint] = []

        async def flush(*, context: str) -> None:
            nonlocal indexed_chunks
            if not buffer:
                return

            points = list(buffer)
            await self._with_retry(
                lambda: self._qdrant.upsert_points(repo_id, points),
                retries=self._upsert_retries,
                delay_seconds=self._upsert_retry_delay_seconds,
                context=context,
            )
            indexed_chunks += len(buffer)
            buffer.clear()

        logger.info(
            "Indexing start repo_id=%s root=%s globs=%s languages=%s",
            repo_id,
            str(root),
            globs,
            languages,
        )

        for info in walker.walk(root):
            discovered_files += 1
            if discovered_files % self._log_every_files == 0:
                logger.info(
                    "Indexing progress repo_id=%s processed_files=%d indexed_files=%d indexed_chunks=%d skipped_chunks=%d errors=%d",
                    repo_id,
                    discovered_files,
                    indexed_files,
                    indexed_chunks,
                    skipped_chunks,
                    len(errors),
                )

            language = (info.language or "text").strip().lower()
            if allowlist is not None and language not in allowlist:
                skipped_files += 1
                continue

            try:
                content = info.path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(IndexingFileError(relative_path=info.relative_path, error=str(exc)))
                skipped_files += 1
                continue
            except OSError as exc:
                errors.append(IndexingFileError(relative_path=info.relative_path, error=str(exc)))
                skipped_files += 1
                continue

            try:
                chunks: list[Chunk] = list(self._chunker.chunk(content, language=language))
            except Exception as exc:
                errors.append(IndexingFileError(relative_path=info.relative_path, error=str(exc)))
                skipped_files += 1
                continue

            if not chunks:
                skipped_files += 1
                continue

            kept_chunks: list[Chunk] = []
            for chunk in chunks:
                if self._dedupe_by_content_hash:
                    if chunk.content_hash in seen_hashes:
                        skipped_chunks += 1
                        continue
                    seen_hashes.add(chunk.content_hash)
                kept_chunks.append(chunk)

            if not kept_chunks:
                skipped_files += 1
                continue

            try:
                texts = [chunk.text for chunk in kept_chunks]
                vectors: list[list[float]] = await self._with_retry(
                    lambda texts=texts: self._embedder.embed(texts),
                    retries=self._embed_retries,
                    delay_seconds=self._embed_retry_delay_seconds,
                    context=f"embed:{info.relative_path}",
                )
            except Exception as exc:
                errors.append(IndexingFileError(relative_path=info.relative_path, error=str(exc)))
                skipped_files += 1
                continue

            if len(vectors) != len(kept_chunks):
                errors.append(
                    IndexingFileError(
                        relative_path=info.relative_path,
                        error="Embedding provider returned unexpected number of vectors",
                    )
                )
                skipped_files += 1
                continue

            indexed_files += 1
            for chunk, vector in zip(kept_chunks, vectors, strict=True):
                payload = ChunkPayload(
                    repo_id=repo_id,
                    path=info.relative_path,
                    language=language,
                    chunk_type=chunk.chunk_type,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    text=chunk.text,
                    content_hash=chunk.content_hash,
                    symbol_scip=chunk.symbol_scip,
                )
                buffer.append(
                    ChunkPoint(
                        id=self._point_id(
                            info=info,
                            chunk_hash=chunk.content_hash,
                            start_line=chunk.start_line,
                            end_line=chunk.end_line,
                        ),
                        vector=list(vector),
                        payload=payload,
                    )
                )

                if len(buffer) >= self._upsert_batch_size:
                    try:
                        await flush(context=f"upsert:{info.relative_path}")
                    except Exception as exc:
                        errors.append(
                            IndexingFileError(relative_path=info.relative_path, error=str(exc))
                        )
                        buffer.clear()
                        break

        try:
            await flush(context="upsert:(final_flush)")
        except Exception as exc:
            errors.append(IndexingFileError(relative_path="(flush)", error=str(exc)))
            buffer.clear()

        duration_seconds = time.monotonic() - start
        logger.info(
            "Indexing done repo_id=%s discovered_files=%d indexed_files=%d indexed_chunks=%d skipped_files=%d skipped_chunks=%d errors=%d duration_seconds=%.3f",
            repo_id,
            discovered_files,
            indexed_files,
            indexed_chunks,
            skipped_files,
            skipped_chunks,
            len(errors),
            duration_seconds,
        )

        return IndexingResult(
            repo_id=repo_id,
            root=root,
            discovered_files=discovered_files,
            indexed_files=indexed_files,
            indexed_chunks=indexed_chunks,
            skipped_files=skipped_files,
            skipped_chunks=skipped_chunks,
            errors=tuple(errors),
            duration_seconds=duration_seconds,
        )
