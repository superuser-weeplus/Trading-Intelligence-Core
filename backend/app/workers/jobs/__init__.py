import logging
from app.database.connection import LocalSessionLocal, init_supabase_engine, SupabaseSessionLocal
from app.services.market_service import MarketService
from app.services.alert_service import AlertService
from app.ai_engine.manager import AIEngineManager
from app.ai_engine.pipeline import FeaturePipeline
import pandas as pd

logger = logging.getLogger("app.workers.jobs")

async def execute_job(job_name: str, payload: dict) -> None:
    """
    Main job execution routing. Resolves DB sessions and calls Services/Engines.
    """
    logger.info(f"Worker executing job '{job_name}' with payload: {payload}")
    
    # 1. Sync Market Data Job
    if job_name == "sync_market":
        symbol = payload.get("symbol")
        timeframe = payload.get("timeframe", "H1")
        count = payload.get("count", 100)
        
        db = LocalSessionLocal()
        try:
            service = MarketService(db)
            new_bars = service.sync_market_data(symbol, timeframe, count)
            logger.info(f"Sync Job Completed. Added {new_bars} bars for {symbol} ({timeframe})")
        finally:
            db.close()
            
    # 2. Check Alerts Job
    elif job_name == "check_alerts":
        # Initialize Supabase
        init_supabase_engine()
        db_local = LocalSessionLocal()
        db_supabase = SupabaseSessionLocal() if SupabaseSessionLocal else db_local
        
        try:
            service = AlertService(db_supabase, db_local)
            triggered = service.check_alerts()
            logger.info(f"Alert Scanner Job Completed. Triggered {triggered} alerts.")
        finally:
            db_local.close()
            if SupabaseSessionLocal:
                db_supabase.close()
                
    # 3. Train AI Model Job
    elif job_name == "train_model":
        symbol = payload.get("symbol")
        timeframe = payload.get("timeframe", "H1")
        model_name = payload.get("model_name", "random_forest")
        
        db = LocalSessionLocal()
        try:
            # Fetch price history from SQLite
            from app.repositories.price_repository import PriceRepository
            repo = PriceRepository(db)
            prices = repo.get_prices(symbol, timeframe, 1000)
            
            if len(prices) < 150:
                logger.warning(f"Insufficient data to train. Syncing EURUSD fallback to train {symbol} ({timeframe}).")
                # Trigger sync
                market_service = MarketService(db)
                market_service.sync_market_data(symbol, timeframe, 1000)
                prices = repo.get_prices(symbol, timeframe, 1000)
                
            if len(prices) < 150:
                logger.error(f"Cannot train model: insufficient bars ({len(prices)}).")
                return
                
            df = pd.DataFrame([{
                "timestamp": p.timestamp, "open": p.open, "high": p.high,
                "low": p.low, "close": p.close, "volume": p.volume
            } for p in prices])
            
            # Prepare feature pipeline
            X, y, timestamps = FeaturePipeline.prepare_data(df)
            
            # Initialize model from manager registry
            model = AIEngineManager.get_model_class(model_name)()
            hyperparameters = AIEngineManager.load_hyperparameters(model_name)
            
            # Train
            metrics = model.train(X, y, hyperparameters)
            
            # Save versioned model
            AIEngineManager.save_model_version(
                model=model,
                symbol=symbol,
                timeframe=timeframe,
                metrics=metrics,
                feature_list=list(X.columns)
            )
            logger.info(f"Model Training Job Completed. Metrics: {metrics}")
        finally:
            db.close()
            
    else:
        logger.error(f"Unknown job name: {job_name}")
