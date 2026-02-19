"""Embedding provider abstractions.

This module defines a small async interface for generating embeddings, plus a
default OpenAI-backed implementation and an in-memory content-hash cache.
"""

from __future__ import annotations

import abc
import asyncio
import hashlib
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Protocol, cast

import httpx

from app.config import Settings, get_settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class RateLimiter(Protocol):
    async def wait(self) -> None: ...


class EmbeddingProvider(abc.ABC):
    """Abstract base class for embedding providers."""

    @property
    def namespace(self) -> str:
        """Namespace used for cache key derivation."""

        return self.__class__.__name__

    @abc.abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for each input text, in order."""


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _chunked(values: list[str], *, size: int) -> list[list[str]]:
    if size <= 0:
        raise ValueError("Batch size must be >= 1")
    if not values:
        return []
    return [values[i : i + size] for i in range(0, len(values), size)]


class AsyncRateLimiter:
    """Simple async rate limiter enforcing a minimum inter-request interval."""

    def __init__(
        self,
        *,
        requests_per_second: float,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0")

        self._min_interval_seconds = 1.0 / requests_per_second
        self._clock = clock
        self._sleeper = sleeper
        self._lock = asyncio.Lock()
        self._next_allowed_at = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = float(self._clock())
            wait_for = self._next_allowed_at - now
            if wait_for > 0:
                await self._sleeper(wait_for)
                now = float(self._clock())

            self._next_allowed_at = max(self._next_allowed_at, now) + self._min_interval_seconds


def _coerce_vector(raw: Any, *, expected_size: int) -> list[float]:
    if not isinstance(raw, list):
        raise TypeError("Embedding vector must be a list")

    raw_values = cast("list[object]", raw)
    vector: list[float] = []
    for value in raw_values:
        if isinstance(value, (int, float)):
            vector.append(float(value))
            continue
        raise TypeError("Embedding vector elements must be numbers")
    if len(vector) != expected_size:
        raise ValueError(f"Expected embedding size {expected_size}, got {len(vector)}")
    return vector


@dataclass(frozen=True, slots=True)
class OpenAIEmbedder(EmbeddingProvider):
    """OpenAI embeddings API implementation.

    Uses the `POST /v1/embeddings` endpoint.
    """

    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    vector_size: int | None = None
    send_dimensions: bool = False
    timeout_seconds: float = 30.0
    max_batch_size: int = 128
    requests_per_second: float | None = None
    rate_limiter: RateLimiter | None = None
    client: httpx.AsyncClient | None = None

    def __post_init__(self) -> None:
        if self.rate_limiter is None and self.requests_per_second is not None:
            object.__setattr__(
                self,
                "rate_limiter",
                AsyncRateLimiter(requests_per_second=self.requests_per_second),
            )

    @property
    def namespace(self) -> str:
        settings = get_settings()
        model = self.model or settings.openai_embedding_model
        base_url = self.base_url or settings.openai_base_url
        vector_size = (
            self.vector_size or settings.embedding_vector_size or settings.qdrant_vector_size
        )
        return f"openai:{base_url}:{model}:{vector_size}"

    def _get_rate_limiter(self) -> RateLimiter | None:
        return self.rate_limiter

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        batches = _chunked(list(texts), size=self.max_batch_size)
        limiter = self._get_rate_limiter()
        vectors: list[list[float]] = []
        for batch in batches:
            if limiter is not None:
                await limiter.wait()
            vectors.extend(await self._embed_batch(batch))

        return vectors

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        settings = get_settings()

        model = self.model or settings.openai_embedding_model
        api_key = self.api_key or settings.openai_api_key
        if not api_key:
            raise RuntimeError("OpenAI API key is not configured")

        base_url = self.base_url or settings.openai_base_url
        expected_size = (
            self.vector_size or settings.embedding_vector_size or settings.qdrant_vector_size
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": model,
            "input": texts,
        }

        if self.send_dimensions and model.startswith("text-embedding-3"):
            payload["dimensions"] = expected_size

        if self.client is None:
            async with httpx.AsyncClient(base_url=base_url, timeout=self.timeout_seconds) as client:
                response = await client.post("/embeddings", headers=headers, json=payload)
        else:
            response = await self.client.post("/embeddings", headers=headers, json=payload)

        response.raise_for_status()

        raw_data = response.json()
        if not isinstance(raw_data, dict):
            raise TypeError("OpenAI embeddings response must be an object")
        data = cast("dict[str, Any]", raw_data)

        raw_items = data.get("data")
        if not isinstance(raw_items, list):
            raise TypeError("OpenAI embeddings response missing 'data' list")

        vectors_by_index: dict[int, list[float]] = {}
        for item in cast("list[object]", raw_items):
            if not isinstance(item, dict):
                continue

            item_dict = cast("dict[str, Any]", item)
            index = item_dict.get("index")
            embedding = item_dict.get("embedding")
            if not isinstance(index, int):
                continue
            vectors_by_index[index] = _coerce_vector(embedding, expected_size=expected_size)

        vectors: list[list[float]] = []
        for idx in range(len(texts)):
            if idx not in vectors_by_index:
                raise RuntimeError(f"OpenAI embeddings response missing index {idx}")
            vectors.append(vectors_by_index[idx])

        return vectors


class CacheEmbedder(EmbeddingProvider):
    """Embedding provider wrapper with in-memory content-hash caching."""

    def __init__(
        self,
        provider: EmbeddingProvider,
        *,
        cache: dict[str, list[float]] | None = None,
    ) -> None:
        self._provider = provider
        self._cache: dict[str, list[float]] = cache or {}

    @property
    def namespace(self) -> str:
        return self._provider.namespace

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        hashes = [f"{self._provider.namespace}:{_content_hash(text)}" for text in texts]
        missing_texts: list[str] = []
        missing_hashes: list[str] = []

        for text, digest in zip(texts, hashes, strict=True):
            if digest in self._cache:
                continue
            missing_texts.append(text)
            missing_hashes.append(digest)

        if missing_texts:
            vectors = await self._provider.embed(missing_texts)
            if len(vectors) != len(missing_texts):
                raise RuntimeError("Embedding provider returned unexpected number of vectors")
            for digest, vector in zip(missing_hashes, vectors, strict=True):
                self._cache[digest] = list(vector)

        return [self._cache[digest] for digest in hashes]


def create_embedder(
    *,
    settings: Settings | None = None,
    client: httpx.AsyncClient | None = None,
    cache: dict[str, list[float]] | None = None,
) -> EmbeddingProvider:
    """Create the configured embedding provider instance."""

    resolved = settings or get_settings()
    provider = (getattr(resolved, "embedding_provider", None) or "openai").lower()

    vector_size = resolved.embedding_vector_size or resolved.qdrant_vector_size
    if provider == "openai":
        embedder: EmbeddingProvider = OpenAIEmbedder(
            model=resolved.openai_embedding_model,
            api_key=resolved.openai_api_key,
            base_url=resolved.openai_base_url,
            vector_size=vector_size,
            send_dimensions=resolved.embedding_vector_size is not None,
            timeout_seconds=resolved.openai_timeout_seconds,
            max_batch_size=resolved.embedding_max_batch_size,
            requests_per_second=resolved.embedding_requests_per_second,
            client=client,
        )
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")

    cache_enabled = bool(getattr(resolved, "embedding_cache_enabled", True))
    if cache_enabled:
        embedder = CacheEmbedder(embedder, cache=cache)

    return embedder


@lru_cache
def get_embedder() -> EmbeddingProvider:
    """Return the default embedding provider instance.

    The default provider is OpenAI-backed with an in-memory cache wrapper.
    """

    return create_embedder()
