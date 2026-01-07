"""Logs do motor."""
from __future__ import annotations

import streamlit as st

state = st.session_state["engine_state"]

st.header("Logs")

if not state.logs:
    st.info("Nenhum log disponível.")
else:
    st.json(list(state.logs)[:50])
