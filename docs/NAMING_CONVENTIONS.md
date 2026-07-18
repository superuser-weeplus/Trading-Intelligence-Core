# Naming Conventions Specification

This document details the naming conventions across Database Schemas, Python Backend, TypeScript Frontend, and React Components.

---

## 1. Database Schemas & Tables

All database table names and column names MUST use `snake_case`.

### Table Schemas
- `market.candles`: OHLCV price history records
- `analysis.indicators`: Calculated technical indicator results
- `analysis.features`: Extracted ML feature vectors
- `signals.trade_signals`: Generated trading signal alerts
- `journal.trade_history`: Executed trade journal logs

---

## 2. Python Backend (`snake_case` & `PascalCase`)

- **Variables & Functions**: `snake_case` (e.g., `calculate_ema()`, `get_data_quality()`)
- **Modules & Files**: `snake_case` (e.g., `monitor_service.py`, `price_repository.py`)
- **Classes & Pydantic Models**: `PascalCase` (e.g., `MonitorRepository`, `CandleModel`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEFRAME`, `MAX_RETRIES`)

---

## 3. TypeScript Frontend (`camelCase` & `PascalCase`)

- **Variables & Functions**: `camelCase` (e.g., `fetchSystemHealth()`, `summaryMetrics`)
- **Types & Interfaces**: `PascalCase` (e.g., `SystemHealthData`, `DataExplorerData`)
- **Files & Services**: `snake_case` or `camelCase` (e.g., `monitor_service.ts`)

---

## 4. React Components (`PascalCase`)

All React component filenames and component declarations MUST use `PascalCase`:

- `SystemHealthView.tsx`
- `DataExplorerView.tsx`
- `ExportHistoryTable.tsx`
- `DataQualityView.tsx`
- `DashboardSummaryBar.tsx`
- `SystemAlertsBanner.tsx`
- `TodayMarketSnapshot.tsx`
