# Tasks for: 008-01_scip-parser

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 008-01_scip-parser
ito tasks next 008-01_scip-parser
ito tasks start 008-01_scip-parser 1.1
ito tasks complete 008-01_scip-parser 1.1
ito tasks shelve 008-01_scip-parser 1.1
ito tasks unshelve 008-01_scip-parser 1.1
ito tasks show 008-01_scip-parser
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
- **Status**: [-] shelved

______________________________________________________________________


### Task 1.2: Create SCIP index parser
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.3: Implement protobuf deserialization for SCIP
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.4: Extract symbol definitions and references
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 1.5: Map SCIP positions to line numbers
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: None

### Task 2.1: Handle language-specific SCIP metadata
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete

### Task 2.2: Write unit tests with sample SCIP indexes
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [x] complete
## Checkpoints

### Checkpoint: Review Implementation

- **Type**: checkpoint (requires human approval)
- **Dependencies**: All Wave 1 tasks
- **Action**: Review the implementation before proceeding
- **Done When**: User confirms implementation is correct
- **Updated At**: 2026-02-18
- **Status**: [-] shelved
