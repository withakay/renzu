## ADDED Requirements

### Requirement: SCIP file parsing
The parser SHALL parse .scip protobuf files.

#### Scenario: SCIP file is parsed
- **WHEN** `ScipParser().parse_file("path/to/index.scip")` is called
- **THEN** a structured index with documents, symbols, and occurrences SHALL be returned

### Requirement: Symbol extraction
The parser SHALL extract symbol definitions and references.

#### Scenario: Definitions are extracted
- **WHEN** parsing completes
- **THEN** all symbol definitions with their ranges SHALL be available

### Requirement: Symbol identifier parsing
The parser SHALL parse SCIP symbol identifiers.

#### Scenario: Symbol ID is parsed
- **WHEN** a symbol ID like `scip-python pypi mypkg 1.0.0 mypkg/Foo#bar().` is encountered
- **THEN** scheme, manager, package name, version, and descriptors SHALL be extracted

### Requirement: Occurrence mapping
The parser SHALL map occurrences to file locations.

#### Scenario: Occurrences are mapped
- **WHEN** parsing completes
- **THEN** each occurrence SHALL have a relative file path and a line/character range
