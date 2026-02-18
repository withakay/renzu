# HTTP API

## Purpose
FastAPI-based HTTP API for debugging and non-MCP clients. Mirrors MCP tool functionality as REST endpoints.

## Scope
- FastAPI app setup
- `/v1/index` - Trigger indexing
- `/v1/search` - Semantic search
- `/v1/snippet` - Fetch file span
- `/v1/glass/*` - Glass operations
- `/healthz`, `/readyz` - Health checks
- Request/response models (Pydantic)

## Depends On
- core
- mcp

## Changes
- [ ] 007-01_http-routes
