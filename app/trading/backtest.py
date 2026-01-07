from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.core.schemas import BacktestConfig, StrategySignal


@dataclass
class BacktestResult:
    total_pnl_usd: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    trades: int
    equity_curve: List[float]


class Backtester:
    def run(self, config: BacktestConfig, signals: List[StrategySignal]) -> BacktestResult:
        return BacktestResult(
            total_pnl_usd=0.0,
            max_drawdown_pct=0.0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            trades=0,
            equity_curve=[],
        )
