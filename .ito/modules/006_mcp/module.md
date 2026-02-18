# MCP

## Purpose
Model Context Protocol server implementation. Exposes code intelligence tools to agent harnesses (OpenCode, Codex CLI, Claude Code).

## Scope
- MCP protocol implementation (stdio or HTTP)
- Tool registration and discovery
- `code_search` tool
- `code_snippet` tool
- `symbols_in_file` tool (Glass)
- `symbol_references` tool (Glass)
- `symbol_definition` tool (Glass)

## Depends On
- core
- retrieval
- glass

## Changes
- [ ] 006-01_mcp-server
- [ ] 006-02_mcp-retrieval-tools
- [ ] 006-03_mcp-glass-tools
