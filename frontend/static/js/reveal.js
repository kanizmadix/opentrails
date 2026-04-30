/* IntersectionObserver-driven scroll fade-up */
(function () {
  if (!("IntersectionObserver" in window)) {
    document.querySelectorAll(".reveal").forEach((el) => el.dataset.visible = "true");
    return;
  }
  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.dataset.visible = "true";
        io.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

  const observe = (root = document) =>
    root.querySelectorAll(".reveal:not([data-visible])").forEach((el) => io.observe(el));

  observe();

  // Re-scan after dynamic content loads
  window.revealScan = observe;
})();
