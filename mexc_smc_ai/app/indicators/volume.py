"""Confluência simples de volume."""
from __future__ import annotations

import pandas as pd


def volume_spike(frame: pd.DataFrame, period: int = 20, mult: float = 1.5) -> pd.Series:
    sma = frame["volume"].rolling(window=period, min_periods=period).mean()
    return frame["volume"] > (sma * mult)
