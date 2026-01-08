"""Gerencia o estado em memória do motor e do dashboard."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime

from app.core.models import OrderBlock, Signal, Trade


@dataclass
class EngineState:
    order_blocks: dict[str, list[OrderBlock]] = field(default_factory=lambda: defaultdict(list))
    signals: deque[Signal] = field(default_factory=lambda: deque(maxlen=500))
    trades: deque[Trade] = field(default_factory=lambda: deque(maxlen=500))
    logs: deque[dict] = field(default_factory=lambda: deque(maxlen=500))
    last_update: datetime | None = None

    def add_order_block(self, key: str, ob: OrderBlock) -> None:
        self.order_blocks[key].append(ob)

    def add_signal(self, signal: Signal) -> None:
        self.signals.appendleft(signal)

    def add_trade(self, trade: Trade) -> None:
        self.trades.appendleft(trade)

    def add_log(self, record: dict) -> None:
        self.logs.appendleft(record)
