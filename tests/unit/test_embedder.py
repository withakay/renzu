"""Unit tests for embedding provider abstractions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast

import httpx
import pytest

from app.indexing.embedder import CacheEmbedder, EmbeddingProvider, OpenAIEmbedder


@dataclass
class FakeProvider(EmbeddingProvider):
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
            assert "dimensions" not in payload

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
                max_batch_size=128,
            )
            vectors = await embedder.embed(["t1", "t2"])

        assert request_count == 1
        assert vectors == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]

    async def test_batches_large_inputs(self) -> None:
        requests: list[list[str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            payload = cast("dict[str, Any]", json.loads(request.content.decode("utf-8")))
            raw_inputs = payload["input"]
            assert isinstance(raw_inputs, list)
            inputs = cast("list[object]", raw_inputs)
            requests.append([str(value) for value in inputs])

            batch = len(requests)
            if batch == 1:
                return httpx.Response(
                    200,
                    json={
                        "data": [
                            {"index": 0, "embedding": [0.0, 0.0, 0.0]},
                            {"index": 1, "embedding": [1.0, 1.0, 1.0]},
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={"data": [{"index": 0, "embedding": [2.0, 2.0, 2.0]}]},
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=3,
                max_batch_size=2,
            )
            vectors = await embedder.embed(["t1", "t2", "t3"])

        assert requests == [["t1", "t2"], ["t3"]]
        assert vectors == [
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0],
        ]

    async def test_rate_limiter_waits_once_per_batch(self) -> None:
        @dataclass
        class RecordingLimiter:
            calls: int = 0

            async def wait(self) -> None:
                self.calls += 1

        limiter = RecordingLimiter()

        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"data": [{"index": 0, "embedding": [0.0, 1.0, 2.0]}]})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=3,
                max_batch_size=1,
                rate_limiter=limiter,
            )
            _ = await embedder.embed(["t1", "t2"])

        assert limiter.calls == 2

    async def test_sends_dimensions_when_enabled(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["dimensions"] == 3
            return httpx.Response(200, json={"data": [{"index": 0, "embedding": [0.0, 1.0, 2.0]}]})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url="https://api.test/v1", transport=transport) as client:
            embedder: EmbeddingProvider = OpenAIEmbedder(
                client=client,
                api_key="sk-test",
                model="text-embedding-3-small",
                vector_size=3,
                send_dimensions=True,
            )
            vectors = await embedder.embed(["t1"])

        assert vectors == [[0.0, 1.0, 2.0]]

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
