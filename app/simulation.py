"""Simplified depth/width penetration model for chemical analysis equipment.

The goal of this module is not metrological accuracy but a self-consistent,
physically motivated model whose outputs vary meaningfully with the selected
element (mass, atomic number, density) and the chosen instrument / beam energy.

Three probe families are modelled:

* ``electron`` – electron-probe techniques (AES, EPMA). Penetration uses the
  well-known Kanaya-Okayama electron range.
* ``ion`` – sputter / ion-beam techniques (SIMS, GD-OES). Penetration uses an
  empirical projected-range expression.
* ``photon`` – photoelectron spectroscopy (XPS). Sampling depth is derived from
  a simplified inelastic mean free path.

All depths are returned in nanometres and lateral widths in micrometres.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal


ProbeType = Literal["electron", "ion", "photon"]


@dataclass(frozen=True)
class Equipment:
    key: str
    name: str
    full_name: str
    probe: ProbeType
    description: str
    default_energy: float  # keV
    min_energy: float  # keV
    max_energy: float  # keV
    beam_diameter_um: float  # nominal probe/beam diameter on the surface
    straggle_factor: float  # lateral spread as a fraction of penetration depth
    depth_scale: float  # per-instrument calibration multiplier
    sputtering: bool  # whether the technique erodes a crater


EQUIPMENT: dict[str, Equipment] = {
    e.key: e
    for e in [
        Equipment(
            key="sims",
            name="SIMS",
            full_name="Secondary Ion Mass Spectrometry",
            probe="ion",
            description=(
                "Primary ion beam sputters the surface; secondary ions are mass "
                "analysed. Excellent depth resolution, trace sensitivity."
            ),
            default_energy=5.0,
            min_energy=0.5,
            max_energy=25.0,
            beam_diameter_um=30.0,
            straggle_factor=0.5,
            depth_scale=1.0,
            sputtering=True,
        ),
        Equipment(
            key="gdoes",
            name="GD-OES",
            full_name="Glow Discharge Optical Emission Spectroscopy",
            probe="ion",
            description=(
                "Plasma sputters a large crater quickly; emitted light is measured. "
                "Fast bulk / thick-coating depth profiling."
            ),
            default_energy=15.0,
            min_energy=5.0,
            max_energy=40.0,
            beam_diameter_um=2500.0,
            straggle_factor=0.1,
            depth_scale=9.0,
            sputtering=True,
        ),
        Equipment(
            key="xps",
            name="XPS",
            full_name="X-ray Photoelectron Spectroscopy",
            probe="photon",
            description=(
                "Soft X-rays eject photoelectrons; only electrons from the top few "
                "nanometres escape. Surface-sensitive chemical states."
            ),
            default_energy=1.4,
            min_energy=0.2,
            max_energy=1.5,
            beam_diameter_um=400.0,
            straggle_factor=0.05,
            depth_scale=1.0,
            sputtering=False,
        ),
        Equipment(
            key="aes",
            name="AES",
            full_name="Auger Electron Spectroscopy",
            probe="electron",
            description=(
                "A finely focused electron beam generates Auger electrons. "
                "Nanoscale lateral resolution, very shallow escape depth."
            ),
            default_energy=5.0,
            min_energy=1.0,
            max_energy=25.0,
            beam_diameter_um=0.05,
            straggle_factor=0.7,
            depth_scale=1.0,
            sputtering=False,
        ),
        Equipment(
            key="epma",
            name="EPMA",
            full_name="Electron Probe Micro-Analysis",
            probe="electron",
            description=(
                "A focused electron beam excites characteristic X-rays from a "
                "micron-scale interaction volume. Quantitative microanalysis."
            ),
            default_energy=15.0,
            min_energy=5.0,
            max_energy=30.0,
            beam_diameter_um=1.0,
            straggle_factor=0.8,
            depth_scale=1.0,
            sputtering=False,
        ),
    ]
}

# Empirical calibration constant for the ion projected-range expression so that,
# e.g., a 5 keV ion into silicon yields a few tens of nanometres.
_ION_RANGE_K = 20.0
# Photon sampling-depth constant (3 x inelastic mean free path).
_PHOTON_K = 6.0


def _electron_depth_nm(energy_keV: float, mass: float, number: int, density: float) -> float:
    """Kanaya-Okayama electron range, converted to nanometres."""
    range_um = 0.0276 * mass * (energy_keV ** 1.67) / ((number ** 0.889) * density)
    return range_um * 1000.0


def _ion_depth_nm(energy_keV: float, number: int, density: float) -> float:
    """Empirical ion projected range in nanometres."""
    return _ION_RANGE_K * energy_keV / ((density ** 0.75) * (number ** (1.0 / 3.0)))


def _photon_depth_nm(energy_keV: float, density: float) -> float:
    """Photoelectron sampling depth (~3x inelastic mean free path) in nm."""
    imfp = _PHOTON_K * (energy_keV ** 0.5) / (density ** 0.5)
    return 3.0 * imfp


def simulate(element: dict, equipment_key: str, energy_keV: float | None = None) -> dict:
    """Compute penetration depth and lateral width for element + equipment.

    Parameters
    ----------
    element:
        Element record with ``atomic_mass``, ``number`` and ``density`` keys.
    equipment_key:
        One of the keys in :data:`EQUIPMENT`.
    energy_keV:
        Beam / photon energy in keV. Defaults to the instrument default and is
        clamped to the instrument's supported range.
    """
    if equipment_key not in EQUIPMENT:
        raise ValueError(f"Unknown equipment: {equipment_key!r}")

    eq = EQUIPMENT[equipment_key]
    energy = eq.default_energy if energy_keV is None else float(energy_keV)
    energy = max(eq.min_energy, min(eq.max_energy, energy))

    mass = float(element.get("atomic_mass") or 1.0)
    number = int(element.get("number") or 1)
    density = float(element.get("density") or 1.0)

    if eq.probe == "electron":
        depth_nm = _electron_depth_nm(energy, mass, number, density)
    elif eq.probe == "ion":
        depth_nm = _ion_depth_nm(energy, number, density)
    else:  # photon
        depth_nm = _photon_depth_nm(energy, density)

    depth_nm *= eq.depth_scale

    depth_um = depth_nm / 1000.0
    width_um = eq.beam_diameter_um + 2.0 * eq.straggle_factor * depth_um

    # A crude sputter-erosion estimate for techniques that dig a crater. It is
    # displayed as supplementary information for sputtering instruments only.
    crater_depth_um = depth_um * (12.0 if eq.sputtering else 0.0)

    return {
        "equipment": eq.key,
        "equipment_name": eq.name,
        "equipment_full_name": eq.full_name,
        "probe": eq.probe,
        "sputtering": eq.sputtering,
        "energy_keV": round(energy, 3),
        "depth_nm": round(depth_nm, 3),
        "depth_um": round(depth_um, 5),
        "width_um": round(width_um, 3),
        "crater_depth_um": round(crater_depth_um, 3),
        "aspect_ratio": round(depth_um / width_um, 4) if width_um else 0.0,
    }


def equipment_catalog() -> list[dict]:
    """Return serialisable metadata for every instrument."""
    return [asdict(eq) for eq in EQUIPMENT.values()]
