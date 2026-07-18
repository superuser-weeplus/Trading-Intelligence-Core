import os
import pkgutil
import importlib
from app.strategies.base_strategy import BaseStrategy

class StrategyRegistry:
    _strategies = {}

    @classmethod
    def discover_strategies(cls):
        cls._strategies = {}
        package_dir = os.path.dirname(__file__)
        
        # Scan files in app/strategies/
        for _, module_name, _ in pkgutil.iter_modules([package_dir]):
            if module_name == "base_strategy":
                continue
            try:
                module = importlib.import_module(f"app.strategies.{module_name}")
                for name, attr in module.__dict__.items():
                    if isinstance(attr, type) and issubclass(attr, BaseStrategy) and attr is not BaseStrategy:
                        instance = attr()
                        cls._strategies[instance.strategy_id] = instance
            except Exception as e:
                # Silent ignore or log
                pass

    @classmethod
    def get_strategy(cls, strategy_id: str) -> BaseStrategy:
        if not cls._strategies:
            cls.discover_strategies()
        if strategy_id not in cls._strategies:
            raise ValueError(f"Strategy '{strategy_id}' not found in registry. Registered: {list(cls._strategies.keys())}")
        return cls._strategies[strategy_id]

    @classmethod
    def get_available_strategies(cls) -> list:
        if not cls._strategies:
            cls.discover_strategies()
        return [
            {
                "id": s.strategy_id,
                "name": s.name,
                "description": s.description,
                "default_parameters": s.default_parameters
            }
            for s in cls._strategies.values()
        ]
