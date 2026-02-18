# Proposal: MCP Retrieval Tools

## Why
Expose search and snippet capabilities as MCP tools for AI agents.

## What
Create `app.mcp.tools.retrieval` module with:
- `code_search(query, repo_id, path_prefix?, language?, top_k?)` tool
- `code_snippet(repo_id, path, start_line, end_line)` tool
- Tool schemas with proper typing
- Integration with SearchService and SnippetService

## Impact
- **Enables**: AI agents can search code and fetch snippets
- **Depends On**: mcp-server, semantic-search, snippet-fetch
- **PRD Reference**: FR-MCP-1, FR-MCP-2

## Out of Scope
- Glass tools
