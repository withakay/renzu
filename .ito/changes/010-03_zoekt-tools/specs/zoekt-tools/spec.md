## ADDED Requirements

### Requirement: code_search_lexical tool
The MCP server SHALL provide a code_search_lexical tool.

#### Scenario: Tool is registered
- **WHEN** MCP server starts with ZOEKT_ENABLED=true
- **THEN** code_search_lexical tool SHALL be discoverable

#### Scenario: Tool accepts lexical query
- **WHEN** code_search_lexical is called with regex query
- **THEN** matching files and lines SHALL be returned

### Requirement: Query syntax support
The tool SHALL support Zoekt query syntax.

#### Scenario: Regex query works
- **WHEN** query contains regex pattern
- **THEN** regex matching SHALL be applied

#### Scenario: Boolean operators work
- **WHEN** query contains AND/OR/NOT
- **THEN** boolean logic SHALL be applied

### Requirement: File pattern parameter
The tool SHALL accept file_pattern parameter.

#### Scenario: File pattern filters results
- **WHEN** file_pattern="*.rs" is provided
- **THEN** only Rust files SHALL be searched

### Requirement: Result format
Results SHALL match semantic search citation format.

#### Scenario: Citations are consistent
- **WHEN** lexical search returns results
- **THEN** format SHALL include: repo_id, path, start_line, end_line, match_text

### Requirement: Graceful fallback
Tool SHALL handle Zoekt unavailability.

#### Scenario: Unavailable returns message
- **WHEN** Zoekt is unavailable
- **THEN** tool SHALL return informative error message
