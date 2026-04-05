/* Theme toggle: light / dark / system, persisted in localStorage */
(function () {
  const KEY = "opentrails:theme";
  const root = document.documentElement;

  function getStored() {
    try { return localStorage.getItem(KEY); } catch (_) { return null; }
  }
  function setStored(v) {
    try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch (_) {}
  }

  function effective() {
    const stored = getStored();
    if (stored === "light" || stored === "dark") return stored;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function apply() {
    const stored = getStored();
    if (stored === "light" || stored === "dark") {
      root.setAttribute("data-theme", stored);
    } else {
      root.removeAttribute("data-theme");
    }
    document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: effective(), explicit: stored } }));
  }

  function toggle() {
    const eff = effective();
    setStored(eff === "dark" ? "light" : "dark");
    apply();
  }

  function setSystem() { setStored(null); apply(); }

  // Apply early
  apply();

  // React to system change when no explicit theme
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (!getStored()) apply();
  });

  // Wire toggle buttons
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-theme-toggle]");
    if (btn) {
      e.preventDefault();
      toggle();
    }
    const sysBtn = e.target.closest("[data-theme-system]");
    if (sysBtn) { e.preventDefault(); setSystem(); }
  });

  window.theme = { toggle, setSystem, effective, apply };
})();
