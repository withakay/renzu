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

### Task 1.1: Finalize change artifacts (specs/design/tasks)

- **Files**:
  - `.ito/changes/003-04_embedding-provider/specs/embedding-provider/spec.md`
  - `.ito/changes/003-04_embedding-provider/design.md`
  - `.ito/changes/003-04_embedding-provider/tasks.md`
- **Dependencies**: None
- **Action**:
  - Ensure specs cover provider abstraction, batching, rate limiting, caching, dimension config, and factory.
  - Add a lightweight design doc describing key decisions and test strategy.
  - Ensure this tasks file references the actual Python files/commands.
- **Verify**: `ito validate 003-04_embedding-provider --strict`
- **Done When**: `ito validate 003-04_embedding-provider --strict` passes.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create EmbeddingProvider abstract base class
- **Files**:
  - `src/app/indexing/embedder.py`
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.1
- **Action**:
  - Implement an async `EmbeddingProvider` ABC with `embed(texts: list[str]) -> list[list[float]]`.
  - Ensure typing is strict-friendly (basedpyright).
- **Verify**: `make test`
- **Done When**: Unit tests pass and `EmbeddingProvider` is used as the core interface.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Implement OpenAI embedding provider
- **Files**:
  - `src/app/indexing/embedder.py`
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.2
- **Action**:
  - Implement an `OpenAIEmbedder` that calls `POST /v1/embeddings` via `httpx`.
  - Validate response shape and embedding dimensionality.
- **Verify**: `make test`
- **Done When**: Unit tests demonstrate correct request/response parsing and dimension validation.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Add batch embedding support with rate limiting
- **Files**:
  - `src/app/indexing/embedder.py`
  - `src/app/config/__init__.py`
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.3
- **Action**:
  - Add provider-side batching for large input lists.
  - Add an async rate limiter between batch requests.
  - Make batch/rate settings configurable.
- **Verify**: `make test`
- **Done When**: Unit tests verify batching produces multiple requests and ordering is preserved.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Implement content hash-based caching
- **Files**:
  - `src/app/indexing/embedder.py`
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.2
- **Action**:
  - Ensure `CacheEmbedder` keys by content hash and provider namespace.
  - Ensure caching avoids duplicate provider calls and supports partial cache hits.
- **Verify**: `make test`
- **Done When**: Unit tests confirm caching behavior and no duplicate calls.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.6: Add embedding dimension configuration
- **Files**:
  - `src/app/config/__init__.py`
  - `src/app/indexing/embedder.py`
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 1.3
- **Action**:
  - Ensure embedding vector size is configurable and enforced.
  - Prefer an explicit embedding vector size when set; otherwise fall back to Qdrant vector size.
- **Verify**: `make test`
- **Done When**: Dimension is configurable via settings and validated in provider parsing.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: Wave 1

### Task 2.1: Implement provider factory pattern
- **Files**:
  - `src/app/indexing/embedder.py`
  - `src/app/indexing/__init__.py`
  - `src/app/config/__init__.py`
- **Dependencies**: None
- **Action**:
  - Add a factory that selects the configured embedding provider and applies caching wrapper.
  - Keep `get_embedder()` as the main entrypoint.
- **Verify**: `make test`
- **Done When**: `get_embedder()` returns the configured provider with caching applied as configured.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Write unit tests with mocked API responses
- **Files**:
  - `tests/unit/test_embedder.py`
- **Dependencies**: Task 2.1
- **Action**:
  - Add unit tests using `httpx.MockTransport` to validate request payloads and parsing.
  - Add tests for batching and cache behavior.
- **Verify**: `make test`
- **Done When**: `pytest -m unit` passes.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.3: Add integration tests against real APIs
- **Files**:
  - `tests/integration/test_openai_embedder_live.py`
  - `pyproject.toml`
- **Dependencies**: Task 2.2
- **Action**:
  - Add a live OpenAI integration test that is skipped unless explicitly enabled.
  - Add a pytest marker for the live API test.
- **Verify**: `pytest -m live_api`
- **Done When**: Live API test runs successfully when enabled and is skipped by default.
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
