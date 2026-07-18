import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("app.database")
logging.basicConfig(level=logging.INFO)

# Define separate declarative bases
LocalBase = declarative_base()
SupabaseBase = declarative_base()

# Local SQLite Engine (for price history & indicators)
logger.info("Initializing Local SQLite Database engine...")
local_engine = create_engine(
    settings.SQLITE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLITE_URL else {}
)
LocalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=local_engine)

# Supabase PostgreSQL Engine (for journal, alerts, and predictions)
supabase_engine = None
SupabaseSessionLocal = None

def init_supabase_engine():
    global supabase_engine, SupabaseSessionLocal
    
    # Try connecting to Supabase PostgreSQL if enabled
    if settings.USE_SUPABASE and settings.SUPABASE_DATABASE_URL:
        try:
            logger.info("Attempting to connect to Supabase Cloud Database...")
            supabase_engine = create_engine(
                settings.SUPABASE_DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            # Test connection
            with supabase_engine.connect() as conn:
                logger.info("Successfully connected to Supabase Database.")
            SupabaseSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=supabase_engine)
            return
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}. Falling back to SQLite for Cloud tables.")
            
    # Offline / Fallback Mode: Reuse Local SQLite engine for all tables
    logger.info("Using local SQLite database for Cloud tables (Offline Fallback Mode).")
    supabase_engine = local_engine
    SupabaseSessionLocal = LocalSessionLocal

init_supabase_engine()

# Dependencies to fetch DB sessions
def get_local_db():
    db = LocalSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase_db():
    db = SupabaseSessionLocal()
    try:
        yield db
    finally:
        db.close()
