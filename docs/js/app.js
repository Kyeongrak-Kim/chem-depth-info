"use strict";

let ELEMENTS = [];

const state = {
  symbol: "Si",
  equipment: "sims",
  energy: null,
  shots: null,
};

const CATEGORY_LABELS = {
  "nonmetals": "비금속",
  "noble-gases": "비활성 기체",
  "alkali-metals": "알칼리 금속",
  "alkaline-earth-metals": "알칼리 토금속",
  "metalloids": "준금속",
  "halogens": "할로겐",
  "post-transition-metals": "전이후 금속",
  "poor-metals": "전이후 금속",
  "transition-metals": "전이 금속",
  "lanthanides": "란타넘족",
  "actinides": "악티늄족",
  "unknown": "기타",
};

const PROBE_LABELS = {
  electron: "전자",
  ion: "이온",
  photon: "광자",
  laser: "레이저",
};

const MODEL_NOTES = {
  electron: "깊이: Kanaya–Okayama 전자 비정, 단면은 배(pear). 입구는 빔, 최대 폭은 배의 가장 넓은 곳.",
  aes: "깊이: 오제 전자 탈출 깊이(~3λ). 폭: 집속 빔 직경(일차 전자 비정이 아님).",
  ion: "깊이: LSS형 이온 투사 범위. 폭: 래스터/양극 직경(이온 횡방향 straggle은 nm).",
  photon: "깊이: 광전자 IMFP의 약 3배(TPP형). 폭: X선 스팟 크기.",
  laser: "깊이: 펄스 에너지·shot에 따른 삭마. 폭: 집속 빔 직경.",
};

function assetUrl(relativePath) {
  return new URL(relativePath, document.baseURI).toString();
}

function buildTable() {
  const grid = document.getElementById("periodic-table");
  grid.innerHTML = "";
  for (const el of ELEMENTS) {
    const cell = document.createElement("button");
    cell.type = "button";
    cell.className = `element cat-${el.category}`;
    cell.style.gridRow = String(el.row);
    cell.style.gridColumn = String(el.col);
    cell.dataset.symbol = el.symbol;
    cell.setAttribute("role", "gridcell");
    cell.title = `${el.name} (Z=${el.number}, ρ=${el.density} g/cm³)`;
    cell.innerHTML = `<span class="num">${el.number}</span><span class="sym">${el.symbol}</span>`;
    cell.addEventListener("click", () => selectElement(el.symbol));
    grid.appendChild(cell);
  }
}

function buildLegend() {
  const legend = document.getElementById("legend");
  legend.innerHTML = "";
  const seen = new Set();
  for (const el of ELEMENTS) {
    if (seen.has(el.category)) continue;
    seen.add(el.category);
    const li = document.createElement("li");
    li.innerHTML = `<span class="swatch cat-${el.category}"></span>${CATEGORY_LABELS[el.category] || el.category}`;
    legend.appendChild(li);
  }
}

function selectElement(symbol) {
  state.symbol = symbol;
  document.querySelectorAll(".element").forEach((n) => {
    n.classList.toggle("selected", n.dataset.symbol === symbol);
  });
  const el = ELEMENTS.find((e) => e.symbol === symbol);
  document.getElementById("selected-label").textContent = `${el.symbol} · ${el.name}`;
  run();
}

function buildEquipment() {
  const list = document.getElementById("equipment-list");
  list.innerHTML = "";
  for (const eq of EQUIPMENT) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "equipment-btn";
    btn.dataset.key = eq.key;
    btn.setAttribute("role", "radio");
    btn.innerHTML =
      `<span class="eq-probe">${PROBE_LABELS[eq.probe] || eq.probe}</span>` +
      `<span class="eq-name">${eq.name}</span>` +
      `<span class="eq-full">${eq.full_name}</span>`;
    btn.addEventListener("click", () => selectEquipment(eq.key));
    list.appendChild(btn);
  }
}

function currentEquipment() {
  return EQUIPMENT.find((e) => e.key === state.equipment);
}

function applyShotsUi(eq) {
  const block = document.getElementById("shots-block");
  if (!eq.uses_shots) {
    block.hidden = true;
    state.shots = null;
    return;
  }
  block.hidden = false;
  const slider = document.getElementById("shots-slider");
  slider.min = String(eq.min_shots);
  slider.max = String(eq.max_shots);
  slider.value = String(eq.default_shots);
  state.shots = eq.default_shots;
  document.getElementById("shots-min").textContent = String(eq.min_shots);
  document.getElementById("shots-max").textContent = String(eq.max_shots);
  updateShotsReadout();
}

function selectEquipment(key) {
  state.equipment = key;
  const eq = currentEquipment();
  document.querySelectorAll(".equipment-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.key === key);
    b.setAttribute("aria-checked", b.dataset.key === key ? "true" : "false");
  });
  document.getElementById("equipment-desc").textContent = eq.description;
  document.getElementById("energy-title").textContent = `3 · ${eq.energy_label || "빔 에너지"}`;
  document.getElementById("energy-min").textContent = `${eq.min_energy} ${eq.energy_unit}`;
  document.getElementById("energy-max").textContent = `${eq.max_energy} ${eq.energy_unit}`;
  const slider = document.getElementById("energy-slider");
  const frac = (eq.default_energy - eq.min_energy) / (eq.max_energy - eq.min_energy);
  slider.value = String(frac);
  state.energy = eq.default_energy;
  updateEnergyReadout();
  applyShotsUi(eq);
  run();
}

function sliderToEnergy() {
  const eq = currentEquipment();
  const frac = parseFloat(document.getElementById("energy-slider").value);
  const e = eq.min_energy + frac * (eq.max_energy - eq.min_energy);
  return Math.round(e * 100) / 100;
}

function updateEnergyReadout() {
  const eq = currentEquipment();
  document.getElementById("energy-readout").textContent = `${state.energy} ${eq.energy_unit}`;
}

function updateShotsReadout() {
  document.getElementById("shots-readout").textContent = String(state.shots);
}

function run() {
  const el = ELEMENTS.find((e) => e.symbol === state.symbol);
  const eq = currentEquipment();
  if (!el || !eq) return;
  const data = simulate(el, state.equipment, state.energy, state.shots);
  data.element = {
    symbol: el.symbol,
    name: el.name,
    number: el.number,
    density: el.density,
    atomic_mass: el.atomic_mass,
  };
  render(data);
}

function fmtLength(um) {
  const nm = um * 1000;
  if (nm < 1000) return `${nm.toFixed(nm < 10 ? 2 : 1)} nm`;
  if (um < 1000) return `${um.toFixed(um < 10 ? 2 : 1)} µm`;
  return `${(um / 1000).toFixed(2)} mm`;
}

function render(data) {
  document.getElementById("m-depth").textContent = fmtLength(data.depth_um);
  document.getElementById("m-width").textContent = fmtLength(data.width_um);
  document.getElementById("m-aspect").textContent = data.aspect_ratio.toFixed(3);

  const shotsMetric = document.getElementById("shots-metric");
  if (data.uses_shots) {
    shotsMetric.hidden = false;
    document.getElementById("m-shots").textContent = String(data.shots);
  } else {
    shotsMetric.hidden = true;
  }

  const craterMetric = document.getElementById("crater-metric");
  if (data.sputtering) {
    craterMetric.hidden = false;
    document.getElementById("crater-label").textContent =
      data.probe === "laser" ? "삭마 크레이터 깊이" : "스퍼터 크레이터 깊이";
    document.getElementById("m-crater").textContent = fmtLength(data.crater_depth_um);
  } else {
    craterMetric.hidden = true;
  }

  const shape = data.volume_shape || "spot";
  document.getElementById("m-depth-label").textContent =
    shape === "pear" ? "배(pear) 깊이" : shape === "beam" ? "삭마 깊이" : "침투 깊이";
  document.getElementById("m-width-label").textContent =
    shape === "pear" ? "배 최대 폭" : shape === "beam" ? "빔 직경" : "분석 폭";

  const unit = data.energy_unit || "keV";
  const shotsBit = data.uses_shots ? ` × ${data.shots} shots` : "";
  document.getElementById("viz-caption").textContent =
    `${data.element.symbol} · ${data.equipment_name} @ ${data.energy_keV} ${unit}${shotsBit} — ` +
    `깊이 ${fmtLength(data.depth_um)}, 폭 ${fmtLength(data.width_um)} (로그 스케일 시각화)`;
  const noteKey = data.equipment === "aes" ? "aes" : data.probe;
  document.getElementById("model-note").textContent = MODEL_NOTES[noteKey] || "";

  drawViz(data);
}

function logScale(um) {
  const lo = -4;
  const hi = 4;
  const v = Math.log10(Math.max(um, 1e-4));
  return Math.min(1, Math.max(0, (v - lo) / (hi - lo)));
}

function drawVolume(ctx, data, cx, surfaceY, halfW, depthPx) {
  const bottom = surfaceY + depthPx;
  const shape = data.volume_shape || "spot";
  const grad = ctx.createLinearGradient(0, surfaceY, 0, bottom);
  grad.addColorStop(0, "rgba(246, 169, 75, 0.9)");
  grad.addColorStop(1, "rgba(246, 169, 75, 0.12)");
  ctx.fillStyle = grad;
  ctx.beginPath();
  if (shape === "pear") {
    const neck = halfW * 0.22;
    const belly = surfaceY + depthPx * 0.55;
    ctx.moveTo(cx - neck, surfaceY);
    ctx.bezierCurveTo(cx - neck, surfaceY + depthPx * 0.16, cx - halfW, surfaceY + depthPx * 0.30, cx - halfW, belly);
    ctx.bezierCurveTo(cx - halfW, surfaceY + depthPx * 0.82, cx - halfW * 0.42, bottom, cx, bottom);
    ctx.bezierCurveTo(cx + halfW * 0.42, bottom, cx + halfW, surfaceY + depthPx * 0.82, cx + halfW, belly);
    ctx.bezierCurveTo(cx + halfW, surfaceY + depthPx * 0.30, cx + neck, surfaceY + depthPx * 0.16, cx + neck, surfaceY);
  } else if (shape === "beam") {
    const inset = halfW * 0.9;
    ctx.moveTo(cx - halfW, surfaceY);
    ctx.lineTo(cx - inset, bottom);
    ctx.lineTo(cx + inset, bottom);
    ctx.lineTo(cx + halfW, surfaceY);
  } else {
    ctx.moveTo(cx - halfW, surfaceY);
    ctx.bezierCurveTo(cx - halfW, surfaceY + depthPx * 0.7, cx - halfW * 0.4, bottom, cx, bottom);
    ctx.bezierCurveTo(cx + halfW * 0.4, bottom, cx + halfW, surfaceY + depthPx * 0.7, cx + halfW, surfaceY);
  }
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "#f6a94b";
  ctx.lineWidth = 1.5;
  ctx.stroke();

  ctx.strokeStyle = "#e8ecf7";
  ctx.fillStyle = "#e8ecf7";
  ctx.lineWidth = 1;
  if (shape === "pear") {
    const belly = surfaceY + depthPx * 0.55;
    ctx.beginPath();
    ctx.moveTo(cx - halfW, belly);
    ctx.lineTo(cx + halfW, belly);
    ctx.stroke();
    ctx.fillText(`배 폭 ${fmtLength(data.width_um)}`, cx + halfW + 4, belly + 4);
  } else {
    ctx.beginPath();
    ctx.moveTo(cx - halfW, surfaceY - 2);
    ctx.lineTo(cx + halfW, surfaceY - 2);
    ctx.stroke();
    const widthLabel = shape === "beam" ? `빔 ${fmtLength(data.width_um)}` : `폭 ${fmtLength(data.width_um)}`;
    ctx.fillText(widthLabel, cx + halfW + 4, surfaceY + 4);
  }
  ctx.beginPath();
  ctx.moveTo(cx, surfaceY);
  ctx.lineTo(cx, bottom);
  ctx.stroke();
  const depthLabel = shape === "pear" ? `배 깊이 ${fmtLength(data.depth_um)}` : `깊이 ${fmtLength(data.depth_um)}`;
  ctx.fillText(depthLabel, cx + 6, bottom + 14);
}

function drawViz(data) {
  const canvas = document.getElementById("viz-canvas");
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  const marginX = 40;
  const surfaceY = 60;
  const usableW = W - marginX * 2;
  const usableH = H - surfaceY - 30;

  ctx.fillStyle = "#111a33";
  ctx.fillRect(marginX, surfaceY, usableW, usableH);
  ctx.strokeStyle = "#2b3a66";
  ctx.strokeRect(marginX, surfaceY, usableW, usableH);

  ctx.strokeStyle = "#5ad1c8";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(marginX, surfaceY);
  ctx.lineTo(W - marginX, surfaceY);
  ctx.stroke();
  ctx.fillStyle = "#9aa6c4";
  ctx.font = "12px system-ui, sans-serif";
  ctx.fillText("표면 (surface)", marginX, surfaceY - 8);

  const depthFrac = logScale(data.depth_um);
  const widthFrac = logScale(data.width_um);

  const halfW = Math.max(6, (widthFrac * usableW) / 2);
  const depthPx = Math.max(6, depthFrac * usableH);
  const cx = marginX + usableW / 2;

  drawVolume(ctx, data, cx, surfaceY, halfW, depthPx);

  if (data.sputtering && data.crater_depth_um > data.depth_um) {
    const craterFrac = logScale(data.crater_depth_um);
    const craterPx = Math.min(usableH, Math.max(depthPx, craterFrac * usableH));
    ctx.setLineDash([5, 4]);
    ctx.strokeStyle = "rgba(90, 209, 200, 0.8)";
    ctx.beginPath();
    ctx.moveTo(cx - halfW, surfaceY);
    ctx.lineTo(cx - halfW * 0.6, surfaceY + craterPx);
    ctx.lineTo(cx + halfW * 0.6, surfaceY + craterPx);
    ctx.lineTo(cx + halfW, surfaceY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#5ad1c8";
    ctx.fillText(`크레이터 ${fmtLength(data.crater_depth_um)}`, marginX + 4, surfaceY + craterPx + 14);
  }
}

function showLoadError(message) {
  const node = document.getElementById("load-error");
  node.hidden = false;
  node.textContent = message;
}

async function init() {
  try {
    const res = await fetch(assetUrl("data/elements.json"));
    if (!res.ok) throw new Error(`elements.json HTTP ${res.status}`);
    ELEMENTS = await res.json();
    state.equipment = EQUIPMENT[0].key;
  } catch (err) {
    console.error(err);
    showLoadError("원소 데이터를 불러오지 못했습니다. 페이지를 새로고침해 주세요.");
    return;
  }

  buildTable();
  buildLegend();
  buildEquipment();

  document.getElementById("energy-slider").addEventListener("input", () => {
    state.energy = sliderToEnergy();
    updateEnergyReadout();
    run();
  });
  document.getElementById("shots-slider").addEventListener("input", () => {
    state.shots = parseInt(document.getElementById("shots-slider").value, 10);
    updateShotsReadout();
    run();
  });

  selectEquipment(state.equipment);
  selectElement(state.symbol);
}

document.addEventListener("DOMContentLoaded", init);
