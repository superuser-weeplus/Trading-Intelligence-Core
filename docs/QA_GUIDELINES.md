# QA & Testing Guidelines Specification

This document defines the Quality Assurance standards enforced by the **QA/Test Agent**.

---

## Quality Assurance Protocols

### 1. Unit Testing Protocol
- All technical indicator algorithms in Sprint 3 MUST include unit tests verifying numerical output against known reference benchmarks (e.g. TA-Lib or TradingView standard outputs).
- Edge cases MUST be tested: empty candle lists, single candle input, missing values, extreme price spikes.

### 2. Integration Testing Protocol
- Pipeline test suite MUST run end-to-end: `Exporter` ──► `Validator` ──► `Importer` ──► `Database`.
- Verification of bulk insert performance and duplicate handling.

### 3. API Response Envelope Testing Protocol
- All `/api/v1/*` endpoints MUST be tested with `FastAPI TestClient` for compliance with `API_STANDARDS.md`:
  - `success`: boolean
  - `data`: payload object or array
  - `error`: `null` or `{ "code": "...", "message": "..." }`
  - `timestamp`: ISO8601 UTC

### 4. Frontend Component QA Protocol
- Run `npx tsc --noEmit` to ensure 0 TypeScript compilation errors.
- Test fallback state handling when backend APIs are unreachable or disconnected.
