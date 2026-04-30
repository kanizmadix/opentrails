/* Destination detail page: intel + weather + currency + attractions */
(async function () {
  if (!document.body.classList.contains("page-destination")) return;

  const params = new URLSearchParams(location.search);
  const dest = params.get("q") || "Paris";
  const cc = params.get("cc") || "";

  const heroTitle = document.getElementById("dest-title");
  const heroSubtitle = document.getElementById("dest-subtitle");
  const hero = document.getElementById("dest-hero");
  const intelGrid = document.getElementById("intel-grid");
  const weatherEl = document.getElementById("weather-card");
  const currencyEl = document.getElementById("currency-card");
  const attractionsEl = document.getElementById("attractions-carousel");
  const packingEl = document.getElementById("packing-card");

  if (heroTitle) heroTitle.textContent = dest;
  if (hero) {
    const slug = dest.toLowerCase().replace(/[^a-z]/g, "-");
    hero.style.backgroundImage = `url('https://picsum.photos/seed/${slug}-hero/1920/1080')`;
  }

  function setCell(label, value, sub = "") {
    return `<div class="intel-cell"><span class="label">${label}</span><span class="value">${value || '—'}</span>${sub ? `<span class="sub">${sub}</span>` : ''}</div>`;
  }

  async function loadIntel() {
    if (!intelGrid) return;
    intelGrid.innerHTML = Array.from({length:6}, () => `<div class="intel-cell"><div class="skeleton" style="height:14px;width:50%;"></div><div class="skeleton" style="height:24px;width:70%;margin-top:8px;"></div></div>`).join("");
    const path = cc ? `/destinations/${cc}/intel` : `/destinations/intel`;
    const data = await window.tryApi(() => window.api.get(path, { params: cc ? undefined : { q: dest } }));
    if (!data) {
      intelGrid.innerHTML = setCell("Status", "Open data unavailable", "Try another destination");
      return;
    }
    if (heroSubtitle) heroSubtitle.textContent = data.tagline || data.summary || `Plan your trip to ${dest}`;
    intelGrid.innerHTML = [
      setCell("Visa", data.visa || data.visa_required || "Check requirements"),
      setCell("Currency", data.currency || data.currency_code || "—", data.currency_name || ""),
      setCell("Language", (data.languages && data.languages.join(", ")) || data.language || "—"),
      setCell("Plug type", (data.plug_types && data.plug_types.join(", ")) || data.plug_type || "—", data.voltage ? `${data.voltage}` : ""),
      setCell("Best season", data.best_season || data.best_time || "Year-round"),
      setCell("Safety", data.safety || "Standard precautions"),
    ].join("");
  }

  async function loadWeather() {
    if (!weatherEl) return;
    const data = await window.tryApi(() => window.api.get("/weather", { params: { q: dest } }));
    if (!data || !data.daily) {
      weatherEl.innerHTML = `<p class="muted">Weather data unavailable.</p>`;
      return;
    }
    const cur = data.current || (data.daily[0] || {});
    weatherEl.innerHTML = `
      <div class="weather-current">
        <div class="temp">${Math.round(cur.temp ?? cur.temperature_max ?? 0)}°</div>
        <div>
          <div class="t-title-3">${cur.summary || cur.weather_description || 'Forecast'}</div>
          <div class="t-caption muted">Feels like ${Math.round(cur.feels_like ?? cur.temp ?? 0)}°</div>
        </div>
      </div>
      <div class="weather-week">
        ${(data.daily || []).slice(0, 7).map((d) => `
          <div class="weather-day">
            <div class="dow">${new Date(d.date).toLocaleDateString([], { weekday: "short" })}</div>
            <div class="hi">${Math.round(d.temp_max ?? d.temperature_max ?? 0)}°</div>
            <div class="lo">${Math.round(d.temp_min ?? d.temperature_min ?? 0)}°</div>
          </div>
        `).join("")}
      </div>
    `;
  }

  async function loadCurrency() {
    if (!currencyEl) return;
    currencyEl.innerHTML = `
      <div class="t-title-3">Currency converter</div>
      <div class="currency-row">
        <input id="amt-from" type="number" value="100" step="1" min="0" />
        <button class="currency-swap" title="Swap" id="cur-swap" aria-label="Swap currencies">⇄</button>
        <input id="amt-to" type="text" readonly value="…" />
      </div>
      <div class="row" style="gap:8px;">
        <select id="cur-from" class="select"><option value="USD">USD</option><option value="EUR">EUR</option><option value="GBP">GBP</option><option value="JPY">JPY</option><option value="INR">INR</option></select>
        <select id="cur-to" class="select"><option value="EUR">EUR</option><option value="USD">USD</option><option value="GBP">GBP</option><option value="JPY">JPY</option><option value="INR">INR</option></select>
      </div>
    `;
    const amt = currencyEl.querySelector("#amt-from");
    const out = currencyEl.querySelector("#amt-to");
    const fromSel = currencyEl.querySelector("#cur-from");
    const toSel = currencyEl.querySelector("#cur-to");

    async function refresh() {
      const data = await window.tryApi(() => window.api.get("/currency/convert", { params: { from: fromSel.value, to: toSel.value, amount: amt.value || 0 } }));
      if (data && (data.result !== undefined)) out.value = `${Number(data.result).toFixed(2)} ${toSel.value}`;
      else out.value = "—";
    }
    [amt, fromSel, toSel].forEach((el) => el.addEventListener("input", refresh));
    currencyEl.querySelector("#cur-swap").addEventListener("click", () => {
      const a = fromSel.value; fromSel.value = toSel.value; toSel.value = a; refresh();
    });
    refresh();
  }

  async function loadAttractions() {
    if (!attractionsEl) return;
    if (window.skeleton) window.skeleton.inject(attractionsEl, "card", 4);
    const data = await window.tryApi(() => window.api.get("/attractions/top", { params: { q: dest, limit: 12 } }));
    const items = (data && (data.results || data.items || data)) || [];
    if (!items.length) { attractionsEl.innerHTML = `<p class="muted">No attractions yet.</p>`; return; }
    attractionsEl.innerHTML = items.map((a) => {
      const slug = (a.name || "").toLowerCase().replace(/[^a-z]/g, "-");
      const img = a.image || `https://picsum.photos/seed/${slug || dest}/640/480`;
      return `
        <div class="card-image card-hover">
          <div class="media" style="background-image:url('${img}');" role="img" aria-label="${a.name}"></div>
          <div class="body">
            <span class="card-title">${a.name}</span>
            <span class="card-meta">${a.kinds || a.category || ''}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  async function loadPacking() {
    if (!packingEl) return;
    const data = await window.tryApi(() => window.api.get("/packing", { params: { q: dest } }));
    const items = (data && (data.items || data)) || [];
    if (!items.length) {
      packingEl.innerHTML = `<div class="t-title-3">Packing list</div><p class="muted">Sample list will populate when AI is connected.</p>`;
      return;
    }
    packingEl.innerHTML = `
      <div class="t-title-3">Packing list</div>
      <div class="packing-list">
        ${items.slice(0, 24).map((it) => `<div class="packing-item">○ ${it.name || it}</div>`).join("")}
      </div>
    `;
  }

  // Build itinerary CTA
  const buildBtn = document.getElementById("build-itinerary-btn");
  if (buildBtn) buildBtn.href = `/itinerary?dest=${encodeURIComponent(dest)}`;

  loadIntel(); loadWeather(); loadCurrency(); loadAttractions(); loadPacking();
})();
