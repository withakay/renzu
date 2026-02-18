# Proposal: Glass Tools

## Why
Expose Glass symbol navigation through application service layer.

## What
Create `app.glass.service` module with:
- `GlassService` class wrapping GlassClient
- Typed request/response models
- Graceful fallback when Glass unavailable
- Response formatting for downstream consumers

## Impact
- **Enables**: Symbol navigation for MCP and HTTP API
- **Depends On**: glass-client
- **PRD Reference**: FR-G1/G2/G3

## Out of Scope
- MCP protocol implementation
