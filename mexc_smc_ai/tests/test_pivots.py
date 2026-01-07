import pandas as pd

from app.indicators.pivots import detect_pivots


def test_detect_pivots_marks_high_low():
    frame = pd.DataFrame(
        {
            "high": [1, 2, 3, 2, 1],
            "low": [1, 0.5, 0.2, 0.5, 1],
        }
    )
    result = detect_pivots(frame, left=1, right=1)
    assert result["pivot_high"].iloc[2]
    assert result["pivot_low"].iloc[2]
