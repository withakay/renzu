"""Semantic search over indexed code chunks."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Protocol, cast

from pydantic import BaseModel, ConfigDict, Field

from app.indexing.embedder import EmbeddingProvider, get_embedder
from app.indexing.qdrant import ChunkPayload, get_qdrant_client

if TYPE_CHECKING:
    from qdrant_client import models


class QdrantSearch(Protocol):
    async def search(
        self,
        query_vector: list[float],
        *,
        limit: int = 10,
        repo_id: str | None = None,
        path_prefix: str | None = None,
        language: str | None = None,
        chunk_type: str | None = None,
    ) -> list[models.ScoredPoint]: ...


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    start_line: int
    end_line: int
    chunk_type: str = Field(min_length=1)
    score: float
    language: str | None = None
    symbol_scip: str | None = None


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    citation: Citation


class SearchService:
    """Perform semantic search against Qdrant using the configured embedder."""

    def __init__(
        self,
        *,
        qdrant: QdrantSearch | None = None,
        embedder: EmbeddingProvider | None = None,
        default_top_k: int = 10,
        max_top_k: int = 100,
        overfetch_multiplier: int = 4,
        overfetch_max: int = 200,
    ) -> None:
        if default_top_k <= 0:
            raise ValueError("default_top_k must be > 0")
        if max_top_k <= 0:
            raise ValueError("max_top_k must be > 0")
        if overfetch_multiplier <= 0:
            raise ValueError("overfetch_multiplier must be > 0")
        if overfetch_max <= 0:
            raise ValueError("overfetch_max must be > 0")

        self._qdrant = qdrant or get_qdrant_client()
        self._embedder = embedder or get_embedder()
        self._default_top_k = default_top_k
        self._max_top_k = max_top_k
        self._overfetch_multiplier = overfetch_multiplier
        self._overfetch_max = overfetch_max

    @staticmethod
    def _coerce_payload(payload: Any) -> ChunkPayload | None:
        if not isinstance(payload, dict):
            return None
        try:
            return ChunkPayload.model_validate(cast("dict[str, Any]", payload))
        except Exception:
            return None

    async def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
        repo_id: str | None = None,
        path_prefix: str | None = None,
        language: str | None = None,
        chunk_type: str | None = None,
    ) -> list[SearchResult]:
        """Search for code chunks semantically similar to the query."""

        query_text = query.strip()
        if not query_text:
            raise ValueError("query must not be empty")

        limit = self._default_top_k if top_k is None else top_k
        if limit <= 0:
            raise ValueError("top_k must be > 0")
        if limit > self._max_top_k:
            raise ValueError(f"top_k must be <= {self._max_top_k}")

        vectors = await self._embedder.embed([query_text])
        if len(vectors) != 1:
            raise RuntimeError("Embedding provider returned unexpected number of vectors")
        query_vector = list(vectors[0])

        fetch_limit = min(max(limit * self._overfetch_multiplier, limit), self._overfetch_max)
        raw_points = await self._qdrant.search(
            query_vector,
            limit=fetch_limit,
            repo_id=repo_id,
            path_prefix=path_prefix,
            language=language,
            chunk_type=chunk_type,
        )

        normalized_prefix = path_prefix.strip() if path_prefix else None
        results: list[SearchResult] = []

        for point in raw_points:
            payload = self._coerce_payload(getattr(point, "payload", None))
            if payload is None:
                continue
            if normalized_prefix and not payload.path.startswith(normalized_prefix):
                continue

            citation = Citation(
                repo_id=payload.repo_id,
                path=payload.path,
                start_line=payload.start_line,
                end_line=payload.end_line,
                chunk_type=payload.chunk_type,
                score=float(getattr(point, "score", 0.0)),
                language=payload.language,
                symbol_scip=payload.symbol_scip,
            )
            results.append(SearchResult(text=payload.text, citation=citation))
            if len(results) >= limit:
                break

        return results


@lru_cache
def get_search_service() -> SearchService:
    return SearchService()
