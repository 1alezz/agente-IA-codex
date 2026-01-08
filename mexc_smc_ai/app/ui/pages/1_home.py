"""Página inicial com status."""
from __future__ import annotations

import streamlit as st

state = st.session_state["engine_state"]

st.header("Status")
col1, col2, col3 = st.columns(3)
col1.metric("Motor", "Rodando" if state.last_update else "Parado")
col2.metric("Última atualização", str(state.last_update) if state.last_update else "-" )
col3.metric("Sinais", len(state.signals))

st.subheader("Erros recentes")
if state.logs:
    st.json(list(state.logs)[:5])
else:
    st.info("Nenhum erro recente registrado.")
