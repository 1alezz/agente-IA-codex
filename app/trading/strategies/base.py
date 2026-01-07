from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from app.core.schemas import StrategySignal


class StrategyDetector(ABC):
    name: str

    @abstractmethod
    def detect(self, candles: pd.DataFrame) -> List[StrategySignal]:
        raise NotImplementedError
