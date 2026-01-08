from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TradingState:
    features: Dict[str, float]
    positions: Dict[str, float]


@dataclass
class TradingAction:
    name: str
    params: Dict[str, float]


class TradingEnvironment:
    def __init__(self, symbols: List[str]) -> None:
        self.symbols = symbols
        self.current_step = 0

    def reset(self) -> TradingState:
        self.current_step = 0
        return TradingState(features={}, positions={})

    def step(self, action: TradingAction) -> TradingState:
        self.current_step += 1
        return TradingState(features={}, positions={})
