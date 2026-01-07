from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


class DataFeed:
    def __init__(self, symbols: List[str], timeframes: List[str]) -> None:
        self.symbols = symbols
        self.timeframes = timeframes
        self._cache: Dict[str, Dict[str, pd.DataFrame]] = {}

    def sync(self, symbols: List[str], timeframes: List[str]) -> None:
        self.symbols = symbols
        self.timeframes = timeframes
        for symbol in symbols:
            self._cache.setdefault(symbol, {})
            for timeframe in timeframes:
                if timeframe not in self._cache[symbol]:
                    self._cache[symbol][timeframe] = self._seed_candles()

    def fetch_latest(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        self.sync(self.symbols, self.timeframes)
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                self._cache[symbol][timeframe] = self._append_candle(self._cache[symbol][timeframe])
        return self._cache

    def _seed_candles(self, count: int = 80) -> pd.DataFrame:
        prices = np.cumsum(np.random.normal(loc=0.0, scale=1.2, size=count)) + 100.0
        opens = prices + np.random.normal(scale=0.3, size=count)
        closes = prices + np.random.normal(scale=0.3, size=count)
        highs = np.maximum(opens, closes) + np.random.uniform(0.1, 0.8, size=count)
        lows = np.minimum(opens, closes) - np.random.uniform(0.1, 0.8, size=count)
        volumes = np.random.uniform(10, 100, size=count)
        return pd.DataFrame(
            {
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
            }
        )

    def _append_candle(self, candles: pd.DataFrame) -> pd.DataFrame:
        last_close = float(candles["close"].iloc[-1])
        drift = np.random.normal(scale=0.6)
        open_price = last_close + np.random.normal(scale=0.2)
        close_price = open_price + drift
        high_price = max(open_price, close_price) + np.random.uniform(0.1, 0.6)
        low_price = min(open_price, close_price) - np.random.uniform(0.1, 0.6)
        volume = float(np.random.uniform(10, 100))
        new_row = pd.DataFrame(
            {
                "open": [open_price],
                "high": [high_price],
                "low": [low_price],
                "close": [close_price],
                "volume": [volume],
            }
        )
        return pd.concat([candles.iloc[1:], new_row], ignore_index=True)
