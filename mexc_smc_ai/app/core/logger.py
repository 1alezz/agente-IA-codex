"""Logger com saída JSON e narrativa humana."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    json_handler = logging.StreamHandler()
    json_handler.setFormatter(JsonFormatter())

    human_handler = logging.StreamHandler()
    human_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
    )

    logger.addHandler(json_handler)
    logger.addHandler(human_handler)
    logger.propagate = False
    return logger
