# Proposal: Zoekt Client

## Why
Connect to Zoekt webserver for fast lexical/regex code search, complementing Qdrant's semantic search.

## What
Create `app.zoekt.client` module with:
- `ZoektClient` HTTP client for Zoekt JSON API
- Connection to configurable ZOEKT_URL
- Query support: substring, regex, boolean operators
- Result parsing with file matches and line ranges

## Impact
- **Enables**: Lexical search for patterns regex can't express semantically
- **Depends On**: config-and-health (ZOEKT_URL config)
- **PRD Reference**: Complements FR-R1

## Out of Scope
- Zoekt indexing
- MCP tools
