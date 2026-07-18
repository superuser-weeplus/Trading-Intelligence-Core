from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.database.models import PriceHistory

class PriceRepository(BaseRepository[PriceHistory]):
    def __init__(self, db: Session):
        super().__init__(db, PriceHistory)

    def get_prices(self, symbol: str, timeframe: str, limit: int = 500) -> List[PriceHistory]:
        return self.db.query(PriceHistory).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timeframe == timeframe
        ).order_by(PriceHistory.timestamp.asc()).all()[-limit:]

    def get_latest_price(self, symbol: str, timeframe: str) -> Optional[PriceHistory]:
        return self.db.query(PriceHistory).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timeframe == timeframe
        ).order_by(PriceHistory.timestamp.desc()).first()

    def check_exists(self, symbol: str, timeframe: str, timestamp: datetime) -> bool:
        return self.db.query(PriceHistory).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timeframe == timeframe,
            PriceHistory.timestamp == timestamp
        ).first() is not None
