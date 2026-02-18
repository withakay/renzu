# Tasks for: 002-01_infra-compose

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 002-01_infra-compose
ito tasks next 002-01_infra-compose
ito tasks start 002-01_infra-compose 1.1
ito tasks complete 002-01_infra-compose 1.1
ito tasks shelve 002-01_infra-compose 1.1
ito tasks unshelve 002-01_infra-compose 1.1
ito tasks show 002-01_infra-compose
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: [Task Name]

- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

______________________________________________________________________


### Task 1.2: Create docker-compose.infra.yml for external services
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] in-progress

### Task 1.3: Add Qdrant service configuration
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.4: Add Glean service configuration (from glean-docker)
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.5: Add Glass service configuration
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.6: Add Ollama service (optional profile)
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.7: Create .env.example with required variables
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

---

## Wave 2
- **Depends On**: None

### Task 2.1: Document service URLs and ports in README
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 2.2: Add healthcheck configurations for each service
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 2.3: Test full stack startup with docker compose up
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint (requires human approval)
- **Dependencies**: All Wave 1 tasks
- **Action**: Review the implementation before proceeding
- **Done When**: User confirms implementation is correct
- **Updated At**: 2026-02-18
- **Status**: [ ] pending
