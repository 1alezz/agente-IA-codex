from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class TurtleSoupDetector(StrategyDetector):
    name = "turtle_soup"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 6:
            return []
        recent = candles.tail(6)
        high = recent["high"].max()
        low = recent["low"].min()
        last = recent.iloc[-1]
        if last["high"] >= high and last["close"] < last["open"]:
            return [
                StrategySignal(
                    name="Turtle Soup",
                    direction="bearish",
                    confidence=0.5,
                    context={"sweep": f"{high:.2f}"},
                )
            ]
        if last["low"] <= low and last["close"] > last["open"]:
            return [
                StrategySignal(
                    name="Turtle Soup",
                    direction="bullish",
                    confidence=0.5,
                    context={"sweep": f"{low:.2f}"},
                )
            ]
        return []
