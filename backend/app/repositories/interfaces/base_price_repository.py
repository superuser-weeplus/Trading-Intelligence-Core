from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class BasePriceRepository(ABC):
    """
    Abstract Base Class for Price Data Repositories matching REPOSITORY_PATTERN.md contract.
    """

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Fetch candle list for symbol and timeframe.
        """
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str, timeframe: str = "H1") -> Optional[float]:
        """
        Fetch latest close price for symbol.
        """
        pass

    @abstractmethod
    def save_candles(self, candles: List[Dict[str, Any]], symbol: str = "XAUUSD", timeframe: str = "H1") -> bool:
        """
        Persist candles into storage.
        """
        pass

    @abstractmethod
    def check_exists(self, symbol: str, timeframe: str, timestamp: datetime) -> bool:
        """
        Check if a price record exists for given symbol, timeframe, and timestamp.
        """
        pass
