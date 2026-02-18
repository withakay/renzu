## ADDED Requirements

### Requirement: symbols_in_file MCP tool
The MCP server SHALL provide a symbols_in_file tool.

#### Scenario: Tool lists symbols
- **WHEN** symbols_in_file is called
- **THEN** symbols in the specified file SHALL be returned

### Requirement: symbol_definition MCP tool
The MCP server SHALL provide a symbol_definition tool.

#### Scenario: Tool returns definition
- **WHEN** symbol_definition is called with symbol_id
- **THEN** definition location SHALL be returned

### Requirement: symbol_references MCP tool
The MCP server SHALL provide a symbol_references tool.

#### Scenario: Tool returns references
- **WHEN** symbol_references is called with symbol_id
- **THEN** all reference locations SHALL be returned

### Requirement: Graceful unavailability
Glass tools SHALL handle unavailability gracefully.

#### Scenario: Unavailable returns message
- **WHEN** Glass is unavailable
- **THEN** tools SHALL return informative error messages
