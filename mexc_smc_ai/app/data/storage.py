"""Storage opcional para histórico (stub)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.logger import get_logger


LOGGER = get_logger(__name__)


def save_history(path: str, frame: pd.DataFrame) -> None:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(db_path, index=False)
    LOGGER.info("history_saved", extra={"message": "Histórico salvo", "path": str(db_path)})
