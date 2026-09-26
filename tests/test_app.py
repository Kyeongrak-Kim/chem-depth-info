"""Tests for the chem-depth-info app and simulation model."""

import json
import os

import pytest

from app import create_app
from app.display import (
    cross_section_svg,
    equipment_html,
    format_length,
    periodic_table_html,
)
from app.simulation import EQUIPMENT, equipment_catalog, simulate

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


def test_epma_svg_is_a_pear_and_laser_width_is_the_beam():
    pear = cross_section_svg(simulate(SI, "epma"))
    assert "volume-pear" in pear
    assert "배 깊이" in pear
    assert "배 폭" in pear
    for key in ("ldims", "libs", "laicpms"):
        result = simulate(SI, key)
        assert result["volume_shape"] == "beam"
        assert result["width_um"] == pytest.approx(EQUIPMENT[key].beam_diameter_um)
    beam = cross_section_svg(simulate(SI, "libs"))
    assert "volume-beam" in beam
    assert simulate(SI, "eds")["volume_shape"] == "pear"
    assert simulate(SI, "epma")["volume_shape"] == "pear"


def test_periodic_table_html_marks_selection():
    from app import load_elements

    html = periodic_table_html(load_elements(), "Fe", "sims")
    assert html.count('class="cd-element') == 118
    assert "selected" in html
    assert "?el=Fe&eq=sims" in html
    assert "비금속" in html


def test_equipment_html_marks_active():
    html = equipment_html(equipment_catalog(), "xps", "Si")
    assert "cd-eq active" in html
    assert "?el=Si&eq=xps" in html
    assert "EDS" in html
    assert "EPMA (WDS)" in html
    assert "LDI-MS" in html
    assert "GD-MS" in html
    assert "LIBS" in html
    assert "LA-ICP-MS" in html


def test_epma_is_wds_and_eds_is_separate():
    assert EQUIPMENT["epma"].name == "EPMA (WDS)"
    assert EQUIPMENT["eds"].name == "EDS"
    assert EQUIPMENT["eds"].probe == "electron"
    eds = simulate(FE, "eds", 15)
    wds = simulate(FE, "epma", 15)
    assert eds["width_um"] > wds["width_um"]


SI = {"symbol": "Si", "name": "Silicon", "number": 14, "density": 2.33, "atomic_mass": 28.085}


def test_routine_spot_widths_match_typical_practice():
    """Analysis width should look like a routine spot, not a fat pear + huge raster."""
    assert simulate(SI, "epma")["width_um"] < 4.0
    assert simulate(SI, "eds")["width_um"] < 5.0
    assert simulate(SI, "eds")["width_um"] > simulate(SI, "epma")["width_um"]
    assert simulate(SI, "sims")["width_um"] < 15.0
    assert simulate(SI, "xps")["width_um"] < 80.0
    assert simulate(SI, "aes")["width_um"] < 0.08
    assert simulate(SI, "libs")["width_um"] < 70.0
    assert simulate(SI, "laicpms")["width_um"] < 30.0
    assert simulate(SI, "ldims")["width_um"] < 50.0
    # Glow discharge really is millimetre-scale.
    assert simulate(SI, "gdoes")["width_um"] > 1000.0


def test_aes_uses_escape_depth_not_kanaya_range():
    aes = simulate(FE, "aes")
    assert aes["depth_nm"] < 20.0


@pytest.mark.parametrize("key", ["gdms", "ldims", "libs", "laicpms"])
def test_more_shots_go_deeper(key):
    eq = EQUIPMENT[key]
    lo = simulate(FE, key, eq.default_energy, eq.min_shots)
    hi = simulate(FE, key, eq.default_energy, eq.max_shots)
    assert hi["depth_nm"] > lo["depth_nm"]
    assert hi["shots"] == eq.max_shots
    assert lo["uses_shots"] is True


def test_shots_clamped_to_range():
    eq = EQUIPMENT["libs"]
    low = simulate(FE, "libs", eq.default_energy, eq.min_shots - 100)
    high = simulate(FE, "libs", eq.default_energy, eq.max_shots + 100)
    assert low["shots"] == eq.min_shots
    assert high["shots"] == eq.max_shots


def test_non_shot_instrument_ignores_shots():
    result = simulate(FE, "xps", None, 999)
    assert result["uses_shots"] is False
    assert result["shots"] == 1


def test_api_simulate_with_shots(client):
    resp = client.post(
        "/api/simulate",
        json={"symbol": "Fe", "equipment": "ldims", "energy": 0.2, "shots": 40},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["equipment"] == "ldims"
    assert body["shots"] == 40
    assert body["energy_unit"] == "mJ"
    assert body["probe"] == "laser"


def test_api_simulate_bad_shots(client):
    resp = client.post(
        "/api/simulate",
        json={"symbol": "Fe", "equipment": "libs", "shots": "nope"},
    )
    assert resp.status_code == 400
