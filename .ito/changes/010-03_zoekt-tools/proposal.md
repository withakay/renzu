# Proposal: Zoekt MCP Tools

## Why
Expose Zoekt lexical search as MCP tools for AI agents.

## What
Create `app.mcp.tools.zoekt` module with:
- `code_search_lexical(query, repo_id?, file_pattern?, top_k?)` tool
- Query syntax: regex, boolean (and/or/not), file: filters
- Result formatting with citations matching semantic search

## Impact
- **Enables**: AI agents can use regex/pattern search
- **Depends On**: mcp-server, zoekt-client
- **PRD Reference**: FR-MCP (extended)

## Out of Scope
- Vector search tools
