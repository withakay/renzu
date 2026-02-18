# Proposal: Docker Infra Compose

## Why
Before building the code-context service, we need external dependencies (Qdrant, Glean, Glass) running locally. A dedicated infra compose file enables early development against real services.

## What
Create `docker/infra-compose.yml` with:
- Qdrant container (ports 6333 REST, 6334 gRPC)
- Glean server container (port 12345)
- Glass server container (port 12346)
- Ollama container (port 11434, optional profile)
- Named volumes for persistence
- Shared network configuration

## Impact
- **Enables**: Development against real dependencies
- **Requires**: Glean Docker build at `/Users/jack/Code/withakay/glean-docker`
- **PRD Reference**: Section 12, Milestone M0

## Out of Scope
- code-context service (handled in docker-full module)
- Production configuration
