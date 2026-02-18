# Proposal: Ollama Provider

## Why
Support local embedding generation via Ollama for offline development and cost reduction.

## What
Create `OllamaEmbedder` in `app.indexing.embedder`:
- HTTP client to Ollama API
- Model selection (nomic-embed-text, etc.)
- Batch embedding support
- Connection error handling

## Impact
- **Enables**: Local embeddings without API calls
- **Depends On**: embedding-provider (protocol definition)
- **PRD Reference**: FR-I3 (API + Ollama)

## Out of Scope
- Ollama server management
