import pandas as pd
from typing import List, Dict, Any, Optional

class TrendService:
    """
    Reusable domain service for Trend Analysis, Moving Averages, and Price Snapshot calculations.
    Eliminates duplicated trend & fallback calculation logic across repositories and services.
    """

    DEFAULT_FALLBACK_PRICES = {
        "XAUUSD": 4032.50,
        "GBPUSD": 1.2750,
        "EURUSD": 1.0850,
        "DXY": 104.20
    }

    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> Optional[float]:
        if len(prices) < period:
            return None
        return float(pd.Series(prices).rolling(window=period).mean().iloc[-1])

    @classmethod
    def determine_trend(cls, current_price: float, sma_value: Optional[float]) -> str:
        if sma_value is None:
            return "Neutral"
        return "Bullish" if current_price >= sma_value else "Bearish"

    @classmethod
    def get_fallback_price(cls, symbol: str) -> float:
        return cls.DEFAULT_FALLBACK_PRICES.get(symbol.upper(), 100.0)

    @classmethod
    def format_snapshot_item(
        cls,
        symbol: str,
        price: Optional[float],
        last_update: str,
        h1_trend: str,
        h4_trend: str
    ) -> Dict[str, Any]:
        final_price = price if price is not None else cls.get_fallback_price(symbol)
        return {
            "symbol": symbol.upper(),
            "price": round(final_price, 2),
            "last_update": last_update,
            "h1_trend": h1_trend,
            "h4_trend": h4_trend
        }
