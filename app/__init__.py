"""chem-depth-info Flask application factory."""

from __future__ import annotations

import json
import os
from functools import lru_cache

from flask import Flask, jsonify, render_template, request

from .simulation import EQUIPMENT, equipment_catalog, simulate

DATA_PATH = os.path.join(os.path.dirname(__file__), "static", "data", "elements.json")


@lru_cache(maxsize=1)
def load_elements() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def elements_by_symbol() -> dict[str, dict]:
    return {e["symbol"]: e for e in load_elements()}


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            elements=load_elements(),
            equipment=equipment_catalog(),
        )

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok", elements=len(load_elements()), equipment=len(EQUIPMENT))

    @app.get("/api/elements")
    def api_elements():
        return jsonify(load_elements())

    @app.get("/api/equipment")
    def api_equipment():
        return jsonify(equipment_catalog())

    @app.post("/api/simulate")
    def api_simulate():
        payload = request.get_json(silent=True) or {}
        symbol = payload.get("symbol")
        equipment_key = payload.get("equipment")
        energy = payload.get("energy")

        element = elements_by_symbol().get(symbol)
        if element is None:
            return jsonify(error=f"Unknown element symbol: {symbol!r}"), 400
        if equipment_key not in EQUIPMENT:
            return jsonify(error=f"Unknown equipment: {equipment_key!r}"), 400

        try:
            energy_val = None if energy in (None, "") else float(energy)
        except (TypeError, ValueError):
            return jsonify(error="energy must be a number"), 400

        result = simulate(element, equipment_key, energy_val)
        result["element"] = {
            "symbol": element["symbol"],
            "name": element["name"],
            "number": element["number"],
            "density": element["density"],
            "atomic_mass": element["atomic_mass"],
        }
        return jsonify(result)

    return app


app = create_app()
