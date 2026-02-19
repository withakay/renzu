## Context

Indexing requires turning text chunks into fixed-size numeric vectors. The project needs a provider abstraction so the indexing pipeline can switch between multiple embedding backends (OpenAI API now; Ollama later) without changing callers.

## Goals

- Provide a small async embedding interface.
- Support OpenAI embeddings via `POST /v1/embeddings`.
- Support batching of large input lists.
- Support rate limiting between batch requests.
- Support content-hash based caching.
- Support configurable model selection and embedding dimensionality.

## Non-Goals

- Ollama embedding implementation (handled in a separate change).
- Persistent cache storage (in-memory cache only for now).

## Decisions

### Interface shape

Use an async `EmbeddingProvider` with `embed(texts: list[str]) -> list[list[float]]` returning one vector per input text in the same order.

### Batching

When the input list is larger than a configured `max_batch_size`, split it into multiple API requests and concatenate results preserving order.

### Rate limiting

Implement a simple async rate limiter that enforces a minimum interval between batch requests when configured.

### Caching

Wrap providers with `CacheEmbedder` that caches by a stable key derived from the provider namespace and a SHA-256 content hash of the input text. This avoids incorrect reuse across providers/models/dimensions.

## Testing

- Unit tests use `httpx.MockTransport` to validate request payloads, response parsing, batching behavior, and caching behavior.
- Live API tests are skipped by default and only run when explicitly enabled via environment variables.
