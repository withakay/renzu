## ADDED Requirements

### Requirement: Configuration via environment variables
The application SHALL load all configuration from environment variables using Pydantic Settings with validation and sensible defaults.

#### Scenario: Default configuration values
- **WHEN** no environment variables are set
- **THEN** the application SHALL use default values: `HTTP_PORT=8000`, `MCP_PORT=9000`, `QDRANT_URL=http://localhost:6333`, `LOG_LEVEL=INFO`

#### Scenario: Environment variable override
- **WHEN** `HTTP_PORT=3000` is set in the environment
- **THEN** the application SHALL use port 3000 for the HTTP server

#### Scenario: Invalid configuration value
- **WHEN** an invalid value is provided for a typed configuration field
- **THEN** the application SHALL fail to start with a clear validation error message

### Requirement: Configuration class structure
Configuration SHALL be organized in a Pydantic Settings class accessible throughout the application.

#### Scenario: Configuration is injectable
- **WHEN** application code needs configuration
- **THEN** it SHALL access a typed configuration object via dependency injection
