import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20, column: str = "close") -> pd.Series:
        return df[column].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20, column: str = "close") -> pd.Series:
        return df[column].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).copy()
        loss = (-delta.where(delta < 0, 0)).copy()

        # Exponential moving average of gains and losses
        avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=period - 1, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan) # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        # If avg_loss was 0 and avg_gain was 0, RSI is 50. If avg_loss was 0 and avg_gain > 0, RSI is 100
        rsi = rsi.fillna(50)
        rsi.loc[avg_loss == 0] = 100.0
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, column: str = "close") -> pd.DataFrame:
        fast_ema = df[column].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df[column].ewm(span=slow_period, adjust=False).mean()
        
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        })

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, num_std: float = 2.0, column: str = "close") -> pd.DataFrame:
        sma = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return pd.DataFrame({
            "bb_upper": upper_band,
            "bb_middle": sma,
            "bb_lower": lower_band
        })

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        # True Range is the maximum of:
        # 1. High - Low
        # 2. Abs(High - Previous Close)
        # 3. Abs(Low - Previous Close)
        prev_close = df["close"].shift(1)
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - prev_close).abs()
        tr3 = (df["low"] - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        # ATR is wilder's moving average of TR
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        return atr

    @classmethod
    def apply_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies a suite of standard indicators to a dataframe.
        """
        df = df.copy()
        if len(df) < 30: # Need enough rows for indicators
            return df
            
        df["sma_20"] = cls.calculate_sma(df, 20)
        df["sma_50"] = cls.calculate_sma(df, 50)
        df["ema_9"] = cls.calculate_ema(df, 9)
        df["rsi_14"] = cls.calculate_rsi(df, 14)
        
        macd_df = cls.calculate_macd(df)
        df["macd"] = macd_df["macd"]
        df["macd_signal"] = macd_df["signal"]
        df["macd_hist"] = macd_df["histogram"]
        
        bb_df = cls.calculate_bollinger_bands(df)
        df["bb_upper"] = bb_df["bb_upper"]
        df["bb_middle"] = bb_df["bb_middle"]
        df["bb_lower"] = bb_df["bb_lower"]
        
        # %B indicates where the price is relative to the bands
        df["bb_percent"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"]).replace(0, np.nan)
        df["bb_percent"] = df["bb_percent"].fillna(0.5)
        
        df["atr_14"] = cls.calculate_atr(df, 14)
        return df
