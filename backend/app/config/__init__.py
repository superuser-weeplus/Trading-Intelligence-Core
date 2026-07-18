import os
from app.config.base import BaseConfig
from app.config.development import DevConfig
from app.config.production import ProdConfig

# Determine environment (defaults to development)
env_name = os.getenv("ENV", "development").lower()

if env_name == "production":
    settings = ProdConfig()
else:
    settings = DevConfig()
