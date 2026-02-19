# Tasks for: 005-01_glass-client

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 005-01_glass-client
ito tasks next 005-01_glass-client
ito tasks start 005-01_glass-client 1.1
ito tasks complete 005-01_glass-client 1.1
ito tasks shelve 005-01_glass-client 1.1
ito tasks unshelve 005-01_glass-client 1.1
ito tasks show 005-01_glass-client
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Add Glass URL configuration

- **Files**: `src/app/config/__init__.py`, `tests/unit/test_main.py`
- **Dependencies**: None
- **Action**:
  - Add `Settings.glass_url` configured via `GLASS_URL`.
  - Ensure tests cover default + env override behavior.
- **Verify**: `make test`
- **Done When**: Settings exposes `glass_url` and tests pass.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create GlassClient class
- **Files**: `src/app/glass/client.py`, `src/app/glass/__init__.py`
- **Dependencies**: None
- **Action**:
  - Add `GlassClient` with async context support and typed models.
- **Verify**: `make test`
- **Done When**: Client imports cleanly and unit tests pass.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.3: Implement connection to Glass server
- **Files**: `src/app/glass/client.py`
- **Dependencies**: None
- **Action**:
  - Connect using `httpx.AsyncClient` with `base_url` from `GLASS_URL`.
  - Add timeouts and resource cleanup.
- **Verify**: `make test`
- **Done When**: Requests are made via configured base URL.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.4: Add list_symbols API call
- **Files**: `src/app/glass/client.py`, `tests/unit/test_glass_client.py`
- **Dependencies**: None
- **Action**:
  - Implement `GlassClient.list_symbols(repo_id, path)`.
- **Verify**: `make test`
- **Done When**: Unit tests validate request/response handling.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.5: Add describe_symbol API call
- **Files**: `src/app/glass/client.py`, `tests/unit/test_glass_client.py`
- **Dependencies**: None
- **Action**:
  - Implement `GlassClient.describe_symbol(symbol_id)`.
- **Verify**: `make test`
- **Done When**: Unit tests validate request/response handling.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.6: Add find_references API call
- **Files**: `src/app/glass/client.py`, `tests/unit/test_glass_client.py`
- **Dependencies**: None
- **Action**:
  - Implement `GlassClient.find_references(symbol_id)`.
- **Verify**: `make test`
- **Done When**: Unit tests validate request/response handling.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: None

### Task 2.1: Handle Glass unavailability gracefully
- **Files**: `src/app/glass/client.py`, `tests/unit/test_glass_client.py`
- **Dependencies**: None
- **Action**:
  - Return empty results when `graceful=True` and Glass is unavailable.
  - Raise typed errors when `graceful=False`.
- **Verify**: `make test`
- **Done When**: Unit tests cover timeout/connection/non-2xx behavior.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 2.2: Write unit tests with mocked Glass
- **Files**: `tests/unit/test_glass_client.py`
- **Dependencies**: None
- **Action**:
  - Use `httpx.MockTransport` to test request payloads and responses.
- **Verify**: `make test`
- **Done When**: Tests cover all client methods and key error paths.
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 2.3: Add integration tests against real Glass
- **Files**: `tests/integration/test_glass_client_integration.py`
- **Dependencies**: None
- **Action**:
  - Add gated smoke tests that run only when real Glass env vars are set.
- **Verify**: `make test`
- **Done When**: Integration tests skip cleanly when not configured.
- **Updated At**: 2026-02-19
- **Status**: [x] complete
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint (requires human approval)
- **Dependencies**: All Wave 1 tasks
- **Action**: Review the implementation before proceeding
- **Done When**: User confirms implementation is correct
- **Updated At**: 2026-02-19
- **Status**: [x] complete
