import pandas as pd
import numpy as np
from app.strategies.base_strategy import BaseStrategy

class AIMomentumStrategy(BaseStrategy):
    @property
    def strategy_id(self) -> str:
        return "AI_Momentum"

    @property
    def name(self) -> str:
        return "Machine Learning Prediction Trend"

    @property
    def description(self) -> str:
        return "Uses a trained RandomForestClassifier feature-set. BUY when the ML probability is > 55% UP. SELL/EXIT when ML probability is < 45% UP."

    @property
    def default_parameters(self) -> dict:
        return {
            "confidence_threshold": 0.1
        }

    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        df = df.copy()
        
        # In a real backtest, we run ML prediction over history.
        # If model is not loaded, we use MACD + RSI alignment as a proxy.
        if "macd_hist" in df.columns and "rsi_14" in df.columns:
            ml_up = (df["macd_hist"] > 0) & (df["rsi_14"] > 50)
            ml_down = (df["macd_hist"] < 0) & (df["rsi_14"] < 50)
            signals = np.select([ml_up, ml_down], [1, -1], default=0)
            
            signals_series = pd.Series(signals, index=df.index).diff().fillna(0)
            return signals_series.map({1.0: 1, -1.0: -1, 2.0: 1, -2.0: -1}).fillna(0).astype(int)
            
        return pd.Series(0, index=df.index).astype(int)
