import pandas as pd
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.repositories.price_repository import PriceRepository
from app.data_collector.collector import MT5Collector
from app.indicator_engine.indicators import TechnicalIndicators
from app.database.models import PriceHistory

class MarketService:
    def __init__(self, db: Session):
        self.repo = PriceRepository(db)
        self.collector = MT5Collector()

    def sync_market_data(self, symbol: str, timeframe: str, count: int = 500) -> int:
        """
        Synchronizes historical candles from MT5 or Yahoo Finance and saves to local SQLite.
        """
        # Fetch rates from collector
        df = self.collector.fetch_historical_data(symbol, timeframe, count)
        
        new_records = 0
        for _, row in df.iterrows():
            timestamp = row['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
                
            # Deduplicate using repository
            exists = self.repo.check_exists(symbol, timeframe, timestamp)
            if not exists:
                price_record = PriceHistory(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume']),
                    spread=float(row['spread'])
                )
                self.repo.create(price_record)
                new_records += 1
                
        return new_records

    def get_prices(self, symbol: str, timeframe: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Returns price candles. If empty, automatically triggers sync.
        """
        prices = self.repo.get_prices(symbol, timeframe, limit)
        if not prices:
            self.sync_market_data(symbol, timeframe, limit)
            prices = self.repo.get_prices(symbol, timeframe, limit)

        return [{
            "timestamp": p.timestamp.isoformat(),
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
            "spread": p.spread
        } for p in prices]

    def get_indicators(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """
        Retrieves prices from repository and calculates indicators on-the-fly.
        """
        prices = self.repo.get_prices(symbol, timeframe, 500)
        if not prices:
            raise ValueError(f"No historical price data found for {symbol} ({timeframe}). Sync first.")

        df = pd.DataFrame([{
            "timestamp": p.timestamp,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume
        } for p in prices])

        # Calculate indicators on the fly
        df_ind = TechnicalIndicators.apply_all(df)
        
        import math
        # Convert df rows to list of dicts
        last_rows = df_ind.tail(100).to_dict(orient="records")
        for r in last_rows:
            if isinstance(r.get('timestamp'), datetime):
                r['timestamp'] = r['timestamp'].isoformat()
            
            # replace NaN floats with None for JSON compliance
            for key, value in r.items():
                if isinstance(value, float) and math.isnan(value):
                    r[key] = None
        return last_rows
