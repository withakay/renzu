# Tasks for: 003-04_embedding-provider

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 003-04_embedding-provider
ito tasks next 003-04_embedding-provider
ito tasks start 003-04_embedding-provider 1.1
ito tasks complete 003-04_embedding-provider 1.1
ito tasks shelve 003-04_embedding-provider 1.1
ito tasks unshelve 003-04_embedding-provider 1.1
ito tasks show 003-04_embedding-provider
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Align embedder module API to specs

- **Files**: `src/app/indexing/embedder.py`, `src/app/indexing/__init__.py`
- **Dependencies**: None
- **Action**:
  Ensure the embedder module exposes a clear provider interface and default factory function.
- **Verify**: `make check`
- **Done When**: The module matches the spec requirements and exports remain stable.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create EmbeddingProvider interface

- **Files**: `src/app/indexing/embedder.py`
- **Dependencies**: None
- **Action**:
  Define `EmbeddingProvider` with `async embed(texts: list[str]) -> list[list[float]]`.
- **Verify**: `make check`
- **Done When**: Types enforce the provider contract and unit tests compile under basedpyright.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Implement OpenAI embedding provider

- **Files**: `src/app/indexing/embedder.py`, `src/app/config/__init__.py`
- **Dependencies**: None
- **Action**:
  Implement `OpenAIEmbedder` calling `POST /v1/embeddings` with configurable model/base URL/API key.
- **Verify**: `make test`
- **Done When**: Unit tests validate request payload and response parsing.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Add batch embedding support with rate limiting

- **Files**: `src/app/indexing/embedder.py`, `src/app/config/__init__.py`
- **Dependencies**: None
- **Action**:
  Add configurable batching (max items per request) and optional per-request rate limiting.
- **Verify**: `make test`
- **Done When**: Unit tests cover batching behavior and rate-limit sleeps.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Implement content hash-based caching

- **Files**: `src/app/indexing/embedder.py`
- **Dependencies**: None
- **Action**:
  Implement `CacheEmbedder` that caches by SHA-256 of text content.
- **Verify**: `make test`
- **Done When**: Cache avoids duplicate provider calls and returns vectors in the original order.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.6: Add embedding dimension configuration

- **Files**: `src/app/config/__init__.py`, `src/app/indexing/embedder.py`
- **Dependencies**: None
- **Action**:
  Ensure the embedder validates output vector dimensionality using a configurable size.
- **Verify**: `make test`
- **Done When**: Mismatched dimensions raise a clear error and tests cover the failure mode.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: Wave 1

### Task 2.1: Implement provider factory pattern

- **Files**: `src/app/indexing/embedder.py`, `src/app/config/__init__.py`
- **Dependencies**: None
- **Action**:
  Implement `get_embedder()` factory selecting a provider based on configuration and applying wrappers.
- **Verify**: `make test`
- **Done When**: Default provider can be constructed from settings without side effects.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Write unit tests with mocked API responses

- **Files**: `tests/unit/test_embedder.py`
- **Dependencies**: Task 2.1
- **Action**:
  Add unit tests for OpenAI response parsing, batching, caching, and factory behavior.
- **Verify**: `make test`
- **Done When**: Tests cover success and error paths without real network calls.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.3: Add integration tests against real APIs

- **Files**: `tests/integration/test_openai_embedder_integration.py`
- **Dependencies**: Task 2.1
- **Action**:
  Add an integration test that calls the real OpenAI embeddings API when credentials are present.
- **Verify**: `make test`
- **Done When**: Test is skipped unless `OPENAI_API_KEY` is configured.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint
- **Dependencies**: None
- **Action**:
  - Run `make check` and `make test` in the change worktree.
  - Review the implementation for correctness, typing (basedpyright), and lint/format compliance.
- **Done When**: `make check` and `make test` pass and tasks are all complete.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
