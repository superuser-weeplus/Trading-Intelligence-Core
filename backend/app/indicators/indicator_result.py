from typing import Dict, Any
from pydantic import BaseModel, Field

class IndicatorResult(BaseModel):
    """
    Standard Pydantic model for indicator outputs matching INDICATOR_INTERFACE.md specification.
    """
    symbol: str = Field(..., description="Trading pair symbol e.g. XAUUSD")
    timeframe: str = Field(..., description="Timeframe e.g. H1, H4, D1")
    indicator: str = Field(..., description="Unique indicator identifier e.g. EMA, RSI")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for calculation")
    values: Any = Field(..., description="Calculated values (float or Dict[str, float])")
    timestamp: str = Field(..., description="ISO 8601 formatted calculation timestamp")
    version: str = Field(default="1.0.0", description="Indicator version specification")

    @property
    def value(self) -> Any:
        """Backward compatible alias for values."""
        return self.values
