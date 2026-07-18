from app.config.base import BaseConfig

class DevConfig(BaseConfig):
    DEBUG: bool = True
    ENV: str = "development"
