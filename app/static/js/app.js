"use strict";

const boot = JSON.parse(document.getElementById("bootstrap-data").textContent);
const ELEMENTS = boot.elements;
const EQUIPMENT = boot.equipment;

const state = {
  symbol: "Si",
  equipment: EQUIPMENT[0].key,
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

let pending = null;
async function run() {
  const body = {
    symbol: state.symbol,
    equipment: state.equipment,
    energy: state.energy,
  };
  if (state.shots != null) body.shots = state.shots;
  if (pending) pending.abort();
  pending = new AbortController();
  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: pending.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    render(data);
  } catch (err) {
    if (err.name !== "AbortError") console.error(err);
  }
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

  const unit = data.energy_unit || "keV";
  const shotsBit = data.uses_shots ? ` × ${data.shots} shots` : "";
  document.getElementById("viz-caption").textContent =
    `${data.element.symbol} · ${data.equipment_name} @ ${data.energy_keV} ${unit}${shotsBit} — ` +
    `깊이 ${fmtLength(data.depth_um)}, 폭 ${fmtLength(data.width_um)} (로그 스케일 시각화)`;

  drawViz(data);
}

function logScale(um) {
  const lo = -4;
  const hi = 4;
  const v = Math.log10(Math.max(um, 1e-4));
  return Math.min(1, Math.max(0, (v - lo) / (hi - lo)));
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

  const grad = ctx.createLinearGradient(0, surfaceY, 0, surfaceY + depthPx);
  grad.addColorStop(0, "rgba(246, 169, 75, 0.85)");
  grad.addColorStop(1, "rgba(246, 169, 75, 0.05)");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.moveTo(cx - halfW, surfaceY);
  ctx.bezierCurveTo(
    cx - halfW, surfaceY + depthPx * 0.7,
    cx - halfW * 0.4, surfaceY + depthPx,
    cx, surfaceY + depthPx
  );
  ctx.bezierCurveTo(
    cx + halfW * 0.4, surfaceY + depthPx,
    cx + halfW, surfaceY + depthPx * 0.7,
    cx + halfW, surfaceY
  );
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "#f6a94b";
  ctx.lineWidth = 1.5;
  ctx.stroke();

  ctx.strokeStyle = "#e8ecf7";
  ctx.fillStyle = "#e8ecf7";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(cx - halfW, surfaceY - 2);
  ctx.lineTo(cx + halfW, surfaceY - 2);
  ctx.stroke();
  ctx.fillText(`폭 ${fmtLength(data.width_um)}`, cx + halfW + 4, surfaceY + 4);

  ctx.beginPath();
  ctx.moveTo(cx, surfaceY);
  ctx.lineTo(cx, surfaceY + depthPx);
  ctx.stroke();
  ctx.fillText(`깊이 ${fmtLength(data.depth_um)}`, cx + 6, surfaceY + depthPx + 14);

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

function init() {
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
