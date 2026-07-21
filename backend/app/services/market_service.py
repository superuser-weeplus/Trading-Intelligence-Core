import math
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.repositories.interfaces.base_price_repository import BasePriceRepository
from app.data_collector.collector import MT5Collector
from app.indicator_engine.indicators import TechnicalIndicators
from app.core.exceptions import DataNotFoundException

class MarketService:
    """
    Market Data Service.
    Interacts strictly via constructor-injected BasePriceRepository abstraction.
    """

    def __init__(self, price_repo: BasePriceRepository, collector: Optional[MT5Collector] = None):
        self.repo = price_repo
        self.collector = collector if collector else MT5Collector()

    def sync_market_data(self, symbol: str, timeframe: str, count: int = 500) -> int:
        """
        Synchronizes historical candles from MT5 or Yahoo Finance and saves to repository.
        """
        df = self.collector.fetch_historical_data(symbol, timeframe, count)
        
        candles_to_save = []
        new_records = 0
        for _, row in df.iterrows():
            timestamp = row['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
                
            exists = self.repo.check_exists(symbol, timeframe, timestamp)
            if not exists:
                candles_to_save.append({
                    "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume']),
                    "spread": float(row['spread'])
                })
                new_records += 1

        if candles_to_save:
            self.repo.save_candles(candles_to_save, symbol=symbol, timeframe=timeframe)

        return new_records

    def get_prices(self, symbol: str, timeframe: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Returns price candles via repository. Automatically syncs if empty.
        """
        prices = self.repo.get_candles(symbol, timeframe, limit)
        if not prices:
            self.sync_market_data(symbol, timeframe, limit)
            prices = self.repo.get_candles(symbol, timeframe, limit)

        return prices

    def get_indicators(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """
        Retrieves prices from repository and calculates indicators.
        """
        prices = self.repo.get_candles(symbol, timeframe, 500)
        if not prices:
            raise DataNotFoundException(f"No historical price data found for {symbol} ({timeframe}). Sync first.")

        df = pd.DataFrame(prices)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        df_ind = TechnicalIndicators.apply_all(df)
        
        last_rows = df_ind.tail(100).to_dict(orient="records")
        for r in last_rows:
            if isinstance(r.get('timestamp'), (datetime, pd.Timestamp)):
                r['timestamp'] = r['timestamp'].isoformat()
            
            for key, value in r.items():
                if isinstance(value, float) and math.isnan(value):
                    r[key] = None
        return last_rows
