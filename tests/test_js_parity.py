"""Compare the JavaScript Pages simulation against the Python model."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from app.simulation import EQUIPMENT, simulate

REPO = Path(__file__).resolve().parents[1]
JS = REPO / "docs" / "js" / "simulation.js"

FE = {"symbol": "Fe", "name": "Iron", "number": 26, "density": 7.87, "atomic_mass": 55.845}
AU = {"symbol": "Au", "name": "Gold", "number": 79, "density": 19.3, "atomic_mass": 196.97}
SI = {"symbol": "Si", "name": "Silicon", "number": 14, "density": 2.33, "atomic_mass": 28.085}

CASES = [
    (FE, "sims", None, None),
    (FE, "gdoes", 15, None),
    (FE, "xps", None, None),
    (FE, "aes", 19.96, None),
    (FE, "epma", 5, None),
    (FE, "eds", 15, None),
    (AU, "epma", 30, None),
    (SI, "sims", 0.5, None),
    (SI, "xps", 0.2, None),
    (FE, "gdms", 1.5, 500),
    (FE, "ldims", 0.12, 20),
    (FE, "libs", 50, 50),
    (SI, "laicpms", 1.5, 100),
    (AU, "libs", 200, 2000),
]


def _js_simulate(element: dict, equipment: str, energy, shots=None) -> dict:
    payload = json.dumps({
        "element": element,
        "equipment": equipment,
        "energy": energy,
        "shots": shots,
    })
    script = f"""
const {{ simulate }} = require({json.dumps(str(JS))});
const input = {payload};
const energy = input.energy === null ? undefined : input.energy;
const shots = input.shots === null ? undefined : input.shots;
process.stdout.write(JSON.stringify(simulate(input.element, input.equipment, energy, shots)));
"""
    proc = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


@pytest.mark.parametrize("element,equipment,energy,shots", CASES)
def test_js_matches_python(element, equipment, energy, shots):
    expected = simulate(element, equipment, energy, shots)
    actual = _js_simulate(element, equipment, energy, shots)
    for key in expected:
        if isinstance(expected[key], float):
            assert actual[key] == pytest.approx(expected[key], rel=1e-9, abs=1e-9), key
        else:
            assert actual[key] == expected[key]


def test_js_covers_every_instrument():
    assert set(EQUIPMENT) == {eq["key"] for eq in json.loads(
        subprocess.run(
            ["node", "-e", f"const {{ EQUIPMENT }} = require({json.dumps(str(JS))}); process.stdout.write(JSON.stringify(EQUIPMENT));"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )}
