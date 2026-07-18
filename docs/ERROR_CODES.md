# Error Codes Registry Specification

All system errors, data validation failures, connection drops, and API exceptions MUST return a registered error code from this registry.

---

## Error Codes Registry Table

| Error Code | Category | Title | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`MD001`** | Market Data | Missing Candle | `WARNING` | Requested candle range contains missing bars or timeline gaps. |
| **`MD002`** | Market Data | Duplicate Candle | `WARNING` | Duplicate timestamps detected and purged during data validation. |
| **`MD003`** | Market Data | Timezone Error | `CRITICAL` | Input timestamp is not in UTC format or contains invalid timezone offset. |
| **`MT001`** | Infrastructure | MT5 Connection Lost | `CRITICAL` | Unable to connect to MetaTrader 5 terminal process. |
| **`DB001`** | Infrastructure | Database Timeout | `CRITICAL` | Supabase / PostgreSQL database query timed out or failed to connect. |
| **`API001`** | API Layer | Invalid Request | `ERROR` | Malformed request parameters, invalid payload schema, or bad query. |
| **`IE001`** | Indicator Engine | Calculation Error | `ERROR` | Insufficient candle bars to calculate technical indicator. |
