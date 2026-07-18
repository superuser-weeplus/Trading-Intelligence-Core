from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class CandleData:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    spread: float

@dataclass
class ExportRequest:
    symbol: str
    timeframe: str
    bars: int
    formats: List[str]
    output_dir: str

@dataclass
class ExportResult:
    symbol: str
    timeframe: str
    bars_fetched: int
    saved_files: List[str] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
