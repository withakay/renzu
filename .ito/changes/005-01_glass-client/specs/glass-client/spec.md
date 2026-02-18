## ADDED Requirements

### Requirement: Glass client connection
The client SHALL connect to configurable Glass server URL.

#### Scenario: Client connects to configured URL
- **WHEN** GlassClient is initialized
- **THEN** it SHALL use GLASS_URL from configuration

### Requirement: List symbols in file
The client SHALL list symbols in a given file.

#### Scenario: Symbols are listed
- **WHEN** `list_symbols(repo_id, path)` is called
- **THEN** a list of symbols with name, kind, range SHALL be returned

### Requirement: Describe symbol
The client SHALL describe a specific symbol.

#### Scenario: Symbol is described
- **WHEN** `describe_symbol(symbol_id)` is called
- **THEN** symbol details including definition location SHALL be returned

### Requirement: Find references
The client SHALL find references to a symbol.

#### Scenario: References are found
- **WHEN** `find_references(symbol_id)` is called
- **THEN** a list of reference locations SHALL be returned

### Requirement: Graceful degradation
The client SHALL handle Glass unavailability gracefully.

#### Scenario: Glass unavailable returns empty
- **WHEN** Glass server is not reachable
- **THEN** methods SHALL return empty results or raise recoverable errors
