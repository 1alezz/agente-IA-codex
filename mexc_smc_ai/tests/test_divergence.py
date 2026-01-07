import pandas as pd

from app.indicators.divergence import detect_rsi_divergence


def test_detects_bullish_divergence():
    frame = pd.DataFrame(
        {
            "low": [10, 9, 8, 7],
            "high": [12, 11, 10, 9],
            "pivot_low": [False, True, False, True],
            "pivot_high": [False, False, False, False],
            "rsi": [30, 25, 28, 35],
        }
    )
    result = detect_rsi_divergence(frame)
    assert result["bull_divergence"].iloc[-1]
