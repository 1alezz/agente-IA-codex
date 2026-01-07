"""Camada de decisão da IA (ENTER ou SKIP)."""
from __future__ import annotations

from app.core.models import Decision


def decide(probability: float, min_probability: float, regime: str, drawdown: float) -> Decision:
    if drawdown < -0.1:
        return Decision(action="SKIP", probability=probability, reason="drawdown_excessivo")
    if regime == "sideways" and probability < min_probability + 0.1:
        return Decision(action="SKIP", probability=probability, reason="regime_lateral")
    if probability >= min_probability:
        return Decision(action="ENTER", probability=probability, reason="probabilidade_ok")
    return Decision(action="SKIP", probability=probability, reason="probabilidade_baixa")
