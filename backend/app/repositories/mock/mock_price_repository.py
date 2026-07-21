import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.repositories.interfaces.base_price_repository import BasePriceRepository

class MockPriceRepository(BasePriceRepository):
    """
    Mock Price Repository implementation generating synthetic candles for testing & offline development.
    """

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self._stored_candles: Dict[str, List[Dict[str, Any]]] = {}

    def get_candles(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict[str, Any]]:
        key = f"{symbol.upper()}_{timeframe.upper()}"
        if key in self._stored_candles and self._stored_candles[key]:
            return self._stored_candles[key][-limit:]

        # Generate synthetic price series
        base_price = 4000.0 if "XAU" in symbol.upper() else (1.2500 if "GBP" in symbol.upper() else 1.0800)
        dates = pd.date_range(end=datetime.now(), periods=min(limit, 500), freq="1h")
        candles = []
        current_price = base_price

        for dt in dates:
            change = np.random.normal(0, 0.5)
            open_p = current_price
            close_p = open_p + change
            high_p = max(open_p, close_p) + abs(np.random.normal(0, 0.2))
            low_p = min(open_p, close_p) - abs(np.random.normal(0, 0.2))
            current_price = close_p

            candles.append({
                "timestamp": dt.isoformat(),
                "open": round(open_p, 4),
                "high": round(high_p, 4),
                "low": round(low_p, 4),
                "close": round(close_p, 4),
                "volume": float(np.random.randint(100, 1000)),
                "spread": 1.0
            })

        self._stored_candles[key] = candles
        return candles

    def get_latest_price(self, symbol: str, timeframe: str = "H1") -> Optional[float]:
        candles = self.get_candles(symbol, timeframe, limit=1)
        return candles[-1]["close"] if candles else 1.0

    def save_candles(self, candles: List[Dict[str, Any]], symbol: str = "XAUUSD", timeframe: str = "H1") -> bool:
        key = f"{symbol.upper()}_{timeframe.upper()}"
        if key not in self._stored_candles:
            self._stored_candles[key] = []
        self._stored_candles[key].extend(candles)
        return True

    def check_exists(self, symbol: str, timeframe: str, timestamp: datetime) -> bool:
        key = f"{symbol.upper()}_{timeframe.upper()}"
        if key not in self._stored_candles:
            return False
        ts_str = timestamp.isoformat()
        return any(c["timestamp"] == ts_str for c in self._stored_candles[key])
