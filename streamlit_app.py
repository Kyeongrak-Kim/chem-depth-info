"""Streamlit UI for chem-depth-info.

Uses the same Python simulation as the Flask app (`app.simulation`).
Run with:

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from app import load_elements
from app.display import cross_section_svg, format_length
from app.simulation import EQUIPMENT, simulate

CAT_COLORS = {
    "nonmetals": "#7ee787",
    "noble-gases": "#a5d8ff",
    "alkali-metals": "#ffa8a8",
    "alkaline-earth-metals": "#ffd8a8",
    "metalloids": "#b2f2bb",
    "halogens": "#99e9f2",
    "post-transition-metals": "#bac8ff",
    "transition-metals": "#ffec99",
    "lanthanides": "#eebefa",
    "actinides": "#fcc2d7",
    "unknown": "#ced4da",
}


st.set_page_config(page_title="chem-depth-info", layout="wide")
st.title("chem-depth-info")
st.caption("분석 장비별 원소 침투 깊이·폭 시뮬레이터 · Streamlit / Python")

elements = load_elements()
by_symbol = {el["symbol"]: el for el in elements}
grid = {(el["row"], el["col"]): el for el in elements}

if "symbol" not in st.session_state:
    st.session_state.symbol = "Si"

st.subheader("1 · 원소 선택")
st.caption(f"선택: **{st.session_state.symbol} · {by_symbol[st.session_state.symbol]['name']}**")

max_row = max(el["row"] for el in elements)
for row in range(1, max_row + 1):
    cols = st.columns(18, gap="small")
    for col in range(1, 19):
        el = grid.get((row, col))
        with cols[col - 1]:
            if el is None:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                continue
            color = CAT_COLORS.get(el["category"], "#ced4da")
            selected = el["symbol"] == st.session_state.symbol
            if st.button(
                el["symbol"],
                key=f"pt-{el['symbol']}",
                help=f"{el['name']} (Z={el['number']})",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.symbol = el["symbol"]
                st.rerun()
            st.markdown(
                f"<div style='height:4px;border-radius:2px;background:{color};margin:-6px 0 4px'></div>",
                unsafe_allow_html=True,
            )

left, right = st.columns((1, 1), gap="large")

with left:
    st.subheader("2 · 분석 장비")
    labels = [f"{eq.name} · {eq.full_name}" for eq in EQUIPMENT.values()]
    keys = list(EQUIPMENT)
    chosen = st.radio("장비", labels, index=0, label_visibility="collapsed")
    eq_key = keys[labels.index(chosen)]
    eq = EQUIPMENT[eq_key]
    st.write(eq.description)

    st.subheader("3 · 빔 에너지")
    energy = st.slider(
        "keV",
        min_value=float(eq.min_energy),
        max_value=float(eq.max_energy),
        value=float(eq.default_energy),
        step=0.01,
        key=f"energy-{eq_key}",
    )

with right:
    result = simulate(by_symbol[st.session_state.symbol], eq_key, energy)
    st.subheader("결과")
    m1, m2, m3 = st.columns(3)
    m1.metric("침투 깊이", format_length(result["depth_um"]))
    m2.metric("분석 폭", format_length(result["width_um"]))
    m3.metric("종횡비", f"{result['aspect_ratio']:.3f}")
    if result["sputtering"]:
        st.metric("스퍼터 크레이터 깊이", format_length(result["crater_depth_um"]))
    st.markdown(
        f"{st.session_state.symbol} · {result['equipment_name']} @ {result['energy_keV']} keV — "
        f"깊이 {format_length(result['depth_um'])}, 폭 {format_length(result['width_um'])} (로그 스케일)",
    )
    st.markdown(cross_section_svg(result), unsafe_allow_html=True)
