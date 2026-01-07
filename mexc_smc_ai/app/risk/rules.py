"""Regras auxiliares de risco."""
from __future__ import annotations


def target_from_atr(entry: float, atr: float, mult: float, direction: str) -> float:
    if direction == "buy":
        return entry + (atr * mult)
    return entry - (atr * mult)
