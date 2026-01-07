from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, List

import pandas as pd

from app.core.logging import LogBuffer, TradeLogBuffer
from app.core.schemas import AgentDecision, AgentStatus, PerformanceSnapshot, PositionSnapshot, StrategySignal, TradingConfig
from app.trading.datafeed import DataFeed
from app.trading.strategies.fvg import FVGDetector
from app.trading.strategies.liquidity import LiquiditySweepDetector
from app.trading.strategies.market_structure import MarketStructureDetector
from app.trading.strategies.moving_average import MovingAverageFilter
from app.trading.strategies.order_blocks import OrderBlockDetector
from app.trading.strategies.rsi_divergence import RSIDivergenceDetector
from app.trading.strategies.turtle_soup import TurtleSoupDetector


class TradingAgent:
    def __init__(self, config: TradingConfig, logger: LogBuffer, trade_logger: TradeLogBuffer) -> None:
        self.config = config
        self.logger = logger
        self.trade_logger = trade_logger
        self.running = False
        self.last_decisions: List[AgentDecision] = []
        self._task: asyncio.Task | None = None
        self._strategies = {
            "order_blocks": OrderBlockDetector(),
            "fvg": FVGDetector(),
            "liquidity_sweeps": LiquiditySweepDetector(),
            "rsi_divergence": RSIDivergenceDetector(),
            "market_structure": MarketStructureDetector(),
            "turtle_soup": TurtleSoupDetector(),
            "moving_average_filter": MovingAverageFilter(),
        }

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        self.logger.add("Agente iniciado e monitorando mercado em modo continuo.")

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        if self._task:
            self._task.cancel()
        self.logger.add("Agente pausado pelo usuário.")

    def update_config(self, config: TradingConfig) -> None:
        self.config = config
        self.logger.add("Configurações atualizadas via dashboard.")

    async def _run_loop(self) -> None:
        while self.running:
            await self._tick()
            await asyncio.sleep(self.config.dashboard.refresh_seconds)

    async def _tick(self) -> None:
        symbols = [asset.symbol for asset in self.config.assets]
        timeframes = sorted({tf for asset in self.config.assets for tf in asset.timeframes})
        feed = DataFeed(symbols, timeframes)
        data = feed.fetch_latest()
        for symbol, frames in data.items():
            for timeframe, candles in frames.items():
                enabled = [key for key, enabled in self.config.strategies.model_dump().items() if enabled]
                bias = self._current_bias(candles)
                checklist = [
                    f"Ativo: {symbol}",
                    f"Timeframe: {timeframe}",
                    f"Bias: {bias}",
                    f"Observando: {', '.join(enabled) if enabled else 'nenhuma estratégia ativa'}",
                ]
                self.logger.add(" | ".join(checklist))
                decision = self._evaluate_symbol(symbol, timeframe, candles)
                if decision:
                    self.last_decisions.append(decision)
                    self.last_decisions = self.last_decisions[-10:]
                else:
                    self.logger.add(f"{symbol} [{timeframe}] sem sinais relevantes no momento.")

    def _evaluate_symbol(self, symbol: str, timeframe: str, candles: pd.DataFrame) -> AgentDecision | None:
        enabled = self.config.strategies.model_dump()
        signals: List[StrategySignal] = []
        for key, detector in self._strategies.items():
            if enabled.get(key, False):
                signals.extend(detector.detect(candles))
        if not signals:
            return None
        reason = "Confluência de sinais ICT identificada." 
        decision = AgentDecision(
            symbol=symbol,
            timeframe=timeframe,
            action="monitor",
            reason=reason,
            signals=signals,
        )
        self.logger.add(
            f"{symbol} [{timeframe}] sinais detectados ({len(signals)}). Decisão: {decision.action}."
        )
        return decision

    def _current_bias(self, candles: pd.DataFrame) -> str:
        if candles.empty:
            return "Neutro (dados insuficientes)"
        return "Neutro"

    def log_trade_event(self, message: str) -> None:
        self.trade_logger.add_trade(message)

    def status(self) -> AgentStatus:
        return AgentStatus(
            running=self.running,
            mode="TESTNET" if self.config.binance.use_testnet else "REAL",
            last_decisions=self.last_decisions,
            performance=self._performance_snapshot(),
            positions=self._positions_snapshot(),
        )

    def _positions_snapshot(self) -> List[PositionSnapshot]:
        return []

    def _performance_snapshot(self) -> PerformanceSnapshot:
        return PerformanceSnapshot(
            total_pnl_usd=0.0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            max_drawdown_pct=0.0,
            trades=0,
        )

    def log_decision_summary(self, decision: AgentDecision) -> None:
        timestamp = datetime.utcnow().isoformat()
        self.logger.add(
            f"{timestamp} - {decision.symbol} {decision.action}: {decision.reason}"
        )
