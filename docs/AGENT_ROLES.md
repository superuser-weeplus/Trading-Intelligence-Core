# AI Development Organization — Roles & Responsibilities Specification

To ensure institutional quality, zero self-grading bias, and modular scalability, Trading Intelligence Core operates under a **7-Role AI Development Organization**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                     AI Development Organization                        │
├───────────────────────────────────┬────────────────────────────────────┤
│ 1. Product Owner (USER)           │ 2. System Architect (ChatGPT)      │
│ 3. Implementation (Antigravity)   │ 4. Code Review Agent               │
│ 5. QA/Test Agent                  │ 6. Architecture Review Agent       │
│ 7. Trading Domain / Quant Agent   │                                    │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 1. Role Matrix & Responsibilities

### 1. Product Owner (The USER)
- **Primary Responsibility**: Project vision, business objectives, feature approval, sprint priorities, final acceptance criteria.
- **Deliverables**: User requests, sprint objectives, business rules.

### 2. System Architect (ChatGPT)
- **Primary Responsibility**: High-level platform design, ADR creation, technology stack selection, macro system architecture.
- **Deliverables**: `ARCHITECTURE.md`, `REPOSITORY_PATTERN.md`, ADR records.

### 3. Implementation Engineer (Antigravity)
- **Primary Responsibility**: Pair programming, executing code changes, building modules, refactoring, frontend UI, backend services.
- **Deliverables**: Python modules (`app/`), React components (`frontend/`), pipeline scripts (`market_data/`).

### 4. Code Review Agent
- **Primary Responsibility**: Inspecting pull requests and code changes for code cleanlines, SOLID adherence, type hints, security, and formatting.
- **Deliverables**: `CODE_REVIEW_GUIDELINES.md` audits, code refactoring recommendations.

### 5. QA/Test Agent
- **Primary Responsibility**: Verifying system health, writing unit tests, running integration tests, testing API response envelopes.
- **Deliverables**: `TESTING_STRATEGY.md`, test suites (`tests/`), validation logs.

### 6. Architecture Review Agent
- **Primary Responsibility**: Enforcing Repository Pattern compliance, API versioning (`/api/v1/`), latency bounds, and error codes.
- **Deliverables**: `ARCHITECTURE_REVIEW_CHECKLIST.md` audits.

### 7. Trading Domain / Quant Research Agent
- **Primary Responsibility**: Validating mathematical formulas for indicators (EMA, RSI, VWAP, ATR, MACD, Bollinger), preventing lookahead bias, verifying candle gap handling.
- **Deliverables**: `TRADING_DOMAIN_REVIEW.md`, quantitative formulas, indicator verification datasets.
