import pandas as pd
import numpy as np
from typing import Tuple, List
from app.indicator_engine.indicators import TechnicalIndicators

class FeaturePipeline:
    # Strict list of features that the models train on
    FEATURE_COLUMNS = [
        "log_return_1", "log_return_3", "log_return_5", "log_return_10", "log_return_20",
        "volatility_5", "volatility_10", "volatility_20",
        "relative_volume_10", "relative_volume_20",
        "hl_spread", "co_spread",
        "close_to_sma20", "close_to_sma50",
        "rsi_14", "macd", "macd_signal", "macd_hist",
        "bb_width", "bb_percent", "atr_14",
        "hour", "day_of_week"
    ]

    @classmethod
    def run_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Step 1: Compute indicators using the Indicators Engine."""
        return TechnicalIndicators.apply_all(df)

    @classmethod
    def engineer_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Step 2: Calculate engineered mathematical, volatility and temporal features."""
        df = df.copy()

        # 1. Log Returns
        for p in [1, 3, 5, 10, 20]:
            df[f"log_return_{p}"] = np.log(df["close"] / df["close"].shift(p))
            
        # 2. Rolling Volatility
        df["volatility_5"] = df["log_return_1"].rolling(window=5).std()
        df["volatility_10"] = df["log_return_1"].rolling(window=10).std()
        df["volatility_20"] = df["log_return_1"].rolling(window=20).std()
        
        # 3. Relative Volume
        volume_sma_10 = df["volume"].rolling(window=10).mean()
        volume_sma_20 = df["volume"].rolling(window=20).mean()
        df["relative_volume_10"] = df["volume"] / volume_sma_10.replace(0, np.nan)
        df["relative_volume_20"] = df["volume"] / volume_sma_20.replace(0, np.nan)
        
        # 4. Spreads & High-Low ranges
        df["hl_spread"] = (df["high"] - df["low"]) / df["close"]
        df["co_spread"] = (df["close"] - df["open"]) / df["close"]
        
        # 5. Price position relative to indicators
        df["close_to_sma20"] = (df["close"] - df["sma_20"]) / df["sma_20"]
        df["close_to_sma50"] = (df["close"] - df["sma_50"]) / df["sma_50"]
        
        # Bollinger Bands Width
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"].replace(0, np.nan)
        
        # 6. Time Features (Hour, Day of week)
        if "timestamp" in df.columns:
            timestamps = pd.to_datetime(df["timestamp"])
            df["hour"] = timestamps.dt.hour
            df["day_of_week"] = timestamps.dt.dayofweek
        else:
            df["hour"] = 0
            df["day_of_week"] = 0

        # Fill NaNs from shifts/rolling windows
        df = df.ffill().bfill()
        return df

    @classmethod
    def select_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Step 3: Keep only the strict list of features chosen for modeling."""
        return df[cls.FEATURE_COLUMNS]

    @classmethod
    def prepare_data(cls, df: pd.DataFrame, label_shift: int = 5) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Processes raw prices and returns (X, y, timestamps) for model training/evaluation.
        Target: Predict if the close price in 'label_shift' periods will be higher than current close (binary classification).
        """
        # Run indicators
        df_ind = cls.run_indicators(df)
        
        # Run feature engineering
        df_features = cls.engineer_features(df_ind)
        
        # Create classification target
        df_features["target"] = (df_features["close"].shift(-label_shift) > df_features["close"]).astype(int)
        
        # Clean up rows that contain NaN in features/target
        clean_df = df_features.dropna(subset=cls.FEATURE_COLUMNS + ["target"])
        clean_df = clean_df.iloc[20:-label_shift]  # remove early rows with incomplete indicators
        
        X = clean_df[cls.FEATURE_COLUMNS]
        y = clean_df["target"]
        timestamps = clean_df["timestamp"] if "timestamp" in clean_df.columns else clean_df.index
        
        return X, y, timestamps

    @classmethod
    def prepare_latest_row(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes price history and returns only the single latest row features for real-time inference.
        """
        df_ind = cls.run_indicators(df)
        df_features = cls.engineer_features(df_ind)
        return df_features[cls.FEATURE_COLUMNS].tail(1)
