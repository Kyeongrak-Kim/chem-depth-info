"use strict";

/**
 * Browser/Node port of app/simulation.py.
 * Depths are nanometres; lateral widths are micrometres.
 */
const ION_RANGE_K = 20.0;
const PHOTON_K = 6.0;
const LASER_K = 1800.0;

const EQUIPMENT = [
  {
    key: "sims",
    name: "SIMS",
    full_name: "Secondary Ion Mass Spectrometry",
    probe: "ion",
    description:
      "일차 이온 빔이 표면을 스퍼터하고, 이차 이온을 질량 분석합니다. 깊이 분해능과 미량 감도가 뛰어납니다.",
    default_energy: 5.0,
    min_energy: 0.5,
    max_energy: 25.0,
    beam_diameter_um: 30.0,
    straggle_factor: 0.5,
    depth_scale: 1.0,
    sputtering: true,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "gdoes",
    name: "GD-OES",
    full_name: "Glow Discharge Optical Emission Spectroscopy",
    probe: "ion",
    description:
      "글로우 방전 플라즈마가 큰 크레이터를 빠르게 깎고 방출광을 측정합니다. 두꺼운 코팅·벌크 깊이 프로파일에 적합합니다.",
    default_energy: 15.0,
    min_energy: 5.0,
    max_energy: 40.0,
    beam_diameter_um: 2500.0,
    straggle_factor: 0.1,
    depth_scale: 9.0,
    sputtering: true,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "gdms",
    name: "GD-MS",
    full_name: "Glow Discharge Mass Spectrometry",
    probe: "ion",
    description:
      "글로우 방전으로 시료를 스퍼터한 뒤 이온을 질량 분석합니다. GD-OES와 비슷한 크레이터지만 미량 감도가 훨씬 높고, 방전 세기와 shot(스퍼터 사이클) 수로 깊이가 늘어납니다.",
    default_energy: 1.5,
    min_energy: 0.5,
    max_energy: 5.0,
    beam_diameter_um: 2000.0,
    straggle_factor: 0.12,
    depth_scale: 14.0,
    sputtering: true,
    uses_shots: true,
    default_shots: 500,
    min_shots: 10,
    max_shots: 10000,
    energy_unit: "keV",
    energy_label: "빔 세기",
  },
  {
    key: "xps",
    name: "XPS",
    full_name: "X-ray Photoelectron Spectroscopy",
    probe: "photon",
    description:
      "연질 X선으로 광전자를 방출시킵니다. 최표면 수 nm만 탈출하므로 화학 결합 상태에 민감합니다.",
    default_energy: 1.4,
    min_energy: 0.2,
    max_energy: 1.5,
    beam_diameter_um: 400.0,
    straggle_factor: 0.05,
    depth_scale: 1.0,
    sputtering: false,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "aes",
    name: "AES",
    full_name: "Auger Electron Spectroscopy",
    probe: "electron",
    description:
      "집속 전자 빔으로 오제 전자를 만듭니다. 나노급 횡방향 분해능, 매우 얕은 탈출 깊이입니다.",
    default_energy: 5.0,
    min_energy: 1.0,
    max_energy: 25.0,
    beam_diameter_um: 0.05,
    straggle_factor: 0.7,
    depth_scale: 1.0,
    sputtering: false,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "eds",
    name: "EDS",
    full_name: "Energy-Dispersive X-ray Spectroscopy",
    probe: "electron",
    description:
      "SEM/EPMA의 에너지 분산형 X선 분광입니다. WDS보다 검출이 빠르고 입체각이 크지만, 상호작용 부피가 더 넓고 정량 정밀도는 떨어집니다.",
    default_energy: 15.0,
    min_energy: 5.0,
    max_energy: 30.0,
    beam_diameter_um: 1.5,
    straggle_factor: 0.95,
    depth_scale: 1.08,
    sputtering: false,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "epma",
    name: "EPMA (WDS)",
    full_name: "Electron Probe Micro-Analysis (Wavelength-Dispersive Spectroscopy)",
    probe: "electron",
    description:
      "파장 분산형(WDS) X선 분광입니다. 집속 전자 빔이 마이크로미터급 상호작용 부피에서 특성 X선을 여기하며, 정량 미소분석의 표준입니다. EDS와 달리 분광 결정으로 파장을 고릅니다.",
    default_energy: 15.0,
    min_energy: 5.0,
    max_energy: 30.0,
    beam_diameter_um: 1.0,
    straggle_factor: 0.8,
    depth_scale: 1.0,
    sputtering: false,
    uses_shots: false,
    default_shots: 1,
    min_shots: 1,
    max_shots: 1,
    energy_unit: "keV",
    energy_label: "빔 에너지",
  },
  {
    key: "ldims",
    name: "LDI-MS",
    full_name: "Laser Desorption/Ionization Mass Spectrometry",
    probe: "laser",
    description:
      "짧은 레이저 펄스가 표면 분자·원자를 탈착·이온화합니다. 펄스 세기와 shot 수에 따라 얕은 크레이터가 깊어집니다.",
    default_energy: 0.12,
    min_energy: 0.01,
    max_energy: 5.0,
    beam_diameter_um: 80.0,
    straggle_factor: 0.25,
    depth_scale: 0.22,
    sputtering: true,
    uses_shots: true,
    default_shots: 20,
    min_shots: 1,
    max_shots: 500,
    energy_unit: "mJ",
    energy_label: "빔 세기",
  },
  {
    key: "libs",
    name: "LIBS",
    full_name: "Laser-Induced Breakdown Spectroscopy",
    probe: "laser",
    description:
      "강한 레이저로 플라즈마를 만들고 방출 스펙트럼을 봅니다. 펄스마다 시료가 삭마되며, shot이 늘면 구멍이 깊어집니다.",
    default_energy: 50.0,
    min_energy: 1.0,
    max_energy: 200.0,
    beam_diameter_um: 120.0,
    straggle_factor: 0.35,
    depth_scale: 1.6,
    sputtering: true,
    uses_shots: true,
    default_shots: 50,
    min_shots: 1,
    max_shots: 2000,
    energy_unit: "mJ",
    energy_label: "빔 세기",
  },
  {
    key: "laicpms",
    name: "LA-ICP-MS",
    full_name: "Laser Ablation Inductively Coupled Plasma Mass Spectrometry",
    probe: "laser",
    description:
      "레이저 삭마로 시료를 떼어 ICP-MS로 보냅니다. 스팟 크기와 펄스 에너지·shot 수가 크레이터 깊이·폭을 결정합니다.",
    default_energy: 1.5,
    min_energy: 0.05,
    max_energy: 15.0,
    beam_diameter_um: 40.0,
    straggle_factor: 0.2,
    depth_scale: 12.0,
    sputtering: true,
    uses_shots: true,
    default_shots: 100,
    min_shots: 1,
    max_shots: 2000,
    energy_unit: "mJ",
    energy_label: "빔 세기",
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

function laserDepthNm(energyMj, number, density) {
  return LASER_K * energyMj ** 0.7 / (density ** 0.55 * number ** 0.15);
}

function roundTo(value, digits) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function simulate(element, equipmentKey, energyKeV, shots) {
  const eq = equipmentByKey(equipmentKey);
  if (!eq) {
    throw new Error(`Unknown equipment: ${JSON.stringify(equipmentKey)}`);
  }

  let energy = energyKeV == null || energyKeV === "" ? eq.default_energy : Number(energyKeV);
  if (!Number.isFinite(energy)) {
    throw new Error("energy must be a number");
  }
  energy = Math.max(eq.min_energy, Math.min(eq.max_energy, energy));

  let shotCount = shots == null || shots === "" ? eq.default_shots : Number(shots);
  if (!Number.isFinite(shotCount)) {
    throw new Error("shots must be a number");
  }
  shotCount = Math.trunc(shotCount);
  if (eq.uses_shots) {
    shotCount = Math.max(eq.min_shots, Math.min(eq.max_shots, shotCount));
  } else {
    shotCount = 1;
  }

  const mass = Number(element.atomic_mass) || 1.0;
  const number = Number(element.number) || 1;
  const density = Number(element.density) || 1.0;

  let depthNm;
  if (eq.probe === "electron") {
    depthNm = electronDepthNm(energy, mass, number, density);
  } else if (eq.probe === "ion") {
    depthNm = ionDepthNm(energy, number, density);
  } else if (eq.probe === "laser") {
    depthNm = laserDepthNm(energy, number, density);
  } else {
    depthNm = photonDepthNm(energy, density);
  }
  depthNm *= eq.depth_scale;

  if (eq.uses_shots) {
    depthNm *= (shotCount / Math.max(eq.default_shots, 1)) ** 0.85;
  }

  const depthUm = depthNm / 1000.0;
  const widthUm = eq.beam_diameter_um + 2.0 * eq.straggle_factor * depthUm;
  let craterDepthUm = 0.0;
  if (eq.uses_shots) {
    craterDepthUm = depthUm * 1.35;
  } else if (eq.sputtering) {
    craterDepthUm = depthUm * 12.0;
  }

  return {
    equipment: eq.key,
    equipment_name: eq.name,
    equipment_full_name: eq.full_name,
    probe: eq.probe,
    sputtering: eq.sputtering,
    uses_shots: eq.uses_shots,
    shots: shotCount,
    energy_keV: roundTo(energy, 3),
    energy_unit: eq.energy_unit,
    energy_label: eq.energy_label,
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
