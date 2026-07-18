# ADR 0004: Enforce Prefix API Versioning (/api/v1/)

- **Status**: Approved
- **Date**: 2026-07-18
- **Context**: As the platform evolves across future sprints, breaking API changes could break client dashboards, mobile apps, or external trading bots.
- **Decision**: All REST endpoints MUST be explicitly versioned via URI path prefix (`/api/v1/`).
- **Consequences**: Protects backward compatibility and permits seamless migration when `v2` or `v3` endpoints are introduced.
