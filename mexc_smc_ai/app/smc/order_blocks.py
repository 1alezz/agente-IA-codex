"""Lógica de identificação e validação de Order Blocks."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pandas as pd

from app.core.models import OrderBlock
from app.indicators.atr import compute_atr


def _ob_range(candle: pd.Series, range_mode: str) -> tuple[float, float]:
    if range_mode == "body":
        low = min(candle["open"], candle["close"])
        high = max(candle["open"], candle["close"])
    else:
        low = candle["low"]
        high = candle["high"]
    return float(low), float(high)


def find_order_blocks(
    frame: pd.DataFrame,
    symbol: str,
    timeframe: str,
    range_mode: str,
    min_move_atr: float,
    min_move_pct: float,
    min_impulse_candles: int,
) -> list[OrderBlock]:
    frame = frame.copy()
    frame["atr"] = compute_atr(frame)
    order_blocks: list[OrderBlock] = []

    for idx in range(1, len(frame)):
        row = frame.iloc[idx]
        if row["pivot_low"]:
            ob_idx = idx - 1
            ob_candle = frame.iloc[ob_idx]
            if ob_candle["close"] < ob_candle["open"]:
                low, high = _ob_range(ob_candle, range_mode)
                move = row["high"] - ob_candle["high"]
                atr_move = move >= (min_move_atr * row["atr"])
                pct_move = (move / ob_candle["close"]) * 100 >= min_move_pct
                if atr_move or pct_move:
                    order_blocks.append(
                        OrderBlock(
                            id=str(uuid4()),
                            symbol=symbol,
                            timeframe=timeframe,
                            direction="bull",
                            created_at=datetime.utcnow(),
                            low=low,
                            high=high,
                            impulse_candles=min_impulse_candles,
                            min_move=move,
                        )
                    )
        if row["pivot_high"]:
            ob_idx = idx - 1
            ob_candle = frame.iloc[ob_idx]
            if ob_candle["close"] > ob_candle["open"]:
                low, high = _ob_range(ob_candle, range_mode)
                move = ob_candle["low"] - row["low"]
                atr_move = move >= (min_move_atr * row["atr"])
                pct_move = (move / ob_candle["close"]) * 100 >= min_move_pct
                if atr_move or pct_move:
                    order_blocks.append(
                        OrderBlock(
                            id=str(uuid4()),
                            symbol=symbol,
                            timeframe=timeframe,
                            direction="bear",
                            created_at=datetime.utcnow(),
                            low=low,
                            high=high,
                            impulse_candles=min_impulse_candles,
                            min_move=move,
                        )
                    )
    return order_blocks


def validate_order_blocks(order_blocks: list[OrderBlock], close: float, invalidate_on_wick: bool) -> list[OrderBlock]:
    validated: list[OrderBlock] = []
    for ob in order_blocks:
        if ob.direction == "bull":
            invalidated = close < ob.low if invalidate_on_wick else close < ob.low
        else:
            invalidated = close > ob.high if invalidate_on_wick else close > ob.high
        if invalidated:
            ob.valid = False
        validated.append(ob)
    return validated
