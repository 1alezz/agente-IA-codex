from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class OrderBlockDetector(StrategyDetector):
    name = "order_blocks"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 3:
            return []
        last = candles.iloc[-1]
        prev = candles.iloc[-2]
        if last["close"] > prev["high"]:
            return [
                StrategySignal(
                    name="Order Block",
                    direction="bullish",
                    confidence=0.6,
                    context={"level": f"{prev['low']:.2f}-{prev['high']:.2f}"},
                )
            ]
        if last["close"] < prev["low"]:
            return [
                StrategySignal(
                    name="Order Block",
                    direction="bearish",
                    confidence=0.6,
                    context={"level": f"{prev['low']:.2f}-{prev['high']:.2f}"},
                )
            ]
        return []
