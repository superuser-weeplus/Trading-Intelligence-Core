from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.repositories.alert_repository import AlertRepository
from app.repositories.price_repository import PriceRepository
from app.database.models import Alert, AlertLog, PriceHistory
from app.indicator_engine.indicators import TechnicalIndicators

class AlertService:
    def __init__(self, db_supabase: Session, db_local: Session):
        self.alert_repo = AlertRepository(db_supabase)
        self.price_repo = PriceRepository(db_local)

    def get_all_alerts(self) -> List[Alert]:
        return self.alert_repo.get_all()

    def get_alert_logs(self, limit: int = 100) -> List[AlertLog]:
        return self.alert_repo.get_alert_logs(limit)

    def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        alert = Alert(
            symbol=alert_data["symbol"],
            metric=alert_data["metric"].upper(),
            operator=alert_data["operator"],
            threshold=float(alert_data["threshold"]),
            status="ACTIVE"
        )
        return self.alert_repo.create(alert)

    def check_alerts(self) -> int:
        """
        Scans active alert triggers and logs triggers.
        """
        active_alerts = self.alert_repo.get_active_alerts()
        if not active_alerts:
            return 0

        triggered_count = 0
        # Group by symbol to reduce indicator calculations
        by_symbol = {}
        for a in active_alerts:
            by_symbol.setdefault(a.symbol, []).append(a)

        for symbol, alerts in by_symbol.items():
            prices = self.price_repo.get_prices(symbol, "H1", 100)
            if not prices:
                continue

            # Convert to DataFrame and compute indicators
            import pandas as pd
            df = pd.DataFrame([{
                "timestamp": p.timestamp, "open": p.open, "high": p.high,
                "low": p.low, "close": p.close, "volume": p.volume
            } for p in prices])
            
            df_ind = TechnicalIndicators.apply_all(df)
            if df_ind.empty:
                continue

            latest = df_ind.tail(1).iloc[0]

            for a in alerts:
                # Resolve metric value
                metric_key = a.metric.lower()
                # Mapping metric options to actual dataframe keys
                metric_map = {
                    "price": "close",
                    "rsi": "rsi_14",
                    "atr": "atr_14"
                }
                mapped_key = metric_map.get(metric_key, metric_key)
                
                if mapped_key not in latest:
                    continue

                current_value = float(latest[mapped_key])
                triggered = False
                
                # Operator evaluation
                if a.operator == ">" and current_value > a.threshold:
                    triggered = True
                elif a.operator == "<" and current_value < a.threshold:
                    triggered = True
                elif a.operator == ">=" and current_value >= a.threshold:
                    triggered = True
                elif a.operator == "<=" and current_value <= a.threshold:
                    triggered = True
                elif a.operator == "==" and current_value == a.threshold:
                    triggered = True

                if triggered:
                    # Log trigger
                    log_entry = AlertLog(
                        alert_id=a.id,
                        symbol=a.symbol,
                        triggered_value=current_value,
                        triggered_at=datetime.utcnow(),
                        message=f"{a.symbol} {a.metric} {a.operator} {a.threshold} (Current: {current_value:.5f})"
                    )
                    self.alert_repo.log_alert_trigger(log_entry)
                    
                    # Update status
                    a.status = "TRIGGERED"
                    self.alert_repo.update()
                    triggered_count += 1

        return triggered_count
