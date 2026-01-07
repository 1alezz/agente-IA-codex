"""Construção de features para IA auxiliar."""
from __future__ import annotations

import pandas as pd

from app.core.models import OrderBlock


def build_features(
    frame: pd.DataFrame,
    ob: OrderBlock,
    bias: str,
    profile: str,
) -> dict:
    last = frame.iloc[-1]
    distance = abs(last["close"] - ((ob.low + ob.high) / 2)) / last["close"]
    rsi_slope = frame["rsi"].diff().iloc[-1]
    volume_ratio = last["volume"] / frame["volume"].rolling(20).mean().iloc[-1]
    return {
        "distance_to_ob": float(distance),
        "rsi": float(last["rsi"]),
        "rsi_slope": float(rsi_slope),
        "bull_div": int(last.get("bull_divergence", False)),
        "bear_div": int(last.get("bear_divergence", False)),
        "volume_ratio": float(volume_ratio) if volume_ratio == volume_ratio else 0.0,
        "bias_bull": int(bias == "bullish"),
        "bias_bear": int(bias == "bearish"),
        "profile_scalp": int(profile == "scalping"),
        "profile_day": int(profile == "daytrade"),
        "profile_swing": int(profile == "swing"),
    }
