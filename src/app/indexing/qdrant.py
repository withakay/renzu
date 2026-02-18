"""Typed wrapper around Qdrant operations for indexing."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel, ConfigDict
from qdrant_client import AsyncQdrantClient, models

from app.config import get_settings

T = TypeVar("T")

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence


class ChunkPayload(BaseModel):
    """Payload schema for indexed code chunks."""

    model_config = ConfigDict(extra="forbid")

    repo_id: str
    path: str
    language: str
    chunk_type: str
    start_line: int
    end_line: int
    text: str
    content_hash: str
    symbol_scip: str | None = None


class ChunkPoint(BaseModel):
    """Input point for upsert operations."""

    id: str | int
    vector: list[float]
    payload: ChunkPayload


class QdrantClient:
    """Wrapper around AsyncQdrantClient with retries and schema helpers."""

    def __init__(
        self,
        url: str | None = None,
        collection_name: str | None = None,
        vector_size: int | None = None,
        *,
        retries: int = 3,
        retry_delay_seconds: float = 0.25,
        timeout_seconds: int = 5,
        client: Any | None = None,
    ) -> None:
        settings = get_settings()
        self.collection_name = collection_name or settings.qdrant_collection
        self.vector_size = vector_size or settings.qdrant_vector_size
        self.retries = retries
        self.retry_delay_seconds = retry_delay_seconds
        self._client: Any = client or AsyncQdrantClient(
            url=url or settings.qdrant_url,
            timeout=timeout_seconds,
        )

    async def _with_retry(self, operation: Callable[[], Awaitable[T]]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                return await operation()
            except Exception as exc:
                last_error = exc
                if attempt == self.retries:
                    raise
                await asyncio.sleep(self.retry_delay_seconds)

        raise RuntimeError("Retry loop ended unexpectedly") from last_error

    async def ensure_collection(self) -> None:
        """Create collection when it does not already exist."""

        response = await self._with_retry(self._client.get_collections)
        collections = getattr(response, "collections", [])
        collection_names = {getattr(collection, "name", "") for collection in collections}

        if self.collection_name in collection_names:
            return

        await self._with_retry(
            lambda: self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
        )

    async def upsert_points(self, repo_id: str, points: Sequence[ChunkPoint]) -> None:
        """Upsert points, enforcing the provided repo_id."""

        point_structs = [
            models.PointStruct(
                id=point.id,
                vector=point.vector,
                payload=point.payload.model_copy(update={"repo_id": repo_id}).model_dump(),
            )
            for point in points
        ]

        await self._with_retry(
            lambda: self._client.upsert(
                collection_name=self.collection_name,
                points=point_structs,
            )
        )

    async def delete_by_repo(self, repo_id: str) -> None:
        """Delete all points by repo identifier."""

        await self._with_retry(
            lambda: self._client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="repo_id",
                                match=models.MatchValue(value=repo_id),
                            )
                        ]
                    )
                ),
            )
        )

    async def search(
        self,
        query_vector: list[float],
        *,
        limit: int = 10,
        repo_id: str | None = None,
        path_prefix: str | None = None,
        language: str | None = None,
    ) -> list[models.ScoredPoint]:
        """Search points with optional payload filters."""

        filter_conditions: list[models.Condition] = []

        if repo_id:
            filter_conditions.append(
                models.FieldCondition(key="repo_id", match=models.MatchValue(value=repo_id))
            )
        if language:
            filter_conditions.append(
                models.FieldCondition(key="language", match=models.MatchValue(value=language))
            )
        if path_prefix:
            filter_conditions.append(
                models.FieldCondition(key="path", match=models.MatchText(text=path_prefix))
            )

        query_filter = models.Filter(must=filter_conditions) if filter_conditions else None
        return await self._with_retry(
            lambda: self._client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
            )
        )

    async def health_check(self) -> bool:
        """Return True when Qdrant is reachable."""

        try:
            await self._with_retry(self._client.get_collections)
            return True
        except Exception:
            return False


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Get a cached Qdrant client instance."""

    return QdrantClient()
