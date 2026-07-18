from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """Unique ID of the strategy (e.g., 'SMA_Cross')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the strategy."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of strategy rules."""
        pass

    @property
    @abstractmethod
    def default_parameters(self) -> dict:
        """Default hyperparameters/settings."""
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame, parameters: dict) -> pd.Series:
        """
        Takes a DataFrame containing calculated indicators.
        Returns a pandas Series of signals:
          - 1: BUY
          - -1: SELL
          - 0: HOLD / Neutral
        """
        pass
