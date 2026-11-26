/* Admin panel — delete confirmation dialog */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const dialog = document.getElementById("delete-dialog");
    const form = document.getElementById("delete-form");
    const message = document.getElementById("delete-message");
    const cancel = document.getElementById("cancel-delete");
    if (!dialog || !form || !cancel) return;

    document.querySelectorAll(".delete-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        form.action = button.dataset.action;
        message.textContent = "The report for " + button.dataset.country + " will be permanently removed.";
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
      });
    });

    cancel.addEventListener("click", function () {
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
    });
  });
})();
