import pandas as pd
import numpy as np
from app.strategies.base_strategy import BaseStrategy

class RSIMeanReversionStrategy(BaseStrategy):
    @property
    def strategy_id(self) -> str:
        return "RSI_Reversal"

    @property
    def name(self) -> str:
        return "RSI Mean Reversion"

    @property
    def description(self) -> str:
        return "BUY when RSI (14) crosses back above 30 from oversold territory. SELL when RSI crosses back below 70 from overbought territory."

    @property
    def default_parameters(self) -> dict:
        return {
            "rsi_period": 14,
            "oversold_threshold": 30.0,
            "overbought_threshold": 70.0
        }

    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        df = df.copy()
        rsi_col = f"rsi_{parameters.get('rsi_period', 14)}"
        if rsi_col not in df.columns:
            rsi_col = "rsi_14"

        oversold = parameters.get("oversold_threshold", 30.0)
        overbought = parameters.get("overbought_threshold", 70.0)
        
        rsi_prev = df[rsi_col].shift(1)
        buy_sig = (rsi_prev < oversold) & (df[rsi_col] >= oversold)
        sell_sig = (rsi_prev > overbought) & (df[rsi_col] <= overbought)
        
        signals = np.select([buy_sig, sell_sig], [1, -1], default=0)
        return pd.Series(signals, index=df.index).astype(int)
