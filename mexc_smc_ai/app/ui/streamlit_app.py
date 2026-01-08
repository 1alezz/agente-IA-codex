"""Streamlit app principal."""
from __future__ import annotations

import streamlit as st

from app.core.config import load_config
from app.core.state import EngineState


st.set_page_config(page_title="MEXC SMC AI", layout="wide")

if "config" not in st.session_state:
    st.session_state["config"] = load_config()
if "engine_state" not in st.session_state:
    st.session_state["engine_state"] = EngineState()

st.sidebar.title("MEXC SMC AI")
st.sidebar.caption("Motor de sinais - Fase 1")

st.title("Dashboard MEXC SMC AI")
st.write("Use o menu lateral para navegar.")
