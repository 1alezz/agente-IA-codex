"""Interface de execução (stub para fase 2)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class ExecutionInterface(ABC):
    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float, price: float | None = None) -> dict:
        raise NotImplementedError


class MexcExecution(ExecutionInterface):
    def place_order(self, symbol: str, side: str, quantity: float, price: float | None = None) -> dict:
        return {
            "status": "stub",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }
