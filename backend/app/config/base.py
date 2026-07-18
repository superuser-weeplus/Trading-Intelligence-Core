from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    APP_NAME: str = "Trading Intelligence Platform"
    DEBUG: bool = True
    ENV: str = "development"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/trading_db"
    SQLITE_URL: str = "sqlite:///./trading_platform_dev.db"
    USE_SQLITE: bool = True
    
    SUPABASE_DATABASE_URL: str = ""
    USE_SUPABASE: bool = False
    
    # MetaTrader 5 Settings
    MT5_LOGIN: int = 0
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""
    MT5_PATH: str = ""
    
    # AI / LLM Settings
    GEMINI_API_KEY: str = ""
    ACTIVE_AI_MODEL: str = "random_forest"  # Default active model: "random_forest", "xgboost", etc.
    
    # Worker Settings
    QUEUE_DRIVER: str = "memory"  # "memory" (in-memory asyncio queue) or "redis" (celery/redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Alert System
    CHECK_INTERVAL_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
