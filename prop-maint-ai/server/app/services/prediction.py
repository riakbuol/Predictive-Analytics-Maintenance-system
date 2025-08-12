from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models_store")
os.makedirs(MODEL_DIR, exist_ok=True)


class PredictionEngine:
    def __init__(self) -> None:
        self.model_path = os.path.join(MODEL_DIR, "rf_model.joblib")
        self.model_version: str | None = None
        self.model: RandomForestClassifier | None = None
        self.feature_columns = [
            "property_age",
            "last_service_days",
            "num_past_issues",
            "season",
            "humidity",
            "temperature",
        ]

    def load(self) -> None:
        if os.path.exists(self.model_path):
            payload = joblib.load(self.model_path)
            self.model = payload["model"]
            self.model_version = payload.get("version")

    def save(self, model: RandomForestClassifier) -> None:
        version = datetime.utcnow().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
        joblib.dump({"model": model, "version": version}, self.model_path)
        self.model_version = version
        self.model = model

    def train_from_csv(self, csv_path: str) -> Dict[str, Any]:
        df = pd.read_csv(csv_path)
        required_cols = set(self.feature_columns + ["category"])
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns in training CSV: {missing}")

        X = df[self.feature_columns]
        y = df["category"].astype(str)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = float(accuracy_score(y_test, preds))

        self.save(model)
        return {"message": "Model trained", "accuracy": acc, "version": self.model_version}

    def predict(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.model is None:
            self.load()
        if self.model is None:
            # naive default classifier if no model is trained
            return [
                {
                    "predicted_category": row.get("fallback_category", "general"),
                    "severity": self._severity_from_urgency(row.get("urgency", "medium")),
                    "priority": self._priority_from_severity(self._severity_from_urgency(row.get("urgency", "medium"))),
                }
                for row in rows
            ]

        features = []
        for row in rows:
            features.append([row.get(col, 0) for col in self.feature_columns])
        X = np.array(features)
        cats = self.model.predict(X)
        out = []
        for i, cat in enumerate(cats):
            severity = self._severity_from_category(str(cat))
            out.append({
                "predicted_category": str(cat),
                "severity": severity,
                "priority": self._priority_from_severity(severity),
            })
        return out

    @staticmethod
    def _severity_from_category(category: str) -> str:
        category_lower = category.lower()
        if any(k in category_lower for k in ["gas", "electrical", "water leak", "plumbing"]):
            return "high"
        if any(k in category_lower for k in ["hvac", "appliance", "roof"]):
            return "medium"
        return "low"

    @staticmethod
    def _severity_from_urgency(urgency: str) -> str:
        m = urgency.lower()
        if m in ("critical", "high"): return "high"
        if m in ("medium",): return "medium"
        return "low"

    @staticmethod
    def _priority_from_severity(severity: str) -> int:
        return {"high": 1, "medium": 2, "low": 3}.get(severity, 3)


engine_singleton = PredictionEngine()