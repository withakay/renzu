## ADDED Requirements

### Requirement: SCIP file parsing
The parser SHALL parse .scip protobuf files.

#### Scenario: SCIP file is parsed
- **WHEN** `parse(path/to/index.scip)` is called
- **THEN** a structured index with symbols and occurrences SHALL be returned

### Requirement: Symbol extraction
The parser SHALL extract symbol definitions and references.

#### Scenario: Definitions are extracted
- **WHEN** parsing completes
- **THEN** all symbol definitions with their ranges SHALL be available

### Requirement: Symbol identifier parsing
The parser SHALL parse SCIP symbol identifiers.

#### Scenario: Symbol ID is parsed
- **WHEN** a symbol ID like `scip:python:...` is encountered
- **THEN** scheme, manager, package, descriptors SHALL be extracted

### Requirement: Occurrence mapping
The parser SHALL map occurrences to file locations.

#### Scenario: Occurrences are mapped
- **WHEN** parsing completes
- **THEN** each occurrence SHALL have file path and byte range
