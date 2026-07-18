from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.database.models import TradeLog

class TradeRepository(BaseRepository[TradeLog]):
    def __init__(self, db: Session):
        super().__init__(db, TradeLog)

    def get_all_trades(self) -> List[TradeLog]:
        return self.db.query(TradeLog).order_by(TradeLog.entry_time.desc()).all()

    def get_closed_trades(self) -> List[TradeLog]:
        return self.db.query(TradeLog).filter(TradeLog.status == "CLOSED").all()

    def get_open_trades(self) -> List[TradeLog]:
        return self.db.query(TradeLog).filter(TradeLog.status == "OPEN").all()
