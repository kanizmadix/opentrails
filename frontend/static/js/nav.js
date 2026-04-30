/* Sticky-blur nav, mobile drawer, active link */
(function () {
  const nav = document.querySelector(".nav");
  if (!nav) return;

  // Scroll state
  const onScroll = () => {
    nav.dataset.scrolled = window.scrollY > 8 ? "true" : "false";
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Active link
  const links = nav.querySelectorAll(".nav-link[href]");
  const path = location.pathname.replace(/\/$/, "") || "/";
  links.forEach((a) => {
    const href = a.getAttribute("href").replace(/\/$/, "") || "/";
    if (href === path) a.setAttribute("aria-current", "page");
  });

  // Drawer
  const drawer = document.querySelector(".nav-drawer");
  const burger = nav.querySelector(".nav-burger");
  if (burger && drawer) {
    burger.addEventListener("click", () => {
      const open = drawer.dataset.open === "true";
      drawer.dataset.open = open ? "false" : "true";
      burger.setAttribute("aria-expanded", open ? "false" : "true");
    });
    drawer.addEventListener("click", (e) => {
      if (e.target.closest(".nav-link")) {
        drawer.dataset.open = "false";
        burger.setAttribute("aria-expanded", "false");
      }
    });
  }
})();
