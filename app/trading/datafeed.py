from __future__ import annotations

from typing import Dict, List

import pandas as pd


class DataFeed:
    def __init__(self, symbols: List[str], timeframes: List[str]) -> None:
        self.symbols = symbols
        self.timeframes = timeframes

    def fetch_latest(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        return {symbol: {timeframe: pd.DataFrame() for timeframe in self.timeframes} for symbol in self.symbols}
