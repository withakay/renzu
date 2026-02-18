## Why

We need a clean project structure to build the Code Context Service. Without a well-organized scaffold, we risk inconsistent module layout, unclear entry points, and difficulty onboarding contributors. This change establishes the foundational structure before adding any business logic.

## What Changes

- Create `src/app/` package layout with logical subpackages
- Add minimal FastAPI application entry point (`app/main.py`)
- Add basic uvicorn configuration for development
- Create placeholder test structure (`tests/`)
- Add `.python-version` for uv/Python version pinning
- Ensure `uv sync` produces a working development environment

## Capabilities

### New Capabilities

- `project-layout`: Standard Python package structure with `src/app/` layout,清晰的职责划分（config, indexing, retrieval, glass, mcp, api），and test directory structure

### Modified Capabilities

None (first change).

## Impact

- Creates new directory structure under `src/`
- Adds minimal FastAPI app that starts but has no routes
- No breaking changes (greenfield project)
- Enables all subsequent changes to build on this structure
