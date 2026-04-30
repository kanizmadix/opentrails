/* Toast notifications */
(function () {
  const root = document.createElement("div");
  root.style.cssText = "position:fixed;top:80px;right:20px;display:flex;flex-direction:column;gap:8px;z-index:1000;pointer-events:none;";
  document.addEventListener("DOMContentLoaded", () => document.body.appendChild(root));

  function toast(msg, kind = "info", ms = 3200) {
    const el = document.createElement("div");
    const colors = {
      info: "var(--color-ink)",
      success: "var(--color-success)",
      warning: "var(--color-warning)",
      error: "var(--color-danger)",
    };
    el.style.cssText = `
      pointer-events:auto;
      max-width:340px;
      padding:12px 18px;
      background:var(--color-bg-elevated);
      color:var(--color-ink);
      border:1px solid var(--color-divider);
      border-left:3px solid ${colors[kind] || colors.info};
      border-radius:14px;
      box-shadow:var(--shadow-lg);
      font-size:0.9375rem;
      transform:translateX(20px);
      opacity:0;
      transition:transform 220ms cubic-bezier(0.16,1,0.3,1),opacity 220ms ease-out;
    `;
    el.textContent = msg;
    root.appendChild(el);
    requestAnimationFrame(() => { el.style.transform = "translateX(0)"; el.style.opacity = "1"; });
    setTimeout(() => {
      el.style.transform = "translateX(20px)";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 250);
    }, ms);
    return el;
  }

  window.toast = {
    info: (m) => toast(m, "info"),
    success: (m) => toast(m, "success"),
    warning: (m) => toast(m, "warning"),
    error: (m) => toast(m, "error"),
  };
})();
