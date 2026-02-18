"""Unit tests for embedding provider abstractions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import cast

import httpx
import pytest

from app.config import get_settings
from app.indexing.embedder import CacheEmbedder, EmbeddingProvider, OpenAIEmbedder


@dataclass
class FakeProvider:
    call_count: int = 0
    last_texts: list[str] | None = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        self.last_texts = list(texts)
        return [[float(idx)] for idx, _ in enumerate(texts)]


@pytest.mark.unit
@pytest.mark.asyncio
class TestCacheEmbedder:
    async def test_cache_avoids_duplicate_calls(self) -> None:
        provider = FakeProvider()
        embedder = CacheEmbedder(provider)

        first = await embedder.embed(["hello"])
        second = await embedder.embed(["hello"])

        assert first == second
        assert provider.call_count == 1

    async def test_cache_batches_missing_texts(self) -> None:
        provider = FakeProvider()
        embedder = CacheEmbedder(provider)

        _ = await embedder.embed(["a", "b", "c"])
        assert provider.call_count == 1
        assert provider.last_texts == ["a", "b", "c"]

        _ = await embedder.embed(["a", "b", "d"])
        assert provider.call_count == 2
        assert provider.last_texts == ["d"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestOpenAIEmbedder:
    async def test_posts_all_texts_in_one_request(self) -> None:
        request_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal request_count
            request_count += 1
            assert request.url.path.endswith("/embeddings")
            assert request.headers.get("Authorization") == "Bearer sk-test"

            payload = json.loads(request.content.decode("utf-8"))
            assert payload["model"] == "text-embedding-3-small"
            assert payload["input"] == ["t1", "t2"]

            return httpx.Response(
                200,
                json={
                    "data": [
                        {"index": 0, "embedding": [0.0, 1.0, 2.0]},
                        {"index": 1, "embedding": [3.0, 4.0, 5.0]},
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=3,
            )
            vectors = await embedder.embed(["t1", "t2"])

        assert request_count == 1
        assert vectors == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]

    async def test_raises_on_dimension_mismatch(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"data": [{"index": 0, "embedding": [0.0, 1.0]}]},
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=3,
            )
            with pytest.raises(ValueError, match="Expected embedding size"):
                await embedder.embed(["t1"])

    async def test_batches_requests_when_configured(self) -> None:
        request_inputs: list[list[str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content.decode("utf-8"))
            inputs = payload["input"]
            assert isinstance(inputs, list)
            inputs_list = list(cast("list[object]", inputs))
            request_inputs.append([str(item) for item in inputs_list])

            text = request_inputs[-1][0]
            value = 1.0 if text == "t1" else 2.0
            return httpx.Response(200, json={"data": [{"index": 0, "embedding": [value]}]})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=1,
                batch_size=1,
            )
            vectors = await embedder.embed(["t1", "t2"])

        assert request_inputs == [["t1"], ["t2"]]
        assert vectors == [[1.0], [2.0]]

    async def test_rate_limits_between_batches(self, monkeypatch: pytest.MonkeyPatch) -> None:
        sleep_calls: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)

        monotonic_values = iter([0.0, 0.01, 0.02])

        from app.indexing import embedder as embedder_module

        original_monotonic = embedder_module.time.monotonic

        def fake_monotonic() -> float:
            try:
                return next(monotonic_values)
            except StopIteration:
                return original_monotonic()

        monkeypatch.setattr(embedder_module.asyncio, "sleep", fake_sleep)
        monkeypatch.setattr(embedder_module.time, "monotonic", fake_monotonic)

        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"data": [{"index": 0, "embedding": [0.0]}]})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=1,
                batch_size=1,
                min_interval_seconds=0.05,
            )
            _ = await embedder.embed(["t1", "t2"])

        assert len(sleep_calls) == 1
        assert abs(sleep_calls[0] - 0.04) < 1e-6


@pytest.mark.unit
class TestEmbedderFactory:
    def test_get_embedder_respects_provider_and_cache_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.indexing.embedder import CacheEmbedder, OpenAIEmbedder, get_embedder

        monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
        monkeypatch.setenv("EMBEDDING_CACHE_ENABLED", "false")
        get_settings.cache_clear()
        get_embedder.cache_clear()
        provider = get_embedder()
        assert isinstance(provider, OpenAIEmbedder)

        monkeypatch.setenv("EMBEDDING_CACHE_ENABLED", "true")
        get_settings.cache_clear()
        get_embedder.cache_clear()
        provider = get_embedder()
        assert isinstance(provider, CacheEmbedder)

    def test_get_embedder_raises_on_unknown_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.indexing.embedder import get_embedder

        monkeypatch.setenv("EMBEDDING_PROVIDER", "nope")
        get_settings.cache_clear()
        get_embedder.cache_clear()
        with pytest.raises(RuntimeError, match="Unsupported embedding provider"):
            _ = get_embedder()
