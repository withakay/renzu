# Docker Infra

## Purpose
External infrastructure services needed for development. Provides Docker Compose configuration for Qdrant, Glean, and Glass without the code-context service.

## Scope
- Qdrant container (ports 6333/6334)
- Glean server container
- Glass server container
- Ollama container (optional profile)
- Volume management for persistence
- Network configuration

## Depends On
- core

## Changes
- [ ] 002-01_infra-compose
