/* Leaflet wrapper using OpenStreetMap tiles */
function ensureLeaflet() {
  return new Promise((resolve, reject) => {
    if (window.L) return resolve(window.L);
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    css.integrity = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=";
    css.crossOrigin = "";
    document.head.appendChild(css);

    const s = document.createElement("script");
    s.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    s.integrity = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=";
    s.crossOrigin = "";
    s.onload = () => resolve(window.L);
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

export async function createMap(elId, opts = {}) {
  const L = await ensureLeaflet();
  const el = typeof elId === "string" ? document.getElementById(elId) : elId;
  if (!el) throw new Error(`Map container not found: ${elId}`);
  el.dataset.loading = "false";
  const map = L.map(el, {
    center: opts.center || [20, 0],
    zoom: opts.zoom ?? 2,
    zoomControl: opts.zoomControl ?? true,
    scrollWheelZoom: opts.scrollWheelZoom ?? true,
    attributionControl: true,
  });
  useOSMTiles(map);
  return map;
}

export function useOSMTiles(map) {
  const L = window.L;
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
}

export function makeMarker(L, kind = "default") {
  return L.divIcon({
    className: "ot-marker-wrap",
    html: `<span class="ot-marker ${kind}"></span>`,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28],
  });
}

export async function addMarker(map, lat, lon, popupHtml, kind = "default") {
  const L = await ensureLeaflet();
  const marker = L.marker([lat, lon], { icon: makeMarker(L, kind) }).addTo(map);
  if (popupHtml) marker.bindPopup(popupHtml);
  return marker;
}

export function fitBounds(map, points, padding = 50) {
  if (!points || !points.length) return;
  const L = window.L;
  const b = L.latLngBounds(points.map((p) => [p.lat, p.lon]));
  map.fitBounds(b, { padding: [padding, padding] });
}

window.OTMap = { createMap, addMarker, fitBounds, useOSMTiles };
