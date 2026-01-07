"""Carrega configurações de YAML e .env."""
from __future__ import annotations

import os
from pathlib import Path

import yaml


def load_config() -> dict:
    base_path = Path(__file__).resolve().parents[2]
    config_path = base_path / "config.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)
