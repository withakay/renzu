# Proposal: Full Docker Compose

## Why
Provide complete stack composition for deployment including code-context service.

## What
Create `docker/compose.yml` with:
- All infra services (Qdrant, Glean, Glass, Ollama optional)
- code-context service with HTTP + MCP ports
- Dockerfile for code-context
- Volume mounts for workspace access
- Network configuration

## Impact
- **Enables**: One-command stack deployment
- **Depends On**: All modules
- **PRD Reference**: Section 12 (Docker)

## Out of Scope
- Production orchestration (Kubernetes)
