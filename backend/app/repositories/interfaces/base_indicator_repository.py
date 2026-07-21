from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseIndicatorRepository(ABC):
    """
    Abstract Base Class for Indicator Result Storage Repositories.
    """

    @abstractmethod
    def save_indicator(self, indicator_result: Any) -> bool:
        """
        Persist indicator result into storage.
        """
        pass

    @abstractmethod
    def load_indicator(self, symbol: str, timeframe: str, indicator_name: str) -> Optional[Any]:
        """
        Load indicator result for a specific symbol, timeframe, and indicator name.
        """
        pass

    @abstractmethod
    def delete_indicator(self, symbol: str, timeframe: str, indicator_name: str) -> bool:
        """
        Delete indicator entry from storage.
        """
        pass
