from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from app.repositories.trade_repository import TradeRepository
from app.database.models import TradeLog

class JournalService:
    def __init__(self, db: Session):
        self.repo = TradeRepository(db)

    def get_all_trades(self) -> List[TradeLog]:
        return self.repo.get_all_trades()

    def create_trade(self, trade_data: Dict[str, Any]) -> TradeLog:
        entry_time = trade_data["entry_time"]
        if isinstance(entry_time, str):
            entry_time = datetime.fromisoformat(entry_time)

        trade = TradeLog(
            symbol=trade_data["symbol"],
            direction=trade_data["direction"],
            size=float(trade_data["size"]),
            entry_time=entry_time,
            entry_price=float(trade_data["entry_price"]),
            status="OPEN",
            notes=trade_data.get("notes"),
            tags=trade_data.get("tags"),
            emotional_state=trade_data.get("emotional_state")
        )
        return self.repo.create(trade)

    def close_trade(self, trade_id: int, exit_data: Dict[str, Any]) -> TradeLog:
        trade = self.repo.get_by_id(trade_id)
        if not trade:
            raise ValueError(f"Trade log {trade_id} not found.")

        exit_time = exit_data["exit_time"]
        if isinstance(exit_time, str):
            exit_time = datetime.fromisoformat(exit_time)

        trade.exit_time = exit_time
        trade.exit_price = float(exit_data["exit_price"])
        trade.commission = float(exit_data.get("commission", 0.0))
        
        # PnL = (Exit - Entry) * Size for BUY, and (Entry - Exit) * Size for SELL
        raw_pnl = (trade.exit_price - trade.entry_price) * trade.size
        if trade.direction == "SELL":
            raw_pnl = -raw_pnl
            
        trade.pnl = raw_pnl - trade.commission
        trade.status = "CLOSED"
        trade.notes = exit_data.get("notes", trade.notes)
        trade.emotional_state = exit_data.get("emotional_state", trade.emotional_state)
        
        self.repo.update()
        return trade

    def get_journal_stats(self) -> Dict[str, Any]:
        closed_trades = self.repo.get_closed_trades()
        if not closed_trades:
            return {
                "total_trades": 0,
                "win_rate_pct": 0.0,
                "profit_factor": 1.0,
                "total_pnl": 0.0,
                "avg_gain": 0.0,
                "avg_loss": 0.0,
                "max_win": 0.0,
                "max_loss": 0.0
            }
            
        pnl_list = [t.pnl for t in closed_trades if t.pnl is not None]
        total_pnl = sum(pnl_list)
        total_trades = len(pnl_list)
        
        gains = [p for p in pnl_list if p > 0]
        losses = [p for p in pnl_list if p <= 0]
        
        win_count = len(gains)
        win_rate = win_count / total_trades if total_trades > 0 else 0.0
        
        avg_gain = sum(gains) / len(gains) if gains else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        
        profit_factor = sum(gains) / abs(sum(losses)) if losses and sum(losses) != 0 else sum(gains)
        
        return {
            "total_trades": total_trades,
            "win_rate_pct": win_rate * 100.0,
            "profit_factor": float(profit_factor),
            "total_pnl": float(total_pnl),
            "avg_gain": float(avg_gain),
            "avg_loss": float(avg_loss),
            "max_win": float(max(pnl_list) if pnl_list else 0.0),
            "max_loss": float(min(pnl_list) if pnl_list else 0.0)
        }
