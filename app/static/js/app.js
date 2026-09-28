"use strict";

const boot = JSON.parse(document.getElementById("bootstrap-data").textContent);

async function computeAll(symbol, eqs, controls) {
  const results = [];
  for (const key of eqs) {
    const ctrl = controls[key];
    const body = { symbol, equipment: key, energy: ctrl.energy };
    if (ctrl.shots != null) body.shots = ctrl.shots;
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    results.push(await res.json());
  }
  return results;
}

document.addEventListener("DOMContentLoaded", () => {
  startWorkspace({
    elements: boot.elements,
    equipment: boot.equipment,
    computeAll,
  });
});
