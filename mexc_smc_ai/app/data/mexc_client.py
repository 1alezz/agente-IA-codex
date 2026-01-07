"""Cliente REST para a MEXC com retry, backoff e rate limit."""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from app.core.config import env
from app.core.logger import get_logger


LOGGER = get_logger(__name__)


@dataclass
class MexcClient:
    base_url: str = env("MEXC_BASE_URL", "https://api.mexc.com") or "https://api.mexc.com"
    timeout: int = int(env("MEXC_TIMEOUT", "10") or 10)
    max_retries: int = 3
    backoff_seconds: float = 1.5

    def _request(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}{path}"
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                if response.status_code == 429:
                    LOGGER.warning(
                        "rate_limit",
                        extra={"message": "Rate limit atingido", "attempt": attempt},
                    )
                    time.sleep(self.backoff_seconds * attempt)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                LOGGER.error(
                    "request_failed",
                    extra={"message": "Falha ao requisitar MEXC", "error": str(exc)},
                )
                time.sleep(self.backoff_seconds * attempt)
        raise RuntimeError("Falha após tentativas na MEXC")

    def get_klines(self, symbol: str, interval: str, limit: int = 200) -> list:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        return self._request("/api/v3/klines", params=params)
