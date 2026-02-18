## ADDED Requirements

### Requirement: src/app package layout
The project SHALL use a `src/app/` package layout with logical subpackages for each domain.

#### Scenario: Standard package structure exists
- **WHEN** the project is initialized
- **THEN** the following directories SHALL exist: `src/app/__init__.py`, `src/app/config/`, `src/app/indexing/`, `src/app/retrieval/`, `src/app/glass/`, `src/app/mcp/`, `src/app/api/`

### Requirement: FastAPI application entry point
The project SHALL provide a FastAPI application instance at `app.main:app` that can be started with uvicorn.

#### Scenario: Application starts successfully
- **WHEN** `uvicorn app.main:app` is executed
- **THEN** the application SHALL start without errors on the configured port

#### Scenario: Application has no routes initially
- **WHEN** the application starts
- **THEN** it SHALL respond with 404 for any path except future health endpoints

### Requirement: Test directory structure
The project SHALL provide a `tests/` directory structure mirroring the `src/app/` layout.

#### Scenario: Test directories exist
- **WHEN** the project is initialized
- **THEN** the following directories SHALL exist: `tests/__init__.py`, `tests/conftest.py`, `tests/unit/`, `tests/integration/`

### Requirement: Python version pinning
The project SHALL pin the Python version via `.python-version` file compatible with uv.

#### Scenario: Python version is specified
- **WHEN** uv sync is run
- **THEN** it SHALL use the Python version specified in `.python-version`

### Requirement: uv sync produces working environment
Running `uv sync` SHALL produce a working development environment.

#### Scenario: uv sync succeeds
- **WHEN** `uv sync` is executed
- **THEN** all dependencies SHALL be installed without errors

#### Scenario: Application runs after sync
- **WHEN** `uv sync` completes and `uv run uvicorn app.main:app` is executed
- **THEN** the application SHALL start successfully
