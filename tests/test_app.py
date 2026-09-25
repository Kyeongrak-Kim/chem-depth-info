"""Tests for the chem-depth-info app and simulation model."""

import json
import os

import pytest

from app import create_app
from app.display import cross_section_svg, format_length
from app.simulation import EQUIPMENT, simulate

FE = {"symbol": "Fe", "name": "Iron", "number": 26, "density": 7.87, "atomic_mass": 55.845}
AU = {"symbol": "Au", "name": "Gold", "number": 79, "density": 19.3, "atomic_mass": 196.97}


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_dataset_has_118_elements():
    path = os.path.join(os.path.dirname(__file__), "..", "app", "static", "data", "elements.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data) == 118
    assert {"number", "symbol", "name", "density", "row", "col"} <= set(data[0])


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["elements"] == 118


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"chem-depth-info" in resp.data


@pytest.mark.parametrize("key", list(EQUIPMENT))
def test_simulate_all_equipment(key):
    result = simulate(FE, key)
    assert result["depth_nm"] > 0
    assert result["width_um"] > 0
    assert result["equipment"] == key


def test_denser_element_penetrates_less():
    for key in EQUIPMENT:
        fe = simulate(FE, key)["depth_nm"]
        au = simulate(AU, key)["depth_nm"]
        assert au < fe, f"expected Au shallower than Fe for {key}"


def test_energy_clamped_to_range():
    eq = EQUIPMENT["sims"]
    low = simulate(FE, "sims", eq.min_energy - 100)
    high = simulate(FE, "sims", eq.max_energy + 100)
    assert low["energy_keV"] == eq.min_energy
    assert high["energy_keV"] == eq.max_energy


def test_higher_energy_penetrates_deeper():
    lo = simulate(FE, "epma", 5)["depth_nm"]
    hi = simulate(FE, "epma", 30)["depth_nm"]
    assert hi > lo


def test_api_simulate_ok(client):
    resp = client.post("/api/simulate", json={"symbol": "Fe", "equipment": "xps"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["element"]["symbol"] == "Fe"
    assert body["probe"] == "photon"


def test_api_simulate_bad_element(client):
    resp = client.post("/api/simulate", json={"symbol": "Zz", "equipment": "xps"})
    assert resp.status_code == 400


def test_api_simulate_bad_equipment(client):
    resp = client.post("/api/simulate", json={"symbol": "Fe", "equipment": "nope"})
    assert resp.status_code == 400


def test_format_length_units():
    assert format_length(0.00628).endswith("nm")
    assert "µm" in format_length(30.0) or "μm" in format_length(30.0)
    assert format_length(2500.0).endswith("mm")


def test_cross_section_svg_contains_labels():
    svg = cross_section_svg(simulate(FE, "sims", 5))
    assert "<svg" in svg
    assert "깊이" in svg
    assert "폭" in svg
