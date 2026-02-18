## ADDED Requirements

### Requirement: Zoekt client connection
The client SHALL connect to configurable Zoekt webserver URL.

#### Scenario: Client connects to configured URL
- **WHEN** ZoektClient is initialized
- **THEN** it SHALL use ZOEKT_URL from configuration

### Requirement: JSON API search
The client SHALL support search via Zoekt JSON API.

#### Scenario: Search returns file matches
- **WHEN** `search("hello world")` is called
- **THEN** file matches with line ranges and context SHALL be returned

### Requirement: Regex query support
The client SHALL support regex queries.

#### Scenario: Regex query is executed
- **WHEN** `search("func\\w+\\(.*\\)")` is called
- **THEN** matching patterns SHALL be returned

### Requirement: Boolean operators
The client SHALL support boolean query operators.

#### Scenario: AND query is executed
- **WHEN** `search("import AND reactor")` is called
- **THEN** files containing both terms SHALL be returned

### Requirement: File pattern filter
The client SHALL support file pattern filtering.

#### Scenario: File pattern is applied
- **WHEN** `search("TODO file:*.py")` is called
- **THEN** only Python files SHALL be searched

### Requirement: Graceful unavailability
The client SHALL handle Zoekt unavailability gracefully.

#### Scenario: Zoekt unavailable returns empty
- **WHEN** Zoekt server is not reachable
- **THEN** search SHALL return empty results with warning log
