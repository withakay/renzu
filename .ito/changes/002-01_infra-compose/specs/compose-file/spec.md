## ADDED Requirements

### Requirement: Qdrant service in compose
The compose file SHALL include a Qdrant service with REST and gRPC ports exposed.

#### Scenario: Qdrant is accessible
- **WHEN** `docker compose -f docker/infra-compose.yml up -d` is run
- **THEN** Qdrant SHALL be accessible at `http://localhost:6333` (REST) and `localhost:6334` (gRPC)

### Requirement: Glean and Glass services
The compose file SHALL include Glean server and Glass server services.

#### Scenario: Glass server is accessible
- **WHEN** the compose stack is running
- **THEN** Glass server SHALL be accessible at `localhost:12346`

### Requirement: Ollama optional profile
The compose file SHALL include Ollama as an optional profile.

#### Scenario: Ollama not started by default
- **WHEN** `docker compose -f docker/infra-compose.yml up -d` is run without profile
- **THEN** Ollama SHALL NOT be running

#### Scenario: Ollama started with profile
- **WHEN** `docker compose -f docker/infra-compose.yml --profile ollama up -d` is run
- **THEN** Ollama SHALL be accessible at `localhost:11434`

### Requirement: Named volumes for persistence
The compose file SHALL use named volumes for Qdrant data.

#### Scenario: Data persists across restarts
- **WHEN** the compose stack is stopped and restarted
- **THEN** previously indexed data SHALL still be available in Qdrant
