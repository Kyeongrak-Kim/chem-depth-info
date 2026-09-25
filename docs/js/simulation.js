"use strict";

/**
 * Browser/Node port of app/simulation.py.
 * Depths are nanometres; lateral widths are micrometres.
 */
const ION_RANGE_K = 20.0;
const PHOTON_K = 6.0;

const EQUIPMENT = [
  {
    key: "sims",
    name: "SIMS",
    full_name: "Secondary Ion Mass Spectrometry",
    probe: "ion",
    description:
      "Primary ion beam sputters the surface; secondary ions are mass analysed. Excellent depth resolution, trace sensitivity.",
    default_energy: 5.0,
    min_energy: 0.5,
    max_energy: 25.0,
    beam_diameter_um: 30.0,
    straggle_factor: 0.5,
    depth_scale: 1.0,
    sputtering: true,
  },
  {
    key: "gdoes",
    name: "GD-OES",
    full_name: "Glow Discharge Optical Emission Spectroscopy",
    probe: "ion",
    description:
      "Plasma sputters a large crater quickly; emitted light is measured. Fast bulk / thick-coating depth profiling.",
    default_energy: 15.0,
    min_energy: 5.0,
    max_energy: 40.0,
    beam_diameter_um: 2500.0,
    straggle_factor: 0.1,
    depth_scale: 9.0,
    sputtering: true,
  },
  {
    key: "xps",
    name: "XPS",
    full_name: "X-ray Photoelectron Spectroscopy",
    probe: "photon",
    description:
      "Soft X-rays eject photoelectrons; only electrons from the top few nanometres escape. Surface-sensitive chemical states.",
    default_energy: 1.4,
    min_energy: 0.2,
    max_energy: 1.5,
    beam_diameter_um: 400.0,
    straggle_factor: 0.05,
    depth_scale: 1.0,
    sputtering: false,
  },
  {
    key: "aes",
    name: "AES",
    full_name: "Auger Electron Spectroscopy",
    probe: "electron",
    description:
      "A finely focused electron beam generates Auger electrons. Nanoscale lateral resolution, very shallow escape depth.",
    default_energy: 5.0,
    min_energy: 1.0,
    max_energy: 25.0,
    beam_diameter_um: 0.05,
    straggle_factor: 0.7,
    depth_scale: 1.0,
    sputtering: false,
  },
  {
    key: "epma",
    name: "EPMA",
    full_name: "Electron Probe Micro-Analysis",
    probe: "electron",
    description:
      "A focused electron beam excites characteristic X-rays from a micron-scale interaction volume. Quantitative microanalysis.",
    default_energy: 15.0,
    min_energy: 5.0,
    max_energy: 30.0,
    beam_diameter_um: 1.0,
    straggle_factor: 0.8,
    depth_scale: 1.0,
    sputtering: false,
  },
];

function equipmentByKey(key) {
  return EQUIPMENT.find((eq) => eq.key === key);
}

function equipmentCatalog() {
  return EQUIPMENT.map((eq) => ({ ...eq }));
}

function electronDepthNm(energyKeV, mass, number, density) {
  const rangeUm = (0.0276 * mass * energyKeV ** 1.67) / (number ** 0.889 * density);
  return rangeUm * 1000.0;
}

function ionDepthNm(energyKeV, number, density) {
  return ION_RANGE_K * energyKeV / (density ** 0.75 * number ** (1.0 / 3.0));
}

function photonDepthNm(energyKeV, density) {
  const imfp = PHOTON_K * energyKeV ** 0.5 / density ** 0.5;
  return 3.0 * imfp;
}

function roundTo(value, digits) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function simulate(element, equipmentKey, energyKeV) {
  const eq = equipmentByKey(equipmentKey);
  if (!eq) {
    throw new Error(`Unknown equipment: ${JSON.stringify(equipmentKey)}`);
  }

  let energy = energyKeV == null || energyKeV === "" ? eq.default_energy : Number(energyKeV);
  if (!Number.isFinite(energy)) {
    throw new Error("energy must be a number");
  }
  energy = Math.max(eq.min_energy, Math.min(eq.max_energy, energy));

  const mass = Number(element.atomic_mass) || 1.0;
  const number = Number(element.number) || 1;
  const density = Number(element.density) || 1.0;

  let depthNm;
  if (eq.probe === "electron") {
    depthNm = electronDepthNm(energy, mass, number, density);
  } else if (eq.probe === "ion") {
    depthNm = ionDepthNm(energy, number, density);
  } else {
    depthNm = photonDepthNm(energy, density);
  }
  depthNm *= eq.depth_scale;

  const depthUm = depthNm / 1000.0;
  const widthUm = eq.beam_diameter_um + 2.0 * eq.straggle_factor * depthUm;
  const craterDepthUm = depthUm * (eq.sputtering ? 12.0 : 0.0);

  return {
    equipment: eq.key,
    equipment_name: eq.name,
    equipment_full_name: eq.full_name,
    probe: eq.probe,
    sputtering: eq.sputtering,
    energy_keV: roundTo(energy, 3),
    depth_nm: roundTo(depthNm, 3),
    depth_um: roundTo(depthUm, 5),
    width_um: roundTo(widthUm, 3),
    crater_depth_um: roundTo(craterDepthUm, 3),
    aspect_ratio: widthUm ? roundTo(depthUm / widthUm, 4) : 0.0,
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { EQUIPMENT, equipmentCatalog, simulate };
}
