"""Paper trades."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

state = st.session_state["engine_state"]

st.header("Paper Trades")

if not state.trades:
    st.info("Nenhum trade simulado.")
else:
    data = [
        {
            "symbol": t.symbol,
            "profile": t.profile,
            "direction": t.direction,
            "status": t.status,
            "entry": t.entry_price,
            "exit": t.exit_price,
            "pnl": t.pnl,
        }
        for t in state.trades
    ]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    pnl_series = df["pnl"].fillna(0).cumsum()
    fig = px.line(pnl_series, title="Equity Curve")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Narrativas")
    for trade in list(state.trades)[:3]:
        st.write(f"Trade {trade.symbol} {trade.profile}")
        st.write(trade.narrative)
