## ADDED Requirements

### Requirement: Symbols in file service
The service SHALL provide symbols_in_file with typed response.

#### Scenario: Service wraps client
- **WHEN** `symbols_in_file(repo_id, path)` is called
- **THEN** a validated response model SHALL be returned

### Requirement: Symbol definition service
The service SHALL provide symbol_definition.

#### Scenario: Definition is retrieved
- **WHEN** `symbol_definition(symbol_id)` is called
- **THEN** symbol definition location and details SHALL be returned

### Requirement: Symbol references service
The service SHALL provide symbol_references.

#### Scenario: References are retrieved
- **WHEN** `symbol_references(symbol_id)` is called
- **THEN** list of reference locations SHALL be returned

### Requirement: Graceful fallback
The service SHALL return informative responses when Glass unavailable.

#### Scenario: Unavailable returns message
- **WHEN** Glass is unavailable
- **THEN** a message indicating unavailability SHALL be returned
