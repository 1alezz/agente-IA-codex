from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict
from urllib.parse import urlencode

import httpx


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, use_testnet: bool = True) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://testnet.binance.vision" if use_testnet else "https://api.binance.com"

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000,
        }
        return self._signed_request("POST", "/api/v3/order", params)

    def _signed_request(self, method: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urlencode(params)
        signature = hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        signed_query = f"{query}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.base_url}{path}?{signed_query}"
        response = httpx.request(method, url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
