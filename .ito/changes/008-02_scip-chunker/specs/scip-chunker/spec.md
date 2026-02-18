## ADDED Requirements

### Requirement: SCIP-based chunking
The chunker SHALL create chunks from SCIP symbol definitions.

#### Scenario: Chunks from SCIP definitions
- **WHEN** `chunk_with_scip(content, scip_index)` is called
- **THEN** chunks SHALL be created for each symbol definition

### Requirement: Symbol metadata in chunks
Chunks SHALL include SCIP symbol identifiers.

#### Scenario: Symbol ID is included
- **WHEN** a SCIP-based chunk is created
- **THEN** `symbol_scip` field SHALL be populated

### Requirement: Hybrid chunking
The chunker SHALL fall back to tree-sitter when SCIP unavailable.

#### Scenario: Tree-sitter fallback
- **WHEN** no SCIP index is available for a file
- **THEN** tree-sitter chunking SHALL be used

### Requirement: Chunk type labeling
SCIP chunks SHALL have distinct chunk_type.

#### Scenario: Chunk type is set
- **WHEN** a SCIP chunk is created
- **THEN** `chunk_type="scip:def"` SHALL be set
