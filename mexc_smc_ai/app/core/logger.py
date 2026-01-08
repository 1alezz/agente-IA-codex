"""Logger com saída JSON e narrativa humana."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    RESERVED_KEYS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()) | {"message"}



class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in self.RESERVED_KEYS:
                continue
            payload[key] = value
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


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    message: str | None = None,
    level: str = "info",
    **fields: Any,
) -> None:
    safe_fields = {}
    for key, value in fields.items():
        if key in JsonFormatter.RESERVED_KEYS:
            safe_fields[f"event_{key}"] = value
        else:
            safe_fields[key] = value
    if message is not None:
        safe_fields["event_message"] = message
    log_method = getattr(logger, level, logger.info)
    log_method(event, extra=safe_fields)
