from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class MarketStructureDetector(StrategyDetector):
    name = "market_structure"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        if len(candles) < 4:
            return []
        last = candles.iloc[-1]
        prev = candles.iloc[-2]
        prev_prev = candles.iloc[-3]
        if last["close"] > prev["high"] and prev["close"] > prev_prev["high"]:
            return [
                StrategySignal(
                    name="Market Structure",
                    direction="bullish",
                    confidence=0.5,
                    context={"break": f"{prev['high']:.2f}"},
                )
            ]
        if last["close"] < prev["low"] and prev["close"] < prev_prev["low"]:
            return [
                StrategySignal(
                    name="Market Structure",
                    direction="bearish",
                    confidence=0.5,
                    context={"break": f"{prev['low']:.2f}"},
                )
            ]
        return []
