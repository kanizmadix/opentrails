/* Horizontal scroll-snap carousel with keyboard arrow nav.
   Markup: <div data-carousel> ... cards ... </div>
*/
(function () {
  function wire(root) {
    if (root.dataset.carouselBound) return;
    root.dataset.carouselBound = "true";
    root.style.outline = "none";
    root.tabIndex = 0;

    root.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        root.scrollBy({ left: root.clientWidth * 0.8, behavior: "smooth" });
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        root.scrollBy({ left: -root.clientWidth * 0.8, behavior: "smooth" });
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-carousel]").forEach(wire);
  });

  window.carousel = { wire };
})();
