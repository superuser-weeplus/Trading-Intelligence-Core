import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.repositories.interfaces.base_price_repository import BasePriceRepository
from app.database.models import PriceHistory
from app.core.exceptions import RepositoryException

logger = logging.getLogger("app.repositories.supabase_price_repository")

class SupabasePriceRepository(BasePriceRepository):
    """
    Concrete Supabase / PostgreSQL implementation of BasePriceRepository using SQLAlchemy ORM.
    Fully optimizes queries at database level using .limit(limit).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_candles(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict[str, Any]]:
        try:
            # Optimize DB query: limit at database level descending, then reverse for chronological order
            records = self.db.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timeframe == timeframe
            ).order_by(desc(PriceHistory.timestamp)).limit(limit).all()

            chronological_records = sorted(records, key=lambda x: x.timestamp)
            return [{
                "timestamp": p.timestamp.isoformat() if isinstance(p.timestamp, datetime) else str(p.timestamp),
                "open": float(p.open),
                "high": float(p.high),
                "low": float(p.low),
                "close": float(p.close),
                "volume": float(p.volume),
                "spread": float(p.spread)
            } for p in chronological_records]
        except Exception as e:
            logger.exception(f"Error querying candles for {symbol} ({timeframe}): {e}")
            raise RepositoryException(f"Database query error: {e}")

    def get_latest_price(self, symbol: str, timeframe: str = "H1") -> Optional[float]:
        try:
            record = self.db.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timeframe == timeframe
            ).order_by(desc(PriceHistory.timestamp)).first()

            return float(record.close) if record else None
        except Exception as e:
            logger.exception(f"Error fetching latest price for {symbol}: {e}")
            return None

    def save_candles(self, candles: List[Dict[str, Any]], symbol: str = "XAUUSD", timeframe: str = "H1") -> bool:
        if not candles:
            return True
        try:
            records = []
            for item in candles:
                ts = item["timestamp"]
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                record = PriceHistory(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=ts,
                    open=float(item["open"]),
                    high=float(item["high"]),
                    low=float(item["low"]),
                    close=float(item["close"]),
                    volume=float(item.get("volume", 0.0)),
                    spread=float(item.get("spread", 0.0))
                )
                records.append(record)
            self.db.bulk_save_objects(records)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error saving candles to database: {e}")
            raise RepositoryException(f"Failed to bulk save price records: {e}")

    def check_exists(self, symbol: str, timeframe: str, timestamp: datetime) -> bool:
        try:
            return self.db.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timeframe == timeframe,
                PriceHistory.timestamp == timestamp
            ).first() is not None
        except Exception as e:
            logger.warning(f"Error checking price existence for {symbol} at {timestamp}: {e}")
            return False
