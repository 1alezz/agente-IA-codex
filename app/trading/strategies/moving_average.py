from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class MovingAverageFilter(StrategyDetector):
    name = "moving_average_filter"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 10:
            return []
        sma = candles["close"].rolling(10).mean().iloc[-1]
        last = candles.iloc[-1]
        if last["close"] > sma:
            return [
                StrategySignal(
                    name="EMA Filter",
                    direction="bullish",
                    confidence=0.4,
                    context={"sma": f"{sma:.2f}"},
                )
            ]
        if last["close"] < sma:
            return [
                StrategySignal(
                    name="EMA Filter",
                    direction="bearish",
                    confidence=0.4,
                    context={"sma": f"{sma:.2f}"},
                )
            ]
        return []
