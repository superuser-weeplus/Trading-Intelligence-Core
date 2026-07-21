import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.repositories.interfaces.base_price_repository import BasePriceRepository
from app.repositories.interfaces.base_indicator_repository import BaseIndicatorRepository
from app.indicators.base_indicator import BaseIndicator
from app.indicators.indicator_result import IndicatorResult
from app.core.exceptions import DataNotFoundException

logger = logging.getLogger("app.services.indicator_service")

class IndicatorService:
    """
    Quantitative Indicator Service orchestrating calculation and persistence.
    Interacts purely via BasePriceRepository and BaseIndicatorRepository interface abstractions.
    """

    def __init__(
        self,
        price_repo: BasePriceRepository,
        indicator_repo: Optional[BaseIndicatorRepository] = None
    ):
        self.price_repo = price_repo
        self.indicator_repo = indicator_repo

    def calculate_indicator(
        self,
        symbol: str,
        timeframe: str,
        indicator: BaseIndicator,
        parameters: Dict[str, Any]
    ) -> IndicatorResult:
        """
        Calculates an indicator from price data fetched via BasePriceRepository.
        """
        candles = self.price_repo.get_candles(symbol, timeframe, limit=1000)
        if not candles:
            raise DataNotFoundException(f"Insufficient candle data to calculate indicator {indicator.name} for {symbol} ({timeframe}).")

        result = indicator.calculate(candles, parameters)
        
        if self.indicator_repo:
            self.indicator_repo.save_indicator(result)

        return result
