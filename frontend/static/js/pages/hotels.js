/* Hotels page: search + split list/map */
import { createMap, addMarker, fitBounds } from "/static/js/leaflet-map.js";

(async function () {
  if (!document.body.classList.contains("page-hotels")) return;

  const form = document.getElementById("hotels-form");
  const list = document.getElementById("hotels-list");
  const mapEl = document.getElementById("hotels-map");
  let map;

  async function ensureMap() {
    if (map) return map;
    map = await createMap("hotels-map", { center: [40.4168, -3.7038], zoom: 4 });
    return map;
  }

  function gradientForName(name) {
    let h = 0;
    for (let i = 0; i < (name || "").length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
    const a = h % 360, b = (a + 40) % 360;
    return `linear-gradient(135deg, hsl(${a},45%,72%), hsl(${b},45%,82%))`;
  }

  function render(items) {
    if (!items || !items.length) {
      list.innerHTML = `<div class="search-empty"><div class="glyph">🏨</div><p>No hotels match. Try a different city.</p></div>`;
      return;
    }
    list.innerHTML = items.map((h, i) => `
      <a class="hotel-card" href="${h.deep_link || '#'}" target="_blank" rel="noopener" data-idx="${i}">
        <div class="photo" style="background:${gradientForName(h.name)};${h.image ? `background-image:url('${h.image}');background-size:cover;background-position:center;` : ''}"></div>
        <div class="body">
          <div>
            <div class="title">${h.name || 'Hotel'}</div>
            <div class="meta">${h.address || h.city || ''} · ${h.stars ? '★'.repeat(Math.round(h.stars)) : ''}</div>
            ${h.rating ? `<div class="rating"><span class="stars">${'★'.repeat(Math.round(h.rating / 2))}</span><span>${h.rating}/10</span></div>` : ''}
          </div>
          <div class="price-row">
            <span class="price">${h.currency || '$'}${Math.round(h.price ?? 0)}</span>
            <span class="per-night">per night</span>
          </div>
        </div>
      </a>
    `).join("");
  }

  async function plot(items) {
    if (!mapEl) return;
    await ensureMap();
    // Clear existing markers
    map.eachLayer((l) => { if (l._latlng) map.removeLayer(l); });
    const points = [];
    for (const h of items || []) {
      if (h.lat && h.lon) {
        await addMarker(map, h.lat, h.lon, `<h4>${h.name}</h4><p>${h.currency || '$'}${Math.round(h.price ?? 0)} / night</p>`, "hotel");
        points.push({ lat: h.lat, lon: h.lon });
      }
    }
    if (points.length) fitBounds(map, points);
  }

  async function search() {
    const fd = new FormData(form);
    const body = {
      city: fd.get("city"),
      check_in: fd.get("check_in"),
      check_out: fd.get("check_out"),
      guests: parseInt(fd.get("guests") || "2", 10),
    };
    if (!body.city || !body.check_in || !body.check_out) {
      window.toast?.warning("City and dates are required.");
      return;
    }
    if (window.skeleton) window.skeleton.inject(list, "card", 4);
    const data = await window.tryApi(() => window.api.post("/hotels/search", body));
    if (!data) return;
    const items = data.results || data.hotels || data.items || [];
    render(items);
    plot(items);
  }

  if (form) {
    form.addEventListener("submit", (e) => { e.preventDefault(); search(); });
    const params = new URLSearchParams(location.search);
    if (params.get("city")) form.querySelector('[name="city"]').value = params.get("city");
    if (params.get("city") && params.get("check_in")) search();
  }

  if (mapEl) await ensureMap();
})();
