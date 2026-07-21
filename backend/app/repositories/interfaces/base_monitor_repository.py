from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseMonitorRepository(ABC):
    """
    Abstract Base Class for Data Monitor Metric Repositories.
    """

    @abstractmethod
    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Calculates global summary metrics across all exported datasets.
        """
        pass

    @abstractmethod
    def get_market_snapshot(self) -> List[Dict[str, Any]]:
        """
        Calculates Market Snapshot data.
        """
        pass

    @abstractmethod
    def get_data_explorer(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Retrieves Data Explorer statistics and freshness for symbol and timeframe.
        """
        pass

    @abstractmethod
    def get_export_history(self) -> List[Dict[str, Any]]:
        """
        Retrieves export history dataset records.
        """
        pass

    @abstractmethod
    def get_data_quality(self) -> List[Dict[str, Any]]:
        """
        Retrieves data quality metrics and gap breakdowns.
        """
        pass
