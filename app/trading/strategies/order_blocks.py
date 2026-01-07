from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import StrategySignal
from app.trading.strategies.base import StrategyDetector


class OrderBlockDetector(StrategyDetector):
    name = "order_blocks"

    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        return []
