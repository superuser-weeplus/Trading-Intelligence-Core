# Testing Strategy Specification

This document details the testing framework and quality assurance strategy for Trading Intelligence Core.

---

## 1. Testing Pyramid Architecture

```
       ▲
      / \     E2E / Dashboard Tests
     /   \    ---------------------
    / Integration \  Exporter ──► Importer Pipeline Tests
   /               \ -------------------------------------
  /   Unit Tests    \ Indicator Engine & Repository Tests
 /───────────────────\
```

---

## 2. Test Suites

### 1. Unit Testing (Backend Core & Indicators)
- **Scope**: Mathematical accuracy of Technical Indicators (EMA, RSI, VWAP, ATR, MACD, Bollinger), Data Models, and Validation Rules.
- **Tooling**: `pytest`
- **Location**: `backend/tests/unit/`

### 2. Integration Testing (Data Foundation Pipeline)
- **Scope**: End-to-end execution of `exporter.py` ──► `validator.py` ──► `importer.py` ──► Database bulk insertion.
- **Tooling**: `pytest` + SQLite / PostgreSQL Test Container
- **Location**: `backend/tests/integration/`

### 3. API Testing (FastAPI Endpoints)
- **Scope**: Response status codes, envelope structure, error handling, and parameter validation across `/api/v1/*`.
- **Tooling**: `FastAPI TestClient` / `pytest`
- **Location**: `backend/tests/api/`

### 4. Frontend Component Testing
- **Scope**: React component rendering, state changes, API mock handling, and quality meters.
- **Tooling**: `Jest` / `React Testing Library`
- **Location**: `frontend/src/__tests__/`
