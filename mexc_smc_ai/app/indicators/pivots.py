"""Detecção de pivots (swing highs/lows)."""
from __future__ import annotations

import pandas as pd


def detect_pivots(frame: pd.DataFrame, left: int, right: int) -> pd.DataFrame:
    highs = frame["high"].values
    lows = frame["low"].values
    pivot_high = [False] * len(frame)
    pivot_low = [False] * len(frame)

    for idx in range(left, len(frame) - right):
        window_high = highs[idx - left : idx + right + 1]
        window_low = lows[idx - left : idx + right + 1]
        pivot_high[idx] = highs[idx] == max(window_high)
        pivot_low[idx] = lows[idx] == min(window_low)

    frame = frame.copy()
    frame["pivot_high"] = pivot_high
    frame["pivot_low"] = pivot_low
    return frame
