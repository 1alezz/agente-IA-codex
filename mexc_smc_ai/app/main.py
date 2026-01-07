"""Entrypoint para executar engine ou lançar dashboard."""
from __future__ import annotations

import argparse
import os
import subprocess

from app.engine.signal_engine import SignalEngine
from app.engine.scheduler import EngineScheduler
from app.core.logger import get_logger
from app.core.state import EngineState
from app.core.config import load_config


LOGGER = get_logger(__name__)


def run_engine() -> None:
    config = load_config()
    state = EngineState()
    engine = SignalEngine(config=config, state=state)
    scheduler = EngineScheduler(engine=engine, polling_seconds=config["engine"]["polling_seconds"])
    LOGGER.info("engine_start", extra={"message": "Iniciando engine de sinais"})
    scheduler.run()


def run_streamlit() -> None:
    LOGGER.info("ui_start", extra={"message": "Abrindo Streamlit"})
    streamlit_cmd = [
        "streamlit",
        "run",
        "app/ui/streamlit_app.py",
    ]
    subprocess.run(streamlit_cmd, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="MEXC SMC AI")
    parser.add_argument("--mode", choices=["engine", "ui"], default="engine")
    args = parser.parse_args()

    if args.mode == "ui":
        run_streamlit()
    else:
        run_engine()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    main()
