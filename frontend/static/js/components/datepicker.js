/* Tiny range date helper: links two native date inputs so end >= start.
   <input type="date" data-range-start="trip"> <input type="date" data-range-end="trip">
*/
(function () {
  function todayISO() { return new Date().toISOString().slice(0, 10); }
  function addDays(iso, n) {
    const d = new Date(iso);
    d.setDate(d.getDate() + n);
    return d.toISOString().slice(0, 10);
  }

  function wire(group) {
    const start = document.querySelector(`[data-range-start="${group}"]`);
    const end = document.querySelector(`[data-range-end="${group}"]`);
    if (!start || !end) return;

    const today = todayISO();
    if (!start.min) start.min = today;
    if (!end.min) end.min = start.value || today;

    start.addEventListener("change", () => {
      end.min = start.value || today;
      if (end.value && end.value < start.value) end.value = addDays(start.value, 1);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const groups = new Set();
    document.querySelectorAll("[data-range-start]").forEach((el) => groups.add(el.dataset.rangeStart));
    groups.forEach(wire);
  });

  window.datepicker = { wire, todayISO, addDays };
})();
