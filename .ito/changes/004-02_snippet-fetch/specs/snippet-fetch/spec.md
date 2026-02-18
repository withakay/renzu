## ADDED Requirements

### Requirement: Snippet fetch by range
The snippet service SHALL fetch file content by line range.

#### Scenario: Snippet is fetched
- **WHEN** `fetch(repo_id, path, start_line=10, end_line=20)` is called
- **THEN** lines 10-20 of the file SHALL be returned

### Requirement: Path traversal protection
The snippet service SHALL prevent path traversal attacks.

#### Scenario: Path traversal is blocked
- **WHEN** `fetch(repo_id, "../etc/passwd", ...)` is called
- **THEN** an error SHALL be raised without reading the file

### Requirement: Line range validation
The snippet service SHALL validate line ranges.

#### Scenario: Invalid range is rejected
- **WHEN** `end_line < start_line` is provided
- **THEN** an error SHALL be raised

#### Scenario: Out of bounds is handled
- **WHEN** line range exceeds file length
- **THEN** available lines SHALL be returned without error
