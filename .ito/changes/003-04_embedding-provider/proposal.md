# Proposal: Embedding Provider

## Why
Abstract embedding generation behind an interface to support multiple providers (API, Ollama).

## What
Create `app.indexing.embedder` module with:
- `EmbeddingProvider` protocol (ABC)
- `OpenAIEmbedder` implementation (API-based)
- `CacheEmbedder` wrapper with content-hash caching
- Batch embedding support
- Configurable model selection

## Impact
- **Enables**: Vector generation for indexing
- **PRD Reference**: FR-I3 (Pluggable embeddings)

## Out of Scope
- Ollama implementation (handled in ollama-provider change)
