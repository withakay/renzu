# Tasks for: 003-05_indexing-pipeline

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 003-05_indexing-pipeline
ito tasks next 003-05_indexing-pipeline
ito tasks start 003-05_indexing-pipeline 1.1
ito tasks complete 003-05_indexing-pipeline 1.1
ito tasks shelve 003-05_indexing-pipeline 1.1
ito tasks unshelve 003-05_indexing-pipeline 1.1
ito tasks show 003-05_indexing-pipeline
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Align task plan with Python implementation

- **Files**: `.ito/changes/003-05_indexing-pipeline/tasks.md`
- **Dependencies**: None
- **Action**:
  Update task descriptions (paths, verify commands, acceptance criteria) to match the actual Python codebase.
- **Verify**: `ito tasks status 003-05_indexing-pipeline`
- **Done When**: Task list is specific, uses correct paths, and uses project verification commands.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create IndexingPipeline orchestrator class
- **Files**: `src/app/indexing/pipeline.py`, `src/app/indexing/__init__.py`
- **Dependencies**: None
- **Action**:
  Add an `IndexingPipeline` orchestrator class with injectable dependencies.
- **Verify**: `make test`
- **Done When**: `IndexingPipeline` is importable and pipeline unit tests pass.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Integrate FileWalker + Chunker + EmbeddingProvider + QdrantClient
- **Files**: `src/app/indexing/pipeline.py`, `src/app/indexing/walker.py`, `src/app/indexing/chunker.py`, `src/app/indexing/embedder.py`, `src/app/indexing/qdrant.py`
- **Dependencies**: None
- **Action**:
  Wire file discovery, chunking, embedding, and storage into the pipeline.
- **Verify**: `make test`
- **Done When**: Pipeline can walk files, chunk content, embed chunks, and upsert into a QdrantStore.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Implement repo indexing workflow
- **Files**: `src/app/indexing/pipeline.py`
- **Dependencies**: None
- **Action**:
  Implement `IndexingPipeline.index_repo(repo_id, path, globs, languages)` as an async method.
- **Verify**: `make test`
- **Done When**: Repo indexing returns a result summary and continues past per-file errors.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Add progress tracking and logging
- **Files**: `src/app/indexing/pipeline.py`
- **Dependencies**: None
- **Action**:
  Add start/progress/done logging and counters for discovered/indexed/skipped/error totals.
- **Verify**: `make test`
- **Done When**: Logs include repo_id and counters; result includes final counters.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.6: Implement delete-and-reindex workflow
- **Files**: `src/app/indexing/pipeline.py`
- **Dependencies**: None
- **Action**:
  Support delete-then-reindex semantics (delete all points for repo_id before indexing).
- **Verify**: `make test`
- **Done When**: Pipeline deletes existing repo points when configured and still indexes afterward.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: Wave 1

### Task 2.1: Add error handling and retry logic
- **Files**: `src/app/indexing/pipeline.py`, `src/app/indexing/qdrant.py`, `src/app/indexing/embedder.py`
- **Dependencies**: None
- **Action**:
  Add retries where appropriate (embedding/upsert), and ensure failures isolate to a single file whenever possible.
- **Verify**: `make test`
- **Done When**: Transient errors can be retried; final failures are surfaced as per-file errors.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Write integration tests for full pipeline
- **Files**: `tests/integration/test_indexing_pipeline_integration.py`
- **Dependencies**: None
- **Action**:
  Add an integration-style test that exercises FileWalker + Chunker + IndexingPipeline end-to-end using in-memory fakes for embedding and storage.
- **Verify**: `make test`
- **Done When**: Tests cover delete-and-reindex behavior and content-hash dedupe.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.3: Add CLI command for indexing
- **Files**: `src/app/cli.py`, `pyproject.toml`
- **Dependencies**: None
- **Action**:
  Add a console script that runs `IndexingPipeline.index_repo(...)` from the command line.
- **Verify**: `python -m app.cli --help`
- **Done When**: CLI accepts repo_id/path/globs/languages flags and exits non-zero on failure.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint (requires human approval)
- **Dependencies**: All Wave 1 tasks
- **Action**: Review the implementation before proceeding
- **Done When**: Self-review complete; `make check` and `make test` are green.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
