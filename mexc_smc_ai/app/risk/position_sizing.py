"""Position sizing simplificado (stub)."""
from __future__ import annotations


def fixed_risk_size(equity: float, risk_pct: float, stop_distance: float) -> float:
    if stop_distance == 0:
        return 0.0
    risk_amount = equity * risk_pct
    return risk_amount / stop_distance
