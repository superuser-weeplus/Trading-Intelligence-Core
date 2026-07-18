from abc import ABC, abstractmethod
import pandas as pd

class BaseModel(ABC):
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series, hyperparameters: dict) -> dict:
        """
        Trains the model on training data.
        Returns a dict of validation metrics (e.g. accuracy, precision, recall).
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Runs inference on features.
        Returns a DataFrame containing:
          - 'direction': "UP", "DOWN" or "HOLD"
          - 'probability': float (chance of UP)
          - 'confidence': float (certainty metric)
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Serializes model parameters/state to disk."""
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Deserializes model parameters/state from disk."""
        pass
