"""Scheduler de polling por timeframe."""
from __future__ import annotations

import time

from app.core.logger import get_logger, log_event
from app.engine.signal_engine import SignalEngine


LOGGER = get_logger(__name__)


class EngineScheduler:
    def __init__(self, engine: SignalEngine, polling_seconds: int) -> None:
        self.engine = engine
        self.polling_seconds = polling_seconds

    def run(self) -> None:
        while True:
            try:
                self.engine.run_cycle()
            except Exception as exc:
                log_event(
                    LOGGER,
                    "engine_cycle_failed",
                    message="Erro no ciclo da engine",
                    error=str(exc),
                    level="error",
                )
            time.sleep(self.polling_seconds)
