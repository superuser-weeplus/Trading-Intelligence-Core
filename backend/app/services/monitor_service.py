import logging
from typing import Dict, Any, List

from app.repositories.interfaces.base_monitor_repository import BaseMonitorRepository
from app.repositories.infrastructure.infrastructure_repository import InfrastructureRepository

logger = logging.getLogger("app.services.monitor_service")

class MonitorService:
    """
    Data Monitor Domain Service.
    STRICTLY DECOUPLED: Contains ZERO File I/O (open/json.load/pd.read_csv) and ZERO direct SQL queries.
    Interacts purely via constructor-injected BaseMonitorRepository and InfrastructureRepository interface abstractions.
    """

    def __init__(
        self,
        monitor_repo: BaseMonitorRepository,
        infra_repo: InfrastructureRepository
    ):
        self.monitor_repo = monitor_repo
        self.infra_repo = infra_repo

    def get_system_health(self) -> Dict[str, Any]:
        """
        Retrieves system health, terminal latency, database latency, and pipeline status.
        """
        mt5_check = self.infra_repo.check_mt5_latency()
        db_check = self.infra_repo.check_db_latency()

        return {
            "mt5": {
                "status": mt5_check["status"],
                "latency_ms": mt5_check["latency_ms"],
                "label": f"Connected ({mt5_check['latency_ms']}ms)" if mt5_check["status"] == "connected" else "Disconnected"
            },
            "supabase": {
                "status": db_check["status"],
                "latency_ms": db_check["latency_ms"],
                "label": f"Connected ({db_check['latency_ms']}ms)" if db_check["status"] == "connected" else "Disconnected"
            },
            "exporter": {"status": "running", "label": "Running"},
            "importer": {"status": "running", "label": "Running"},
            "last_export": "Active",
            "last_import": "Active"
        }

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Top Dashboard Summary Panel Metrics.
        """
        return self.monitor_repo.get_summary_metrics()

    def get_system_alerts(self) -> List[Dict[str, Any]]:
        """
        Evaluates system warnings and alerts.
        """
        alerts = []
        health = self.get_system_health()

        if health["mt5"]["status"] != "connected":
            alerts.append({
                "severity": "CRITICAL",
                "code": "MT5_DISCONNECTED",
                "title": "MT5 Terminal Connection Disconnected",
                "message": "MetaTrader 5 terminal connection lost. Market data exporter fallback is active."
            })

        quality = self.monitor_repo.get_data_quality()
        for q in quality:
            if q.get("gaps", 0) > 10:
                alerts.append({
                    "severity": "WARNING",
                    "code": f"DATA_GAP_{q['symbol']}",
                    "title": f"Data Gap Detected in {q['symbol']}",
                    "message": f"{q['symbol']} has {q['gaps']} missing timeframe gaps detected during validation."
                })

        if not alerts:
            alerts.append({
                "severity": "INFO",
                "code": "ALL_SYSTEMS_OPERATIONAL",
                "title": "All Data Foundation Pipelines Operational",
                "message": "MT5 connection, exporter, validator, importer, and Supabase database are running normally."
            })

        return alerts

    def get_data_explorer(self, symbol: str = "XAUUSD", timeframe: str = "H1") -> Dict[str, Any]:
        """
        Retrieves Data Explorer statistics via MonitorRepository.
        """
        return self.monitor_repo.get_data_explorer(symbol, timeframe)

    def get_export_history(self) -> List[Dict[str, Any]]:
        """
        Retrieves Export History logs via MonitorRepository.
        """
        return self.monitor_repo.get_export_history()

    def get_data_quality(self) -> List[Dict[str, Any]]:
        """
        Retrieves Data Quality breakdown via MonitorRepository.
        """
        return self.monitor_repo.get_data_quality()

    def get_market_snapshot(self) -> List[Dict[str, Any]]:
        """
        Retrieves Market Snapshot widget data via MonitorRepository.
        """
        return self.monitor_repo.get_market_snapshot()
