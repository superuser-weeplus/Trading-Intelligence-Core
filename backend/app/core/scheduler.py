import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.workers import worker

logger = logging.getLogger("app.core.scheduler")

# Active symbols configured for sync & evaluation
ACTIVE_SYMBOLS = ["XAUUSDc", "GBPUSDc", "EURUSDc", "USDJPYc", "DX-Y.NYB"]

async def run_automated_pipeline():
    """
    Automated pipeline triggered by scheduler:
    1. Triggers market sync for all symbols.
    2. Runs alert scanner trigger.
    """
    logger.info("Scheduler triggering automated market sync and evaluation pipeline...")
    
    for symbol in ACTIVE_SYMBOLS:
        # Enqueue price history sync to SQLite
        await worker.enqueue("sync_market", {"symbol": symbol, "count": 100})
        
    # Enqueue alert checks
    await worker.enqueue("check_alerts", {})

class SystemScheduler:
    _scheduler = None

    @classmethod
    def start(cls):
        if cls._scheduler is not None:
            return
            
        cls._scheduler = AsyncIOScheduler()
        
        # Schedule the automated pipeline to run every 1 hour
        # (Can also schedule at specific daily time, e.g. cron: hour=8, minute=0)
        cls._scheduler.add_job(
            run_automated_pipeline,
            "interval",
            minutes=60,
            id="automated_pipeline_hourly"
        )
        
        # Immediate run on startup for dev testing
        cls._scheduler.add_job(
            run_automated_pipeline,
            "date",
            id="automated_pipeline_startup"
        )
        
        cls._scheduler.start()
        logger.info("System Scheduler started successfully.")

    @classmethod
    def stop(cls):
        if cls._scheduler is not None:
            cls._scheduler.shutdown()
            cls._scheduler = None
            logger.info("System Scheduler stopped.")
