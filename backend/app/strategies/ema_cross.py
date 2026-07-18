import pandas as pd
import numpy as np
from app.strategies.base_strategy import BaseStrategy

class EMACrossStrategy(BaseStrategy):
    @property
    def strategy_id(self) -> str:
        return "SMA_Cross"

    @property
    def name(self) -> str:
        return "Simple Moving Average Cross"

    @property
    def description(self) -> str:
        return "BUY when EMA 9 crosses above SMA 20 (bullish crossover). SELL when EMA 9 crosses below SMA 20 (bearish crossover)."

    @property
    def default_parameters(self) -> dict:
        return {
            "fast_period": 9,
            "slow_period": 20
        }

    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        df = df.copy()
        fast_col = f"ema_{parameters.get('fast_period', 9)}"
        slow_col = f"sma_{parameters.get('slow_period', 20)}"
        
        # Fallback to defaults if specific columns are missing
        if fast_col not in df.columns:
            fast_col = "ema_9"
        if slow_col not in df.columns:
            slow_col = "sma_20"
            
        signals = np.where(df[fast_col] > df[slow_col], 1, -1)
        signals_series = pd.Series(signals, index=df.index).diff().fillna(0)
        
        # Map to transitions: 2 -> 1 (BUY), -2 -> -1 (SELL)
        return signals_series.map({2.0: 1, -2.0: -1}).fillna(0).astype(int)
