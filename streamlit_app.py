"""Streamlit UI for chem-depth-info.

Uses the same Python simulation as the Flask app (`app.simulation`).
The layout and colors follow the Flask page so it does not look like
default Streamlit chrome.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from app import load_elements
from app.display import (
    STREAMLIT_CSS,
    energy_head_html,
    equipment_html,
    header_html,
    periodic_table_html,
    results_html,
)
from app.simulation import EQUIPMENT, equipment_catalog, simulate

st.set_page_config(page_title="chem-depth-info", layout="wide", initial_sidebar_state="collapsed")
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
st.markdown(header_html(), unsafe_allow_html=True)

elements = load_elements()
by_symbol = {el["symbol"]: el for el in elements}
catalog = equipment_catalog()
valid_eq = {eq["key"] for eq in catalog}

params = st.query_params
symbol = params.get("el", "Si")
eq_key = params.get("eq", "sims")
if symbol not in by_symbol:
    symbol = "Si"
if eq_key not in valid_eq:
    eq_key = "sims"

eq = EQUIPMENT[eq_key]
energy = st.session_state.get(f"energy-{eq_key}", float(eq.default_energy))

table, controls, results = st.columns((1.45, 0.85, 1.0), gap="medium")

with table:
    st.markdown(periodic_table_html(elements, symbol, eq_key), unsafe_allow_html=True)

with controls:
    st.markdown(equipment_html(catalog, eq_key, symbol), unsafe_allow_html=True)
    st.markdown(energy_head_html(energy), unsafe_allow_html=True)
    energy = st.slider(
        "빔 에너지",
        min_value=float(eq.min_energy),
        max_value=float(eq.max_energy),
        value=float(eq.default_energy),
        step=0.01,
        key=f"energy-{eq_key}",
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="cd-energy-scale"><span>{eq.min_energy:g} keV</span>'
        f"<span>{eq.max_energy:g} keV</span></div>"
        f'<p class="cd-desc">{eq.description}</p>',
        unsafe_allow_html=True,
    )

with results:
    result = simulate(by_symbol[symbol], eq_key, energy)
    st.markdown(results_html(result, symbol), unsafe_allow_html=True)
