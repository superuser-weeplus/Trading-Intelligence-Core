from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_local_db, get_supabase_db
from app.config import settings
from app.services.market_service import MarketService
from app.services.journal_service import JournalService
from app.services.alert_service import AlertService
from app.ai_engine.manager import AIEngineManager
from app.ai_engine.pipeline import FeaturePipeline
from app.ai_engine.llm_helper import LLMHelper
from app.backtesting.engine import BacktestEngine
from app.strategies import StrategyRegistry
from app.workers import worker

app = FastAPI(title="Trading Intelligence Platform API")

# Configure CORS so Next.js frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start and Stop background worker and scheduler on startup/shutdown
@app.on_event("startup")
async def startup_event():
    # Start background job worker
    await worker.start()
    
    # Start system automated scheduler
    from app.core.scheduler import SystemScheduler
    SystemScheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    # Stop background job worker
    await worker.stop()
    
    # Stop system automated scheduler
    from app.core.scheduler import SystemScheduler
    SystemScheduler.stop()

llm_helper = LLMHelper()

# --- Symbol Translation Helper (Exness Cent Accounts Suffix Mapping) ---
SYMBOL_MAP = {
    "XAUUSD": "XAUUSDc",
    "GBPUSD": "GBPUSDc",
    "EURUSD": "EURUSDc",
    "USDJPY": "USDJPYc",
    "DXY": "DX-Y.NYB"
}

def translate_symbol(symbol: str) -> str:
    return SYMBOL_MAP.get(symbol.upper(), symbol)

# --- Data Monitor Dashboard Routes (Sprint 2 & 2.1) ---
from app.api.v1.monitor_router import router as monitor_router_v1

app.include_router(monitor_router_v1)

# Legacy backward compatibility endpoints (redirecting to v1)
@app.get("/api/monitor/health")
def legacy_get_monitor_health(db: Session = Depends(get_local_db)):
    return MonitorService(db).get_system_health()

@app.get("/api/monitor/explorer")
def legacy_get_monitor_explorer(symbol: str = Query("XAUUSD"), timeframe: str = Query("H1"), db: Session = Depends(get_local_db)):
    return MonitorService(db).get_data_explorer(symbol, timeframe)

@app.get("/api/monitor/history")
def legacy_get_monitor_history(db: Session = Depends(get_local_db)):
    return MonitorService(db).get_export_history()

@app.get("/api/monitor/quality")
def legacy_get_monitor_quality(db: Session = Depends(get_local_db)):
    return MonitorService(db).get_data_quality()

# --- Market Data Routes ---

@app.post("/api/market/sync")
def sync_market_data(
    symbol: str = Query(..., description="e.g. EURUSD, GBPUSD, DXY"),
    timeframe: str = Query("H1", description="M1, M5, H1, D1"),
    count: int = Query(500, description="Number of historical candles to fetch"),
    db: Session = Depends(get_local_db)
):
    try:
        mapped_symbol = translate_symbol(symbol)
        service = MarketService(db)
        new_records = service.sync_market_data(mapped_symbol, timeframe, count)
        return {"success": True, "message": f"Synced {new_records} new bars for {symbol} ({timeframe})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/prices")
def get_prices(
    symbol: str = Query(..., description="EURUSD, GBPUSD, DXY"),
    timeframe: str = Query("H1"),
    limit: int = Query(500),
    db: Session = Depends(get_local_db)
):
    try:
        mapped_symbol = translate_symbol(symbol)
        service = MarketService(db)
        return service.get_prices(mapped_symbol, timeframe, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Technical Indicators Routes ---

@app.get("/api/indicators")
def get_indicators(
    symbol: str = Query(...),
    timeframe: str = Query("H1"),
    db: Session = Depends(get_local_db)
):
    try:
        mapped_symbol = translate_symbol(symbol)
        service = MarketService(db)
        return service.get_indicators(mapped_symbol, timeframe)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- AI & Machine Learning Routes ---

@app.post("/api/ai/train")
async def train_model(
    symbol: str = Query(...),
    timeframe: str = Query("H1")
):
    """
    Asynchronously enqueues the training job in the background worker queue.
    """
    mapped_symbol = translate_symbol(symbol)
    await worker.enqueue("train_model", {
        "symbol": mapped_symbol,
        "timeframe": timeframe,
        "model_name": settings.ACTIVE_AI_MODEL
    })
    return {"success": True, "message": f"Enqueued training job for {symbol} ({timeframe}) using {settings.ACTIVE_AI_MODEL}"}

@app.get("/api/ai/predict")
def get_prediction(
    symbol: str = Query(...),
    timeframe: str = Query("H1"),
    db: Session = Depends(get_local_db)
):
    mapped_symbol = translate_symbol(symbol)
    
    # 1. Fetch raw prices
    from app.repositories.price_repository import PriceRepository
    price_repo = PriceRepository(db)
    prices = price_repo.get_prices(mapped_symbol, timeframe, 100)
    
    if len(prices) < 30:
        raise HTTPException(status_code=400, detail="Insufficient price data to run prediction features.")
        
    import pandas as pd
    df = pd.DataFrame([{
        "timestamp": p.timestamp, "open": p.open, "high": p.high,
        "low": p.low, "close": p.close, "volume": p.volume
    } for p in prices])
    
    # 2. Load latest model using manager
    model = AIEngineManager.load_latest_model(mapped_symbol, timeframe, settings.ACTIVE_AI_MODEL)
    
    # 3. Extract latest feature row via pipeline
    X_latest = FeaturePipeline.prepare_latest_row(df)
    
    # 4. Predict
    pred_df = model.predict(X_latest)
    pred_res = pred_df.iloc[0].to_dict()
    
    # 5. Add indicators context for LLM narrative
    df_ind = FeaturePipeline.run_indicators(df)
    latest_ind = df_ind.tail(1).to_dict(orient="records")[0]
    
    # 6. Generate LLM Narrative Advice
    indicators_dict = {
        "close": latest_ind["close"],
        "rsi_14": latest_ind["rsi_14"],
        "macd_hist": latest_ind["macd_hist"],
        "bb_percent": latest_ind["bb_percent"],
        "atr_14": latest_ind["atr_14"]
    }
    
    rationale = llm_helper.generate_market_rationale(mapped_symbol, timeframe, indicators_dict, pred_res)
    pred_res["llm_rationale"] = rationale
    
    return pred_res

@app.post("/api/ai/chat")
def chat_strategy_advisor(
    message: str = Body(embed=True),
    current_state: dict = Body(default={})
):
    response = llm_helper.chat_with_strategy_advisor(message, current_state)
    return {"response": response}

# --- Strategy Lab & Backtesting Routes ---

@app.get("/api/strategies")
def get_strategies():
    return StrategyRegistry.get_available_strategies()

@app.post("/api/backtest")
def run_backtest(
    symbol: str = Body(...),
    timeframe: str = Body("H1"),
    strategy: str = Body(...),
    initial_capital: float = Body(10000.0),
    commission: float = Body(0.0001),
    stop_loss_pct: float = Body(0.02),
    take_profit_pct: float = Body(0.04)
):
    mapped_symbol = translate_symbol(symbol)
    res = BacktestEngine.run_backtest(
        symbol=mapped_symbol,
        timeframe=timeframe,
        strategy=strategy,
        initial_capital=initial_capital,
        commission=commission,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# --- Trading Journal Routes (Supabase DB) ---

@app.get("/api/journal")
def get_journal(db: Session = Depends(get_supabase_db)):
    service = JournalService(db)
    return service.get_all_trades()

@app.post("/api/journal")
def log_trade(trade_data: dict = Body(...), db: Session = Depends(get_supabase_db)):
    try:
        if "symbol" in trade_data:
            trade_data["symbol"] = translate_symbol(trade_data["symbol"])
        service = JournalService(db)
        return service.create_trade(trade_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/journal/close/{trade_id}")
def close_trade(trade_id: int, exit_data: dict = Body(...), db: Session = Depends(get_supabase_db)):
    try:
        service = JournalService(db)
        return service.close_trade(trade_id, exit_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/journal/stats")
def get_journal_stats(db: Session = Depends(get_supabase_db)):
    service = JournalService(db)
    return service.get_journal_stats()

# --- Alert Engine Routes (Supabase DB) ---

@app.get("/api/alerts")
def get_alerts(
    db: Session = Depends(get_supabase_db),
    db_local: Session = Depends(get_local_db)
):
    service = AlertService(db, db_local)
    return service.get_all_alerts()

@app.post("/api/alerts")
def create_alert(
    alert_data: dict = Body(...),
    db: Session = Depends(get_supabase_db),
    db_local: Session = Depends(get_local_db)
):
    try:
        if "symbol" in alert_data:
            alert_data["symbol"] = translate_symbol(alert_data["symbol"])
        service = AlertService(db, db_local)
        return service.create_alert(alert_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/alerts/logs")
def get_alert_logs(
    db: Session = Depends(get_supabase_db),
    db_local: Session = Depends(get_local_db)
):
    service = AlertService(db, db_local)
    return service.get_alert_logs()

@app.post("/api/alerts/check")
def trigger_alert_check(
    db: Session = Depends(get_supabase_db),
    db_local: Session = Depends(get_local_db)
):
    service = AlertService(db, db_local)
    triggered = service.check_alerts()
    return {"success": True, "triggered_count": triggered}
