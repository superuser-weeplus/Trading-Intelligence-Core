from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.database.connection import LocalBase, SupabaseBase

# --- Local SQLite Models ---

class PriceHistory(LocalBase):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, index=True, nullable=False)  # e.g., M1, M5, H1, D1
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    spread = Column(Float, default=0.0)

class TechnicalIndicator(LocalBase):
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    indicator_name = Column(String, nullable=False)  # e.g. "RSI", "MACD", "BB"
    values = Column(JSON, nullable=False)  # e.g. {"rsi": 30.5} or {"macd": 0.5, "signal": 0.4}

# --- Supabase Cloud Models ---

class AIPrediction(SupabaseBase):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    direction = Column(String, nullable=False)  # "UP", "DOWN", "HOLD"
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    feature_importance = Column(JSON, nullable=True)  # dict of features and weights
    llm_rationale = Column(String, nullable=True)     # Text summary from Gemini

class TradeLog(SupabaseBase):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    direction = Column(String, nullable=False)  # "BUY" or "SELL"
    size = Column(Float, nullable=False)        # Lot size
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, default=0.0)            # Profit and Loss
    commission = Column(Float, default=0.0)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)         # Comma-separated strings, e.g. "trend,fomo"
    emotional_state = Column(String, nullable=True)  # e.g. "disciplined", "greedy", "scared"
    status = Column(String, default="OPEN")     # "OPEN" or "CLOSED"

class Alert(SupabaseBase):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    metric = Column(String, nullable=False)       # e.g. "PRICE", "RSI", "MACD"
    operator = Column(String, nullable=False)     # ">", "<", "CROSS_ABOVE", "CROSS_BELOW"
    threshold = Column(Float, nullable=False)
    status = Column(String, default="ACTIVE")     # "ACTIVE", "TRIGGERED", "DISABLED"
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    logs = relationship("AlertLog", back_populates="alert", cascade="all, delete-orphan")

class AlertLog(SupabaseBase):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    triggered_value = Column(Float, nullable=False)
    message = Column(String, nullable=False)

    alert = relationship("Alert", back_populates="logs")

class MarketPrice(SupabaseBase):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    spread = Column(Float, default=0.0)

class DatasetManifest(SupabaseBase):
    __tablename__ = "dataset_manifests"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, index=True, nullable=False)
    total_bars = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    health_score = Column(Float, default=100.0)
    last_imported_at = Column(DateTime, default=datetime.utcnow)
