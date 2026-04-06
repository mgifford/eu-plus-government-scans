(function () {
  "use strict";

  var DATA_FILE = "social-media-data.json";
  var PREVIEW_LIMIT = 5;
  var PLATFORM_KEYS = {
    Twitter: "twitter",
    X: "x",
    Bluesky: "bluesky",
    Mastodon: "mastodon",
    Facebook: "facebook",
    LinkedIn: "linkedin",
  };
  var dataPromise = null;
  var panelSequence = 0;

  function init() {
    var tables = findSocialTables();
    if (!tables.length) {
      return;
    }

    tables.forEach(makeSortable);
    loadDrilldownData().then(function (data) {
      if (!data || !data.platform_drilldowns) {
        return;
      }
      tables.forEach(function (table) {
        enhanceTable(table, data.platform_drilldowns);
      });
    });

    document.addEventListener("click", handleDocumentClick);
    document.addEventListener("keydown", handleDocumentKeydown);
  }

  function loadDrilldownData() {
    if (!dataPromise) {
      dataPromise = fetch(new URL(DATA_FILE, window.location.href).href, {
        headers: { Accept: "application/json" },
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Unable to load drilldown data");
          }
          return response.json();
        })
        .catch(function () {
          return null;
        });
    }
    return dataPromise;
  }

  function findSocialTables() {
    return Array.from(document.querySelectorAll("table")).filter(function (table) {
      var headers = getHeaderLabels(table);
      if (headers.indexOf("Country") === -1 || headers.indexOf("Scan Period") === -1) {
        return false;
      }
      return Object.keys(PLATFORM_KEYS).some(function (label) {
        return headers.indexOf(label) !== -1;
      });
    });
  }

  function getHeaderLabels(table) {
    return Array.from(table.querySelectorAll("thead th")).map(function (cell) {
      return cell.textContent.trim();
    });
  }

  function makeSortable(table) {
    if (table.dataset.sortableReady === "true") {
      return;
    }
    table.dataset.sortableReady = "true";
    table.classList.add("sm-sortable");

    var headers = Array.from(table.querySelectorAll("thead th"));
    headers.forEach(function (header, columnIndex) {
      header.setAttribute("aria-sort", "none");
      header.setAttribute("tabindex", "0");

      function sortHandler(event) {
        if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
          return;
        }
        if (event.type === "keydown") {
          event.preventDefault();
        }

        var ascending = header.getAttribute("aria-sort") !== "ascending";
        headers.forEach(function (cell) {
          cell.setAttribute("aria-sort", "none");
        });
        header.setAttribute("aria-sort", ascending ? "ascending" : "descending");
        sortTable(table, columnIndex, ascending);
      }

      header.addEventListener("click", sortHandler);
      header.addEventListener("keydown", sortHandler);
    });
  }

  function sortTable(table, columnIndex, ascending) {
    var tbody = table.querySelector("tbody");
    if (!tbody) {
      return;
    }

    var rows = Array.from(tbody.querySelectorAll("tr"));
    var totalRow = null;
    if (rows.length) {
      var lastRow = rows[rows.length - 1];
      var firstCell = lastRow.querySelector("td");
      if (firstCell && firstCell.textContent.indexOf("Total") !== -1) {
        totalRow = rows.pop();
      }
    }

    rows.sort(function (left, right) {
      var leftValue = getSortableCellValue(left, columnIndex);
      var rightValue = getSortableCellValue(right, columnIndex);

      if (leftValue === null) {
        return ascending ? 1 : -1;
      }
      if (rightValue === null) {
        return ascending ? -1 : 1;
      }
      if (typeof leftValue === "number" && typeof rightValue === "number") {
        return ascending ? leftValue - rightValue : rightValue - leftValue;
      }
      return ascending
        ? String(leftValue).localeCompare(String(rightValue))
        : String(rightValue).localeCompare(String(leftValue));
    });

    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
    if (totalRow) {
      tbody.appendChild(totalRow);
    }
  }

  function getSortableCellValue(row, columnIndex) {
    var cell = row.querySelectorAll("td")[columnIndex];
    if (!cell) {
      return null;
    }
    if (cell.dataset.sortVal !== undefined) {
      return parseFloat(cell.dataset.sortVal);
    }

    var text = cell.textContent.trim();
    if (!text || text === "—") {
      return null;
    }
    if (text.slice(-1) === "%") {
      return parseFloat(text);
    }

    var numberValue = parseInt(text.replace(/,/g, ""), 10);
    return isNaN(numberValue) ? text.toLowerCase() : numberValue;
  }

  function enhanceTable(table, drilldowns) {
    if (table.dataset.drilldownReady === "true") {
      return;
    }
    table.dataset.drilldownReady = "true";

    var headers = getHeaderLabels(table);
    var countryColumn = headers.indexOf("Country");
    var platformColumns = [];
    headers.forEach(function (label, index) {
      if (PLATFORM_KEYS[label]) {
        platformColumns.push({ index: index, label: label, key: PLATFORM_KEYS[label] });
      }
    });

    table.querySelectorAll("tbody tr").forEach(function (row) {
      var cells = row.querySelectorAll("td");
      if (!cells.length || !cells[countryColumn]) {
        return;
      }

      var country = cells[countryColumn].textContent.trim();
      if (country.indexOf("Total") !== -1) {
        return;
      }

      platformColumns.forEach(function (column) {
        var cell = cells[column.index];
        if (!cell) {
          return;
        }

        var rawValue = cell.textContent.replace(/,/g, "").trim();
        var count = parseInt(rawValue, 10);
        if (isNaN(count) || count <= 0) {
          return;
        }

        var platformRecords = (
          drilldowns[country] &&
          drilldowns[country][column.key]
        ) || [];
        if (!platformRecords.length) {
          return;
        }

        cell.dataset.sortVal = String(count);
        cell.textContent = "";
        cell.appendChild(
          buildDrilldownControl(country, column.label, count, platformRecords)
        );
      });
    });
  }

  function buildDrilldownControl(country, platformLabel, count, records) {
    var wrapper = document.createElement("span");
    wrapper.className = "table-drilldown";

    var trigger = document.createElement("button");
    trigger.className = "table-drilldown__trigger";
    trigger.type = "button";
    trigger.textContent = count.toLocaleString();
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("title", "Preview " + platformLabel + " pages for " + country);

    var panel = document.createElement("div");
    panel.className = "table-drilldown__panel";
    panel.hidden = true;
    panel.id = "table-drilldown-panel-" + (++panelSequence);
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", platformLabel + " pages for " + country);
    trigger.setAttribute("aria-controls", panel.id);

    panel.appendChild(buildPanelTitle(country, platformLabel, count));
    panel.appendChild(buildPanelDescription(country, platformLabel, count, records.length));
    panel.appendChild(buildPreviewList(records));
    panel.appendChild(buildPreviewSummary(count, records.length));
    panel.appendChild(buildPanelHint());
    panel.appendChild(buildDownloadButton(country, platformLabel, records));

    wrapper.appendChild(trigger);
    wrapper.appendChild(panel);

    wrapper.addEventListener("mouseenter", function () {
      openPanel(wrapper, false);
    });
    wrapper.addEventListener("mouseleave", function (event) {
      closePanelIfIdle(wrapper, event);
    });
    wrapper.addEventListener("focusin", function () {
      openPanel(wrapper, false);
    });
    wrapper.addEventListener("focusout", function (event) {
      closePanelIfIdle(wrapper, event);
    });
    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      togglePinned(wrapper);
    });

    return wrapper;
  }

  function buildPanelTitle(country, platformLabel, count) {
    var title = document.createElement("p");
    title.className = "table-drilldown__title";
    title.textContent = platformLabel + ": " + count.toLocaleString() + " pages in " + country;
    return title;
  }

  function buildPanelDescription(country, platformLabel, count, availableCount) {
    var text = document.createElement("p");
    text.className = "table-drilldown__description";
    text.textContent =
      availableCount.toLocaleString() +
      " scanned pages in " +
      country +
      " had at least one " +
      platformLabel +
      " link.";
    if (count !== availableCount) {
      text.textContent += " Preview and CSV use the currently available drilldown records.";
    }
    return text;
  }

  function buildPreviewList(records) {
    var list = document.createElement("ul");
    list.className = "table-drilldown__list";

    records.slice(0, PREVIEW_LIMIT).forEach(function (record) {
      var item = document.createElement("li");
      var link = document.createElement("a");
      link.href = record.page_url;
      link.textContent = record.page_url;
      link.rel = "noopener noreferrer";
      item.appendChild(link);

      if (record.detected_links && record.detected_links.length) {
        var meta = document.createElement("span");
        meta.className = "table-drilldown__meta";
        meta.textContent = "Detected: " + record.detected_links[0];
        item.appendChild(meta);
      }

      list.appendChild(item);
    });

    return list;
  }

  function buildPreviewSummary(count, availableCount) {
    var summary = document.createElement("p");
    summary.className = "table-drilldown__summary";
    if (availableCount > PREVIEW_LIMIT) {
      summary.textContent =
        "Showing the first " +
        PREVIEW_LIMIT +
        " of " +
        availableCount.toLocaleString() +
        " matching pages.";
    } else {
      summary.textContent =
        "Showing all " +
        availableCount.toLocaleString() +
        " matching pages in the preview.";
    }
    if (count > availableCount) {
      summary.textContent += " The table count is higher than the current downloadable subset.";
    }
    return summary;
  }

  function buildPanelHint() {
    var hint = document.createElement("p");
    hint.className = "table-drilldown__hint";
    hint.textContent =
      "Hover or focus previews this panel. Activate the number to keep it open and download the full CSV.";
    return hint;
  }

  function buildDownloadButton(country, platformLabel, records) {
    var button = document.createElement("button");
    button.className = "table-drilldown__download";
    button.type = "button";
    button.textContent = "Download CSV";
    button.addEventListener("click", function () {
      downloadCsv(country, platformLabel, records);
    });
    return button;
  }

  function togglePinned(wrapper) {
    var pinned = wrapper.dataset.pinned === "true";
    if (pinned) {
      wrapper.dataset.pinned = "false";
      closePanel(wrapper);
      return;
    }
    closeAllPanels(wrapper);
    wrapper.dataset.pinned = "true";
    openPanel(wrapper, true);
  }

  function openPanel(wrapper, preservePinned) {
    var trigger = wrapper.querySelector(".table-drilldown__trigger");
    var panel = wrapper.querySelector(".table-drilldown__panel");
    if (!trigger || !panel) {
      return;
    }
    if (!preservePinned && wrapper.dataset.pinned !== "true") {
      wrapper.dataset.pinned = "false";
    }
    wrapper.classList.add("is-open");
    panel.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
  }

  function closePanel(wrapper) {
    var trigger = wrapper.querySelector(".table-drilldown__trigger");
    var panel = wrapper.querySelector(".table-drilldown__panel");
    if (!trigger || !panel) {
      return;
    }
    wrapper.classList.remove("is-open");
    panel.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
  }

  function closePanelIfIdle(wrapper, event) {
    var relatedTarget = event.relatedTarget;
    if (relatedTarget && wrapper.contains(relatedTarget)) {
      return;
    }
    if (wrapper.dataset.pinned === "true") {
      return;
    }
    closePanel(wrapper);
  }

  function closeAllPanels(exceptWrapper) {
    document.querySelectorAll(".table-drilldown").forEach(function (wrapper) {
      if (wrapper === exceptWrapper) {
        return;
      }
      wrapper.dataset.pinned = "false";
      closePanel(wrapper);
    });
  }

  function handleDocumentClick(event) {
    var target = event.target;
    if (target.closest(".table-drilldown")) {
      return;
    }
    closeAllPanels(null);
  }

  function handleDocumentKeydown(event) {
    if (event.key !== "Escape") {
      return;
    }
    closeAllPanels(null);
  }

  function downloadCsv(country, platformLabel, records) {
    var lines = [
      ["country", "platform", "page_url", "detected_links"].join(","),
    ];
    records.forEach(function (record) {
      lines.push([
        csvEscape(country),
        csvEscape(platformLabel),
        csvEscape(record.page_url),
        csvEscape((record.detected_links || []).join(" | ")),
      ].join(","));
    });

    var blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    var slug = (country + "-" + platformLabel)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
    link.href = url;
    link.download = slug + "-pages.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function csvEscape(value) {
    return '"' + String(value || "").replace(/"/g, '""') + '"';
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
