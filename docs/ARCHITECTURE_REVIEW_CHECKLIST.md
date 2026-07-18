# Architecture Review Checklist

This checklist is used by the **Architecture Review Agent** to audit system changes and prevent architectural decay.

---

## Architectural Audit Items

### 1. Layered Architecture & Decoupling
- [ ] Are all API routers placed inside `app/api/v1/`?
- [ ] Does the presentation layer call Services instead of accessing Repositories or DB directly?
- [ ] Does the Service layer interact exclusively with `BaseRepository` abstractions?

### 2. Repository Pattern Verification
- [ ] Are new data models backed by a Repository interface?
- [ ] Is fallback logic (Supabase -> SQLite -> CSV) maintained cleanly inside the Repository?

### 3. API Versioning & Envelope
- [ ] Are all routes prefixed with `/api/v1/`?
- [ ] Does every response conform to the frozen Unified Response Envelope?

### 4. Latency & Performance Bounds
- [ ] Does Health API measure and return connection ping latency in milliseconds (`latency_ms`)?
- [ ] Are connection pings optimized to complete within performance bounds (< 50ms)?

### 5. Error Code Registration
- [ ] Are all thrown exceptions mapped to a registered code in `ERROR_CODES.md` (`MD001`, `MT001`, `DB001`, etc.)?
