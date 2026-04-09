/* Skeleton loaders. Insert lightweight placeholder content into a target. */
(function () {
  function row(w = "60%") {
    return `<div class="skeleton" style="height:14px;width:${w};margin:6px 0;border-radius:7px;"></div>`;
  }
  function block(h = "120px") {
    return `<div class="skeleton" style="height:${h};width:100%;border-radius:14px;"></div>`;
  }
  function card({ media = true } = {}) {
    return `
      <div class="card" style="padding:0;overflow:hidden;">
        ${media ? `<div class="skeleton" style="height:180px;width:100%;border-radius:0;"></div>` : ""}
        <div style="padding:20px 24px 28px;">
          ${row("70%")}
          ${row("45%")}
          ${row("85%")}
        </div>
      </div>
    `;
  }

  function inject(target, type = "card", count = 3) {
    if (!target) return;
    const fns = { row, block, card };
    const fn = fns[type] || card;
    target.innerHTML = Array.from({ length: count }, () => fn()).join("");
  }

  window.skeleton = { row, block, card, inject };
})();
