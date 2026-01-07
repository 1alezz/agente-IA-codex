"""Trailing stop por ATR."""
from __future__ import annotations


def trailing_stop_long(current_stop: float, close: float, atr: float, mult: float) -> float:
    candidate = close - (atr * mult)
    return max(current_stop, candidate)


def trailing_stop_short(current_stop: float, close: float, atr: float, mult: float) -> float:
    candidate = close + (atr * mult)
    return min(current_stop, candidate)
