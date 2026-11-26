/* Attendance form — live totals and inline validation */

(function () {
  "use strict";

  const NON_ATTENDANCE = ["total_locations", "total_pastors", "workers_brothers", "workers_sisters", "total_online"];

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("attendance-form");
    if (!form) return;

    const numberInputs = Array.from(form.querySelectorAll('input[type="number"]'));
    const requiredFields = Array.from(form.querySelectorAll("[required]"));
    const totalInPerson = document.getElementById("total-inperson");
    const totalOnline = document.getElementById("total-online");
    const totalGrand = document.getElementById("total-grand");
    const workersTotal = document.getElementById("workers-total");
    const submitButton = document.getElementById("submit-btn");
    const progressCount = document.getElementById("progress-count");
    const progressFill = document.getElementById("progress-fill");
    const bumpTimers = new WeakMap();

    function numericValue(input) {
      const parsed = parseInt(input.value, 10);
      return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
    }

    function setTotal(element, value) {
      if (!element) return;
      if (element.textContent === String(value)) return;
      element.textContent = String(value);
      element.classList.add("bump");
      const previous = bumpTimers.get(element);
      if (previous) clearTimeout(previous);
      bumpTimers.set(element, setTimeout(function () {
        element.classList.remove("bump");
      }, 180));
    }

    function isValidValue(input) {
      const value = (input.value || "").trim();
      if (!value) return false;
      if (input.type === "number") {
        const parsed = Number(value);
        return Number.isInteger(parsed) && parsed >= 0;
      }
      return true;
    }

    function updateProgress() {
      const filled = requiredFields.filter(isValidValue).length;
      if (progressCount) progressCount.textContent = filled + " of " + requiredFields.length;
      if (progressFill) progressFill.style.width = (filled / requiredFields.length) * 100 + "%";
    }

    function updateTotals() {
      let inPerson = 0;

      numberInputs.forEach(function (input) {
        if (NON_ATTENDANCE.indexOf(input.name) !== -1) return;
        inPerson += numericValue(input);
      });

      const online = numericValue(form.elements["total_online"]);
      setTotal(totalInPerson, inPerson);
      setTotal(totalOnline, online);
      setTotal(totalGrand, inPerson + online);
      setTotal(workersTotal, numericValue(form.elements["workers_brothers"]) + numericValue(form.elements["workers_sisters"]));
      updateProgress();
    }

    function setError(input, message) {
      const field = input.closest(".field");
      if (!field) return;
      const existing = field.querySelector(".field-error");
      if (existing) existing.remove();

      input.classList.toggle("is-invalid", Boolean(message));
      input.setAttribute("aria-invalid", message ? "true" : "false");
      input.classList.toggle("is-valid", !message && isValidValue(input));

      if (message) {
        const paragraph = document.createElement("p");
        paragraph.className = "field-error";
        paragraph.textContent = message;
        field.appendChild(paragraph);
      }
    }

    numberInputs.forEach(function (input) {
      input.addEventListener("input", function () {
        updateTotals();
        if (input.classList.contains("is-invalid")) setError(input, "");
        else input.classList.toggle("is-valid", isValidValue(input));
      });
      input.addEventListener("blur", function () {
        const parsed = parseInt(input.value, 10);
        if (input.value !== "" && (!Number.isFinite(parsed) || parsed < 0)) input.value = "0";
        updateTotals();
      });
    });

    const country = form.elements["country"];
    if (country) country.addEventListener("change", function () {
      if (country.classList.contains("is-invalid")) setError(country, "");
      else country.classList.toggle("is-valid", isValidValue(country));
      updateProgress();
    });

    updateTotals();

    form.addEventListener("submit", function (event) {
      let firstInvalid = null;

      requiredFields.forEach(function (input) {
        const value = (input.value || "").trim();
        let message = "";

        if (!value) {
          message = "This field is required.";
        } else if (input.type === "number" && (!Number.isInteger(Number(value)) || Number(value) < 0)) {
          message = "Enter a whole number of 0 or more.";
        }

        setError(input, message);
        if (message && !firstInvalid) firstInvalid = input;
      });

      if (firstInvalid) {
        event.preventDefault();
        firstInvalid.focus();
        firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }

      if (submitButton) {
        submitButton.classList.add("is-loading");
        submitButton.disabled = true;
      }
    });
  });
})();
