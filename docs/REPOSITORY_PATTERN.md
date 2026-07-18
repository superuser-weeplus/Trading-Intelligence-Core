# Repository Pattern Specification

Trading Intelligence Core enforces the Repository Pattern to decouple business service logic from underlying data storage mechanisms.

---

## 1. Architectural Principle

```
┌────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)            │
└───────────────────────────┬────────────────────────────┘
                            │ (Depends only on Interface)
                            ▼
┌────────────────────────────────────────────────────────┐
│             BasePriceRepository (Interface)            │
└──────┬────────────────────┼────────────────────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Supabase    │     │     CSV      │     │     Mock     │
│  Repository  │     │  Repository  │     │  Repository  │
└──────────────┘     └──────────────┘     └──────────────┘
```

**CRITICAL RULE**: No Service, Engine, or API Router may directly query SQL databases, read CSV files, or parse JSON payloads. All data access MUST pass through a Repository implementation.

---

## 2. Standard Repository Interface Contract

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BasePriceRepository(ABC):

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch candle list for symbol and timeframe."""
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        """Fetch latest close price."""
        pass

    @abstractmethod
    def save_candles(self, candles: List[Dict[str, Any]]) -> bool:
        """Persist candles into storage."""
        pass
```

---

## 3. Concrete Repository Implementations

1. `SupabasePriceRepository`: Connects via SQLAlchemy ORM / Supabase Client to execute SQL queries on `market_prices`.
2. `CSVPriceRepository`: Reads and writes OHLCV data from `backend/market_data/output/{symbol}/{TF}.csv`.
3. `MockPriceRepository`: Generates synthetic price data for unit testing and offline development.
