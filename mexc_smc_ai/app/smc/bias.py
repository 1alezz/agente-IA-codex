"""Bias simples por timeframe maior."""
from __future__ import annotations

import pandas as pd


def compute_bias(frame: pd.DataFrame) -> str:
    if len(frame) < 2:
        return "neutral"
    last = frame.iloc[-1]
    prev = frame.iloc[-2]
    if last["close"] > prev["close"]:
        return "bullish"
    if last["close"] < prev["close"]:
        return "bearish"
    return "neutral"
