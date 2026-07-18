# Indicator Engine Interface Specification

This document defines the frozen contract for the **Indicator Engine** (Sprint 3). Every technical indicator algorithm MUST implement this standard abstract interface.

---

## 1. Abstract Indicator Interface Contract

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class IndicatorResult(BaseModel):
    symbol: str
    timeframe: str
    indicator: str
    parameters: Dict[str, Any]
    value: Any  # Union[float, Dict[str, float]]
    timestamp: str
    version: str = "1.0.0"

class BaseIndicator(ABC):
    """
    Abstract Base Class for all Quantitative Technical Indicators.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Indicator unique identifier name (e.g. 'EMA', 'RSI')."""
        pass

    @abstractmethod
    def calculate(
        self,
        candles: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> IndicatorResult:
        """
        Calculates indicator outputs from input OHLCV candle list.
        """
        pass
```

---

## 2. Standardized Indicators List for Sprint 3

The following 6 indicators MUST be implemented following `BaseIndicator`:

1. **EMA (Exponential Moving Average)**: Parameter `period` (e.g. 20, 50, 200).
2. **RSI (Relative Strength Index)**: Parameter `period` (e.g. 14).
3. **VWAP (Volume Weighted Average Price)**: Parameters `anchor` (`day`, `week`).
4. **ATR (Average True Range)**: Parameter `period` (e.g. 14).
5. **MACD (Moving Average Convergence Divergence)**: Parameters `fast_period` (12), `slow_period` (26), `signal_period` (9). Output: `{ macd, signal, histogram }`.
6. **Bollinger Bands**: Parameters `period` (20), `std_dev` (2.0). Output: `{ upper, middle, lower }`.
