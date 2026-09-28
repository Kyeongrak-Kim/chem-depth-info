"""Streamlit UI for chem-depth-info.

The periodic table, instrument picker, and depth figure live in one component.
Choosing an element or an instrument updates that frame in place, so the page
does not reload and the scroll position stays put. Several instruments can be
selected and drawn together on one length scale.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app import load_elements
from app.display import STREAMLIT_CSS, header_html
from app.simulation import equipment_catalog

_PICKER = components.declare_component(
    "chem_picker",
    path=str(Path(__file__).resolve().parent / "app" / "picker"),
)

st.set_page_config(page_title="chem-depth-info", layout="wide", initial_sidebar_state="collapsed")
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
st.markdown(header_html(), unsafe_allow_html=True)

_PICKER(
    elements=load_elements(),
    equipment=equipment_catalog(),
    key="chem_picker",
)
