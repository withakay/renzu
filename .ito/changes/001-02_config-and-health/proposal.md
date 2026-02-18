## Why

Services need configuration from environment variables and health endpoints for orchestration. Without these, the service cannot be deployed or monitored. Docker Compose and orchestration tools require `/healthz` and `/readyz` endpoints to manage service lifecycle.

## What Changes

- Add Pydantic Settings class for configuration (`app/config.py`)
- Load configuration from environment variables with sensible defaults
- Add structured JSON logging setup (`app/logging_config.py`)
- Add `/healthz` endpoint (always 200 if process is alive)
- Add `/readyz` endpoint (200 if dependencies are reachable, 503 otherwise)
- Add basic dependency check stub for Qdrant (ping endpoint)

## Capabilities

### New Capabilities

- `configuration`: Pydantic Settings-based configuration loaded from environment variables with validation and defaults
- `health-endpoints`: `/healthz` (liveness) and `/readyz` (readiness) endpoints for orchestration health checks
- `structured-logging`: JSON-formatted structured logging with configurable log level

### Modified Capabilities

None (adds to `project-layout` from 001-01).

## Impact

- Adds `app/config.py`, `app/logging_config.py`, `app/dependencies.py`
- Adds `/healthz` and `/readyz` routes to FastAPI app
- Requires `QDRANT_URL`, `HTTP_PORT`, `LOG_LEVEL` environment variables (with defaults)
- Enables Docker health checks in subsequent changes
