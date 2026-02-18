# Proposal: MCP Server

## Why
Expose code-context capabilities via MCP protocol for AI agent integration.

## What
Create `app.mcp.server` module with:
- FastMCP server instance
- Stdio transport support
- Server metadata and capabilities
- Tool registration framework

## Impact
- **Enables**: AI agents can discover and call tools
- **PRD Reference**: Section 8 (MCP Tools)

## Out of Scope
- Individual tool implementations
