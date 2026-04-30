/* Trips and wishlist management */
(async function () {
  if (!document.body.classList.contains("page-trip") && !document.body.classList.contains("page-wishlist")) return;

  const tripsGrid = document.getElementById("trips-grid");
  const wishlistGrid = document.getElementById("wishlist-grid");

  function gradient(seed) {
    let h = 0; for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
    return `linear-gradient(135deg, hsl(${h%360},45%,72%), hsl(${(h+50)%360},45%,82%))`;
  }

  async function loadTrips() {
    if (!tripsGrid) return;
    if (window.skeleton) window.skeleton.inject(tripsGrid, "card", 3);
    const data = await window.tryApi(() => window.api.get("/trips"));
    const items = (data && (data.results || data.items || data)) || [];
    if (!items.length) {
      tripsGrid.innerHTML = `<div class="empty-state"><div class="glyph">🧳</div><p>No saved trips yet.</p><a class="btn btn-primary" href="/itinerary" style="margin-top:16px;">Plan your first trip</a></div>`;
      return;
    }
    tripsGrid.innerHTML = items.map((t) => {
      const slug = (t.destination || "trip").toLowerCase().replace(/[^a-z]/g, "-");
      const bg = `url('https://picsum.photos/seed/${slug}/640/360')`;
      return `
        <a class="trip-card" href="/trip?id=${encodeURIComponent(t.id)}">
          <div class="cover" style="background-image:${bg};background-size:cover;background-position:center;${!t.destination ? `background:${gradient(slug)};` : ''}"></div>
          <div class="body">
            <div class="title">${t.destination || 'Untitled trip'}</div>
            <div class="dates">${t.start_date || ''} — ${t.end_date || ''}</div>
          </div>
        </a>
      `;
    }).join("");
  }

  async function loadWishlist() {
    if (!wishlistGrid) return;
    if (window.skeleton) window.skeleton.inject(wishlistGrid, "card", 4);
    const data = await window.tryApi(() => window.api.get("/wishlist"));
    const items = (data && (data.results || data.items || data)) || [];
    if (!items.length) {
      wishlistGrid.innerHTML = `<div class="empty-state"><div class="glyph">♡</div><p>Your wishlist is empty.</p></div>`;
      return;
    }
    wishlistGrid.innerHTML = items.map((w) => `
      <div class="wishlist-item">
        <button class="remove" data-remove-id="${w.id}" aria-label="Remove">×</button>
        <span class="name">${w.name || w.title}</span>
        <span class="kind">${w.kind || w.type || ''}</span>
      </div>
    `).join("");

    wishlistGrid.querySelectorAll("[data-remove-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.removeId;
        const ok = await window.tryApi(() => window.api.del(`/wishlist/${id}`));
        if (ok !== null) {
          btn.closest(".wishlist-item").remove();
          window.toast?.success("Removed from wishlist.");
        }
      });
    });
  }

  loadTrips();
  loadWishlist();
})();
