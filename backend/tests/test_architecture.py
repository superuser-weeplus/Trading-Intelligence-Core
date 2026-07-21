import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import LocalBase
from app.repositories.supabase.supabase_price_repository import SupabasePriceRepository
from app.repositories.csv.csv_price_repository import CSVPriceRepository
from app.repositories.mock.mock_price_repository import MockPriceRepository
from app.repositories.infrastructure.infrastructure_repository import InfrastructureRepository
from app.repositories.monitor_repository import MonitorRepository
from app.services.market_service import MarketService
from app.services.monitor_service import MonitorService
from app.indicators.base_indicator import BaseIndicator
from app.indicators.indicator_result import IndicatorResult
from app.strategies import StrategyRegistry

@pytest.fixture
def temp_db():
    engine = create_engine("sqlite:///:memory:")
    LocalBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_supabase_price_repository(temp_db):
    repo = SupabasePriceRepository(temp_db)
    
    candles = [{
        "timestamp": datetime(2026, 7, 16, 12, 0).isoformat(),
        "open": 1.1200,
        "high": 1.1250,
        "low": 1.1180,
        "close": 1.1220,
        "volume": 100.0,
        "spread": 1.0
    }]
    assert repo.save_candles(candles, symbol="EURUSDc", timeframe="H1") is True
    
    fetched = repo.get_candles("EURUSDc", "H1")
    assert len(fetched) == 1
    assert fetched[0]["close"] == 1.1220
    assert repo.get_latest_price("EURUSDc", "H1") == 1.1220
    assert repo.check_exists("EURUSDc", "H1", datetime(2026, 7, 16, 12, 0)) is True

def test_mock_price_repository():
    repo = MockPriceRepository()
    candles = repo.get_candles("XAUUSD", "H1", limit=50)
    assert len(candles) == 50
    assert "close" in candles[0]
    assert repo.get_latest_price("XAUUSD", "H1") is not None

def test_market_service_with_di(temp_db):
    repo = SupabasePriceRepository(temp_db)
    service = MarketService(price_repo=repo)
    
    new_records = service.sync_market_data("DXY", "H1", 10)
    assert new_records > 0
    
    prices = service.get_prices("DXY", "H1")
    assert len(prices) > 0
    assert "close" in prices[0]

def test_monitor_service_with_di(temp_db):
    price_repo = SupabasePriceRepository(temp_db)
    monitor_repo = MonitorRepository(price_repo=price_repo)
    infra_repo = InfrastructureRepository(db=temp_db)
    
    service = MonitorService(monitor_repo=monitor_repo, infra_repo=infra_repo)
    health = service.get_system_health()
    assert "mt5" in health
    assert "supabase" in health
    
    summary = service.get_summary_metrics()
    assert summary["symbols"] == 4

def test_indicator_framework_skeleton():
    result = IndicatorResult(
        symbol="XAUUSD",
        timeframe="H1",
        indicator="EMA",
        parameters={"period": 20},
        values=2040.5,
        timestamp=datetime.now().isoformat()
    )
    assert result.symbol == "XAUUSD"
    assert result.value == 2040.5

def test_strategy_registry():
    strategies = StrategyRegistry.get_available_strategies()
    assert len(strategies) >= 3
    strategy = StrategyRegistry.get_strategy("SMA_Cross")
    assert strategy.name == "Simple Moving Average Cross"
