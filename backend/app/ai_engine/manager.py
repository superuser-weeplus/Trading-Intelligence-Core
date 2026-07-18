import os
import json
import yaml
import logging
from datetime import datetime
from typing import Dict, Type, Any

from app.config import settings
from app.ai_engine.base_model import BaseModel
from app.ai_engine.models.random_forest import RandomForestModel
from app.ai_engine.models.xgboost import XGBoostModel
from app.ai_engine.models.lightgbm import LightGBMModel
from app.ai_engine.models.lstm import LSTMModel
from app.ai_engine.models.transformer import TransformerModel

logger = logging.getLogger("app.ai_engine.manager")

class AIEngineManager:
    # Model Registry mapping keys to model classes
    REGISTRY: Dict[str, Type[BaseModel]] = {
        "random_forest": RandomForestModel,
        "randomforest": RandomForestModel,
        "xgboost": XGBoostModel,
        "lightgbm": LightGBMModel,
        "lstm": LSTMModel,
        "transformer": TransformerModel
    }

    @classmethod
    def get_model_class(cls, model_name: str) -> Type[BaseModel]:
        normalized_name = model_name.lower().strip()
        if normalized_name not in cls.REGISTRY:
            raise ValueError(f"Model '{model_name}' is not registered. Registered: {list(cls.REGISTRY.keys())}")
        return cls.REGISTRY[normalized_name]

    @classmethod
    def load_hyperparameters(cls, model_name: str) -> dict:
        """
        Loads parameters from app/config/models/{model_name}.yaml
        """
        normalized_name = model_name.lower().replace("_", "").strip()
        # Map variant names to files
        file_map = {
            "randomforest": "randomforest.yaml",
            "xgboost": "xgboost.yaml"
        }
        filename = file_map.get(normalized_name, f"{normalized_name}.yaml")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "models", filename)
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading hyperparameters from {config_path}: {e}")
                
        logger.warning(f"No hyperparameter config found at {config_path}. Using default empty dict.")
        return {}

    @classmethod
    def get_model_dir(cls, symbol: str, timeframe: str) -> str:
        """
        Directory structure for saved versioned models:
        backend/app/ai_engine/saved_models/{symbol}/{timeframe}/
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "saved_models", symbol, timeframe)
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def save_model_version(cls, model: BaseModel, symbol: str, timeframe: str, metrics: dict, feature_list: list) -> str:
        """
        Saves versioned model: model_{timestamp}.pkl, metrics_{timestamp}.json, feature_list_{timestamp}.json.
        Also updates a 'latest_version.json' file mapping to this latest version.
        """
        model_dir = cls.get_model_dir(symbol, timeframe)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save files
        model_filename = f"model_{timestamp}.pkl"
        model_path = os.path.join(model_dir, model_filename)
        model.save(model_path)
        
        # Save metrics
        metrics_filename = f"metrics_{timestamp}.json"
        with open(os.path.join(model_dir, metrics_filename), "w") as f:
            json.dump(metrics, f, indent=4)
            
        # Save feature list
        features_filename = f"features_{timestamp}.json"
        with open(os.path.join(model_dir, features_filename), "w") as f:
            json.dump(feature_list, f, indent=4)
            
        # Update latest mapping
        latest_info = {
            "latest_timestamp": timestamp,
            "model_file": model_filename,
            "metrics_file": metrics_filename,
            "features_file": features_filename,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(os.path.join(model_dir, "latest_version.json"), "w") as f:
            json.dump(latest_info, f, indent=4)
            
        logger.info(f"Saved versioned model model_{timestamp}.pkl to {model_dir}")
        return timestamp

    @classmethod
    def load_latest_model(cls, symbol: str, timeframe: str, model_name: str) -> BaseModel:
        """
        Loads the latest trained model from the latest_version.json file.
        If no model is found, returns a newly instantiated model object (untrained).
        """
        model_class = cls.get_model_class(model_name)
        model_instance = model_class()
        
        model_dir = cls.get_model_dir(symbol, timeframe)
        latest_json_path = os.path.join(model_dir, "latest_version.json")
        
        if os.path.exists(latest_json_path):
            try:
                with open(latest_json_path, "r") as f:
                    latest_info = json.load(f)
                model_path = os.path.join(model_dir, latest_info["model_file"])
                model_instance.load(model_path)
                logger.info(f"Loaded latest model version {latest_info['latest_timestamp']} from {model_path}")
            except Exception as e:
                logger.error(f"Error loading latest model from {latest_json_path}: {e}")
        else:
            logger.warning(f"No saved model version found for {symbol} ({timeframe}). Returning untrained model instance.")
            
        return model_instance
