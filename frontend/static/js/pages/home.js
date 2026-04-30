/* Home page wiring */
(function () {
  if (!document.body.classList.contains("page-home")) return;

  const form = document.getElementById("home-search-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = form.querySelector("input[name='q']");
      const q = (input.value || "").trim();
      if (!q) { input.focus(); return; }
      window.location.href = `/search?q=${encodeURIComponent(q)}`;
    });
  }

  // Quick-chip presets
  document.querySelectorAll("[data-quick-search]").forEach((chip) => {
    chip.addEventListener("click", () => {
      window.location.href = `/search?q=${encodeURIComponent(chip.dataset.quickSearch)}`;
    });
  });

  // Spotlight: load suggested destinations
  const spotlight = document.getElementById("spotlight");
  if (spotlight && window.api) {
    const seed = ["Paris", "Tokyo", "Lisbon", "New York", "Bali", "Cape Town", "Reykjavík", "Kyoto"];
    spotlight.innerHTML = seed.map((name) => {
      const seedSlug = name.toLowerCase().replace(/[^a-z]/g, "-");
      const img = `https://picsum.photos/seed/${seedSlug}/640/480`;
      return `
        <a class="card-image card-hover" href="/destination?q=${encodeURIComponent(name)}">
          <div class="media" style="background-image:url('${img}');" role="img" aria-label="${name} skyline"></div>
          <div class="body">
            <span class="card-title">${name}</span>
            <span class="card-meta">Explore →</span>
          </div>
        </a>
      `;
    }).join("");
  }
})();
