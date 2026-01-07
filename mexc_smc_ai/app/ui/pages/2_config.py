"""Página de configuração."""
from __future__ import annotations

import streamlit as st

config = st.session_state["config"]

st.header("Configurações")

symbols = st.multiselect("Símbolos", options=config["symbols"], default=config["symbols"])
timeframes = st.multiselect(
    "Timeframes de execução",
    options=config["timeframes"]["execution_tf"],
    default=config["timeframes"]["execution_tf"],
)

st.subheader("Order Blocks")
config["order_block"]["pivot_left"] = st.number_input("Pivot Left", 1, 10, config["order_block"]["pivot_left"])
config["order_block"]["pivot_right"] = st.number_input("Pivot Right", 1, 10, config["order_block"]["pivot_right"])
config["order_block"]["range_mode"] = st.selectbox("Range Mode", ["wick", "body"], index=0)

st.subheader("IA")
config["ai"]["min_probability"] = st.slider("Probabilidade mínima", 0.0, 1.0, config["ai"]["min_probability"])

if st.button("Salvar config"):
    config["symbols"] = symbols
    config["timeframes"]["execution_tf"] = timeframes
    st.success("Configuração atualizada em memória")
