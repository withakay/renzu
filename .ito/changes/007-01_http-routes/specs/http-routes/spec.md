## ADDED Requirements

### Requirement: Index endpoint
The API SHALL provide POST /v1/index to trigger indexing.

#### Scenario: Index is triggered
- **WHEN** POST /v1/index with `{repo_id, path, globs}` is received
- **THEN** indexing SHALL be triggered and a job ID returned

### Requirement: Search endpoint
The API SHALL provide POST /v1/search for semantic search.

#### Scenario: Search returns results
- **WHEN** POST /v1/search with `{query, repo_id, top_k}` is received
- **THEN** search results SHALL be returned as JSON

### Requirement: Snippet endpoint
The API SHALL provide POST /v1/snippet for file retrieval.

#### Scenario: Snippet is returned
- **WHEN** POST /v1/snippet with `{repo_id, path, start_line, end_line}` is received
- **THEN** file content SHALL be returned

### Requirement: Glass endpoints
The API SHALL provide Glass endpoints.

#### Scenario: List symbols endpoint
- **WHEN** POST /v1/glass/list_symbols with `{repo_id, path}` is received
- **THEN** symbols SHALL be returned

### Requirement: Error handling
The API SHALL return structured error responses.

#### Scenario: Error is formatted
- **WHEN** an error occurs
- **THEN** response SHALL include `{"error": "...", "detail": "..."}`
