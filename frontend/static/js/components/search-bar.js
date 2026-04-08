/* Global search bar with Nominatim autocomplete. */
(function () {
  const NOMINATIM = "https://nominatim.openstreetmap.org/search";

  function debounce(fn, ms = 220) {
    let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  }

  async function geocode(q) {
    const url = `${NOMINATIM}?format=jsonv2&addressdetails=1&limit=6&q=${encodeURIComponent(q)}`;
    try {
      const res = await fetch(url, { headers: { "Accept": "application/json" } });
      if (!res.ok) return [];
      return await res.json();
    } catch (_) { return []; }
  }

  function renderItem(item) {
    const main = item.display_name.split(",").slice(0, 2).join(",").trim();
    const sub = item.display_name.split(",").slice(2).join(",").trim();
    return `
      <div class="autocomplete-item" role="option" data-lat="${item.lat}" data-lon="${item.lon}" data-name="${main.replace(/"/g, "&quot;")}">
        <span>${main}</span>
        ${sub ? `<span class="sub">${sub}</span>` : ""}
      </div>
    `;
  }

  function attach(input) {
    if (input.dataset.searchBarBound) return;
    input.dataset.searchBarBound = "true";
    const wrap = input.closest(".search-wrap") || input.parentElement;
    if (!wrap) return;
    wrap.style.position = wrap.style.position || "relative";

    const list = document.createElement("div");
    list.className = "autocomplete";
    list.hidden = true;
    list.setAttribute("role", "listbox");
    wrap.appendChild(list);

    const onInput = debounce(async () => {
      const q = input.value.trim();
      if (q.length < 2) { list.hidden = true; list.innerHTML = ""; return; }
      const results = await geocode(q);
      if (!results.length) { list.hidden = true; return; }
      list.innerHTML = results.map(renderItem).join("");
      list.hidden = false;
    }, 240);

    input.addEventListener("input", onInput);

    list.addEventListener("click", (e) => {
      const item = e.target.closest(".autocomplete-item");
      if (!item) return;
      input.value = item.dataset.name;
      input.dataset.lat = item.dataset.lat;
      input.dataset.lon = item.dataset.lon;
      list.hidden = true;
      input.dispatchEvent(new CustomEvent("place:selected", {
        detail: { name: item.dataset.name, lat: parseFloat(item.dataset.lat), lon: parseFloat(item.dataset.lon) },
        bubbles: true,
      }));
    });

    document.addEventListener("click", (e) => {
      if (!wrap.contains(e.target)) list.hidden = true;
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('input[data-search-bar]').forEach(attach);
  });

  window.searchBar = { attach };
})();
