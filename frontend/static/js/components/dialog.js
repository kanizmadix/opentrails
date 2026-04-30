/* Lightweight dialog open/close helper.
   Usage:
     <button data-dialog-open="my-modal">Open</button>
     <div class="dialog-backdrop" data-dialog-id="my-modal"></div>
     <div class="dialog" data-dialog-id="my-modal" role="dialog" aria-modal="true">
       <button data-dialog-close>×</button>
     </div>
*/
(function () {
  function setOpen(id, open) {
    document.querySelectorAll(`[data-dialog-id="${id}"]`).forEach((el) => {
      el.dataset.open = open ? "true" : "false";
    });
    document.body.style.overflow = open ? "hidden" : "";
    if (open) {
      const dlg = document.querySelector(`.dialog[data-dialog-id="${id}"]`);
      if (dlg) {
        const focusable = dlg.querySelector("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])");
        if (focusable) focusable.focus();
      }
    }
  }

  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-dialog-open]");
    if (opener) {
      e.preventDefault();
      setOpen(opener.dataset.dialogOpen, true);
      return;
    }
    const closer = e.target.closest("[data-dialog-close]");
    if (closer) {
      e.preventDefault();
      const dlg = closer.closest("[data-dialog-id]");
      if (dlg) setOpen(dlg.dataset.dialogId, false);
      return;
    }
    const backdrop = e.target.closest(".dialog-backdrop[data-dialog-id]");
    if (backdrop && e.target === backdrop) {
      setOpen(backdrop.dataset.dialogId, false);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll('.dialog[data-open="true"]').forEach((d) => setOpen(d.dataset.dialogId, false));
    }
  });

  window.dialog = { open: (id) => setOpen(id, true), close: (id) => setOpen(id, false) };
})();
