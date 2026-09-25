"""Shared formatting and SVG helpers for Streamlit (and tests)."""

from __future__ import annotations

import math


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
