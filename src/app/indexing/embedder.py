"""Embedding provider abstractions.

This module defines a small async interface for generating embeddings, plus a
default OpenAI-backed implementation and an in-memory content-hash cache.
"""

from __future__ import annotations

import abc
import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Protocol, cast

import httpx

from app.config import Settings, get_settings


class RateLimiter(Protocol):
    async def wait(self) -> None: ...


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for each input text, in order."""
        ...


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _coerce_vector(raw: Any, *, expected_size: int | None) -> list[float]:
    if not isinstance(raw, list):
        raise TypeError("Embedding vector must be a list")

    raw_values = cast("list[object]", raw)
    vector: list[float] = []
    for value in raw_values:
        if isinstance(value, (int, float)):
            vector.append(float(value))
            continue
        raise TypeError("Embedding vector elements must be numbers")
    if expected_size is not None and len(vector) != expected_size:
        raise ValueError(f"Expected embedding size {expected_size}, got {len(vector)}")
    return vector


@dataclass(slots=True)
class OpenAIEmbedder(EmbeddingProvider):
    """OpenAI embeddings API implementation.

    Uses the `POST /v1/embeddings` endpoint.
    """

    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    vector_size: int | None = None
    send_dimensions: bool = False
    batch_size: int | None = None
    min_interval_seconds: float | None = None
    timeout_seconds: float = 30.0
    max_batch_size: int = 128
    requests_per_second: float | None = None
    send_dimensions: bool = False
    rate_limiter: RateLimiter | None = None
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
        payload: dict[str, Any] = {
            "model": model,
            "input": texts,
        }
        if self.send_dimensions:
            payload["dimensions"] = expected_size

        async with self._lock:
            if self.rate_limiter is not None:
                await self.rate_limiter.wait()
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

        batch_size = self.batch_size or self.max_batch_size or settings.embedding_batch_size
        if batch_size <= 0:
            raise ValueError("embedding_batch_size must be > 0")

        min_interval_seconds = self.min_interval_seconds
        if min_interval_seconds is None:
            if self.requests_per_second:
                min_interval_seconds = 1.0 / self.requests_per_second
            else:
                min_interval_seconds = settings.embedding_min_interval_seconds

        if min_interval_seconds < 0:
            raise ValueError("min_interval_seconds must be >= 0")

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


@dataclass(slots=True)
class OllamaEmbedder(EmbeddingProvider):
    """Ollama embeddings API implementation.

    Uses the local Ollama HTTP API (`POST /api/embed`).
    """

    model: str | None = None
    base_url: str | None = None
    vector_size: int | None = None
    batch_size: int | None = None
    min_interval_seconds: float | None = None
    timeout_seconds: float = 30.0
    client: httpx.AsyncClient | None = None

    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _last_request_monotonic: float | None = field(default=None, init=False, repr=False)
    _verified_models: set[str] = field(default_factory=set, init=False, repr=False)
    _verify_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

    @staticmethod
    def _model_matches_tag(model: str, tag: str) -> bool:
        if model == tag:
            return True
        # Ollama commonly reports tags like "nomic-embed-text:latest".
        return bool(":" in tag and model == tag.split(":", 1)[0])

    async def health_check(self) -> None:
        """Raise a descriptive error if Ollama is unreachable."""

        settings = get_settings()
        base_url = self.base_url or settings.ollama_url

        try:
            if self.client is None:
                async with httpx.AsyncClient(base_url=base_url, timeout=2.0) as client:
                    response = await client.get("/api/version")
            else:
                response = await self.client.get("/api/version")
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"Timed out connecting to Ollama at {base_url}") from exc
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Ollama is not reachable at {base_url} (is the server running?)"
            ) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Failed to check Ollama health at {base_url}") from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise RuntimeError(
                f"Ollama returned HTTP {status} from {base_url}/api/version"
            ) from exc

    async def _ensure_model_available(self, *, model: str, base_url: str) -> None:
        key = f"{base_url}::{model}"
        if key in self._verified_models:
            return

        async with self._verify_lock:
            if key in self._verified_models:
                return

            try:
                if self.client is None:
                    async with httpx.AsyncClient(base_url=base_url, timeout=2.0) as client:
                        response = await client.get("/api/tags")
                else:
                    response = await self.client.get("/api/tags")
            except httpx.TimeoutException as exc:
                raise RuntimeError(f"Timed out connecting to Ollama at {base_url}") from exc
            except httpx.ConnectError as exc:
                raise RuntimeError(
                    f"Ollama is not reachable at {base_url} (is the server running?)"
                ) from exc
            except httpx.HTTPError as exc:
                raise RuntimeError(f"Failed to query Ollama models at {base_url}") from exc

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                raise RuntimeError(
                    f"Ollama returned HTTP {status} from {base_url}/api/tags"
                ) from exc

            raw_data = response.json()
            if not isinstance(raw_data, dict):
                raise TypeError("Ollama tags response must be an object")
            data = cast("dict[str, Any]", raw_data)
            raw_models = data.get("models")
            if not isinstance(raw_models, list):
                raise TypeError("Ollama tags response missing 'models' list")

            available: list[str] = []
            for item in cast("list[object]", raw_models):
                if not isinstance(item, dict):
                    continue
                name = cast("dict[str, Any]", item).get("name")
                if isinstance(name, str) and name:
                    available.append(name)

            if not any(self._model_matches_tag(model, tag) for tag in available):
                raise RuntimeError(
                    "Ollama model is not available locally: "
                    f"{model}. Run `ollama pull {model}` (or set OLLAMA_EMBEDDING_MODEL to an installed model)."
                )

            self._verified_models.add(key)

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
        base_url: str,
        expected_size: int | None,
        min_interval_seconds: float,
    ) -> list[list[float]]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "input": texts,
        }

        async with self._lock:
            await self._sleep_if_needed(min_interval_seconds=min_interval_seconds)
            try:
                if self.client is None:
                    async with httpx.AsyncClient(
                        base_url=base_url, timeout=self.timeout_seconds
                    ) as client:
                        response = await client.post("/api/embed", headers=headers, json=payload)
                else:
                    response = await self.client.post("/api/embed", headers=headers, json=payload)
                self._last_request_monotonic = time.monotonic()
            except httpx.TimeoutException as exc:
                raise RuntimeError(f"Timed out connecting to Ollama at {base_url}") from exc
            except httpx.ConnectError as exc:
                raise RuntimeError(
                    f"Ollama is not reachable at {base_url} (is the server running?)"
                ) from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise RuntimeError(f"Ollama returned HTTP {status} from {base_url}/api/embed") from exc

        raw_data = response.json()
        if not isinstance(raw_data, dict):
            raise TypeError("Ollama embed response must be an object")
        data = cast("dict[str, Any]", raw_data)

        raw_embeddings = data.get("embeddings")
        if raw_embeddings is None and "embedding" in data:
            raw_embeddings = [data.get("embedding")]

        if not isinstance(raw_embeddings, list):
            raise TypeError("Ollama embed response missing 'embeddings' list")

        embeddings_list = cast("list[object]", raw_embeddings)
        if len(embeddings_list) != len(texts):
            raise RuntimeError(
                f"Ollama embed response returned {len(embeddings_list)} vectors for {len(texts)} texts"
            )

        vectors: list[list[float]] = []
        for raw_vector in embeddings_list:
            vectors.append(_coerce_vector(raw_vector, expected_size=expected_size))
        return vectors

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        settings = get_settings()

        model = (self.model or settings.ollama_embedding_model).strip()
        if not model:
            raise ValueError("ollama_embedding_model must not be empty")
        base_url = self.base_url or settings.ollama_url
        expected_size = self.vector_size or settings.embedding_vector_size

        await self._ensure_model_available(model=model, base_url=base_url)

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
                    base_url=base_url,
                    expected_size=expected_size,
                    min_interval_seconds=min_interval_seconds,
                )
            )

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
        return getattr(self._provider, "namespace", self._provider.__class__.__name__)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        hashes = [f"{self.namespace}:{_content_hash(text)}" for text in texts]
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

    settings = get_settings()

    provider_name = settings.embedding_provider.strip().lower()
    match provider_name:
        case "openai":
            provider: EmbeddingProvider = OpenAIEmbedder()
        case "ollama":
            provider = OllamaEmbedder()
        case _:
            raise RuntimeError(f"Unsupported embedding provider: {settings.embedding_provider}")

    if settings.embedding_cache_enabled:
        provider = CacheEmbedder(provider)

    return provider
