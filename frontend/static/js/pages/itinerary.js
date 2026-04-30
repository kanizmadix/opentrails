/* Itinerary page: form -> POST /api/itinerary/generate -> day timeline */
(async function () {
  if (!document.body.classList.contains("page-itinerary")) return;

  const form = document.getElementById("itin-form");
  const out = document.getElementById("itin-results");
  const summary = document.getElementById("itin-summary");

  function fmtTime(t) {
    if (!t) return "";
    if (typeof t === "string" && t.includes(":")) return t;
    return t;
  }

  function renderItin(data) {
    if (!data || !data.days || !data.days.length) {
      out.innerHTML = `<div class="search-empty"><div class="glyph">✶</div><p>Couldn't generate an itinerary. Try again.</p></div>`;
      return;
    }
    const days = data.days;
    const totalCost = data.total_cost ?? data.budget?.total ?? days.reduce((s, d) => s + (d.estimated_cost || 0), 0);
    const cur = data.currency || "$";

    out.innerHTML = `
      <div class="timeline">
        ${days.map((d, idx) => `
          <div class="timeline-day reveal" data-visible="true">
            <div class="timeline-day-header">
              <div>
                <div class="t-eyebrow">Day ${idx + 1}</div>
                <h3 class="timeline-day-title">${d.title || `Day ${idx + 1}`}</h3>
              </div>
              <span class="timeline-day-date">${d.date || ''}</span>
            </div>
            ${d.summary ? `<p class="muted" style="margin-bottom:16px;">${d.summary}</p>` : ''}
            <div class="timeline-activities">
              ${(d.activities || []).map((a) => `
                <div class="activity">
                  <span class="activity-time">${fmtTime(a.time) || a.slot || ''}</span>
                  <div class="activity-body">
                    <span class="activity-title">${a.title || a.name}</span>
                    ${a.description ? `<span class="activity-desc">${a.description}</span>` : ''}
                    <div class="activity-meta">
                      ${a.duration ? `<span>⏱ ${a.duration}</span>` : ''}
                      ${a.cost ? `<span>${cur}${a.cost}</span>` : ''}
                      ${a.location ? `<span>📍 ${a.location}</span>` : ''}
                    </div>
                  </div>
                </div>
              `).join("") || '<p class="muted t-small">No activities listed.</p>'}
            </div>
          </div>
        `).join("")}
      </div>
    `;

    if (summary) {
      const breakdown = data.budget?.breakdown || {};
      const max = Math.max(1, ...Object.values(breakdown));
      summary.innerHTML = `
        <div class="card">
          <div class="t-title-3" style="margin-bottom:12px;">Trip summary</div>
          <div class="muted t-small">${data.destination || ''} · ${days.length} day${days.length === 1 ? '' : 's'}</div>
          <hr/>
          <div class="budget">
            ${Object.entries(breakdown).map(([k, v]) => `
              <div class="budget-row"><span>${k}</span><span>${cur}${Math.round(v)}</span></div>
              <div class="budget-bar"><span style="width:${(v / max * 100).toFixed(0)}%"></span></div>
            `).join("")}
            <div class="budget-row total"><span>Total</span><span>${cur}${Math.round(totalCost)}</span></div>
          </div>
          <div class="itin-share-bar" style="margin-top:16px;">
            <button class="btn btn-primary" id="save-trip-btn">Save trip</button>
            <button class="btn btn-ghost" id="share-trip-btn">Share</button>
          </div>
        </div>
      `;
      summary.querySelector("#save-trip-btn")?.addEventListener("click", async () => {
        const r = await window.tryApi(() => window.api.post("/trips/save", { destination: data.destination, itinerary: data }));
        if (r) window.toast?.success("Trip saved.");
      });
      summary.querySelector("#share-trip-btn")?.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(location.href);
          window.toast?.success("Link copied to clipboard.");
        } catch (_) { window.toast?.warning("Couldn't copy."); }
      });
    }
  }

  async function generate() {
    const fd = new FormData(form);
    const body = {
      destination: fd.get("destination"),
      start_date: fd.get("start_date"),
      end_date: fd.get("end_date"),
      travelers: parseInt(fd.get("travelers") || "1", 10),
      budget: parseFloat(fd.get("budget") || 0) || null,
      vibe: fd.getAll("vibe"),
      currency: fd.get("currency") || "USD",
    };
    if (!body.destination || !body.start_date || !body.end_date) {
      window.toast?.warning("Destination and dates are required.");
      return;
    }
    if (window.skeleton) window.skeleton.inject(out, "card", 3);
    const data = await window.tryApi(() => window.api.post("/itinerary/generate", body));
    if (data) renderItin(data);
  }

  if (form) {
    form.addEventListener("submit", (e) => { e.preventDefault(); generate(); });
    const params = new URLSearchParams(location.search);
    if (params.get("dest")) form.querySelector('[name="destination"]').value = params.get("dest");
  }

  // Vibe chips toggle
  document.querySelectorAll(".vibe-row .chip").forEach((c) => {
    c.addEventListener("click", () => {
      const pressed = c.getAttribute("aria-pressed") === "true";
      c.setAttribute("aria-pressed", pressed ? "false" : "true");
      const hidden = c.querySelector("input[type='hidden']");
      if (hidden) hidden.disabled = pressed;
    });
  });
})();
