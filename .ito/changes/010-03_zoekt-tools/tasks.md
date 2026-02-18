# Tasks for: 010-03_zoekt-tools

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 010-03_zoekt-tools
ito tasks next 010-03_zoekt-tools
ito tasks start 010-03_zoekt-tools 1.1
ito tasks complete 010-03_zoekt-tools 1.1
ito tasks shelve 010-03_zoekt-tools 1.1
ito tasks unshelve 010-03_zoekt-tools 1.1
ito tasks show 010-03_zoekt-tools
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


### Task 1.2: Create code_search_lexical MCP tool
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.3: Implement query syntax support (regex, boolean)
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.4: Add file_pattern parameter
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 1.5: Format results consistent with semantic search
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

### Task 2.1: Write unit tests for Zoekt tools
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-18
- **Status**: [ ] pending

### Task 2.2: Add integration tests
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
