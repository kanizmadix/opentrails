/* Global search page: tabs + URL-state + endpoint dispatch */
(function () {
  if (!document.body.classList.contains("page-search")) return;

  const params = new URLSearchParams(location.search);
  const q = params.get("q") || "";
  const initialTab = params.get("tab") || "destinations";

  const input = document.getElementById("search-input");
  if (input) input.value = q;

  function setTab(name) {
    document.querySelectorAll(".search-tab").forEach((t) => {
      t.setAttribute("aria-selected", t.dataset.tab === name ? "true" : "false");
    });
    document.querySelectorAll(".search-tabpanel").forEach((p) => {
      p.dataset.active = p.dataset.tab === name ? "true" : "false";
    });
    const u = new URL(location.href);
    u.searchParams.set("tab", name);
    history.replaceState(null, "", u);
    if (q) loadTab(name, q);
  }

  document.querySelectorAll(".search-tab").forEach((t) => {
    t.addEventListener("click", () => setTab(t.dataset.tab));
  });

  function emptyMsg(panel, msg = "No results yet. Try another search.") {
    panel.innerHTML = `<div class="search-empty"><div class="glyph">○</div><p>${msg}</p></div>`;
  }
  function loadingMsg(panel) {
    if (window.skeleton) window.skeleton.inject(panel, "card", 3);
    else panel.innerHTML = "<p class='muted'>Searching…</p>";
  }

  async function loadTab(name, query) {
    const panel = document.querySelector(`.search-tabpanel[data-tab="${name}"]`);
    if (!panel) return;
    loadingMsg(panel);
    try {
      let html = "";
      if (name === "destinations") {
        const data = await window.api.get("/destinations/search", { params: { q: query } }).catch(() => null);
        const items = (data && (data.results || data.items || data)) || [];
        if (!items.length) return emptyMsg(panel, "No destinations matched.");
        html = items.slice(0, 12).map((d) => `
          <a class="card-tile" href="/destination?q=${encodeURIComponent(d.name || d.title || query)}${d.country_code ? `&cc=${d.country_code}` : ""}">
            <span style="font-size:1.5rem;">📍</span>
            <span class="stack" style="gap:2px;">
              <strong>${d.name || d.title || query}</strong>
              <span class="muted t-caption">${d.country || d.region || ""}</span>
            </span>
          </a>
        `).join("");
      } else if (name === "attractions") {
        const data = await window.api.get("/attractions/search", { params: { q: query } }).catch(() => null);
        const items = (data && (data.results || data.items || data)) || [];
        if (!items.length) return emptyMsg(panel, "No attractions found. Try \"Eiffel\", \"Colosseum\", or a city name.");
        html = items.slice(0, 18).map((a) => `
          <a class="card-tile" href="${a.url || '#'}">
            <span style="font-size:1.5rem;">🎟</span>
            <span class="stack" style="gap:2px;">
              <strong>${a.name}</strong>
              <span class="muted t-caption">${a.kinds || a.category || ""}</span>
            </span>
          </a>
        `).join("");
      } else if (name === "flights") {
        emptyMsg(panel, "Search flights with origin and dates →");
        panel.querySelector(".search-empty").innerHTML += `<a class="btn btn-primary btn-lg" style="margin-top:16px;" href="/flights?to=${encodeURIComponent(query)}">Open flight search</a>`;
        return;
      } else if (name === "hotels") {
        emptyMsg(panel, "Search hotels with dates and guests →");
        panel.querySelector(".search-empty").innerHTML += `<a class="btn btn-primary btn-lg" style="margin-top:16px;" href="/hotels?city=${encodeURIComponent(query)}">Open hotel search</a>`;
        return;
      }
      panel.innerHTML = `<div class="search-results">${html}</div>`;
    } catch (err) {
      console.error(err);
      emptyMsg(panel, "Couldn't load results. Try again.");
    }
  }

  const form = document.getElementById("search-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const v = (input.value || "").trim();
      if (!v) return;
      const u = new URL(location.href);
      u.searchParams.set("q", v);
      location.href = u.toString();
    });
  }

  setTab(initialTab);
})();
