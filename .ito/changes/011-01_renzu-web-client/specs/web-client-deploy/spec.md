<!-- ITO:START -->
## ADDED Requirements

### Requirement: Web client builds to static assets

The system SHALL support a production static build for the web client.

#### Scenario: Build succeeds in CI/local

- **WHEN** a maintainer runs the frontend build command
- **THEN** optimized static assets are generated without requiring backend runtime inside the frontend container

### Requirement: Web client is containerized for local deployment

The system SHALL provide a Docker image for serving the static web client.

#### Scenario: Container serves frontend over HTTP

- **WHEN** the web client container starts
- **THEN** it serves the built static assets on a configurable port using a static web server

#### Scenario: API base URL is configurable

- **WHEN** the container is started with an API base URL environment variable or build arg
- **THEN** the frontend uses that value for API requests without code changes
<!-- ITO:END -->
