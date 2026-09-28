"use strict";

function assetUrl(relativePath) {
  return new URL(relativePath, document.baseURI).toString();
}

function showLoadError(message) {
  const node = document.getElementById("load-error");
  node.hidden = false;
  node.textContent = message;
}

document.addEventListener("DOMContentLoaded", async () => {
  let elements;
  try {
    const res = await fetch(assetUrl("data/elements.json"));
    if (!res.ok) throw new Error(`elements.json HTTP ${res.status}`);
    elements = await res.json();
  } catch (err) {
    console.error(err);
    showLoadError("원소 데이터를 불러오지 못했습니다. 페이지를 새로고침해 주세요.");
    return;
  }

  startWorkspace({
    elements,
    equipment: EQUIPMENT,
    computeAll(symbol, eqs, controls) {
      const el = elements.find((item) => item.symbol === symbol);
      return eqs.map((key) => {
        const ctrl = controls[key];
        const data = simulate(el, key, ctrl.energy, ctrl.shots);
        data.element = {
          symbol: el.symbol,
          name: el.name,
          number: el.number,
          density: el.density,
          atomic_mass: el.atomic_mass,
        };
        return data;
      });
    },
  });
});
