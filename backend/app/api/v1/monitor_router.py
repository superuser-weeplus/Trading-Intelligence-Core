from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any

from app.api.deps import get_monitor_service
from app.services.monitor_service import MonitorService

router = APIRouter(prefix="/api/v1/monitor", tags=["Data Monitor v1"])

@router.get("/health")
def get_health(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns system connection health and latency in milliseconds.
    """
    return service.get_system_health()

@router.get("/summary")
def get_summary_metrics(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns top Dashboard Summary metrics panel data.
    """
    return service.get_summary_metrics()

@router.get("/alerts")
def get_system_alerts(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns active system warning and critical alerts.
    """
    return service.get_system_alerts()

@router.get("/explorer")
def get_explorer_data(
    symbol: str = Query("XAUUSD"),
    timeframe: str = Query("H1"),
    service: MonitorService = Depends(get_monitor_service)
):
    """
    Returns Data Explorer statistics including Data Freshness.
    """
    return service.get_data_explorer(symbol, timeframe)

@router.get("/history")
def get_export_history(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns Export History table log entries.
    """
    return service.get_export_history()

@router.get("/quality")
def get_data_quality(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns Data Quality check breakdown per symbol.
    """
    return service.get_data_quality()

@router.get("/snapshot")
def get_market_snapshot(service: MonitorService = Depends(get_monitor_service)):
    """
    Returns Today's Market Snapshot widget data.
    """
    return service.get_market_snapshot()
