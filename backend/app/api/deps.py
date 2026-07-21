from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_local_db
from app.repositories.interfaces.base_price_repository import BasePriceRepository
from app.repositories.interfaces.base_monitor_repository import BaseMonitorRepository
from app.repositories.supabase.supabase_price_repository import SupabasePriceRepository
from app.repositories.csv.csv_price_repository import CSVPriceRepository
from app.repositories.monitor_repository import MonitorRepository
from app.repositories.infrastructure.infrastructure_repository import InfrastructureRepository
from app.services.monitor_service import MonitorService
from app.services.market_service import MarketService

def get_price_repository(db: Session = Depends(get_local_db)) -> BasePriceRepository:
    return SupabasePriceRepository(db)

def get_csv_price_repository() -> BasePriceRepository:
    return CSVPriceRepository()

def get_monitor_repository(price_repo: BasePriceRepository = Depends(get_price_repository)) -> BaseMonitorRepository:
    return MonitorRepository(price_repo=price_repo)

def get_infrastructure_repository(db: Session = Depends(get_local_db)) -> InfrastructureRepository:
    return InfrastructureRepository(db)

def get_monitor_service(
    monitor_repo: BaseMonitorRepository = Depends(get_monitor_repository),
    infra_repo: InfrastructureRepository = Depends(get_infrastructure_repository)
) -> MonitorService:
    return MonitorService(monitor_repo=monitor_repo, infra_repo=infra_repo)

def get_market_service(
    price_repo: BasePriceRepository = Depends(get_price_repository)
) -> MarketService:
    return MarketService(price_repo=price_repo)
