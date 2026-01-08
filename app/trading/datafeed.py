from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import httpx


class DataFeed:
    def __init__(self, symbols: List[str], timeframes: List[str], use_testnet: bool = True) -> None:
        self.symbols = symbols
        self.timeframes = timeframes
        self.use_testnet = use_testnet
        self._cache: Dict[str, Dict[str, pd.DataFrame]] = {}

    def sync(self, symbols: List[str], timeframes: List[str], use_testnet: bool | None = None) -> None:
        self.symbols = symbols
        self.timeframes = timeframes
        if use_testnet is not None:
            self.use_testnet = use_testnet
        for symbol in symbols:
            self._cache.setdefault(symbol, {})
            for timeframe in timeframes:
                if timeframe not in self._cache[symbol]:
                    self._cache[symbol][timeframe] = self._seed_candles()

    def fetch_latest(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        self.sync(self.symbols, self.timeframes)
        if self.use_testnet:
            live = self._fetch_live()
            if live:
                return live
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                self._cache[symbol][timeframe] = self._append_candle(self._cache[symbol][timeframe])
        return self._cache

    def _fetch_live(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        base_url = "https://testnet.binance.vision" if self.use_testnet else "https://api.binance.com"
        data: Dict[str, Dict[str, pd.DataFrame]] = {}
        for symbol in self.symbols:
            data[symbol] = {}
            for timeframe in self.timeframes:
                candles = self._fetch_klines(base_url, symbol, timeframe)
                if candles is not None:
                    data[symbol][timeframe] = candles
                else:
                    data[symbol][timeframe] = self._cache.get(symbol, {}).get(timeframe, self._seed_candles())
        self._cache = data
        return data

    def _fetch_klines(self, base_url: str, symbol: str, interval: str) -> pd.DataFrame | None:
        url = f"{base_url}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": 120}
        try:
            response = httpx.get(url, params=params, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        payload = response.json()
        if not payload:
            return None
        rows = [
            {
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
            }
            for item in payload
        ]
        return pd.DataFrame(rows)

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
