(function () {
  "use strict";

  var storageKey = "eu-gov-scans-theme";
  var root = document.documentElement;
  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function getStoredTheme() {
    try {
      var stored = localStorage.getItem(storageKey);
      if (stored === "light" || stored === "dark") {
        return stored;
      }
    } catch (error) {
      return null;
    }
    return null;
  }

  function getEffectiveTheme() {
    var explicitTheme = root.getAttribute("data-theme");
    if (explicitTheme === "light" || explicitTheme === "dark") {
      return explicitTheme;
    }
    return mediaQuery.matches ? "dark" : "light";
  }

  function persistTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      // Ignore storage failures and still apply the theme for this session.
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    persistTheme(theme);
    updateToggle(theme);
  }

  function updateToggle(theme) {
    var button = document.querySelector("[data-theme-toggle]");
    if (!button) {
      return;
    }

    var nextTheme = theme === "dark" ? "light" : "dark";
    var actionLabel = "Switch to " + nextTheme + " mode";

    button.setAttribute("aria-pressed", String(theme === "dark"));
    button.setAttribute("aria-label", actionLabel);
    button.setAttribute("title", actionLabel);
    button.dataset.theme = theme;

    var labelNode = button.querySelector("[data-theme-toggle-text]");
    if (labelNode) {
      labelNode.textContent = actionLabel;
    }
  }

  function handleToggleClick() {
    var currentTheme = getEffectiveTheme();
    applyTheme(currentTheme === "dark" ? "light" : "dark");
  }

  function handleSystemThemeChange() {
    if (getStoredTheme()) {
      return;
    }
    updateToggle(getEffectiveTheme());
  }

  function initializeToggle() {
    var button = document.querySelector("[data-theme-toggle]");
    if (!button) {
      return;
    }

    updateToggle(getEffectiveTheme());
    button.addEventListener("click", handleToggleClick);

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", handleSystemThemeChange);
    } else if (typeof mediaQuery.addListener === "function") {
      mediaQuery.addListener(handleSystemThemeChange);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeToggle);
    return;
  }

  initializeToggle();
})();
