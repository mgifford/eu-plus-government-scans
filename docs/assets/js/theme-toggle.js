(function () {
  "use strict";

  var storageKey = "eu-gov-scans-theme";
  var root = document.documentElement;
  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function getStoredMode() {
    try {
      var value = localStorage.getItem(storageKey);
      if (value === "light" || value === "dark") {
        return value;
      }
    } catch (error) {
      return "system";
    }
    return "system";
  }

  function saveMode(mode) {
    try {
      if (mode === "system") {
        localStorage.removeItem(storageKey);
      } else {
        localStorage.setItem(storageKey, mode);
      }
    } catch (error) {
      // Ignore storage failures and keep the active session usable.
    }
  }

  function resolveTheme(mode) {
    if (mode === "light" || mode === "dark") {
      return mode;
    }
    return mediaQuery.matches ? "dark" : "light";
  }

  // Three-button control: System / Light / Dark, as rendered by _includes/header.html.
  var modeButtons = document.querySelectorAll(".theme-mode-btn[data-theme-value]");

  // Legacy single-button control, still used by the standalone network.html page.
  var legacyButton = document.querySelector("[data-theme-toggle]");

  function updateModeButtons(mode) {
    for (var i = 0; i < modeButtons.length; i++) {
      var button = modeButtons[i];
      var selected = button.getAttribute("data-theme-value") === mode;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    }
  }

  function updateLegacyButton(theme) {
    if (!legacyButton) {
      return;
    }

    var icon = legacyButton.querySelector("[data-theme-toggle-icon]");
    var text = legacyButton.querySelector("[data-theme-toggle-text]");
    var label = "Switch to " + (theme === "dark" ? "light" : "dark") + " mode";

    if (icon) {
      icon.textContent = theme === "dark" ? "☀" : "☾";
    }

    legacyButton.dataset.theme = theme;
    legacyButton.setAttribute("aria-label", label);
    legacyButton.setAttribute("title", label);

    if (text) {
      text.textContent = label;
    }
  }

  function applyMode(mode) {
    var theme = resolveTheme(mode);
    root.setAttribute("data-theme-mode", mode);
    root.setAttribute("data-theme", theme);
    updateModeButtons(mode);
    updateLegacyButton(theme);
  }

  function selectMode(mode) {
    saveMode(mode);
    applyMode(mode);
  }

  function syncWithSystem() {
    // Only follow the OS when the user has not pinned an explicit preference.
    if (getStoredMode() === "system") {
      applyMode("system");
    }
  }

  function init() {
    if (!modeButtons.length && !legacyButton) {
      return;
    }

    applyMode(getStoredMode());

    for (var i = 0; i < modeButtons.length; i++) {
      modeButtons[i].addEventListener("click", function (event) {
        selectMode(event.currentTarget.getAttribute("data-theme-value"));
      });
    }

    if (legacyButton) {
      legacyButton.addEventListener("click", function () {
        selectMode(resolveTheme(getStoredMode()) === "dark" ? "light" : "dark");
      });
    }

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", syncWithSystem);
    } else if (typeof mediaQuery.addListener === "function") {
      mediaQuery.addListener(syncWithSystem);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
