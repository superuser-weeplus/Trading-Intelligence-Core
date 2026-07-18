# Time & Timezone Policy Specification

Timezone inconsistencies create severe bugs in quantitative trading, backtesting, and AI data engineering. Trading Intelligence Core enforces a strict time policy across all components.

---

## 1. Core Rules

1. **Store Everything in UTC**: All timestamps stored in Database tables, CSV files, and JSON payloads MUST be in Universal Coordinated Time (UTC).
2. **Frontend Local Display Only**: Conversion to user local timezone (e.g. Asia/Bangkok UTC+7) is strictly limited to UI presentation layer in React components.
3. **Never Store Broker Local Time**: Broker local time (e.g. MT5 Server Time GMT+2/GMT+3) MUST be converted to UTC immediately upon ingestion at the Exporter level.
4. **ISO8601 Format Standard**: Timestamps must be serialized using ISO8601 format with explicit `Z` suffix or offset: `2026-07-18T16:00:00Z`.
5. **Always Timezone-Aware**: Python `datetime` objects MUST be timezone-aware (`timezone.utc`). Naive datetimes are strictly prohibited.

---

## 2. Python Code Implementation Rule

```python
from datetime import datetime, timezone

# CORRECT (Timezone-aware UTC)
now_utc = datetime.now(timezone.utc)
iso_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

# INCORRECT (Forbidden - Naive datetime)
now_naive = datetime.now() # FORBIDDEN
```

---

## 3. Database & File Persistence Standard

- PostgreSQL / Supabase column type: `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`)
- Dataframes & CSV: Saved as `YYYY-MM-DD HH:MM:SS` (UTC) or ISO8601 string.
