"""Pipeline principal: dados -> indicadores -> SMC -> IA -> sinais."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pandas as pd

from app.ai.decision import decide
from app.ai.features import build_features
from app.ai.model import build_model
from app.core.logger import get_logger, log_event
from app.core.models import Signal
from app.core.state import EngineState
from app.data.feed import fetch_candles
from app.data.mexc_client import MexcClient
from app.indicators.atr import compute_atr
from app.indicators.divergence import detect_rsi_divergence
from app.indicators.pivots import detect_pivots
from app.indicators.rsi import compute_rsi
from app.indicators.volume import volume_spike
from app.smc.bias import compute_bias
from app.smc.confluence import bias_allows, ob_touch
from app.smc.order_blocks import find_order_blocks, validate_order_blocks
from app.engine.paper_broker import PaperBroker


LOGGER = get_logger(__name__)


class SignalEngine:
    def __init__(self, config: dict, state: EngineState) -> None:
        self.config = config
        self.state = state
        self.client = MexcClient()
        self.paper_broker = PaperBroker(state=state)
        self.model = build_model(config["ai"]["model_type"])
        self.cooldowns: dict[str, datetime] = {}

    def _enrich_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame = detect_pivots(
            frame,
            left=self.config["order_block"]["pivot_left"],
            right=self.config["order_block"]["pivot_right"],
        )
        frame["rsi"] = compute_rsi(frame["close"])
        frame = detect_rsi_divergence(frame)
        frame["atr"] = compute_atr(frame, period=self.config["risk"]["atr_period"])
        frame["volume_spike"] = volume_spike(
            frame,
            period=self.config["confluence"]["volume_sma_period"],
            mult=self.config["confluence"]["volume_spike_mult"],
        )
        return frame

    def process_symbol_timeframe(self, symbol: str, timeframe: str, bias: str) -> None:
        frame = fetch_candles(self.client, symbol, timeframe)
        frame = self._enrich_frame(frame)

        obs = find_order_blocks(
            frame,
            symbol=symbol,
            timeframe=timeframe,
            range_mode=self.config["order_block"]["range_mode"],
            min_move_atr=self.config["order_block"]["min_move_atr"],
            min_move_pct=self.config["order_block"]["min_move_pct"],
            min_impulse_candles=self.config["order_block"]["min_impulse_candles"],
        )

        last_close = float(frame["close"].iloc[-1])
        validated = validate_order_blocks(
            obs,
            close=last_close,
            invalidate_on_wick=self.config["order_block"]["invalidate_on_wick"],
        )

        for ob in validated:
            if not ob.valid:
                continue
            key = f"{symbol}-{timeframe}-{ob.id}"
            if self._cooldown_active(key):
                continue
            last = frame.iloc[-1]
            direction = "buy" if ob.direction == "bull" else "sell"
            touch = ob_touch(ob, last["high"], last["low"], last["close"])
            div_ok = (last["bull_divergence"] if ob.direction == "bull" else last["bear_divergence"])
            vol_ok = bool(last["volume_spike"])
            bias_ok = bias_allows(direction, bias)

            confluence_map = {
                "touch": "ok" if touch else "fail",
                "divergence": "ok" if div_ok else "fail",
                "volume": "ok" if vol_ok else "fail",
                "bias": bias,
            }

            if not touch:
                continue
            if self.config["confluence"]["require_rsi_divergence"] and not div_ok:
                continue
            if self.config["confluence"]["require_volume_spike"] and not vol_ok:
                continue
            if self.config["confluence"]["require_bias_alignment"] and not bias_ok:
                continue

            for profile, settings in self.config["profiles"].items():
                if not settings["enabled"]:
                    continue
                features = build_features(frame, ob, bias=bias, profile=profile)
                probability = self.model.predict_proba(features)
                decision = decide(
                    probability=probability,
                    min_probability=settings["ai_threshold"],
                    regime="trend" if bias != "neutral" else "sideways",
                    drawdown=0.0,
                )
                signal = Signal(
                    id=str(uuid4()),
                    symbol=symbol,
                    timeframe=timeframe,
                    profile=profile,
                    direction=direction,
                    score=probability,
                    reason=decision.reason,
                    timestamp=datetime.utcnow(),
                    order_block_id=ob.id,
                    confluences=confluence_map,
                    status="enter" if decision.action == "ENTER" else "skip",
                )
                self.state.add_signal(signal)
                self.state.add_log(
                    {
                        "event": "signal_generated",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "profile": profile,
                        "decision": decision.action,
                        "probability": probability,
                        "reason": decision.reason,
                    }
                )
                log_event(
                    LOGGER,
                    "signal_generated",
                    message="Sinal gerado",
                    symbol=symbol,
                    timeframe=timeframe,
                    profile=profile,
                    direction=direction,
                    decision=decision.action,
                )
                if decision.action == "ENTER":
                    self.paper_broker.open_trade(signal, frame, ob)
                    self._mark_cooldown(key)

    def run_cycle(self) -> None:
        higher_tfs = self.config["timeframes"]["higher_tf"]
        exec_tfs = self.config["timeframes"]["execution_tf"]
        for symbol in self.config["symbols"]:
            bias = "neutral"
            for tf in higher_tfs:
                higher_frame = fetch_candles(self.client, symbol, tf)
                bias = compute_bias(higher_frame)
            for tf in exec_tfs:
                self.process_symbol_timeframe(symbol, tf, bias)
        self.state.last_update = datetime.utcnow()

    def _cooldown_active(self, key: str) -> bool:
        cooldown_minutes = self.config["engine"]["cooldown_minutes"]
        if key not in self.cooldowns:
            return False
        elapsed = datetime.utcnow() - self.cooldowns[key]
        return elapsed.total_seconds() < (cooldown_minutes * 60)

    def _mark_cooldown(self, key: str) -> None:
        self.cooldowns[key] = datetime.utcnow()
