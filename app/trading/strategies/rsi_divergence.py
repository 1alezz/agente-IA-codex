from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class RSIDivergenceDetector(StrategyDetector):
    name = "rsi_divergence"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 6:
            return []
        closes = candles["close"]
        delta = closes.diff()
        gain = delta.where(delta > 0, 0.0).rolling(5).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(5).mean()
        rs = gain / loss.replace(0, 1e-6)
        rsi = 100 - (100 / (1 + rs))
        price_change = closes.iloc[-1] - closes.iloc[-3]
        rsi_change = rsi.iloc[-1] - rsi.iloc[-3]
        if price_change < 0 and rsi_change > 0:
            return [
                StrategySignal(
                    name="RSI Divergence",
                    direction="bullish",
                    confidence=0.45,
                    context={"rsi": f"{rsi.iloc[-1]:.1f}"},
                )
            ]
        if price_change > 0 and rsi_change < 0:
            return [
                StrategySignal(
                    name="RSI Divergence",
                    direction="bearish",
                    confidence=0.45,
                    context={"rsi": f"{rsi.iloc[-1]:.1f}"},
                )
            ]
        return []
