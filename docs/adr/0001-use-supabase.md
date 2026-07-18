# ADR 0001: Use Supabase / PostgreSQL as Primary Data Store

- **Status**: Approved
- **Date**: 2026-07-18
- **Context**: The platform requires a high-performance, scalable database for market data, indicators, and ML features with relational integrity and real-time capabilities.
- **Decision**: Adopt Supabase (PostgreSQL) as the primary cloud database engine with offline fallback to local SQLite.
- **Consequences**: Enables SQL analytical queries, vector extensions for AI, and seamless cloud synchronization.
