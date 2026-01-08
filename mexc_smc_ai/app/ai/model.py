"""Modelo IA auxiliar (plugável)."""
from __future__ import annotations

import numpy as np

from app.core.logger import get_logger, log_event
from app.core.logger import get_logger


LOGGER = get_logger(__name__)


class BaseModel:
    def predict_proba(self, features: dict) -> float:
        raise NotImplementedError


class LogisticRegressionModel(BaseModel):
    def __init__(self) -> None:
        try:
            from sklearn.linear_model import LogisticRegression

            self.model = LogisticRegression()
            self.trained = False
        except Exception as exc:
            log_event(
                LOGGER,
                "model_init_failed",
                message="Falha ao iniciar LogisticRegression",
                error=str(exc),
                level="warning",
            LOGGER.warning(
                "model_init_failed",
                extra={"message": "Falha ao iniciar LogisticRegression", "error": str(exc)},
            )
            self.model = None
            self.trained = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if self.model is None:
            return
        self.model.fit(X, y)
        self.trained = True

    def predict_proba(self, features: dict) -> float:
        if self.model is None or not self.trained:
            return 0.5
        vector = np.array([list(features.values())])
        return float(self.model.predict_proba(vector)[0][1])


def build_model(model_type: str) -> BaseModel:
    if model_type == "logistic_regression":
        return LogisticRegressionModel()
    log_event(
        LOGGER,
        "unknown_model",
        message="Modelo desconhecido, usando fallback",
        level="warning",
    )
    LOGGER.warning("unknown_model", extra={"message": "Modelo desconhecido, usando fallback"})
    return LogisticRegressionModel()
