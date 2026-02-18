## ADDED Requirements

### Requirement: File discovery with globs
The file walker SHALL discover files matching include globs and excluding exclude globs.

#### Scenario: Include patterns are applied
- **WHEN** `walk(root, include=["**/*.py"], exclude=["**/test_*"])` is called
- **THEN** only Python files not matching test_* SHALL be yielded

### Requirement: Language detection
The walker SHALL detect language from file extension.

#### Scenario: Language is detected for Python file
- **WHEN** a file with `.py` extension is discovered
- **THEN** the yielded FileInfo SHALL have `language="python"`

#### Scenario: Unknown extension returns None
- **WHEN** a file with unknown extension is discovered
- **THEN** the yielded FileInfo SHALL have `language=None`

### Requirement: File metadata
The walker SHALL extract file metadata.

#### Scenario: File size and mtime are extracted
- **WHEN** a file is discovered
- **THEN** FileInfo SHALL include `size_bytes` and `modified_at`

### Requirement: Max file size filter
The walker SHALL skip files exceeding max_size configuration.

#### Scenario: Large files are skipped
- **WHEN** a file exceeds `max_size_bytes` config
- **THEN** it SHALL NOT be yielded
