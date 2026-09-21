"""Generate the static periodic-table dataset used by the web app.

Run this once with `mendeleev` installed to (re)create
`app/static/data/elements.json`. The runtime app only depends on Flask and
reads the generated JSON, so `mendeleev`/`pandas` are not runtime dependencies.

Usage:
    pip install mendeleev
    python scripts/generate_elements.py
"""

from __future__ import annotations

import json
import math
import os

from mendeleev import element as get_element

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "app", "static", "data", "elements.json")

# Grid placement for the two rare-earth rows so the front-end can lay out a
# classic periodic table. mendeleev exposes group_id as None for these, so we
# assign explicit columns (3..17) and dedicated display rows (8 and 9).
LANTHANIDES = list(range(57, 72))  # La (57) .. Lu (71)
ACTINIDES = list(range(89, 104))  # Ac (89) .. Lr (103)


def grid_position(el) -> tuple[int, int]:
    """Return (row, column) 1-indexed positions for the CSS grid."""
    z = el.atomic_number
    if z in LANTHANIDES:
        return 8, 3 + (z - 57)
    if z in ACTINIDES:
        return 9, 3 + (z - 89)
    return el.period, el.group_id


def main() -> None:
    elements = []
    for z in range(1, 119):
        el = get_element(z)
        row, col = grid_position(el)
        density = el.density  # g/cm^3 at standard conditions (may be None)
        elements.append(
            {
                "number": z,
                "symbol": el.symbol,
                "name": el.name,
                "atomic_mass": round(el.atomic_weight, 4) if el.atomic_weight else None,
                # Fall back to a light default density so the model is defined
                # for gaseous / unmeasured elements.
                "density": round(density, 4) if density else 1.0,
                "row": row,
                "col": col,
                "category": (el.series or "unknown").lower().replace(" ", "-"),
            }
        )

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(elements, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {len(elements)} elements to {os.path.relpath(OUT_PATH, HERE)}")


if __name__ == "__main__":
    main()
