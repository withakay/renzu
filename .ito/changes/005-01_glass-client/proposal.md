# Proposal: Glass Client

## Why
Connect to Glass server for symbol navigation (definitions, references, document symbols).

## What
Create `app.glass.client` module with:
- `GlassClient` HTTP client wrapper
- Connection to configurable GLASS_URL
- Methods: `list_symbols(repo_id, path)`, `describe_symbol(symbol_id)`, `find_references(symbol_id)`
- Error handling for unavailable Glass

## Impact
- **Enables**: Symbol navigation for MCP tools
- **Depends On**: config-and-health (GLASS_URL config)
- **PRD Reference**: FR-G1/G2/G3 (Glass tools)

## Out of Scope
- MCP tool definitions
