from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.indicators.indicator_result import IndicatorResult

class BaseIndicator(ABC):
    """
    Abstract Base Class for all Quantitative Technical Indicators matching INDICATOR_INTERFACE.md.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Indicator unique identifier name (e.g. 'EMA', 'RSI').
        """
        pass

    @abstractmethod
    def calculate(
        self,
        candles: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> IndicatorResult:
        """
        Calculates indicator outputs from input OHLCV candle list.
        """
        pass
