---
name: "renzu-mcp-cli"
description: "CLI for the Renzu MCP server. Call tools, list resources, and get prompts."
---

# renzu-mcp CLI

## Tool Commands

### code_search

Semantic code search with optional repo/path/language filters

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool code_search --query <value> --repo-id <value> --path-prefix <value> --language <value> --top-k <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--query` | string | yes |  |
| `--repo-id` | string | yes |  |
| `--path-prefix` | string | no | JSON string |
| `--language` | string | no | JSON string |
| `--top-k` | integer | no |  |

### code_snippet

Fetch a repository-relative snippet by inclusive line range

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool code_snippet --repo-id <value> --path <value> --start-line <value> --end-line <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--repo-id` | string | yes |  |
| `--path` | string | yes |  |
| `--start-line` | integer | yes |  |
| `--end-line` | integer | yes |  |

### code_search_lexical

Lexical/regex code search with Zoekt query syntax

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool code_search_lexical --query <value> --repo-id <value> --file-pattern <value> --top-k <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--query` | string | yes |  |
| `--repo-id` | string | yes |  |
| `--file-pattern` | string | no | JSON string |
| `--top-k` | integer | no |  |

### symbols_in_file

List symbols in a repository file

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool symbols_in_file --repo-id <value> --path <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--repo-id` | string | yes |  |
| `--path` | string | yes |  |

### symbol_definition

Find the definition location for a symbol

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool symbol_definition --symbol-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--symbol-id` | string | yes |  |

### symbol_references

Find reference locations for a symbol

```bash
uv run --with fastmcp python renzu-mcp-cli.py call-tool symbol_references --symbol-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--symbol-id` | string | yes |  |

## Utility Commands

```bash
uv run --with fastmcp python renzu-mcp-cli.py list-tools
uv run --with fastmcp python renzu-mcp-cli.py list-resources
uv run --with fastmcp python renzu-mcp-cli.py read-resource <uri>
uv run --with fastmcp python renzu-mcp-cli.py list-prompts
uv run --with fastmcp python renzu-mcp-cli.py get-prompt <name> [key=value ...]
```
