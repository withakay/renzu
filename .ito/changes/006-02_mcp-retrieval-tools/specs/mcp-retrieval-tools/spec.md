## ADDED Requirements

### Requirement: code_search tool
The MCP server SHALL provide a code_search tool.

#### Scenario: Tool is registered
- **WHEN** MCP server starts
- **THEN** code_search tool SHALL be discoverable

#### Scenario: Tool accepts parameters
- **WHEN** code_search is called with query and repo_id
- **THEN** search results SHALL be returned

### Requirement: code_snippet tool
The MCP server SHALL provide a code_snippet tool.

#### Scenario: Tool fetches snippet
- **WHEN** code_snippet is called with repo_id, path, lines
- **THEN** file content SHALL be returned

### Requirement: Tool schemas
Tools SHALL have proper JSON schemas.

#### Scenario: Schema is valid
- **WHEN** tool schema is requested
- **THEN** valid JSON Schema with required/optional parameters SHALL be returned
