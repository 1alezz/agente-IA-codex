"""Monitoramento de sinais."""
from __future__ import annotations

import pandas as pd
import streamlit as st

state = st.session_state["engine_state"]

st.header("Sinais")

if not state.signals:
    st.info("Nenhum sinal gerado ainda.")
else:
    data = [
        {
            "symbol": s.symbol,
            "tf": s.timeframe,
            "profile": s.profile,
            "direction": s.direction,
            "score": round(s.score, 3),
            "status": s.status,
            "reason": s.reason,
        }
        for s in state.signals
    ]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.subheader("Narrativa")
    for signal in list(state.signals)[:5]:
        st.write(f"{signal.symbol} {signal.timeframe} {signal.profile} -> {signal.status}")
        st.json(signal.confluences)
