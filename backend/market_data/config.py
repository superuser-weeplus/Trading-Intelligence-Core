import os
import yaml
from typing import List, Dict, Any

class ConfigLoader:
    """
    Loads configuration settings from settings.yaml file and handles environment overrides.
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "settings.yaml")
            
        self.config_path = config_path
        self._raw_config = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @property
    def mt5_config(self) -> Dict[str, Any]:
        return self._raw_config.get("mt5", {})

    @property
    def symbols(self) -> List[str]:
        return self._raw_config.get("symbols", ["XAUUSD", "GBPUSD", "EURUSD", "DXY"])

    @property
    def symbol_mapping(self) -> Dict[str, str]:
        return self._raw_config.get("symbol_mapping", {})

    @property
    def timeframes(self) -> List[str]:
        return self._raw_config.get("timeframes", ["M1", "M5", "M15", "H1", "H4", "D1"])

    @property
    def default_bars(self) -> int:
        return int(self._raw_config.get("default_bars", 5000))

    @property
    def export_formats(self) -> List[str]:
        return self._raw_config.get("export_formats", ["csv", "json"])

    @property
    def output_dir(self) -> str:
        out_dir = self._raw_config.get("output_dir", "./output")
        if not os.path.isabs(out_dir):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            out_dir = os.path.abspath(os.path.join(base_dir, out_dir))
        return out_dir

    def resolve_symbol(self, symbol: str) -> str:
        """
        Translates user symbol to broker-specific symbol if mapped in settings.yaml.
        """
        return self.symbol_mapping.get(symbol.upper(), symbol)
