"""Modelos principais usados pelo motor."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class Candle:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class OrderBlock:
    id: str
    symbol: str
    timeframe: str
    direction: Literal["bull", "bear"]
    created_at: datetime
    low: float
    high: float
    valid: bool = True
    mitigated: bool = False
    impulse_candles: int = 0
    min_move: float = 0.0


@dataclass(slots=True)
class Signal:
    id: str
    symbol: str
    timeframe: str
    profile: Literal["scalping", "daytrade", "swing"]
    direction: Literal["buy", "sell"]
    score: float
    reason: str
    timestamp: datetime
    order_block_id: str
    confluences: dict[str, str] = field(default_factory=dict)
    status: Literal["enter", "skip"] = "skip"


@dataclass(slots=True)
class Trade:
    id: str
    symbol: str
    timeframe: str
    profile: str
    direction: str
    entry_price: float
    stop_price: float
    target_price: float
    status: Literal["open", "closed"]
    opened_at: datetime
    closed_at: datetime | None = None
    exit_price: float | None = None
    pnl: float | None = None
    narrative: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Decision:
    action: Literal["ENTER", "SKIP"]
    probability: float
    reason: str
