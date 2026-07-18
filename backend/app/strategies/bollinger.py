import pandas as pd
import numpy as np
from app.strategies.base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    @property
    def strategy_id(self) -> str:
        return "Bollinger_Breakout"

    @property
    def name(self) -> str:
        return "Bollinger Bands Breakout"

    @property
    def description(self) -> str:
        return "BUY when close price breaks above the upper Bollinger Band. SELL/EXIT when close breaks below lower band."

    @property
    def default_parameters(self) -> dict:
        return {}

    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        df = df.copy()
        if "bb_upper" not in df.columns or "bb_lower" not in df.columns:
            return pd.Series(0, index=df.index).astype(int)
            
        buy_sig = df["close"] > df["bb_upper"]
        sell_sig = df["close"] < df["bb_lower"]
        
        signals = np.select([buy_sig, sell_sig], [1, -1], default=0)
        return pd.Series(signals, index=df.index).astype(int)
