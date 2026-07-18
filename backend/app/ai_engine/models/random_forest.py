import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from app.ai_engine.base_model import BaseModel

class RandomForestModel(BaseModel):
    def __init__(self):
        self.model = None

    def train(self, X: pd.DataFrame, y: pd.Series, hyperparameters: dict) -> dict:
        # Resolve hyperparameters
        n_estimators = hyperparameters.get("n_estimators", 100)
        max_depth = hyperparameters.get("max_depth", None)
        min_samples_split = hyperparameters.get("min_samples_split", 2)
        min_samples_leaf = hyperparameters.get("min_samples_leaf", 1)
        random_state = hyperparameters.get("random_state", 42)

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1
        )

        # Simple train-test split (80/20 temporal split for time-series validation)
        split = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split], X.iloc[split:]
        y_train, y_val = y.iloc[:split], y.iloc[split:]

        self.model.fit(X_train, y_train)

        # Evaluate
        preds = self.model.predict(X_val)
        
        return {
            "accuracy": float(accuracy_score(y_val, preds)),
            "precision": float(precision_score(y_val, preds, zero_division=0)),
            "recall": float(recall_score(y_val, preds, zero_division=0))
        }

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            # Return dummy predictions if model is not trained yet
            return pd.DataFrame({
                "direction": ["HOLD"] * len(X),
                "probability": [0.5] * len(X),
                "confidence": [0.0] * len(X)
            }, index=X.index)

        # Get probabilities
        probs = self.model.predict_proba(X)[:, 1] # Probability of class 1 (UP)
        
        directions = []
        confidences = []
        
        for p in probs:
            if p > 0.55:
                directions.append("UP")
                confidences.append(float((p - 0.5) * 2.0))
            elif p < 0.45:
                directions.append("DOWN")
                confidences.append(float((0.5 - p) * 2.0))
            else:
                directions.append("HOLD")
                confidences.append(float(1.0 - abs(p - 0.5) * 2.0))
                
        return pd.DataFrame({
            "direction": directions,
            "probability": [float(p) for p in probs],
            "confidence": confidences
        }, index=X.index)

    def save(self, path: str) -> None:
        if self.model is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            joblib.dump(self.model, path)

    def load(self, path: str) -> None:
        if os.path.exists(path):
            self.model = joblib.load(path)
        else:
            raise FileNotFoundError(f"Model file not found at {path}")
