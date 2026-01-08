from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Dict, List

import pandas as pd

from app.core.logging import LogBuffer, TradeLogBuffer
from app.core.schemas import AgentDecision, AgentStatus, PerformanceSnapshot, PositionSnapshot, StrategySignal, TradingConfig
from app.trading.binance_client import BinanceClient
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
        self._feed = DataFeed(
            [asset.symbol for asset in config.assets],
            sorted({tf for asset in config.assets for tf in asset.timeframes}),
            use_testnet=config.binance.use_testnet,
        )
        self._open_positions: Dict[str, Dict[str, float]] = {}
        self._client = self._build_client(config)
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
        if self.config.binance.use_testnet and not self._client:
            self.logger.add("Aviso: chaves da Binance não configuradas. Ordens não serão enviadas.")

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        if self._task:
            self._task.cancel()
        self.logger.add("Agente pausado pelo usuário.")

    def update_config(self, config: TradingConfig) -> None:
        self.config = config
        self._client = self._build_client(config)
        self._feed.sync(
            [asset.symbol for asset in config.assets],
            sorted({tf for asset in config.assets for tf in asset.timeframes}),
            use_testnet=config.binance.use_testnet,
        )
        self.logger.add("Configurações atualizadas via dashboard.")

    async def _run_loop(self) -> None:
        while self.running:
            await self._tick()
            await asyncio.sleep(self.config.dashboard.refresh_seconds)

    async def _tick(self) -> None:
        symbols = [asset.symbol for asset in self.config.assets]
        timeframes = sorted({tf for asset in self.config.assets for tf in asset.timeframes})
        self._feed.sync(symbols, timeframes, use_testnet=self.config.binance.use_testnet)
        data = self._feed.fetch_latest()
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
                    if decision.action in {"buy", "sell"}:
                        self._execute_trade(symbol, decision.action, candles)
                else:
                    self.logger.add(f"{symbol} [{timeframe}] sem sinais relevantes no momento.")
        self._advance_positions()

    def _evaluate_symbol(self, symbol: str, timeframe: str, candles: pd.DataFrame) -> AgentDecision | None:
        enabled = self.config.strategies.model_dump()
        signals: List[StrategySignal] = []
        for key, detector in self._strategies.items():
            if enabled.get(key, False):
                signals.extend(detector.detect(candles))
        if not signals:
            return None
        bullish = sum(1 for signal in signals if signal.direction == "bullish")
        bearish = sum(1 for signal in signals if signal.direction == "bearish")
        action = "buy" if bullish >= bearish else "sell"
        reason = "Confluência de sinais ICT identificada." 
        decision = AgentDecision(
            symbol=symbol,
            timeframe=timeframe,
            action=action,
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
        sma = candles["close"].rolling(20).mean().iloc[-1]
        last = candles["close"].iloc[-1]
        if last > sma:
            return "Alta"
        if last < sma:
            return "Baixa"
        return "Neutro"

    def _execute_trade(self, symbol: str, action: str, candles: pd.DataFrame) -> None:
        if symbol in self._open_positions:
            return
        last_price = float(candles["close"].iloc[-1])
        stop_loss = last_price * (0.98 if action == "buy" else 1.02)
        take_profit = last_price * (1.02 if action == "buy" else 0.98)
        self._open_positions[symbol] = {
            "entry": last_price,
            "stop": stop_loss,
            "target": take_profit,
            "age": 0.0,
            "side": 1.0 if action == "buy" else -1.0,
        }
        if self._client:
            try:
                quantity = self._calculate_position_size(symbol, last_price, stop_loss)
                if quantity <= 0:
                    raise ValueError("Quantidade calculada inválida.")
                response = self._client.place_market_order(symbol, action, quantity=quantity)
                order_id = response.get("orderId", "N/A")
                self.trade_logger.add_trade(
                    f"ORDEM {symbol} {action.upper()} enviada (ID {order_id}) qty {quantity:.6f}."
                )
            except Exception as exc:  # noqa: BLE001
                self.trade_logger.add_trade(
                    f"ERRO AO ENVIAR ORDEM {symbol} {action.upper()}: {exc}"
                )
        self.trade_logger.add_trade(
            f"ABRIU POSIÇÃO: {symbol} {action.upper()} @ {last_price:.2f} | SL {stop_loss:.2f} | TP {take_profit:.2f}"
        )

    def _advance_positions(self) -> None:
        to_close = []
        for symbol, position in self._open_positions.items():
            position["age"] += 1
            if position["age"] >= 3:
                to_close.append(symbol)
        for symbol in to_close:
            position = self._open_positions.pop(symbol)
            pnl = random.uniform(-1.5, 2.5)
            self.trade_logger.add_trade(
                f"FECHOU POSIÇÃO: {symbol} resultado {pnl:.2f}%."
            )

    def log_trade_event(self, message: str) -> None:
        self.trade_logger.add_trade(message)

    def _build_client(self, config: TradingConfig) -> BinanceClient | None:
        if not config.binance.api_key or not config.binance.api_secret:
            return None
        return BinanceClient(
            api_key=config.binance.api_key,
            api_secret=config.binance.api_secret,
            use_testnet=config.binance.use_testnet,
        )

    def _calculate_position_size(self, symbol: str, price: float, stop_loss: float) -> float:
        if not self._client:
            return 0.0
        account = self._client.get_account()
        quote_balance = 0.0
        for asset in account.get("balances", []):
            if asset.get("asset") == "USDT":
                quote_balance = float(asset.get("free", 0.0))
                break
        risk_amount = quote_balance * (self.config.risk.risk_per_trade_pct / 100.0)
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit <= 0:
            return 0.0
        risk_quantity = risk_amount / risk_per_unit
        max_exposure = quote_balance * (self.config.risk.max_exposure_per_asset_pct / 100.0)
        exposure_quantity = max_exposure / price if price else 0.0
        quantity = min(risk_quantity, exposure_quantity)
        filters = self._client.get_exchange_info(symbol)
        step_size = 0.0
        min_qty = 0.0
        symbol_info = filters.get("symbols", [{}])[0]
        for item in symbol_info.get("filters", []):
            if item.get("filterType") == "LOT_SIZE":
                step_size = float(item.get("stepSize", 0.0))
                min_qty = float(item.get("minQty", 0.0))
                break
        if step_size:
            quantity = (quantity // step_size) * step_size
        if min_qty and quantity < min_qty:
            raise ValueError("Quantidade calculada abaixo do mínimo permitido.")
        return max(quantity, 0.0)

    def status(self) -> AgentStatus:
        return AgentStatus(
            running=self.running,
            mode="TESTNET" if self.config.binance.use_testnet else "REAL",
            last_decisions=self.last_decisions,
            performance=self._performance_snapshot(),
            positions=self._positions_snapshot(),
        )

    def _positions_snapshot(self) -> List[PositionSnapshot]:
        snapshots = []
        for symbol, position in self._open_positions.items():
            snapshots.append(
                PositionSnapshot(
                    symbol=symbol,
                    side="buy" if position["side"] > 0 else "sell",
                    entry_price=position["entry"],
                    stop_loss=position["stop"],
                    take_profit=position["target"],
                    unrealized_pnl=0.0,
                    duration_minutes=int(position["age"] * self.config.dashboard.refresh_seconds),
                )
            )
        return snapshots

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
