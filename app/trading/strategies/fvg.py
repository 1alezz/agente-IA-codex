from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class FVGDetector(StrategyDetector):
    name = "fvg"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        return []
