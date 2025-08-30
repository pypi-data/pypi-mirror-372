document.addEventListener("DOMContentLoaded", function () {
  function initFormset(fs) {
    const viewAllUrl = fs.dataset.viewAllUrl;
    const viewAllCount = fs.dataset.viewAllCount || "0";
    const iconType = (fs.dataset.viewAllIcon || "view").toLowerCase();
    const iconClass = iconType === "change" || iconType === "pencil" ? "changelink" : "viewlink";

    if (!viewAllUrl) {
      return; // No destination URL (likely on add page before parent is saved)
    }

    // Only inject the link if count exceeds the maximum allowed to display (when provided)
    const maxAttr = fs.dataset.maximumNumberOfRelatedRowsToDisplay;
    if (maxAttr !== undefined && maxAttr !== null && String(maxAttr).trim() !== "") {
      const maxDisplay = parseInt(maxAttr, 10);
      const totalCount = parseInt(viewAllCount, 10) || 0;
      if (Number.isFinite(maxDisplay) && totalCount <= maxDisplay) {
        return; // Do not inject if not exceeding the maximum shown inline
      }
    }

    function insertIfReady() {
      const addRow = fs.querySelector("tr.add-row");
      if (!addRow) return false; // Wait until Django injects the add-row

      if (fs.querySelector("tr.view-all-row")) {
        return true; // Already added as separate row
      }

      const firstCell = addRow.querySelector("td");
      const colspanValue = firstCell && firstCell.getAttribute("colspan");
      const headerCount = fs.querySelectorAll("table thead th").length || 1;

      const viewAllRow = document.createElement("tr");
      viewAllRow.classList.add("add-row", "view-all-row");

      const td = document.createElement("td");
      td.setAttribute("colspan", colspanValue || String(headerCount));
      const link = document.createElement("a");
      link.className = "view-all-link";
      // Add Django admin icon class
      link.classList.add(iconClass);
      link.href = viewAllUrl;
      link.textContent = `View all (${viewAllCount})`;
      td.appendChild(link);

      viewAllRow.appendChild(td);
      addRow.insertAdjacentElement("afterend", viewAllRow);
      return true; // Inserted
    }

    if (insertIfReady()) return;

    // Observe until Django's inlines JS injects the add-row
    const targetNode = fs.querySelector("table > tbody") || fs;
    const observer = new MutationObserver(function () {
      if (insertIfReady()) {
        observer.disconnect();
      }
    });
    observer.observe(targetNode, { childList: true, subtree: true });

    // Safety: stop observing after a short delay
    setTimeout(function () { observer.disconnect(); }, 5000);
  }

  function initAll() {
    document.querySelectorAll(".js-inline-admin-formset").forEach(initFormset);
  }

  // Run after DOM is ready and again on full load for safety
  initAll();
  window.addEventListener("load", initAll, { once: true });
});
