"""Detecção simples de divergência entre preço e RSI."""
from __future__ import annotations

import pandas as pd


def detect_rsi_divergence(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["bull_divergence"] = False
    frame["bear_divergence"] = False

    lows = frame[frame["pivot_low"]]
    highs = frame[frame["pivot_high"]]

    if len(lows) >= 2:
        last_two = lows.tail(2)
        price_lower_low = last_two["low"].iloc[-1] < last_two["low"].iloc[-2]
        rsi_higher_low = last_two["rsi"].iloc[-1] > last_two["rsi"].iloc[-2]
        if price_lower_low and rsi_higher_low:
            frame.loc[last_two.index[-1], "bull_divergence"] = True

    if len(highs) >= 2:
        last_two = highs.tail(2)
        price_higher_high = last_two["high"].iloc[-1] > last_two["high"].iloc[-2]
        rsi_lower_high = last_two["rsi"].iloc[-1] < last_two["rsi"].iloc[-2]
        if price_higher_high and rsi_lower_high:
            frame.loc[last_two.index[-1], "bear_divergence"] = True

    return frame
