from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.database.models import Alert, AlertLog

class AlertRepository(BaseRepository[Alert]):
    def __init__(self, db: Session):
        super().__init__(db, Alert)

    def get_active_alerts(self) -> List[Alert]:
        return self.db.query(Alert).filter(Alert.status == "ACTIVE").all()

    def get_alert_logs(self, limit: int = 100) -> List[AlertLog]:
        return self.db.query(AlertLog).order_by(AlertLog.triggered_at.desc()).limit(limit).all()

    def log_alert_trigger(self, alert_log: AlertLog) -> AlertLog:
        self.db.add(alert_log)
        self.db.commit()
        self.db.refresh(alert_log)
        return alert_log
