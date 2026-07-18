import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.indicator_engine.indicators import TechnicalIndicators
from app.ai_engine.pipeline import FeaturePipeline
from app.backtesting.engine import BacktestEngine

def test_technical_indicators():
    # Create mock price data
    dates = pd.date_range(start="2026-01-01", periods=100, freq="1h")
    # Sine wave close price with some trend
    close_prices = 100.0 + np.sin(np.linspace(0, 10, 100)) * 5 + np.linspace(0, 2, 100)
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.5,
        "high": close_prices + 1.0,
        "low": close_prices - 1.0,
        "close": close_prices,
        "volume": np.random.randint(100, 1000, 100)
    })
    
    df_ind = TechnicalIndicators.apply_all(df)
    
    # Assert standard indicators exist
    assert "sma_20" in df_ind.columns
    assert "ema_9" in df_ind.columns
    assert "rsi_14" in df_ind.columns
    assert "macd" in df_ind.columns
    assert "bb_upper" in df_ind.columns
    assert "atr_14" in df_ind.columns
    
    # Check bounds
    assert df_ind["rsi_14"].dropna().min() >= 0
    assert df_ind["rsi_14"].dropna().max() <= 100

def test_feature_pipeline():
    dates = pd.date_range(start="2026-01-01", periods=100, freq="1h")
    close_prices = 100.0 + np.sin(np.linspace(0, 10, 100)) * 5
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.5,
        "high": close_prices + 1.0,
        "low": close_prices - 1.0,
        "close": close_prices,
        "volume": np.random.randint(100, 1000, 100)
    })
    
    X, y, timestamps = FeaturePipeline.prepare_data(df)
    
    # Check sizes and targets
    assert len(X) > 0
    assert len(X) == len(y)
    assert "log_return_1" in X.columns
    assert "rsi_14" in X.columns
    assert set(y.unique()).issubset({0, 1})
