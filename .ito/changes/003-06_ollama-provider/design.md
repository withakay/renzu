## Context

This change adds a local embedding provider backed by Ollama so development and testing can run offline without paid API calls.

## Goals

- Provide an `EmbeddingProvider` implementation that uses the Ollama HTTP API.
- Support configurable model selection (defaulting to `nomic-embed-text`).
- Support batch embedding requests.
- Surface connection and configuration errors with actionable messages.

## Non-Goals

- Starting/stopping Ollama or managing the server lifecycle.
- Automatically pulling models.

## Design

### Implementation location

- The provider lives in `src/app/indexing/embedder.py` as `OllamaEmbedder` and is wired through `get_embedder()`.
- Configuration is provided via `src/app/config/__init__.py`:
  - `OLLAMA_URL` (default `http://localhost:11434`)
  - `OLLAMA_EMBEDDING_MODEL` (default `nomic-embed-text`)

### HTTP endpoints

- `GET /api/tags` is used to verify that the configured model is already installed locally.
- `POST /api/embed` is used to generate embeddings for a batch of input texts.
- `GET /api/version` is used by `health_check()` to validate connectivity.

### Error handling

- Connection and timeout failures are converted into `RuntimeError` with messages that help the caller diagnose:
  - unreachable server
  - model missing locally (suggests `ollama pull <model>`)

### Verification

- Unit tests mock Ollama via `httpx.MockTransport`.
- Integration tests run only when Ollama is reachable and skip when the model is not installed.
