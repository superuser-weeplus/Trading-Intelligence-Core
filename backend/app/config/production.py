from app.config.base import BaseConfig

class ProdConfig(BaseConfig):
    DEBUG: bool = False
    ENV: str = "production"
    # Production overrides go here
