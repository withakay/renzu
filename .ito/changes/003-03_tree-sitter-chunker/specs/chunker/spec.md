## ADDED Requirements

### Requirement: Tree-sitter semantic chunking
The chunker SHALL extract semantic blocks using tree-sitter.

#### Scenario: Functions are extracted from Python
- **WHEN** `chunk(content, language="python")` is called on a file with functions
- **THEN** chunks SHALL be yielded with `chunk_type="ts:function"` and correct line spans

#### Scenario: Classes are extracted from Python
- **WHEN** `chunk(content, language="python")` is called on a file with classes
- **THEN** chunks SHALL be yielded with `chunk_type="ts:class"`

### Requirement: Fallback chunking
The chunker SHALL fall back to window/line chunking for unsupported languages.

#### Scenario: Unknown language uses fallback
- **WHEN** `chunk(content, language="unknown")` is called
- **THEN** chunks SHALL be yielded with `chunk_type="fallback:window"`

### Requirement: Chunk metadata
Each chunk SHALL include metadata for Qdrant payload.

#### Scenario: Chunk has required metadata
- **WHEN** a chunk is yielded
- **THEN** it SHALL include: `text`, `start_line`, `end_line`, `start_byte`, `end_byte`, `chunk_type`

### Requirement: Maximum chunk size
The chunker SHALL respect max_chunk_bytes configuration.

#### Scenario: Large chunks are split
- **WHEN` a semantic block exceeds `max_chunk_bytes`
- **THEN** it SHALL be split into multiple chunks
