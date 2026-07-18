import pytest
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import LocalBase
from app.database.models import PriceHistory
from app.repositories.price_repository import PriceRepository
from app.services.market_service import MarketService
from app.strategies import StrategyRegistry

@pytest.fixture
def temp_db():
    # Setup temporary SQLite database in memory for testing
    engine = create_engine("sqlite:///:memory:")
    LocalBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_price_repository(temp_db):
    repo = PriceRepository(temp_db)
    
    # 1. Create a price record
    record = PriceHistory(
        symbol="EURUSDc",
        timeframe="H1",
        timestamp=datetime(2026, 7, 16, 12, 0),
        open=1.1200,
        high=1.1250,
        low=1.1180,
        close=1.1220,
        volume=100.0,
        spread=1.0
    )
    repo.create(record)
    
    # 2. Assert query retrieval
    prices = repo.get_prices("EURUSDc", "H1")
    assert len(prices) == 1
    assert prices[0].close == 1.1220
    
    # 3. Check exist check
    assert repo.check_exists("EURUSDc", "H1", datetime(2026, 7, 16, 12, 0)) is True
    assert repo.check_exists("EURUSDc", "H1", datetime(2026, 7, 16, 13, 0)) is False

def test_market_service(temp_db):
    service = MarketService(temp_db)
    
    # Inject dummy candles manually or check sync fallback
    # Since we mapped DXY to Yahoo Finance, let's sync and verify it pulls from Yahoo fallback
    new_records = service.sync_market_data("DXY", "H1", 10)
    assert new_records > 0
    
    prices = service.get_prices("DXY", "H1")
    assert len(prices) > 0
    assert "close" in prices[0]

def test_strategy_registry():
    # Dynamic strategy plugin discovery
    strategies = StrategyRegistry.get_available_strategies()
    assert len(strategies) >= 3  # SMA_Cross, RSI_Reversal, AI_Momentum
    
    # Verify we can resolve SMA_Cross
    strategy = StrategyRegistry.get_strategy("SMA_Cross")
    assert strategy.name == "Simple Moving Average Cross"
