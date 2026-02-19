# Tasks for: 006-03_mcp-glass-tools

## Execution Notes

- **Tool**: Any (OpenCode, Codex, Claude Code)
- **Mode**: Sequential (or parallel if tool supports)
- **Template**: Enhanced task format with waves, verification, and status tracking
- **Tracking**: Prefer the tasks CLI to drive status updates and pick work

```bash
ito tasks status 006-03_mcp-glass-tools
ito tasks next 006-03_mcp-glass-tools
ito tasks start 006-03_mcp-glass-tools 1.1
ito tasks complete 006-03_mcp-glass-tools 1.1
ito tasks shelve 006-03_mcp-glass-tools 1.1
ito tasks unshelve 006-03_mcp-glass-tools 1.1
ito tasks show 006-03_mcp-glass-tools
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
- **Updated At**: 2026-02-19
- **Status**: [x] complete

______________________________________________________________________


### Task 1.2: Create symbols_in_file MCP tool
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.3: Create symbol_definition MCP tool
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.4: Create symbol_references MCP tool
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 1.5: Add conditional registration (Glass enabled)
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-19
- **Status**: [x] complete

---

## Wave 2
- **Depends On**: None

### Task 2.1: Write unit tests for glass MCP tools
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
- **Updated At**: 2026-02-19
- **Status**: [x] complete

### Task 2.2: Add integration tests
- **Files**: `path/to/file.rs`
- **Dependencies**: None
- **Action**:
  [Describe what needs to be done]
- **Verify**: `cargo test --workspace`
- **Done When**: [Success criteria]
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
