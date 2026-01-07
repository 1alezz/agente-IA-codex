from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class FVGDetector(StrategyDetector):
    name = "fvg"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 3:
            return []
        c1 = candles.iloc[-3]
        c2 = candles.iloc[-2]
        c3 = candles.iloc[-1]
        if c2["low"] > c1["high"] and c3["low"] > c1["high"]:
            return [
                StrategySignal(
                    name="FVG",
                    direction="bullish",
                    confidence=0.55,
                    context={"gap": f"{c1['high']:.2f}-{c2['low']:.2f}"},
                )
            ]
        if c2["high"] < c1["low"] and c3["high"] < c1["low"]:
            return [
                StrategySignal(
                    name="FVG",
                    direction="bearish",
                    confidence=0.55,
                    context={"gap": f"{c2['high']:.2f}-{c1['low']:.2f}"},
                )
            ]
        return []
