"""Embedding provider abstractions.

This module defines a small async interface for generating embeddings, plus a
default OpenAI-backed implementation and an in-memory content-hash cache.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Protocol, cast, runtime_checkable

import httpx

from app.config import get_settings


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for each input text, in order."""

        ...


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


@dataclass(slots=True)
class OpenAIEmbedder:
    """OpenAI embeddings API implementation.

    Uses the `POST /v1/embeddings` endpoint.
    """

    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    vector_size: int | None = None
    batch_size: int | None = None
    min_interval_seconds: float | None = None
    timeout_seconds: float = 30.0
    client: httpx.AsyncClient | None = None

    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _last_request_monotonic: float | None = field(default=None, init=False, repr=False)

    async def _sleep_if_needed(self, *, min_interval_seconds: float) -> None:
        if min_interval_seconds <= 0:
            return

        last = self._last_request_monotonic
        if last is None:
            return

        now = time.monotonic()
        delta = now - last
        remaining = min_interval_seconds - delta
        if remaining > 0:
            await asyncio.sleep(remaining)

    async def _embed_batch(
        self,
        texts: list[str],
        *,
        model: str,
        api_key: str,
        base_url: str,
        expected_size: int,
        min_interval_seconds: float,
    ) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "input": texts,
        }

        async with self._lock:
            await self._sleep_if_needed(min_interval_seconds=min_interval_seconds)
            if self.client is None:
                async with httpx.AsyncClient(
                    base_url=base_url, timeout=self.timeout_seconds
                ) as client:
                    response = await client.post("/embeddings", headers=headers, json=payload)
            else:
                response = await self.client.post("/embeddings", headers=headers, json=payload)
            self._last_request_monotonic = time.monotonic()

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

    async def embed(self, texts: list[str]) -> list[list[float]]:
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

        batch_size = self.batch_size or settings.embedding_batch_size
        if batch_size <= 0:
            raise ValueError("embedding_batch_size must be > 0")

        min_interval_seconds = self.min_interval_seconds
        if min_interval_seconds is None:
            min_interval_seconds = settings.embedding_min_interval_seconds

        if len(texts) <= batch_size:
            return await self._embed_batch(
                texts,
                model=model,
                api_key=api_key,
                base_url=base_url,
                expected_size=expected_size,
                min_interval_seconds=min_interval_seconds,
            )

        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(
                await self._embed_batch(
                    batch,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    expected_size=expected_size,
                    min_interval_seconds=min_interval_seconds,
                )
            )

        return vectors


class CacheEmbedder:
    """Embedding provider wrapper with in-memory content-hash caching."""

    def __init__(
        self,
        provider: EmbeddingProvider,
        *,
        cache: dict[str, list[float]] | None = None,
    ) -> None:
        self._provider = provider
        self._cache: dict[str, list[float]] = cache or {}

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        hashes = [_content_hash(text) for text in texts]
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


@lru_cache
def get_embedder() -> EmbeddingProvider:
    """Return the default embedding provider instance.

    The default provider is OpenAI-backed with an in-memory cache wrapper.
    """

    settings = get_settings()

    provider_name = settings.embedding_provider.strip().lower()
    match provider_name:
        case "openai":
            provider: EmbeddingProvider = OpenAIEmbedder()
        case _:
            raise RuntimeError(f"Unsupported embedding provider: {settings.embedding_provider}")

    if settings.embedding_cache_enabled:
        provider = CacheEmbedder(provider)

    return provider
