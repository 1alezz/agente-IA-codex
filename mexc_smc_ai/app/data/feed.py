"""Camada de feed para normalizar OHLCV."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from app.core.models import Candle
from app.core.logger import get_logger, log_event
from app.data.mexc_client import MexcClient


LOGGER = get_logger(__name__)


def normalize_klines(symbol: str, timeframe: str, klines: list) -> pd.DataFrame:
    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "trades",
        "taker_base",
        "taker_quote",
        "ignore",
    ]
    frame = pd.DataFrame(klines, columns=columns)
    frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True)
    frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms", utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        frame[col] = frame[col].astype(float)
    frame["symbol"] = symbol
    frame["timeframe"] = timeframe
    return frame


def fetch_candles(client: MexcClient, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
    log_event(
        LOGGER,
        "fetch_candles",
        message="Buscando candles",
        symbol=symbol,
        timeframe=timeframe,
    )
    klines = client.get_klines(symbol=symbol, interval=timeframe, limit=limit)
    return normalize_klines(symbol, timeframe, klines)


def latest_candle(frame: pd.DataFrame) -> Candle:
    last = frame.iloc[-1]
    return Candle(
        symbol=last["symbol"],
        timeframe=last["timeframe"],
        timestamp=datetime.fromtimestamp(last["close_time"].timestamp(), tz=timezone.utc),
        open=float(last["open"]),
        high=float(last["high"]),
        low=float(last["low"]),
        close=float(last["close"]),
        volume=float(last["volume"]),
    )
