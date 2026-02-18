# Proposal: MCP Glass Tools

## Why
Expose symbol navigation as MCP tools for AI agents.

## What
Create `app.mcp.tools.glass` module with:
- `symbols_in_file(repo_id, path)` tool
- `symbol_references(symbol_id)` tool
- `symbol_definition(symbol_id)` tool
- Integration with GlassService

## Impact
- **Enables**: AI agents can navigate symbols
- **Depends On**: mcp-server, glass-tools
- **PRD Reference**: FR-MCP-3, FR-MCP-4, FR-MCP-5

## Out of Scope
- Retrieval tools
