from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Deque, List


class LogBuffer:
    def __init__(self, max_entries: int = 500) -> None:
        self._entries: Deque[str] = deque(maxlen=max_entries)

    def add(self, message: str) -> None:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self._entries.appendleft(f"[{timestamp} UTC] {message}")

    def list(self) -> List[str]:
        return list(self._entries)


class TradeLogBuffer(LogBuffer):
    def add_trade(self, message: str) -> None:
        self.add(message)


def configure_logger(buffer: LogBuffer) -> logging.Logger:
    logger = logging.getLogger("trading_agent")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]

    class BufferHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            buffer.add(self.format(record))

    buffer_handler = BufferHandler()
    buffer_handler.setFormatter(formatter)
    logger.addHandler(buffer_handler)
    return logger
