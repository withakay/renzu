## ADDED Requirements

### Requirement: Healthz endpoint for liveness
The application SHALL provide a `/healthz` endpoint that indicates the process is alive.

#### Scenario: Healthz returns 200
- **WHEN** a GET request is made to `/healthz`
- **THEN** the response SHALL have status 200 and body `{"status": "ok"}`

### Requirement: Readyz endpoint for readiness
The application SHALL provide a `/readyz` endpoint that indicates the application is ready to serve requests.

#### Scenario: All dependencies healthy
- **WHEN** a GET request is made to `/readyz` and all dependencies are reachable
- **THEN** the response SHALL have status 200 and body `{"status": "ready"}`

#### Scenario: Qdrant not reachable
- **WHEN** a GET request is made to `/readyz` and Qdrant is not reachable
- **THEN** the response SHALL have status 503 and body `{"status": "not ready", "checks": {"qdrant": "unhealthy"}}`

### Requirement: Dependency health checks
The readiness check SHALL verify connectivity to external dependencies.

#### Scenario: Qdrant health check
- **WHEN** the readiness check runs
- **THEN** it SHALL attempt to connect to Qdrant and report its status
