# Tasks for: 003-06_ollama-provider

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 003-06_ollama-provider
ito tasks next 003-06_ollama-provider
ito tasks start 003-06_ollama-provider 1.1
ito tasks complete 003-06_ollama-provider 1.1
ito tasks shelve 003-06_ollama-provider 1.1
ito tasks unshelve 003-06_ollama-provider 1.1
ito tasks show 003-06_ollama-provider
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Review existing embedding provider surface

- **Files**: `src/app/indexing/embedder.py`, `src/app/config/__init__.py`, `tests/unit/test_embedder.py`
- **Dependencies**: None
- **Action**:
  Confirm the embedding provider protocol, factory wiring, and configuration surface are the right place to add Ollama support.
- **Verify**: `make check && make test`
- **Done When**: The Ollama provider work integrates without changing the public provider protocol.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create Ollama embedder provider

- **Files**: `src/app/indexing/embedder.py`, `src/app/config/__init__.py`
- **Dependencies**: Task 1.1
- **Action**:
  Implement `OllamaEmbedder` that conforms to the `EmbeddingProvider` protocol and can be selected via `EMBEDDING_PROVIDER=ollama`.
- **Verify**: `make check && make test`
- **Done When**: `get_embedder()` returns `OllamaEmbedder` when configured.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Implement Ollama API client for embeddings

- **Files**: `src/app/indexing/embedder.py`
- **Dependencies**: Task 1.2
- **Action**:
  Use the Ollama HTTP API (`GET /api/tags`, `POST /api/embed`) to generate embeddings, including batch support.
- **Verify**: `make check && make test`
- **Done When**: `OllamaEmbedder.embed([...])` returns one vector per input text.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Add model pulling verification

- **Files**: `src/app/indexing/embedder.py`, `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.3
- **Action**:
  Verify the configured model is present locally (via `/api/tags`) and raise a descriptive error that suggests `ollama pull <model>` when missing.
- **Verify**: `make check && make test`
- **Done When**: Missing models fail fast with an actionable message.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Support nomic-embed-text and other local models

- **Files**: `src/app/config/__init__.py`, `src/app/indexing/embedder.py`
- **Dependencies**: Task 1.2
- **Action**:
  Provide a configurable default model (`OLLAMA_EMBEDDING_MODEL`) and allow any installed model name.
- **Verify**: `make check && make test`
- **Done When**: Setting `OLLAMA_EMBEDDING_MODEL` selects the model used by the embedder.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.6: Add connection health check

- **Files**: `src/app/indexing/embedder.py`, `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.2
- **Action**:
  Add a lightweight `health_check()` method that hits `/api/version` and surfaces connection errors clearly.
- **Verify**: `make check && make test`
- **Done When**: Health checks succeed when Ollama is reachable and fail with descriptive errors when not.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: Wave 1

### Task 2.1: Handle Ollama unavailability gracefully

- **Files**: `src/app/indexing/embedder.py`, `src/app/indexing/pipeline.py`
- **Dependencies**: None
- **Action**:
  Wrap HTTP errors with actionable `RuntimeError` messages so callers can report failures without crashing.
- **Verify**: `make test` (unit) and `uv run pytest -m integration -v`
- **Done When**: Connection failures are translated into stable, descriptive errors.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Write unit tests with mocked Ollama

- **Files**: `tests/unit/test_embedder.py`
- **Dependencies**: Task 2.1
- **Action**:
  Add MockTransport-based unit tests for model verification, caching, and health check behavior.
- **Verify**: `make test`
- **Done When**: Unit tests cover success + failure paths without requiring Ollama to run.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.3: Add integration tests against local Ollama

- **Files**: `tests/integration/test_ollama_embedder_integration.py`
- **Dependencies**: Task 2.2
- **Action**:
  Add an integration test that runs only when Ollama is reachable; skip when the model is not installed.
- **Verify**: `uv run pytest -m integration -v`
- **Done When**: Integration suite passes with appropriate skips when Ollama is unavailable.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
______________________________________________________________________

## Wave 3 (Checkpoint)

- **Depends On**: Wave 2

### Task 3.1: Review implementation

- **Type**: checkpoint (self-review)
- **Files**: `src/app/indexing/embedder.py`, `tests/unit/test_embedder.py`, `tests/integration/test_ollama_embedder_integration.py`
- **Dependencies**: None
- **Action**:
  Confirm the implementation meets the proposal (Ollama provider, model selection, batch embedding, and error handling) and run checks/tests.
- **Verify**: `make check && make test` and `uv run pytest -m integration -v`
- **Done When**: Checks/tests pass (with expected skips for unavailable services).
- **Updated At**: 2026-02-18
- **Status**: [x] complete
