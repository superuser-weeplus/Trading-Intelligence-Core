# API Standards Specification

All REST APIs in Trading Intelligence Core MUST follow these frozen API conventions.

---

## 1. Versioning Protocol

All API endpoints must be prefixed with `/api/v1/`:

```
http://localhost:8000/api/v1/{module}/{endpoint}
```

---

## 2. Route Groups

The API surface is categorized into 6 standard route groups:

| Route Group | Base Path | Description |
| :--- | :--- | :--- |
| **System** | `/api/v1/system` | Health checks, pipeline status, latency, export history, system alerts |
| **Market** | `/api/v1/market` | OHLCV prices, candle queries, symbol metadata, sync endpoints |
| **Analysis** | `/api/v1/analysis` | Quantitative indicator outputs, market structure analysis |
| **Signals** | `/api/v1/signals` | Trade signal alerts, entry/SL/TP triggers, strategy backtests |
| **AI** | `/api/v1/ai` | ML directional predictions, confidence scores, feature vectors |
| **Journal** | `/api/v1/journal` | Trade history logging, execution performance stats, P&L metrics |

---

## 3. Unified Response Envelope Standard

Every API endpoint response (both HTTP 200 Success and HTTP 4xx/5xx Error) MUST return the following JSON envelope format:

### Success Response Example (HTTP 200)
```json
{
  "success": true,
  "data": {
    "symbol": "XAUUSD",
    "timeframe": "H1",
    "rows": 5000
  },
  "error": null,
  "timestamp": "2026-07-18T16:00:00Z"
}
```

### Error Response Example (HTTP 400 / 500)
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "MD001",
    "message": "Missing Candle data for XAUUSD H1",
    "details": "Requested date range contains 50 missing bars"
  },
  "timestamp": "2026-07-18T16:00:00Z"
}
```

---

## 4. HTTP Status Codes Protocol

- `200 OK`: Request succeeded and returned valid envelope.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Invalid request parameters or contract validation failed.
- `404 Not Found`: Requested symbol, timeframe, or resource does not exist.
- `500 Internal Server Error`: Backend error (must detail error code in envelope).
