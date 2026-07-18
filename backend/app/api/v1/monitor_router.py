from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database.connection import get_local_db
from app.services.monitor_service import MonitorService

router = APIRouter(prefix="/api/v1/monitor", tags=["Data Monitor v1"])

@router.get("/health")
def get_health(db: Session = Depends(get_local_db)):
    """
    Returns system connection health and latency in milliseconds (latency_ms).
    """
    service = MonitorService(db)
    return service.get_system_health()

@router.get("/summary")
def get_summary_metrics(db: Session = Depends(get_local_db)):
    """
    Returns top Dashboard Summary metrics panel data.
    """
    service = MonitorService(db)
    return service.get_summary_metrics()

@router.get("/alerts")
def get_system_alerts(db: Session = Depends(get_local_db)):
    """
    Returns active system warning and critical alerts (🟡 Warning / 🔴 Critical).
    """
    service = MonitorService(db)
    return service.get_system_alerts()

@router.get("/explorer")
def get_explorer_data(
    symbol: str = Query("XAUUSD"),
    timeframe: str = Query("H1"),
    db: Session = Depends(get_local_db)
):
    """
    Returns Data Explorer statistics including Data Freshness.
    """
    service = MonitorService(db)
    return service.get_data_explorer(symbol, timeframe)

@router.get("/history")
def get_export_history(db: Session = Depends(get_local_db)):
    """
    Returns Export History table log entries.
    """
    service = MonitorService(db)
    return service.get_export_history()

@router.get("/quality")
def get_data_quality(db: Session = Depends(get_local_db)):
    """
    Returns Data Quality check breakdown per symbol.
    """
    service = MonitorService(db)
    return service.get_data_quality()

@router.get("/snapshot")
def get_market_snapshot(db: Session = Depends(get_local_db)):
    """
    Returns Today's Market Snapshot widget data.
    """
    service = MonitorService(db)
    return service.get_market_snapshot()
