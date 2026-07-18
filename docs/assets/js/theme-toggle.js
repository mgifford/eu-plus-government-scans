(function () {
  "use strict";

  var storageKey = "eu-gov-scans-theme";
  var root = document.documentElement;
  var mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  var allowedModes = ["system", "light", "dark"];

  function titleCase(value) {
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function getStoredMode() {
    try {
      var value = localStorage.getItem(storageKey);
      if (allowedModes.indexOf(value) !== -1) {
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

  // Popover control: single trigger + System/Light/Dark radio panel,
  // as rendered by _includes/header.html.
  var trigger = document.getElementById("theme-trigger");
  var triggerLabel = document.getElementById("theme-trigger-label");
  var panel = document.getElementById("theme-panel");
  var status = document.getElementById("theme-status");
  var radios = panel
    ? [].slice.call(panel.querySelectorAll('input[name="theme"]'))
    : [];

  // Legacy single-button control, still used by the standalone network.html page.
  var legacyButton = document.querySelector("[data-theme-toggle]");

  var selectedMode = "system";

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

  function updatePopoverInterface(announce) {
    if (!trigger) {
      return;
    }

    for (var i = 0; i < radios.length; i++) {
      radios[i].checked = radios[i].value === selectedMode;
    }

    if (triggerLabel) {
      triggerLabel.textContent =
        "Theme: " + titleCase(selectedMode) + ". Choose colour theme.";
    }

    if (status && announce) {
      status.textContent =
        "Selected theme: " +
        titleCase(selectedMode) +
        ". Effective theme: " +
        titleCase(resolveTheme(selectedMode)) +
        ".";
    }
  }

  function applyMode(mode, announce) {
    var theme = resolveTheme(mode);
    root.setAttribute("data-theme-mode", mode);
    root.setAttribute("data-theme", theme);
    updatePopoverInterface(announce);
    updateLegacyButton(theme);
  }

  function selectMode(mode, announce) {
    selectedMode = mode;
    saveMode(mode);
    applyMode(mode, announce);
  }

  function isPanelOpen() {
    return !!panel && !panel.hidden;
  }

  function openPanel() {
    panel.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
    var checked = radios.filter(function (radio) {
      return radio.checked;
    })[0];
    if (checked) {
      checked.focus();
    }
  }

  function closePanel(restoreFocus) {
    panel.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    if (restoreFocus) {
      trigger.focus();
    }
  }

  function syncWithSystem() {
    // Only follow the OS when the user has not pinned an explicit preference.
    if (getStoredMode() === "system") {
      applyMode("system", true);
    }
  }

  function init() {
    if (!trigger && !legacyButton) {
      return;
    }

    selectedMode = getStoredMode();
    applyMode(selectedMode, false);

    if (trigger && panel) {
      trigger.addEventListener("click", function () {
        if (isPanelOpen()) {
          closePanel(true);
        } else {
          openPanel();
        }
      });

      radios.forEach(function (radio) {
        radio.addEventListener("change", function (event) {
          selectMode(event.target.value, true);
        });
      });

      document.addEventListener("click", function (event) {
        if (
          isPanelOpen() &&
          !event.target.closest(".theme-control")
        ) {
          closePanel(false);
        }
      });

      document.addEventListener("focusin", function (event) {
        if (
          isPanelOpen() &&
          !event.target.closest(".theme-control")
        ) {
          closePanel(false);
        }
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && isPanelOpen()) {
          event.preventDefault();
          closePanel(true);
        }
      });
    }

    if (legacyButton) {
      legacyButton.addEventListener("click", function () {
        selectMode(
          resolveTheme(getStoredMode()) === "dark" ? "light" : "dark",
          true
        );
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
