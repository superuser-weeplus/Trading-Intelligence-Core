# Data Contracts Specification

This document defines the frozen data models and schemas used across Trading Intelligence Core. All modules (Ingestion, Repositories, Indicator Engine, AI Models, APIs) MUST strictly adhere to these contract schemas.

---

## 1. Candle Data Model (`Candle`)

Represents a single standardized OHLCV bar.

### Schema Specification
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "timestamp": "2026-07-18T16:00:00Z",
  "open": 4030.50,
  "high": 4035.20,
  "low": 4028.10,
  "close": 4032.50,
  "tick_volume": 1250,
  "spread": 15,
  "real_volume": 0,
  "source": "MT5",
  "quality_score": 100
}
```

### Field Definitions
| Field | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Ticker symbol (e.g. XAUUSD, GBPUSD, EURUSD, DXY) | Yes |
| `timeframe` | `string` | Standard timeframe code (M1, M5, M15, H1, H4, D1) | Yes |
| `timestamp` | `ISO8601 UTC` | Timezone-aware ISO8601 UTC timestamp | Yes |
| `open` | `float` | Opening price | Yes |
| `high` | `float` | Highest price during timeframe | Yes |
| `low` | `float` | Lowest price during timeframe | Yes |
| `close` | `float` | Closing price | Yes |
| `tick_volume` | `integer` | Total tick updates count | Yes |
| `spread` | `integer` | Bid-Ask spread in points | Yes |
| `real_volume` | `integer` | Traded volume contracts (0 if unavailable) | Yes |
| `source` | `string` | Source system (`MT5`, `YAHOO`, `SYNTHETIC`) | Yes |
| `quality_score` | `integer` | Data quality score (0 to 100) | Yes |

---

## 2. Indicator Result Data Model (`IndicatorResult`)

Represents the calculated output of an indicator algorithm.

### Schema Specification
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "indicator": "RSI",
  "parameters": { "period": 14 },
  "value": {
    "rsi": 64.52,
    "state": "NEUTRAL"
  },
  "timestamp": "2026-07-18T16:00:00Z",
  "version": "1.0.0"
}
```

### Field Definitions
| Field | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Asset ticker symbol | Yes |
| `timeframe` | `string` | Timeframe code | Yes |
| `indicator` | `string` | Indicator name identifier (e.g. EMA, RSI, VWAP, ATR, MACD, BOLLINGER) | Yes |
| `parameters` | `dict` | Key-value dictionary of calculation parameters | Yes |
| `value` | `dict \| float` | Single numeric value or structured multi-output dictionary | Yes |
| `timestamp` | `ISO8601 UTC` | Candle closing timestamp corresponding to the result | Yes |
| `version` | `string` | Version of the indicator calculation logic | Yes |

---

## 3. Signal Data Model (`Signal`)

Represents a trading signal produced by quantitative rules or AI models.

### Schema Specification
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "signal_type": "BUY",
  "confidence": 0.85,
  "entry": 4032.50,
  "stop_loss": 4015.00,
  "take_profit": 4070.00,
  "timestamp": "2026-07-18T16:00:00Z"
}
```

### Field Definitions
| Field | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Ticker symbol | Yes |
| `timeframe` | `string` | Timeframe code | Yes |
| `signal_type` | `string` | Direction enum: `BUY`, `SELL`, `NEUTRAL` | Yes |
| `confidence` | `float` | Model confidence probability (0.0 to 1.0) | Yes |
| `entry` | `float` | Recommended entry price | Yes |
| `stop_loss` | `float` | Recommended stop loss price | Yes |
| `take_profit` | `float` | Recommended take profit price | Yes |
| `timestamp` | `ISO8601 UTC` | Time of signal generation | Yes |
