from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from cryptography.fernet import Fernet

from app.core.schemas import TradingConfig


DATA_DIR = Path("data")
CONFIG_FILE = DATA_DIR / "config.json"
KEY_FILE = DATA_DIR / "key.bin"


class ConfigStorage:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(self._load_or_create_key())

    def load(self) -> TradingConfig:
        if not CONFIG_FILE.exists():
            config = TradingConfig()
            self.save(config)
            return config
        payload = json.loads(CONFIG_FILE.read_text())
        decrypted = self._decrypt_sensitive(payload)
        return TradingConfig.model_validate(decrypted)

    def save(self, config: TradingConfig) -> None:
        payload = config.model_dump()
        encrypted = self._encrypt_sensitive(payload)
        CONFIG_FILE.write_text(json.dumps(encrypted, indent=2, sort_keys=True))

    def _load_or_create_key(self) -> bytes:
        if KEY_FILE.exists():
            return KEY_FILE.read_bytes()
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        return key

    def _encrypt_sensitive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        binance = payload.get("binance", {})
        for key in ("api_key", "api_secret"):
            value = binance.get(key)
            if value:
                binance[key] = self._fernet.encrypt(value.encode()).decode()
        payload["binance"] = binance
        return payload

    def _decrypt_sensitive(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        binance = payload.get("binance", {})
        for key in ("api_key", "api_secret"):
            value = binance.get(key)
            if value:
                binance[key] = self._fernet.decrypt(value.encode()).decode()
        payload["binance"] = binance
        return payload
