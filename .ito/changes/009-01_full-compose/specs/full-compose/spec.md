## ADDED Requirements

### Requirement: code-context service
The compose file SHALL include the code-context service.

#### Scenario: Service is defined
- **WHEN** `docker compose up` is run
- **THEN** code-context SHALL start with HTTP and MCP ports exposed

### Requirement: Port configuration
The code-context service SHALL expose configured ports.

#### Scenario: Ports are exposed
- **WHEN** the service starts
- **THEN** HTTP port (8000) and MCP port (9000) SHALL be accessible

### Requirement: Volume mounts
The compose file SHALL mount workspace for indexing.

#### Scenario: Workspace is mounted
- **WHEN** the service starts
- **THEN** configured workspace path SHALL be accessible inside container

### Requirement: Network configuration
Services SHALL communicate on shared network.

#### Scenario: Services can reach each other
- **WHEN** code-context needs Qdrant
- **THEN** it SHALL reach it via internal network hostname

### Requirement: Depends_on configuration
code-context SHALL depend on infra services.

#### Scenario: Services start in order
- **WHEN** compose up is run
- **THEN** Qdrant SHALL start before code-context
