## ADDED Requirements

### Requirement: JSON structured logging
The application SHALL output logs in JSON format with structured fields.

#### Scenario: Log output is JSON
- **WHEN** the application logs a message
- **THEN** the output SHALL be valid JSON with fields: `timestamp`, `level`, `message`, `logger`

#### Scenario: Log level is configurable
- **WHEN** `LOG_LEVEL=DEBUG` is set
- **THEN** debug-level messages SHALL appear in the output

### Requirement: Request logging
HTTP requests SHALL be logged with relevant metadata.

#### Scenario: Request logged with metadata
- **WHEN** an HTTP request is received
- **THEN** the log SHALL include: `method`, `path`, `status_code`, `duration_ms`
