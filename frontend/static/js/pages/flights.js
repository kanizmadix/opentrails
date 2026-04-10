/* Flights page: search form + results + fare calendar */
(function () {
  if (!document.body.classList.contains("page-flights")) return;

  const form = document.getElementById("flights-form");
  const results = document.getElementById("flight-results");
  const calendar = document.getElementById("fare-calendar");

  function fmtTime(iso) {
    if (!iso) return "—";
    try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }
    catch (_) { return iso; }
  }
  function fmtDuration(mins) {
    if (!mins && mins !== 0) return "—";
    const h = Math.floor(mins / 60), m = mins % 60;
    return `${h}h ${m}m`;
  }
  function airlineCode(name) {
    return (name || "??").slice(0, 2).toUpperCase();
  }

  function render(items) {
    if (!items || !items.length) {
      results.innerHTML = `<div class="search-empty"><div class="glyph">✈</div><p>No flights for this query yet. Try different dates.</p></div>`;
      return;
    }
    results.innerHTML = items.map((f) => `
      <a class="flight-card" href="${f.deep_link || '#'}" target="_blank" rel="noopener">
        <span class="flight-airline" aria-label="${f.airline || 'Airline'}">${airlineCode(f.airline)}</span>
        <div class="flight-route">
          <div class="times">
            <span>${fmtTime(f.depart_at)}</span>
            <span class="arrow"></span>
            <span>${fmtTime(f.arrive_at)}</span>
          </div>
          <div class="meta">
            <span>${f.origin || '—'} → ${f.destination || '—'}</span>
            <span>${fmtDuration(f.duration_minutes)}</span>
            <span>${f.stops === 0 ? 'Nonstop' : `${f.stops || 0} stop${f.stops === 1 ? '' : 's'}`}</span>
            ${f.airline ? `<span>${f.airline}</span>` : ''}
          </div>
        </div>
        <div class="flight-price">
          <span class="amount">${f.currency || '$'}${Math.round(f.price ?? f.total ?? 0)}</span>
          <span class="per">total</span>
        </div>
      </a>
    `).join("");
  }

  function renderCalendar(payload) {
    if (!calendar || !payload || !payload.days) { if (calendar) calendar.innerHTML = ""; return; }
    calendar.innerHTML = payload.days.slice(0, 28).map((d) => {
      const cls = d.is_cheap ? "fare-cell cheap" : "fare-cell";
      return `<div class="${cls}" data-date="${d.date}">
        <div class="day">${new Date(d.date).toLocaleDateString([], { weekday: "short" })}</div>
        <div class="price">${d.price ? '$' + Math.round(d.price) : '—'}</div>
      </div>`;
    }).join("");
  }

  async function search() {
    const fd = new FormData(form);
    const body = {
      origin: fd.get("origin"),
      destination: fd.get("destination"),
      depart_date: fd.get("depart_date"),
      return_date: fd.get("return_date") || null,
      passengers: parseInt(fd.get("passengers") || "1", 10),
    };
    if (!body.origin || !body.destination || !body.depart_date) {
      window.toast?.warning("Origin, destination and depart date are required.");
      return;
    }
    if (window.skeleton) window.skeleton.inject(results, "card", 4);
    const data = await window.tryApi(() => window.api.post("/flights/search", body));
    if (!data) return;
    render(data.results || data.flights || data.items || []);
    if (data.fare_calendar) renderCalendar(data.fare_calendar);
  }

  if (form) {
    form.addEventListener("submit", (e) => { e.preventDefault(); search(); });

    // Prefill from query string
    const params = new URLSearchParams(location.search);
    ["origin", "destination", "to", "depart_date", "return_date", "passengers"].forEach((k) => {
      const v = params.get(k);
      const inp = form.querySelector(`[name="${k === 'to' ? 'destination' : k}"]`);
      if (v && inp) inp.value = v;
    });
    if (params.get("origin") && params.get("destination") && params.get("depart_date")) {
      search();
    }
  }
})();
