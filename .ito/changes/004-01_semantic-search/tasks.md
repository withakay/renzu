# Tasks for: 004-01_semantic-search

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 004-01_semantic-search
ito tasks next 004-01_semantic-search
ito tasks start 004-01_semantic-search 1.1
ito tasks complete 004-01_semantic-search 1.1
ito tasks shelve 004-01_semantic-search 1.1
ito tasks unshelve 004-01_semantic-search 1.1
ito tasks show 004-01_semantic-search
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: [Task Name]

- **Files**: `.ito/changes/004-01_semantic-search/tasks.md`
- **Dependencies**: None
- **Action**:
  Update this task plan to reference the Python implementation files and verification commands.
- **Verify**: `make check && make test-all`
- **Done When**: Tasks reference real file paths, and verification commands match the project Makefile.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create SearchService class
- **Files**: `src/app/retrieval/search.py`, `src/app/retrieval/__init__.py`
- **Dependencies**: None
- **Action**:
  Add `SearchService` with injectable dependencies and a cached constructor.
- **Verify**: `make check && make test`
- **Done When**: `SearchService` is implemented and unit tests pass.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.3: Implement semantic search with embedding generation
- **Files**: `src/app/retrieval/search.py`
- **Dependencies**: None
- **Action**:
  Embed the query via the configured embedding provider and query Qdrant with the resulting vector.
- **Verify**: `make check && make test`
- **Done When**: Query embedding + Qdrant search are wired and tested.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.4: Add result ranking and scoring
- **Files**: `src/app/retrieval/search.py`
- **Dependencies**: None
- **Action**:
  Return results in Qdrant-provided order, preserving the Qdrant similarity score in citations.
- **Verify**: `make test`
- **Done When**: Results include similarity scores and are returned in ranked order.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.5: Implement filter support (repo_id, path_prefix, language, chunk_type)
- **Files**: `src/app/retrieval/search.py`, `src/app/indexing/qdrant.py`
- **Dependencies**: None
- **Action**:
  Add filter arguments and pass them through to Qdrant; additionally enforce `path_prefix` in application code.
- **Verify**: `make check && make test`
- **Done When**: Filters (repo_id, path_prefix, language, chunk_type) are supported and tested.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.6: Create SearchResult and Citation models
- **Files**: `src/app/retrieval/search.py`
- **Dependencies**: None
- **Action**:
  Define models for search results and citations matching PRD-required fields.
- **Verify**: `make check && make test`
- **Done When**: Models exist and citations include required fields.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: None

### Task 2.1: Write unit tests for search service
- **Files**: `tests/unit/test_search_service.py`
- **Dependencies**: None
- **Action**:
  Add unit tests covering embedding call, filter forwarding, path_prefix enforcement, and citation fields.
- **Verify**: `make test`
- **Done When**: Unit tests pass.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 2.2: Add integration tests with real Qdrant
- **Files**: `tests/integration/test_search_service_integration.py`
- **Dependencies**: None
- **Action**:
  Add an integration test that upserts points into a temporary Qdrant collection and queries via `SearchService`.
- **Verify**: `make test-all`
- **Done When**: Integration test passes (or skips when Qdrant is unavailable).
- **Updated At**: 2026-02-19
- **Status**: [x] complete
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint (requires human approval)
- **Dependencies**: All Wave 1 tasks
- **Action**: Review the implementation before proceeding
- **Done When**: User confirms implementation is correct
- **Updated At**: 2026-02-19
- **Status**: [-] shelved
