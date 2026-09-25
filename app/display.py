"""Shared formatting, SVG, and Flask-matching HTML for Streamlit."""

from __future__ import annotations

import html
import math
from collections.abc import Iterable

CATEGORY_LABELS = {
    "nonmetals": "비금속",
    "noble-gases": "비활성 기체",
    "alkali-metals": "알칼리 금속",
    "alkaline-earth-metals": "알칼리 토금속",
    "metalloids": "준금속",
    "halogens": "할로겐",
    "post-transition-metals": "전이후 금속",
    "transition-metals": "전이 금속",
    "lanthanides": "란타넘족",
    "actinides": "악티늄족",
    "unknown": "기타",
}

STREAMLIT_CSS = """
<style>
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background: radial-gradient(1200px 600px at 20% -10%, #16203c 0%, #0b1020 60%) !important;
    color: #e8ecf7;
  }
  [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], #MainMenu, footer, .stDeployButton,
  [data-testid="stAppDeployButton"] { display: none !important; }
  .stMainBlockContainer, .block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 2rem !important;
    max-width: 1500px !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    background: #141b30;
    border: 1px solid #263156;
    border-radius: 14px;
    padding: 16px 14px 18px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
  }
  .cd-panel {
    background: #141b30;
    border: 1px solid #263156;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
    margin: 12px 0 16px;
  }
  [data-testid="stSlider"] label { color: #9aa6c4 !important; }
  [data-testid="stSlider"] div[data-baseweb="slider"] { padding-top: 4px; }

  .cd-header { text-align: center; padding: 8px 8px 4px; }
  .cd-header h1 {
    margin: 0;
    font-size: clamp(1.4rem, 3vw, 2.1rem);
    letter-spacing: 0.5px;
    background: linear-gradient(90deg, #5ad1c8, #f6a94b);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  .cd-header p { margin: 6px 0 0; color: #9aa6c4; font-size: 0.95rem; }
  .cd-panel-title {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
  }
  .cd-panel-title h2 { margin: 0; font-size: 1.05rem; color: #e8ecf7; }
  .cd-pill {
    font-size: 0.85rem; padding: 4px 10px; border-radius: 999px;
    background: #1c2542; border: 1px solid #263156; color: #9aa6c4;
  }
  .cd-pill-accent { color: #08201e; background: #5ad1c8; border-color: #5ad1c8; font-weight: 600; }
  .cd-periodic {
    display: grid;
    grid-template-columns: repeat(18, minmax(0, 1fr));
    grid-auto-rows: 1fr;
    gap: 3px;
  }
  .cd-element {
    position: relative;
    aspect-ratio: 1 / 1;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 5px;
    background: var(--cat, #ced4da);
    color: #0b1020;
    text-decoration: none;
    padding: 2px;
    font-weight: 600;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-width: 0;
    outline: 2px solid transparent;
    transition: transform 0.08s ease, box-shadow 0.08s ease;
  }
  .cd-element:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 2; }
  .cd-element.selected { outline-color: #fff; box-shadow: 0 0 0 2px #f6a94b; z-index: 3; }
  .cd-element .num { position: absolute; top: 2px; left: 4px; font-size: 0.58rem; opacity: 0.75; }
  .cd-element .sym { font-size: clamp(0.72rem, 1.25vw, 1.05rem); line-height: 1; }
  .cat-nonmetals { --cat: #7ee787; }
  .cat-noble-gases { --cat: #a5d8ff; }
  .cat-alkali-metals { --cat: #ffa8a8; }
  .cat-alkaline-earth-metals { --cat: #ffd8a8; }
  .cat-metalloids { --cat: #b2f2bb; }
  .cat-halogens { --cat: #99e9f2; }
  .cat-post-transition-metals { --cat: #bac8ff; }
  .cat-transition-metals { --cat: #ffec99; }
  .cat-lanthanides { --cat: #eebefa; }
  .cat-actinides { --cat: #fcc2d7; }
  .cat-unknown { --cat: #ced4da; }
  .cd-legend {
    list-style: none; display: flex; flex-wrap: wrap; gap: 6px 12px;
    padding: 12px 0 0; margin: 0; font-size: 0.72rem; color: #9aa6c4;
  }
  .cd-legend li { display: flex; align-items: center; gap: 5px; }
  .cd-legend .swatch { width: 12px; height: 12px; border-radius: 3px; background: var(--cat); }
  .cd-eq-list { display: flex; flex-direction: column; gap: 8px; }
  .cd-eq {
    display: block; text-align: left; text-decoration: none;
    border: 1px solid #263156; background: #1c2542; color: #e8ecf7;
    border-radius: 10px; padding: 10px 12px;
  }
  .cd-eq:hover { border-color: #5ad1c8; }
  .cd-eq.active { border-color: #5ad1c8; background: #1f3a44; box-shadow: inset 0 0 0 1px #5ad1c8; }
  .cd-eq .eq-name { font-weight: 700; }
  .cd-eq .eq-full { display: block; font-size: 0.72rem; color: #9aa6c4; margin-top: 2px; }
  .cd-eq .eq-probe {
    float: right; font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 0.5px; color: #5ad1c8;
  }
  .cd-energy-head { display: flex; align-items: center; justify-content: space-between; margin: 16px 0 8px; }
  .cd-energy-head h3 { margin: 0; font-size: 1rem; color: #e8ecf7; }
  .cd-energy-scale { display: flex; justify-content: space-between; font-size: 0.72rem; color: #9aa6c4; }
  .cd-desc { font-size: 0.8rem; color: #9aa6c4; margin: 10px 0 0; }
  .cd-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .cd-metric {
    background: #1c2542; border: 1px solid #263156; border-radius: 10px; padding: 10px 12px;
  }
  .cd-metric-label { display: block; font-size: 0.72rem; color: #9aa6c4; }
  .cd-metric-value { display: block; font-size: 1.25rem; font-weight: 700; margin-top: 3px; color: #5ad1c8; }
  .cd-viz { margin: 14px 0 0; }
  .cd-viz svg {
    width: 100%; height: auto; background: #0a0f1f;
    border: 1px solid #263156; border-radius: 10px; display: block;
  }
  .cd-viz figcaption { font-size: 0.75rem; color: #9aa6c4; margin-top: 8px; text-align: center; }
</style>
"""


def _href(symbol: str, equipment: str) -> str:
    return f"?el={html.escape(symbol, quote=True)}&eq={html.escape(equipment, quote=True)}"


def header_html() -> str:
    return (
        '<header class="cd-header">'
        "<h1>chem-depth-info</h1>"
        "<p>분석 장비별 원소 침투 <strong>깊이·폭</strong> 시뮬레이터</p>"
        "</header>"
    )


def periodic_table_html(elements: Iterable[dict], selected_symbol: str, equipment_key: str) -> str:
    cells = []
    seen: list[str] = []
    for el in elements:
        if el["category"] not in seen:
            seen.append(el["category"])
        selected = " selected" if el["symbol"] == selected_symbol else ""
        title = html.escape(f"{el['name']} (Z={el['number']}, ρ={el['density']} g/cm³)")
        cells.append(
            f'<a class="cd-element cat-{html.escape(el["category"])}{selected}" '
            f'style="grid-row:{int(el["row"])};grid-column:{int(el["col"])}" '
            f'href="{_href(el["symbol"], equipment_key)}" title="{title}">'
            f'<span class="num">{int(el["number"])}</span>'
            f'<span class="sym">{html.escape(el["symbol"])}</span></a>'
        )
    legend = "".join(
        f'<li><span class="swatch cat-{html.escape(cat)}"></span>'
        f'{html.escape(CATEGORY_LABELS.get(cat, cat))}</li>'
        for cat in seen
    )
    selected = next((e for e in elements if e["symbol"] == selected_symbol), None)
    pill = "—"
    if selected:
        pill = html.escape(f"{selected['symbol']} · {selected['name']}")
    return (
        '<div class="cd-panel-title"><h2>1 · 원소 선택</h2>'
        f'<span class="cd-pill">{pill}</span></div>'
        f'<div class="cd-periodic" role="grid">{"".join(cells)}</div>'
        f'<ul class="cd-legend">{legend}</ul>'
    )


def equipment_html(equipment: Iterable[dict], selected_key: str, symbol: str) -> str:
    cards = []
    for eq in equipment:
        active = " active" if eq["key"] == selected_key else ""
        cards.append(
            f'<a class="cd-eq{active}" href="{_href(symbol, eq["key"])}">'
            f'<span class="eq-probe">{html.escape(eq["probe"])}</span>'
            f'<span class="eq-name">{html.escape(eq["name"])}</span>'
            f'<span class="eq-full">{html.escape(eq["full_name"])}</span></a>'
        )
    return (
        '<div class="cd-panel-title"><h2>2 · 분석 장비</h2></div>'
        f'<div class="cd-eq-list">{"".join(cards)}</div>'
    )


def energy_head_html(energy_keV: float) -> str:
    return (
        '<div class="cd-energy-head"><h3>3 · 빔 에너지</h3>'
        f'<span class="cd-pill cd-pill-accent">{energy_keV:g} keV</span></div>'
    )


def results_html(result: dict, symbol: str) -> str:
    crater = ""
    if result["sputtering"]:
        crater = (
            '<div class="cd-metric"><span class="cd-metric-label">스퍼터 크레이터 깊이</span>'
            f'<span class="cd-metric-value">{html.escape(format_length(result["crater_depth_um"]))}</span></div>'
        )
    caption = (
        f'{html.escape(symbol)} · {html.escape(result["equipment_name"])} @ {result["energy_keV"]} keV — '
        f'깊이 {html.escape(format_length(result["depth_um"]))}, '
        f'폭 {html.escape(format_length(result["width_um"]))} (로그 스케일 시각화)'
    )
    return (
        '<div class="cd-panel-title"><h2>결과</h2></div>'
        '<div class="cd-metrics">'
        '<div class="cd-metric"><span class="cd-metric-label">침투 깊이</span>'
        f'<span class="cd-metric-value">{html.escape(format_length(result["depth_um"]))}</span></div>'
        '<div class="cd-metric"><span class="cd-metric-label">분석 폭</span>'
        f'<span class="cd-metric-value">{html.escape(format_length(result["width_um"]))}</span></div>'
        '<div class="cd-metric"><span class="cd-metric-label">종횡비 (깊이/폭)</span>'
        f'<span class="cd-metric-value">{result["aspect_ratio"]:.3f}</span></div>'
        f"{crater}</div>"
        f'<figure class="cd-viz">{cross_section_svg(result)}'
        f"<figcaption>{caption}</figcaption></figure>"
    )


def format_length(um: float) -> str:
    nm = um * 1000.0
    if nm < 1000:
        return f"{nm:.2f} nm" if nm < 10 else f"{nm:.1f} nm"
    if um < 1000:
        return f"{um:.2f} µm" if um < 10 else f"{um:.1f} µm"
    return f"{um / 1000.0:.2f} mm"


def log_scale(um: float) -> float:
    lo, hi = -4.0, 4.0
    v = math.log10(max(um, 1e-4))
    return min(1.0, max(0.0, (v - lo) / (hi - lo)))


def cross_section_svg(result: dict) -> str:
    width, height = 640, 360
    margin_x, surface_y = 40, 60
    usable_w = width - margin_x * 2
    usable_h = height - surface_y - 30
    cx = margin_x + usable_w / 2
    half_w = max(6.0, log_scale(result["width_um"]) * usable_w / 2)
    depth_px = max(6.0, log_scale(result["depth_um"]) * usable_h)
    bottom = surface_y + depth_px

    crater = ""
    if result["sputtering"] and result["crater_depth_um"] > result["depth_um"]:
        crater_px = min(usable_h, max(depth_px, log_scale(result["crater_depth_um"]) * usable_h))
        crater = (
            f'<polyline fill="none" stroke="#5ad1c8" stroke-dasharray="5 4" '
            f'points="{cx - half_w},{surface_y} {cx - half_w * 0.6},{surface_y + crater_px} '
            f'{cx + half_w * 0.6},{surface_y + crater_px} {cx + half_w},{surface_y}"/>'
            f'<text x="{margin_x + 4}" y="{surface_y + crater_px + 14}" fill="#5ad1c8" font-size="12">'
            f'크레이터 {format_length(result["crater_depth_um"])}</text>'
        )

    return f"""
<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="단면 시각화">
  <rect x="{margin_x}" y="{surface_y}" width="{usable_w}" height="{usable_h}" fill="#111a33" stroke="#2b3a66"/>
  <line x1="{margin_x}" y1="{surface_y}" x2="{width - margin_x}" y2="{surface_y}" stroke="#5ad1c8" stroke-width="2"/>
  <text x="{margin_x}" y="{surface_y - 8}" fill="#9aa6c4" font-size="12">표면 (surface)</text>
  <path d="M {cx - half_w} {surface_y}
           C {cx - half_w} {surface_y + depth_px * 0.7}, {cx - half_w * 0.4} {bottom}, {cx} {bottom}
           C {cx + half_w * 0.4} {bottom}, {cx + half_w} {surface_y + depth_px * 0.7}, {cx + half_w} {surface_y} Z"
        fill="rgba(246,169,75,0.55)" stroke="#f6a94b"/>
  <line x1="{cx - half_w}" y1="{surface_y - 2}" x2="{cx + half_w}" y2="{surface_y - 2}" stroke="#e8ecf7"/>
  <text x="{cx + half_w + 4}" y="{surface_y + 4}" fill="#e8ecf7" font-size="12">폭 {format_length(result["width_um"])}</text>
  <line x1="{cx}" y1="{surface_y}" x2="{cx}" y2="{bottom}" stroke="#e8ecf7"/>
  <text x="{cx + 6}" y="{bottom + 14}" fill="#e8ecf7" font-size="12">깊이 {format_length(result["depth_um"])}</text>
  {crater}
</svg>
"""
