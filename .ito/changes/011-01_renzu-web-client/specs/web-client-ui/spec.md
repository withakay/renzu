<!-- ITO:START -->
## ADDED Requirements

### Requirement: UI exposes core Renzu workflows

The system SHALL provide a browser-based interface that lets users execute indexing, semantic search, snippet retrieval, and Glass symbol operations without using the command line.

#### Scenario: Index repository from UI

- **WHEN** a user submits repo id, path, and globs in the indexing form
- **THEN** the UI sends a request to `POST /v1/index` and displays structured success or error output

#### Scenario: Execute semantic search from UI

- **WHEN** a user submits query, repo id, and optional filters
- **THEN** the UI sends a request to `POST /v1/search` and renders ordered hits with file path, line range, score, and text

#### Scenario: Fetch snippet from UI

- **WHEN** a user submits repo id, path, start/end lines, and context
- **THEN** the UI sends a request to `POST /v1/snippet` and displays snippet content and metadata

#### Scenario: Run Glass workflows from UI

- **WHEN** a user submits valid payloads for list symbols, describe symbol, or find references
- **THEN** the UI sends requests to corresponding `/v1/glass/*` endpoints and renders API payloads, including graceful unavailable states

### Requirement: UI provides predictable UX for API calls

The system SHALL provide consistent loading, error, and result states for all API operations.

#### Scenario: Request in flight

- **WHEN** an API mutation or query is running
- **THEN** the related UI section shows an in-progress state and prevents duplicate submits

#### Scenario: Request failure

- **WHEN** an API call fails due to validation, dependency, or server error
- **THEN** the UI shows a human-readable error summary and the raw API error payload

#### Scenario: Request success

- **WHEN** an API call succeeds
- **THEN** the UI shows formatted output and a copyable JSON view of the response
<!-- ITO:END -->
