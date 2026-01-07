"""Confluências para validação de sinais."""
from __future__ import annotations

from app.core.models import OrderBlock


def ob_touch(ob: OrderBlock, high: float, low: float, close: float) -> bool:
    return (low <= ob.high and high >= ob.low) or (ob.low <= close <= ob.high)


def bias_allows(direction: str, bias: str) -> bool:
    if bias == "neutral":
        return True
    if direction == "buy":
        return bias == "bullish"
    return bias == "bearish"
