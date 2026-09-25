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
    "poor-metals": "전이후 금속",
    "transition-metals": "전이 금속",
    "lanthanides": "란타넘족",
    "actinides": "악티늄족",
    "unknown": "기타",
}

PROBE_LABELS = {
    "electron": "전자",
    "ion": "이온",
    "photon": "광자",
    "laser": "레이저",
}

STREAMLIT_CSS = """
<style>
  html { font-size: clamp(13px, 1.45vw, 16px); }
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background:
      radial-gradient(900px 480px at 12% -8%, #24315a 0%, transparent 58%),
      radial-gradient(720px 420px at 92% 8%, #1d3a3a 0%, transparent 50%),
      linear-gradient(180deg, #0d1428 0%, #080d1c 40%) !important;
    color: #eef2fb !important;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans KR", sans-serif !important;
  }
  [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], #MainMenu, footer, .stDeployButton,
  [data-testid="stAppDeployButton"] { display: none !important; }
  .stMainBlockContainer, .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1520px !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    background: rgba(18, 26, 48, 0.86);
    border: 1px solid #2a3760;
    border-radius: 16px;
    padding: 16px 14px 18px;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.38);
  }
  .cd-panel {
    background: rgba(18, 26, 48, 0.86);
    border: 1px solid #2a3760;
    border-radius: 16px;
    padding: clamp(12px, 1.6vw, 18px);
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.38);
    margin: 10px 0 16px;
  }
  [data-testid="stSlider"] label { color: #9aa6c4 !important; font-size: clamp(0.78rem, 1.3vw, 0.92rem) !important; }
  [data-testid="stSlider"] div[data-baseweb="slider"] { padding-top: 4px; }

  .cd-header { text-align: center; padding: 6px 8px 2px; }
  .cd-header h1 {
    margin: 0;
    font-size: clamp(1.35rem, 3.4vw, 2.25rem);
    letter-spacing: 0.4px;
    background: linear-gradient(90deg, #5ad1c8, #8ee4de 42%, #f6a94b);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  .cd-header p { margin: 8px 0 0; color: #9aa6c4; font-size: clamp(0.82rem, 1.6vw, 1rem); }
  .cd-panel-title {
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    margin-bottom: 12px;
  }
  .cd-panel-title h2 { margin: 0; font-size: clamp(0.95rem, 1.6vw, 1.12rem); color: #eef2fb; }
  .cd-pill {
    font-size: clamp(0.72rem, 1.2vw, 0.85rem); padding: 4px 10px; border-radius: 999px;
    background: #1a2340; border: 1px solid #2a3760; color: #9aa6c4; white-space: nowrap;
  }
  .cd-pill-accent { color: #08201e; background: #5ad1c8; border-color: #5ad1c8; font-weight: 700; }
  .cd-periodic {
    display: grid;
    grid-template-columns: repeat(18, minmax(0, 1fr));
    grid-auto-rows: 1fr;
    gap: clamp(2px, 0.28vw, 4px);
  }

  /* Streamlit restyles markdown <a> to theme-blue. Force ink on element tiles. */
  .stApp a.cd-element,
  .stApp a.cd-element:link,
  .stApp a.cd-element:visited,
  .stApp a.cd-element:hover,
  .stApp a.cd-element:active,
  [data-testid="stMarkdownContainer"] a.cd-element,
  [data-testid="stMarkdownContainer"] a.cd-element:link,
  [data-testid="stMarkdownContainer"] a.cd-element:visited,
  [data-testid="stMarkdownContainer"] a.cd-element:hover,
  [data-testid="stMarkdownContainer"] a.cd-element:active {
    color: #0b1020 !important;
    text-decoration: none !important;
  }
  .stApp a.cd-element .num,
  .stApp a.cd-element .sym,
  [data-testid="stMarkdownContainer"] a.cd-element .num,
  [data-testid="stMarkdownContainer"] a.cd-element .sym {
    color: #0b1020 !important;
  }
  .stApp a.cd-eq,
  .stApp a.cd-eq:link,
  .stApp a.cd-eq:visited,
  .stApp a.cd-eq:hover,
  [data-testid="stMarkdownContainer"] a.cd-eq,
  [data-testid="stMarkdownContainer"] a.cd-eq:link,
  [data-testid="stMarkdownContainer"] a.cd-eq:visited {
    color: #eef2fb !important;
    text-decoration: none !important;
  }

  .cd-element {
    position: relative;
    aspect-ratio: 1 / 1;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.22), transparent 42%),
      var(--cat, #ced4da);
    color: #0b1020 !important;
    text-decoration: none !important;
    padding: 2px;
    font-weight: 700;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-width: 0;
    outline: 2px solid transparent;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
  }
  .cd-element:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,0.35); z-index: 2; }
  .cd-element.selected { outline-color: #fff; box-shadow: 0 0 0 2px #f6a94b; z-index: 3; }
  .cd-element .num { position: absolute; top: 2px; left: 4px; font-size: clamp(0.38rem, 0.72vw, 0.62rem); opacity: 0.72; color: #0b1020 !important; }
  .cd-element .sym { font-size: clamp(0.52rem, 1.25vw, 1.05rem); line-height: 1; color: #0b1020 !important; }
  .cat-nonmetals { --cat: #7ee787; }
  .cat-noble-gases { --cat: #a5d8ff; }
  .cat-alkali-metals { --cat: #ffa8a8; }
  .cat-alkaline-earth-metals { --cat: #ffd8a8; }
  .cat-metalloids { --cat: #b2f2bb; }
  .cat-halogens { --cat: #99e9f2; }
  .cat-post-transition-metals, .cat-poor-metals { --cat: #bac8ff; }
  .cat-transition-metals { --cat: #ffec99; }
  .cat-lanthanides { --cat: #eebefa; }
  .cat-actinides { --cat: #fcc2d7; }
  .cat-unknown { --cat: #ced4da; }
  .cd-legend {
    list-style: none; display: flex; flex-wrap: wrap; gap: 6px 12px;
    padding: 12px 0 0; margin: 0; font-size: clamp(0.64rem, 1.1vw, 0.74rem); color: #9aa6c4;
  }
  .cd-legend li { display: flex; align-items: center; gap: 5px; }
  .cd-legend .swatch { width: 12px; height: 12px; border-radius: 3px; background: var(--cat); }
  .cd-eq-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
  .cd-eq {
    display: block; text-align: left; text-decoration: none !important;
    border: 1px solid #2a3760;
    background: linear-gradient(180deg, #202a4c, #1a2340);
    color: #eef2fb !important;
    border-radius: 12px; padding: 9px 10px;
  }
  .cd-eq:hover { border-color: #5ad1c8; }
  .cd-eq.active {
    border-color: #5ad1c8; background: linear-gradient(180deg, #21464a, #1b3540);
    box-shadow: inset 0 0 0 1px #5ad1c8;
  }
  .cd-eq .eq-name { font-weight: 750; font-size: clamp(0.78rem, 1.2vw, 0.92rem); color: #eef2fb !important; }
  .cd-eq .eq-full { display: block; font-size: clamp(0.62rem, 1vw, 0.72rem); color: #9aa6c4 !important; margin-top: 2px; line-height: 1.3; }
  .cd-eq .eq-probe {
    float: right; font-size: 0.62rem; text-transform: uppercase;
    letter-spacing: 0.4px; color: #5ad1c8 !important;
    background: rgba(90, 209, 200, 0.16); border-radius: 999px; padding: 2px 7px;
  }
  .cd-energy-head { display: flex; align-items: center; justify-content: space-between; margin: 16px 0 8px; }
  .cd-energy-head h3 { margin: 0; font-size: clamp(0.9rem, 1.5vw, 1.02rem); color: #eef2fb; }
  .cd-energy-scale { display: flex; justify-content: space-between; font-size: clamp(0.64rem, 1.05vw, 0.74rem); color: #9aa6c4; }
  .cd-desc { font-size: clamp(0.74rem, 1.2vw, 0.84rem); color: #9aa6c4; margin: 10px 0 0; line-height: 1.45; }
  .cd-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .cd-metric {
    background: linear-gradient(180deg, #202a4c, #1a2340);
    border: 1px solid #2a3760; border-radius: 12px; padding: 11px 12px;
    box-shadow: inset 3px 0 0 #5ad1c8;
  }
  .cd-metric-label { display: block; font-size: clamp(0.64rem, 1.05vw, 0.74rem); color: #9aa6c4; }
  .cd-metric-value { display: block; font-size: clamp(1.02rem, 2vw, 1.32rem); font-weight: 750; margin-top: 3px; color: #5ad1c8; }
  .cd-viz { margin: 14px 0 0; }
  .cd-viz svg {
    width: 100%; height: auto; background: #070c1a;
    border: 1px solid #2a3760; border-radius: 12px; display: block;
  }
  .cd-viz figcaption { font-size: clamp(0.68rem, 1.1vw, 0.78rem); color: #9aa6c4; margin-top: 8px; text-align: center; line-height: 1.4; }

  @media (max-width: 720px) {
    .cd-periodic { gap: 1.5px; }
    .cd-element .num { display: none; }
    .cd-element .sym { font-size: clamp(0.42rem, 2.5vw, 0.7rem) !important; }
    .cd-eq-list { grid-template-columns: 1fr; }
    .cd-eq .eq-full { display: none; }
    .stMainBlockContainer, .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
  }
  @media (min-width: 1280px) {
    .cd-element .sym { font-size: clamp(0.82rem, 1.05vw, 1.08rem) !important; }
    .cd-element .num { font-size: 0.62rem !important; }
  }
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
            f'style="grid-row:{int(el["row"])};grid-column:{int(el["col"])};'
            f'color:#0b1020!important;text-decoration:none"'
            f' href="{_href(el["symbol"], equipment_key)}" title="{title}">'
            f'<span class="num" style="color:#0b1020!important">{int(el["number"])}</span>'
            f'<span class="sym" style="color:#0b1020!important">{html.escape(el["symbol"])}</span></a>'
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
        probe = PROBE_LABELS.get(eq["probe"], eq["probe"])
        cards.append(
            f'<a class="cd-eq{active}" href="{_href(symbol, eq["key"])}" '
            f'style="color:#eef2fb!important;text-decoration:none">'
            f'<span class="eq-probe">{html.escape(probe)}</span>'
            f'<span class="eq-name">{html.escape(eq["name"])}</span>'
            f'<span class="eq-full">{html.escape(eq["full_name"])}</span></a>'
        )
    return (
        '<div class="cd-panel-title"><h2>2 · 분석 장비</h2></div>'
        f'<div class="cd-eq-list">{"".join(cards)}</div>'
    )


def energy_head_html(energy: float, label: str = "빔 에너지", unit: str = "keV") -> str:
    return (
        f'<div class="cd-energy-head"><h3>3 · {html.escape(label)}</h3>'
        f'<span class="cd-pill cd-pill-accent">{energy:g} {html.escape(unit)}</span></div>'
    )


def shots_head_html(shots: int) -> str:
    return (
        '<div class="cd-energy-head"><h3>4 · Shot 수</h3>'
        f'<span class="cd-pill cd-pill-accent">{int(shots)}</span></div>'
    )


def results_html(result: dict, symbol: str) -> str:
    crater = ""
    if result["sputtering"]:
        crater_label = "삭마 크레이터 깊이" if result["probe"] == "laser" else "스퍼터 크레이터 깊이"
        crater = (
            f'<div class="cd-metric"><span class="cd-metric-label">{crater_label}</span>'
            f'<span class="cd-metric-value">{html.escape(format_length(result["crater_depth_um"]))}</span></div>'
        )
    shots_metric = ""
    if result.get("uses_shots"):
        shots_metric = (
            '<div class="cd-metric"><span class="cd-metric-label">Shot 수</span>'
            f'<span class="cd-metric-value">{int(result["shots"])}</span></div>'
        )
    unit = result.get("energy_unit", "keV")
    shots_bit = f' × {int(result["shots"])} shots' if result.get("uses_shots") else ""
    caption = (
        f'{html.escape(symbol)} · {html.escape(result["equipment_name"])} @ '
        f'{result["energy_keV"]:g} {html.escape(unit)}{shots_bit} — '
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
        f"{shots_metric}{crater}</div>"
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
