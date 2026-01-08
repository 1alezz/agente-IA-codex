import pandas as pd

from app.smc.order_blocks import find_order_blocks
from app.indicators.pivots import detect_pivots


def test_finds_bullish_order_block():
    frame = pd.DataFrame(
        {
            "open": [10, 9, 8, 9, 10],
            "close": [9, 8, 9, 10, 11],
            "high": [10, 9, 9, 10, 11],
            "low": [9, 8, 7, 8, 9],
        }
    )
    frame = detect_pivots(frame, left=1, right=1)
    obs = find_order_blocks(
        frame,
        symbol="BTCUSDT",
        timeframe="15m",
        range_mode="wick",
        min_move_atr=0.1,
        min_move_pct=0.1,
        min_impulse_candles=1,
    )
    assert any(ob.direction == "bull" for ob in obs)
