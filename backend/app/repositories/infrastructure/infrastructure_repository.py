import os
import time
import shutil
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger("app.repositories.infrastructure_repository")

class InfrastructureRepository:
    """
    Repository dedicated to infrastructure health monitoring:
    MT5 latency checks, Database connection latency, Disk space usage, and pipeline health.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def check_mt5_latency(self) -> Dict[str, Any]:
        """
        Pings MT5 Terminal and measures connection latency in milliseconds.
        """
        start = time.perf_counter()
        connected = False
        try:
            import MetaTrader5 as mt5
            if mt5.initialize():
                connected = True
                mt5.shutdown()
        except Exception as e:
            logger.warning(f"MT5 ping failed: {e}")
            connected = False

        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "status": "connected" if connected else "disconnected",
            "latency_ms": latency_ms if connected else 0
        }

    def check_db_latency(self) -> Dict[str, Any]:
        """
        Pings Database (Supabase Cloud / SQLite) and measures connection latency in milliseconds.
        """
        start = time.perf_counter()
        connected = False
        try:
            if self.db:
                self.db.execute(text("SELECT 1"))
                connected = True
            else:
                from app.database.connection import LocalSessionLocal
                session = LocalSessionLocal()
                session.execute(text("SELECT 1"))
                session.close()
                connected = True
        except Exception as e:
            logger.warning(f"Database latency check failed: {e}")
            connected = False

        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "status": "connected" if connected else "disconnected",
            "latency_ms": latency_ms if connected else 0
        }

    def check_disk_usage(self, path: str = ".") -> Dict[str, Any]:
        """
        Calculates disk usage metrics (total, used, free, usage_pct).
        """
        try:
            stat = shutil.disk_usage(path)
            usage_pct = round((stat.used / stat.total) * 100, 2)
            return {
                "total_gb": round(stat.total / (1024 ** 3), 2),
                "used_gb": round(stat.used / (1024 ** 3), 2),
                "free_gb": round(stat.free / (1024 ** 3), 2),
                "usage_pct": usage_pct
            }
        except Exception as e:
            logger.warning(f"Failed to check disk usage for path {path}: {e}")
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_pct": 0}
