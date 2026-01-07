from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class MovingAverageFilter(StrategyDetector):
    name = "moving_average_filter"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        return []
