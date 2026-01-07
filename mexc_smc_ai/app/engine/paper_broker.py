"""Simulação de trades (paper trading)."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pandas as pd

from app.core.models import OrderBlock, Signal, Trade
from app.core.state import EngineState
from app.indicators.atr import compute_atr
from app.risk.rules import target_from_atr
from app.risk.trailing import trailing_stop_long, trailing_stop_short


class PaperBroker:
    def __init__(self, state: EngineState) -> None:
        self.state = state

    def open_trade(self, signal: Signal, frame: pd.DataFrame, ob: OrderBlock) -> None:
        atr = compute_atr(frame).iloc[-1]
        entry = float(frame["close"].iloc[-1])
        stop = ob.low if signal.direction == "buy" else ob.high
        if signal.direction == "buy":
            stop -= atr * 0.5
        else:
            stop += atr * 0.5
        mult = 1.5
        target = target_from_atr(entry, atr, mult, signal.direction)
        trade = Trade(
            id=str(uuid4()),
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            profile=signal.profile,
            direction=signal.direction,
            entry_price=entry,
            stop_price=stop,
            target_price=target,
            status="open",
            opened_at=datetime.utcnow(),
            narrative=[
                f"OB {ob.direction} validado entre {ob.low:.2f}-{ob.high:.2f}",
                f"Entrada simulada {entry:.2f}",
                f"Stop inicial {stop:.2f}",
                f"Alvo inicial {target:.2f}",
            ],
        )
        self.state.add_trade(trade)

    def update_trades(self, frame: pd.DataFrame) -> None:
        if not self.state.trades:
            return
        atr = compute_atr(frame).iloc[-1]
        last = frame.iloc[-1]
        for trade in list(self.state.trades):
            if trade.status != "open":
                continue
            if trade.direction == "buy":
                trade.stop_price = trailing_stop_long(trade.stop_price, last["close"], atr, 1.2)
                if last["low"] <= trade.stop_price:
                    trade.status = "closed"
                    trade.exit_price = trade.stop_price
            else:
                trade.stop_price = trailing_stop_short(trade.stop_price, last["close"], atr, 1.2)
                if last["high"] >= trade.stop_price:
                    trade.status = "closed"
                    trade.exit_price = trade.stop_price
            if trade.status == "closed":
                trade.closed_at = datetime.utcnow()
                trade.pnl = (trade.exit_price - trade.entry_price) if trade.direction == "buy" else (trade.entry_price - trade.exit_price)
                trade.narrative.append(f"Trade encerrado com PnL {trade.pnl:.2f}")
