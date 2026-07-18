import pandas as pd
import numpy as np
from app.strategies.base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    @property
    def strategy_id(self) -> str:
        return "MACD_Crossover"

    @property
    def name(self) -> str:
        return "MACD Histogram Crossover"

    @property
    def description(self) -> str:
        return "BUY when MACD Histogram crosses above zero. SELL when MACD Histogram crosses below zero."

    @property
    def default_parameters(self) -> dict:
        return {}

    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        df = df.copy()
        hist_col = "macd_hist"
        if hist_col not in df.columns:
            # Fallback placeholder if column missing
            return pd.Series(0, index=df.index).astype(int)
            
        hist_prev = df[hist_col].shift(1)
        buy_sig = (hist_prev < 0) & (df[hist_col] >= 0)
        sell_sig = (hist_prev > 0) & (df[hist_col] <= 0)
        
        signals = np.select([buy_sig, sell_sig], [1, -1], default=0)
        return pd.Series(signals, index=df.index).astype(int)
