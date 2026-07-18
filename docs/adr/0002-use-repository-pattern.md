# ADR 0002: Enforce Repository Pattern Across All Data Access

- **Status**: Approved
- **Date**: 2026-07-18
- **Context**: Direct database queries or CSV reads in service and API layers lead to tight coupling and make storage migration or offline testing difficult.
- **Decision**: Mandate the Repository Pattern (`BaseRepository` interfaces) for all data operations. Services MUST NOT query storage directly.
- **Consequences**: Enables effortless switching between Supabase SQL, local CSV files, and Mock datasets without modifying service code.
