"use strict";

const COMPARE_COLORS = [
  "#f6a94b",
  "#5ad1c8",
  "#8eb6ff",
  "#ff8fb8",
  "#d2f58a",
  "#e2b0ff",
  "#ffd166",
  "#7ee0d0",
  "#ffb088",
  "#c5d4ff",
];

const CATEGORY_LABELS = {
  nonmetals: "비금속",
  "noble-gases": "비활성 기체",
  "alkali-metals": "알칼리 금속",
  "alkaline-earth-metals": "알칼리 토금속",
  metalloids: "준금속",
  halogens: "할로겐",
  "post-transition-metals": "전이후 금속",
  "poor-metals": "전이후 금속",
  "transition-metals": "전이 금속",
  lanthanides: "란타넘족",
  actinides: "악티늄족",
  unknown: "기타",
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

function startWorkspace({ elements, equipment, computeAll }) {
  const state = {
    symbol: elements.some((el) => el.symbol === "Si") ? "Si" : elements[0].symbol,
    eqs: [equipment[0].key],
    controls: {},
  };
  let runToken = 0;

  function eqByKey(key) {
    return equipment.find((eq) => eq.key === key);
  }

  function ensureControl(key) {
    if (state.controls[key]) return;
    const eq = eqByKey(key);
    state.controls[key] = {
      energy: eq.default_energy,
      shots: eq.uses_shots ? eq.default_shots : null,
    };
  }

  function buildTable() {
    const grid = document.getElementById("periodic-table");
    grid.innerHTML = "";
    for (const el of elements) {
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
    for (const el of elements) {
      if (seen.has(el.category)) continue;
      seen.add(el.category);
      const li = document.createElement("li");
      li.innerHTML = `<span class="swatch cat-${el.category}"></span>${CATEGORY_LABELS[el.category] || el.category}`;
      legend.appendChild(li);
    }
  }

  function selectElement(symbol) {
    state.symbol = symbol;
    document.querySelectorAll(".element").forEach((node) => {
      node.classList.toggle("selected", node.dataset.symbol === symbol);
    });
    const el = elements.find((item) => item.symbol === symbol);
    document.getElementById("selected-label").textContent = `${el.symbol} · ${el.name}`;
    run();
  }

  function buildEquipment() {
    const list = document.getElementById("equipment-list");
    list.innerHTML = "";
    for (const eq of equipment) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "equipment-btn";
      btn.dataset.key = eq.key;
      btn.setAttribute("role", "checkbox");
      btn.innerHTML =
        `<span class="eq-probe">${PROBE_LABELS[eq.probe] || eq.probe}</span>` +
        `<span class="eq-name">${eq.name}</span>` +
        `<span class="eq-full">${eq.full_name}</span>`;
      btn.addEventListener("click", () => toggleEquipment(eq.key));
      list.appendChild(btn);
    }
  }

  function syncEquipmentButtons() {
    document.querySelectorAll(".equipment-btn").forEach((btn) => {
      const on = state.eqs.includes(btn.dataset.key);
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function toggleEquipment(key) {
    const index = state.eqs.indexOf(key);
    if (index >= 0) {
      if (state.eqs.length === 1) return;
      state.eqs.splice(index, 1);
    } else {
      state.eqs.push(key);
      ensureControl(key);
    }
    syncEquipmentButtons();
    renderControls(true);
    run();
  }

  function energyFromFrac(eq, frac) {
    const energy = eq.min_energy + frac * (eq.max_energy - eq.min_energy);
    return Math.round(energy * 100) / 100;
  }

  function fracFromEnergy(eq, energy) {
    const span = eq.max_energy - eq.min_energy;
    if (!span) return 0;
    return (energy - eq.min_energy) / span;
  }

  function writeReadouts(key) {
    const card = document.querySelector(`.control-card[data-key="${key}"]`);
    if (!card) return;
    const eq = eqByKey(key);
    const ctrl = state.controls[key];
    card.querySelector('[data-readout="energy"]').textContent = `${ctrl.energy} ${eq.energy_unit}`;
    const shots = card.querySelector('[data-readout="shots"]');
    if (shots) shots.textContent = String(ctrl.shots);
  }

  function cardHtml(key) {
    const eq = eqByKey(key);
    const ctrl = state.controls[key];
    const frac = fracFromEnergy(eq, ctrl.energy);
    let shots = "";
    if (eq.uses_shots) {
      shots = `
        <div class="energy-head" style="margin-top:10px">
          <h3>Shot 수</h3>
          <span class="pill pill-accent" data-readout="shots">${ctrl.shots}</span>
        </div>
        <input type="range" data-kind="shots" min="${eq.min_shots}" max="${eq.max_shots}" step="1" value="${ctrl.shots}" />
        <div class="energy-scale"><span>${eq.min_shots}</span><span>${eq.max_shots}</span></div>`;
    }
    return `
      <div class="control-card" data-key="${key}">
        <div class="energy-head">
          <h3>${eq.name} · ${eq.energy_label || "빔 에너지"}</h3>
          <span class="pill pill-accent" data-readout="energy">${ctrl.energy} ${eq.energy_unit}</span>
        </div>
        <input type="range" data-kind="energy" min="0" max="1" step="0.001" value="${frac}" />
        <div class="energy-scale"><span>${eq.min_energy} ${eq.energy_unit}</span><span>${eq.max_energy} ${eq.energy_unit}</span></div>
        ${shots}
      </div>`;
  }

  function renderControls(rebuild) {
    const stack = document.getElementById("control-stack");
    const signature = state.eqs.join(",");
    if (!rebuild && stack.dataset.signature === signature) {
      state.eqs.forEach(writeReadouts);
      return;
    }
    stack.dataset.signature = signature;
    stack.innerHTML = state.eqs.map(cardHtml).join("");
    stack.querySelectorAll('input[type="range"]').forEach((input) => {
      input.addEventListener("input", () => {
        const key = input.closest(".control-card").dataset.key;
        const eq = eqByKey(key);
        if (input.dataset.kind === "energy") {
          state.controls[key].energy = energyFromFrac(eq, parseFloat(input.value));
        } else {
          state.controls[key].shots = parseInt(input.value, 10);
        }
        writeReadouts(key);
        run();
      });
    });
  }

  function fmtLength(um) {
    const nm = um * 1000;
    if (nm < 1000) return `${nm.toFixed(nm < 10 ? 2 : 1)} nm`;
    if (um < 1000) return `${um.toFixed(um < 10 ? 2 : 1)} µm`;
    return `${(um / 1000).toFixed(2)} mm`;
  }

  function logScale(um) {
    const lo = -4;
    const hi = 4;
    const v = Math.log10(Math.max(um, 1e-4));
    return Math.min(1, Math.max(0, (v - lo) / (hi - lo)));
  }

  function traceVolume(ctx, shape, cx, surfaceY, half, depthPx, neck) {
    const bottom = surfaceY + depthPx;
    ctx.beginPath();
    if (shape === "pear") {
      const n = Math.max(0.4, Math.min(neck, half * 0.85));
      const belly = surfaceY + depthPx * 0.55;
      ctx.moveTo(cx - n, surfaceY);
      ctx.bezierCurveTo(cx - n, surfaceY + depthPx * 0.16, cx - half, surfaceY + depthPx * 0.3, cx - half, belly);
      ctx.bezierCurveTo(cx - half, surfaceY + depthPx * 0.82, cx - half * 0.42, bottom, cx, bottom);
      ctx.bezierCurveTo(cx + half * 0.42, bottom, cx + half, surfaceY + depthPx * 0.82, cx + half, belly);
      ctx.bezierCurveTo(cx + half, surfaceY + depthPx * 0.3, cx + n, surfaceY + depthPx * 0.16, cx + n, surfaceY);
    } else if (shape === "beam") {
      const inset = half * 0.9;
      ctx.moveTo(cx - half, surfaceY);
      ctx.lineTo(cx - inset, bottom);
      ctx.lineTo(cx + inset, bottom);
      ctx.lineTo(cx + half, surfaceY);
    } else {
      ctx.moveTo(cx - half, surfaceY);
      ctx.bezierCurveTo(cx - half, surfaceY + depthPx * 0.7, cx - half * 0.4, bottom, cx, bottom);
      ctx.bezierCurveTo(cx + half * 0.4, bottom, cx + half, surfaceY + depthPx * 0.7, cx + half, surfaceY);
    }
    ctx.closePath();
  }

  function drawSingle(data) {
    const canvas = document.getElementById("viz-canvas");
    canvas.width = 640;
    canvas.height = 360;
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

    const halfW = Math.max(6, (logScale(data.width_um) * usableW) / 2);
    const depthPx = Math.max(6, logScale(data.depth_um) * usableH);
    const cx = marginX + usableW / 2;
    const shape = data.volume_shape || "spot";
    const bottom = surfaceY + depthPx;
    const grad = ctx.createLinearGradient(0, surfaceY, 0, bottom);
    grad.addColorStop(0, "rgba(246, 169, 75, 0.9)");
    grad.addColorStop(1, "rgba(246, 169, 75, 0.12)");
    const neck = shape === "pear" ? halfW * 0.22 : halfW;
    traceVolume(ctx, shape, cx, surfaceY, halfW, depthPx, neck);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = "#f6a94b";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.strokeStyle = "#e8ecf7";
    ctx.fillStyle = "#e8ecf7";
    ctx.font = "12px system-ui, sans-serif";
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

    if (data.sputtering && data.crater_depth_um > data.depth_um && shape !== "pear") {
      const craterPx = Math.min(usableH, Math.max(depthPx, logScale(data.crater_depth_um) * usableH));
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

  function drawCompare(results) {
    const canvas = document.getElementById("viz-canvas");
    canvas.width = 960;
    canvas.height = 460;
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    const marginL = 86;
    const marginR = 28;
    const marginT = 36;
    const marginB = 28;
    const plotW = W - marginL - marginR;
    const plotH = H - marginT - marginB;
    const maxDepth = Math.max(...results.map((item) => item.depth_um), 1e-6);
    const maxHalf = Math.max(...results.map((item) => item.width_um / 2), 1e-6);
    const span = Math.max(maxDepth, maxHalf, 1e-6);
    const px = Math.min(plotH / span, plotW / 2 / span);
    const cx = marginL + plotW / 2;
    const surfaceY = marginT;

    ctx.fillStyle = "#111a33";
    ctx.fillRect(marginL, marginT, plotW, plotH);
    ctx.strokeStyle = "#2b3a66";
    ctx.strokeRect(marginL, marginT, plotW, plotH);
    ctx.strokeStyle = "#5ad1c8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(marginL, surfaceY);
    ctx.lineTo(W - marginR, surfaceY);
    ctx.stroke();
    ctx.fillStyle = "#9aa6c4";
    ctx.font = "13px system-ui, sans-serif";
    ctx.fillText("표면", marginL, surfaceY - 10);
    ctx.fillStyle = "#e8ecf7";
    const axisBottom = surfaceY + maxDepth * px;
    ctx.fillText(`최대 깊이 ${fmtLength(maxDepth)}`, 8, Math.min(H - 8, axisBottom));
    ctx.strokeStyle = "#e8ecf7";
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(cx, surfaceY);
    ctx.lineTo(cx, axisBottom);
    ctx.stroke();
    ctx.setLineDash([]);

    const ordered = results
      .map((item, index) => ({ item, index }))
      .sort((a, b) => b.item.depth_um - a.item.depth_um);
    for (const { item, index } of ordered) {
      const color = COMPARE_COLORS[index % COMPARE_COLORS.length];
      const half = Math.max(0.8, (item.width_um / 2) * px);
      const depthPx = Math.max(0.8, item.depth_um * px);
      const beam = item.beam_diameter_um || item.width_um;
      const neck = Math.max(0.4, (beam / 2) * px);
      traceVolume(ctx, item.volume_shape || "spot", cx, surfaceY, half, depthPx, neck);
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.42;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.7;
      ctx.stroke();
    }
  }

  function render(results) {
    const metrics = document.getElementById("metrics");
    const legend = document.getElementById("compare-legend");
    const caption = document.getElementById("viz-caption");
    const note = document.getElementById("model-note");
    if (results.length === 1) {
      const data = results[0];
      metrics.hidden = false;
      legend.hidden = true;
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
      const shotsBit = data.uses_shots ? ` × ${data.shots} shots` : "";
      caption.textContent =
        `${data.element.symbol} · ${data.equipment_name} @ ${data.energy_keV} ${data.energy_unit || "keV"}${shotsBit} — ` +
        `깊이 ${fmtLength(data.depth_um)}, 폭 ${fmtLength(data.width_um)} (로그 스케일 시각화)`;
      const noteKey = data.equipment === "aes" ? "aes" : data.probe;
      note.textContent = MODEL_NOTES[noteKey] || "";
      drawSingle(data);
    } else {
      metrics.hidden = true;
      legend.hidden = false;
      legend.innerHTML = results
        .map((data, index) => {
          const color = COMPARE_COLORS[index % COMPARE_COLORS.length];
          return (
            `<li><span class="swatch" style="background:${color}"></span>` +
            `${data.equipment_name} · 깊이 ${fmtLength(data.depth_um)} · 폭 ${fmtLength(data.width_um)}</li>`
          );
        })
        .join("");
      const symbol = results[0].element.symbol;
      caption.textContent =
        `${symbol} · ${results.length}개 장비. 가로와 세로는 같은 길이 눈금이라, 더 깊은 방법이 더 길게 내려갑니다.`;
      note.textContent = "한 장만 고르면 로그 눈금 단면으로 돌아갑니다.";
      drawCompare(results);
    }
    if (typeof window.reportFrameHeight === "function") window.reportFrameHeight();
  }

  async function run() {
    const token = ++runToken;
    const desc = document.getElementById("equipment-desc");
    if (state.eqs.length === 1) {
      desc.textContent = eqByKey(state.eqs[0]).description || "";
    } else {
      desc.textContent = "고른 장비를 같은 길이 눈금 위에 겹쳐 그립니다.";
    }
    let results;
    try {
      results = await computeAll(state.symbol, state.eqs.slice(), state.controls);
    } catch (err) {
      if (err && err.name === "AbortError") return;
      console.error(err);
      return;
    }
    if (token !== runToken || !results) return;
    render(results);
  }

  buildTable();
  buildLegend();
  buildEquipment();
  ensureControl(state.eqs[0]);
  syncEquipmentButtons();
  renderControls(true);
  selectElement(state.symbol);
}
