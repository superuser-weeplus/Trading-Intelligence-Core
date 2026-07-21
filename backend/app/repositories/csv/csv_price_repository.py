import os
import time
import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.repositories.interfaces.base_price_repository import BasePriceRepository
from app.core.exceptions import RepositoryException

logger = logging.getLogger("app.repositories.csv_price_repository")

class CSVPriceRepository(BasePriceRepository):
    """
    Concrete CSV implementation of BasePriceRepository.
    Reads and writes OHLCV data from market_data/output/{symbol}/{TF}.csv.
    Includes in-memory TTL caching to prevent excessive disk reads.
    """

    def __init__(self, output_dir: Optional[str] = None, cache_ttl_seconds: int = 5):
        if output_dir:
            self.output_dir = output_dir
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "market_data", "output"))
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_csv_path(self, symbol: str, timeframe: str) -> str:
        return os.path.join(self.output_dir, symbol.upper(), f"{timeframe.upper()}.csv")

    def _load_dataframe(self, symbol: str, timeframe: str) -> pd.DataFrame:
        csv_path = self._get_csv_path(symbol, timeframe)
        cache_key = f"{symbol.upper()}_{timeframe.upper()}"
        now = time.time()

        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["df"]

        if not os.path.exists(csv_path):
            return pd.DataFrame()

        try:
            df = pd.read_csv(csv_path)
            if not df.empty and "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            self._cache[cache_key] = {"df": df, "timestamp": now}
            return df
        except Exception as e:
            logger.warning(f"Failed to read CSV at {csv_path}: {e}")
            return pd.DataFrame()

    def get_candles(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict[str, Any]]:
        df = self._load_dataframe(symbol, timeframe)
        if df.empty:
            return []

        sliced_df = df.tail(limit)
        results = []
        for _, row in sliced_df.iterrows():
            ts = row["timestamp"]
            ts_str = ts.isoformat() if isinstance(ts, (datetime, pd.Timestamp)) else str(ts)
            results.append({
                "timestamp": ts_str,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "spread": float(row.get("spread", 0.0))
            })
        return results

    def get_latest_price(self, symbol: str, timeframe: str = "H1") -> Optional[float]:
        df = self._load_dataframe(symbol, timeframe)
        if df.empty or "close" not in df.columns:
            return None
        return float(df["close"].iloc[-1])

    def save_candles(self, candles: List[Dict[str, Any]], symbol: str = "XAUUSD", timeframe: str = "H1") -> bool:
        if not candles:
            return True
        csv_path = self._get_csv_path(symbol, timeframe)
        try:
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            new_df = pd.DataFrame(candles)
            new_df.to_csv(csv_path, index=False)
            cache_key = f"{symbol.upper()}_{timeframe.upper()}"
            if cache_key in self._cache:
                del self._cache[cache_key]
            return True
        except Exception as e:
            logger.exception(f"Error saving candles to {csv_path}: {e}")
            raise RepositoryException(f"Failed to save candles to CSV: {e}")

    def check_exists(self, symbol: str, timeframe: str, timestamp: datetime) -> bool:
        df = self._load_dataframe(symbol, timeframe)
        if df.empty or "timestamp" not in df.columns:
            return False
        matches = df[df["timestamp"] == pd.to_datetime(timestamp)]
        return not matches.empty
