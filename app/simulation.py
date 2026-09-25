"""Simplified depth/width penetration model for chemical analysis equipment.

The goal of this module is not metrological accuracy but a self-consistent,
physically motivated model whose outputs vary meaningfully with the selected
element (mass, atomic number, density) and the chosen instrument / beam energy
(and, for pulsed techniques, shot count).

Four probe families are modelled:

* ``electron`` – electron-probe techniques (AES, EDS, EPMA/WDS). Penetration
  uses the Kanaya–Okayama electron range.
* ``ion`` – sputter / glow-discharge techniques (SIMS, GD-OES, GD-MS).
  Penetration uses an empirical projected-range expression.
* ``photon`` – photoelectron spectroscopy (XPS). Sampling depth is derived from
  a simplified inelastic mean free path.
* ``laser`` – pulsed optical techniques (LDI-MS, LIBS, LA-ICP-MS). Single-pulse
  ablation depth scales with pulse energy and is accumulated over shots.

All depths are returned in nanometres and lateral widths in micrometres.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal


ProbeType = Literal["electron", "ion", "photon", "laser"]


@dataclass(frozen=True)
class Equipment:
    key: str
    name: str
    full_name: str
    probe: ProbeType
    description: str
    default_energy: float
    min_energy: float
    max_energy: float
    beam_diameter_um: float
    straggle_factor: float
    depth_scale: float
    sputtering: bool
    uses_shots: bool = False
    default_shots: int = 1
    min_shots: int = 1
    max_shots: int = 1
    energy_unit: str = "keV"
    energy_label: str = "빔 에너지"


EQUIPMENT: dict[str, Equipment] = {
    e.key: e
    for e in [
        Equipment(
            key="sims",
            name="SIMS",
            full_name="Secondary Ion Mass Spectrometry",
            probe="ion",
            description=(
                "일차 이온 빔이 표면을 스퍼터하고, 이차 이온을 질량 분석합니다. "
                "깊이 분해능과 미량 감도가 뛰어납니다."
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
                "글로우 방전 플라즈마가 큰 크레이터를 빠르게 깎고 방출광을 측정합니다. "
                "두꺼운 코팅·벌크 깊이 프로파일에 적합합니다."
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
            key="gdms",
            name="GD-MS",
            full_name="Glow Discharge Mass Spectrometry",
            probe="ion",
            description=(
                "글로우 방전으로 시료를 스퍼터한 뒤 이온을 질량 분석합니다. "
                "GD-OES와 비슷한 크레이터지만 미량 감도가 훨씬 높고, "
                "방전 세기와 shot(스퍼터 사이클) 수로 깊이가 늘어납니다."
            ),
            default_energy=1.5,
            min_energy=0.5,
            max_energy=5.0,
            beam_diameter_um=2000.0,
            straggle_factor=0.12,
            depth_scale=14.0,
            sputtering=True,
            uses_shots=True,
            default_shots=500,
            min_shots=10,
            max_shots=10000,
            energy_unit="keV",
            energy_label="빔 세기",
        ),
        Equipment(
            key="xps",
            name="XPS",
            full_name="X-ray Photoelectron Spectroscopy",
            probe="photon",
            description=(
                "연질 X선으로 광전자를 방출시킵니다. 최표면 수 nm만 탈출하므로 "
                "화학 결합 상태에 민감합니다."
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
                "집속 전자 빔으로 오제 전자를 만듭니다. 나노급 횡방향 분해능, "
                "매우 얕은 탈출 깊이입니다."
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
            key="eds",
            name="EDS",
            full_name="Energy-Dispersive X-ray Spectroscopy",
            probe="electron",
            description=(
                "SEM/EPMA의 에너지 분산형 X선 분광입니다. WDS보다 검출이 빠르고 "
                "입체각이 크지만, 상호작용 부피가 더 넓고 정량 정밀도는 떨어집니다."
            ),
            default_energy=15.0,
            min_energy=5.0,
            max_energy=30.0,
            beam_diameter_um=1.5,
            straggle_factor=0.95,
            depth_scale=1.08,
            sputtering=False,
        ),
        Equipment(
            key="epma",
            name="EPMA (WDS)",
            full_name="Electron Probe Micro-Analysis (Wavelength-Dispersive Spectroscopy)",
            probe="electron",
            description=(
                "파장 분산형(WDS) X선 분광입니다. 집속 전자 빔이 마이크로미터급 "
                "상호작용 부피에서 특성 X선을 여기하며, 정량 미소분석의 표준입니다. "
                "EDS와 달리 분광 결정으로 파장을 고릅니다."
            ),
            default_energy=15.0,
            min_energy=5.0,
            max_energy=30.0,
            beam_diameter_um=1.0,
            straggle_factor=0.8,
            depth_scale=1.0,
            sputtering=False,
        ),
        Equipment(
            key="ldims",
            name="LDI-MS",
            full_name="Laser Desorption/Ionization Mass Spectrometry",
            probe="laser",
            description=(
                "짧은 레이저 펄스가 표면 분자·원자를 탈착·이온화합니다. "
                "펄스 세기와 shot 수에 따라 얕은 크레이터가 깊어집니다."
            ),
            default_energy=0.12,
            min_energy=0.01,
            max_energy=5.0,
            beam_diameter_um=80.0,
            straggle_factor=0.25,
            depth_scale=0.22,
            sputtering=True,
            uses_shots=True,
            default_shots=20,
            min_shots=1,
            max_shots=500,
            energy_unit="mJ",
            energy_label="빔 세기",
        ),
        Equipment(
            key="libs",
            name="LIBS",
            full_name="Laser-Induced Breakdown Spectroscopy",
            probe="laser",
            description=(
                "강한 레이저로 플라즈마를 만들고 방출 스펙트럼을 봅니다. "
                "펄스마다 시료가 삭마되며, shot이 늘면 구멍이 깊어집니다."
            ),
            default_energy=50.0,
            min_energy=1.0,
            max_energy=200.0,
            beam_diameter_um=120.0,
            straggle_factor=0.35,
            depth_scale=1.6,
            sputtering=True,
            uses_shots=True,
            default_shots=50,
            min_shots=1,
            max_shots=2000,
            energy_unit="mJ",
            energy_label="빔 세기",
        ),
        Equipment(
            key="laicpms",
            name="LA-ICP-MS",
            full_name="Laser Ablation Inductively Coupled Plasma Mass Spectrometry",
            probe="laser",
            description=(
                "레이저 삭마로 시료를 떼어 ICP-MS로 보냅니다. "
                "스팟 크기와 펄스 에너지·shot 수가 크레이터 깊이·폭을 결정합니다."
            ),
            default_energy=1.5,
            min_energy=0.05,
            max_energy=15.0,
            beam_diameter_um=40.0,
            straggle_factor=0.2,
            depth_scale=12.0,
            sputtering=True,
            uses_shots=True,
            default_shots=100,
            min_shots=1,
            max_shots=2000,
            energy_unit="mJ",
            energy_label="빔 세기",
        ),
    ]
}

# Empirical calibration constant for the ion projected-range expression so that,
# e.g., a 5 keV ion into silicon yields a few tens of nanometres.
_ION_RANGE_K = 20.0
# Photon sampling-depth constant (3 x inelastic mean free path).
_PHOTON_K = 6.0
# Single-pulse optical/thermal ablation scale (nm at ~1 mJ into a light target).
_LASER_K = 1800.0


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


def _laser_depth_nm(energy_mJ: float, number: int, density: float) -> float:
    """Single-pulse optical/thermal ablation depth in nanometres."""
    return _LASER_K * (energy_mJ ** 0.7) / ((density ** 0.55) * (number ** 0.15))


def simulate(
    element: dict,
    equipment_key: str,
    energy_keV: float | None = None,
    shots: int | None = None,
) -> dict:
    """Compute penetration depth and lateral width for element + equipment.

    Parameters
    ----------
    element:
        Element record with ``atomic_mass``, ``number`` and ``density`` keys.
    equipment_key:
        One of the keys in :data:`EQUIPMENT`.
    energy_keV:
        Beam / photon energy in keV, or pulse energy in mJ for laser probes.
        Defaults to the instrument default and is clamped to its range.
    shots:
        Pulse / sputter-cycle count for instruments with ``uses_shots``.
        Ignored otherwise. Defaults to the instrument default and is clamped.
    """
    if equipment_key not in EQUIPMENT:
        raise ValueError(f"Unknown equipment: {equipment_key!r}")

    eq = EQUIPMENT[equipment_key]
    energy = eq.default_energy if energy_keV is None else float(energy_keV)
    energy = max(eq.min_energy, min(eq.max_energy, energy))

    shot_count = eq.default_shots if shots is None else int(shots)
    if eq.uses_shots:
        shot_count = max(eq.min_shots, min(eq.max_shots, shot_count))
    else:
        shot_count = 1

    mass = float(element.get("atomic_mass") or 1.0)
    number = int(element.get("number") or 1)
    density = float(element.get("density") or 1.0)

    if eq.probe == "electron":
        depth_nm = _electron_depth_nm(energy, mass, number, density)
    elif eq.probe == "ion":
        depth_nm = _ion_depth_nm(energy, number, density)
    elif eq.probe == "laser":
        depth_nm = _laser_depth_nm(energy, number, density)
    else:
        depth_nm = _photon_depth_nm(energy, density)

    depth_nm *= eq.depth_scale

    # Pulsed / cycled techniques: depth at the instrument's default shot count
    # is the calibrated value; more shots grow the crater sublinearly.
    if eq.uses_shots:
        depth_nm *= (shot_count / max(eq.default_shots, 1)) ** 0.85

    depth_um = depth_nm / 1000.0
    width_um = eq.beam_diameter_um + 2.0 * eq.straggle_factor * depth_um

    if eq.uses_shots:
        crater_depth_um = depth_um * 1.35
    elif eq.sputtering:
        crater_depth_um = depth_um * 12.0
    else:
        crater_depth_um = 0.0

    return {
        "equipment": eq.key,
        "equipment_name": eq.name,
        "equipment_full_name": eq.full_name,
        "probe": eq.probe,
        "sputtering": eq.sputtering,
        "uses_shots": eq.uses_shots,
        "shots": shot_count,
        "energy_keV": round(energy, 3),
        "energy_unit": eq.energy_unit,
        "energy_label": eq.energy_label,
        "depth_nm": round(depth_nm, 3),
        "depth_um": round(depth_um, 5),
        "width_um": round(width_um, 3),
        "crater_depth_um": round(crater_depth_um, 3),
        "aspect_ratio": round(depth_um / width_um, 4) if width_um else 0.0,
    }


def equipment_catalog() -> list[dict]:
    """Return serialisable metadata for every instrument."""
    return [asdict(eq) for eq in EQUIPMENT.values()]
