# Tasks for: 007-01_http-routes

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 007-01_http-routes
ito tasks next 007-01_http-routes
ito tasks start 007-01_http-routes 1.1
ito tasks complete 007-01_http-routes 1.1
ito tasks shelve 007-01_http-routes 1.1
ito tasks unshelve 007-01_http-routes 1.1
ito tasks show 007-01_http-routes
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Define error envelope + exception handlers

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Add a consistent error response model and register exception handlers for
  validation errors and application errors.
- **Verify**: `make test`
- **Done When**:
  - Validation errors return `{"error": "validation_error", "detail": "..."}`
  - Application errors return `{"error": "...", "detail": "..."}`
- **Updated At**: 2026-02-18
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create FastAPI router for /v1/* endpoints

- **Files**: `src/app/api/routes.py`, `src/app/main.py`
- **Dependencies**: None
- **Action**:
  Create an `APIRouter(prefix="/v1")` and ensure it is registered on the FastAPI
  application.
- **Verify**: `make test`
- **Done When**: `/v1/*` endpoints appear in FastAPI routing table and OpenAPI.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Implement POST /v1/index endpoint

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Implement indexing orchestration that:
  - validates the filesystem root
  - walks files by glob
  - chunks content
  - writes chunks to Qdrant
  - stores an in-memory mapping of `repo_id -> root_path` for subsequent calls
- **Verify**: `make test`
- **Done When**: POST `/v1/index` returns `{ok, job_id, repo_id, root_path, indexed_files, indexed_chunks}`.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Implement POST /v1/search endpoint

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Implement semantic search that:
  - requires `repo_id` to be indexed first
  - builds a query vector
  - queries Qdrant and returns structured hits
- **Verify**: `make test`
- **Done When**: POST `/v1/search` returns `{ok, repo_id, query, hits: [...]}`.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Implement POST /v1/snippet endpoint

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Implement file span retrieval that:
  - requires `repo_id` to be indexed first
  - safely joins repo root + relative path
  - validates the requested line range
  - returns the requested line span
- **Verify**: `make test`
- **Done When**: POST `/v1/snippet` returns `{ok, repo_id, path, start_line, end_line, content}`.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.6: Add request/response Pydantic models

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Define request/response models for index/search/snippet, plus shared error
  response shapes.
- **Verify**: `make check`
- **Done When**: Models validate requests and OpenAPI includes schemas.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: None

### Task 2.1: Implement /v1/glass/* endpoints

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Add endpoints to expose Glass service operations over HTTP:
  - POST `/v1/glass/list_symbols`
  - POST `/v1/glass/find_references`
  - POST `/v1/glass/describe`
- **Verify**: `make test`
- **Done When**: Each endpoint returns a stable `{ok, available, formatted, data?, error?}` envelope.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Add OpenAPI documentation

- **Files**: `src/app/api/routes.py`
- **Dependencies**: None
- **Action**:
  Ensure endpoints have accurate request/response schemas, error response
  schemas, and basic metadata (summary/description where needed).
- **Verify**: `make test`
- **Done When**: `/openapi.json` includes the `/v1/*` paths with correct models.
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.3: Write unit tests for HTTP routes

- **Files**: `tests/unit/test_api_routes.py`, `tests/integration/test_glass_routes_integration.py`
- **Dependencies**: None
- **Action**:
  Add unit and integration tests that validate request validation, error
  responses, and basic response shapes.
- **Verify**: `make test`
- **Done When**: Tests cover `/v1/index`, `/v1/search`, `/v1/snippet`, and `/v1/glass/*`.
- **Updated At**: 2026-02-18
- **Status**: [x] complete
