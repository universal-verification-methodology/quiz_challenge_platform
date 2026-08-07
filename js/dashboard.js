/**
 * Public leaderboard page — fetches sanitized rows from the results worker.
 */
(function () {
  const bodyEl = document.getElementById("board-body");
  const metaEl = document.getElementById("board-meta");
  const scoringEl = document.getElementById("scoring-note");
  const tableEl = document.getElementById("board-table");
  const tabs = document.querySelectorAll(".mode-tab");
  let mode = "full";
  let cachedRows = [];
  let sortKey = "score";
  let sortDir = "desc";

  function fmtDate(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch (_) {
      return String(iso).slice(0, 10);
    }
  }

  function fmtMs(ms) {
    if (window.QCBenchmark && QCBenchmark.fmtMs) return QCBenchmark.fmtMs(ms);
    const s = Math.round((ms || 0) / 1000);
    return s < 60 ? s + "s" : Math.floor(s / 60) + "m " + (s % 60) + "s";
  }

  async function loadSite() {
    try {
      const res = await fetch("config/site.json?v=6", { cache: "no-store" });
      if (!res.ok) return {};
      return res.json();
    } catch (_) {
      return {};
    }
  }

  function leaderboardUrl(site, wantMode) {
    const base =
      (site.results && site.results.leaderboard_endpoint) ||
      (site.results && site.results.endpoint) ||
      "";
    if (!base) return "";
    const u = new URL(base.replace(/\/+$/, "") + "/leaderboard");
    u.searchParams.set("mode", wantMode);
    return u.toString();
  }

  /** Always three slots: easy / medium / hard (never cleared/max). */
  function formatClearedEMH(row) {
    const counts = row && row.cleared_by_difficulty;
    if (Array.isArray(counts) && counts.length) {
      return [0, 1, 2].map((i) => Number(counts[i]) || 0).join("/");
    }
    const label = row && row.cleared_label != null ? String(row.cleared_label) : "";
    if (label.split("/").length === 3) return label;
    return "—/—/—";
  }

  function sortValue(row, key) {
    if (key === "cleared_levels") {
      const cleared = Number(row.cleared_levels) || 0;
      const max = Number(row.max_levels) || 0;
      return cleared + cleared / Math.max(max, 1);
    }
    if (key === "display_name") {
      return String(row.display_name || "").toLowerCase();
    }
    if (key === "module_title") {
      return String(row.module_title || "").toLowerCase();
    }
    if (key === "completed_at") {
      const t = Date.parse(row.completed_at || "");
      return Number.isFinite(t) ? t : 0;
    }
    const n = Number(row[key]);
    return Number.isFinite(n) ? n : 0;
  }

  function sortedRows(rows) {
    const list = rows.slice();
    const dir = sortDir === "asc" ? 1 : -1;
    list.sort((a, b) => {
      const av = sortValue(a, sortKey);
      const bv = sortValue(b, sortKey);
      if (typeof av === "string" || typeof bv === "string") {
        const cmp = String(av).localeCompare(String(bv), undefined, {
          sensitivity: "base",
          numeric: true,
        });
        if (cmp !== 0) return cmp * dir;
      } else if (av !== bv) {
        return (av < bv ? -1 : 1) * dir;
      }
      // Stable-ish fallback: keep official rank order.
      return (Number(a.rank) || 0) - (Number(b.rank) || 0);
    });
    return list;
  }

  function updateSortHeaders() {
    if (!tableEl) return;
    tableEl.querySelectorAll("th[data-sort]").forEach((th) => {
      const key = th.getAttribute("data-sort");
      if (key === sortKey) {
        th.setAttribute("aria-sort", sortDir === "asc" ? "ascending" : "descending");
      } else {
        th.setAttribute("aria-sort", "none");
      }
    });
  }

  function renderRows(rows) {
    bodyEl.innerHTML = "";
    if (!rows || !rows.length) {
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td colspan="11" class="board-empty">No published results yet for this mode. Complete a quest and claim a certificate with consent to appear here.</td>';
      bodyEl.appendChild(tr);
      return;
    }
    const ordered = sortedRows(rows);
    ordered.forEach((row) => {
      const tr = document.createElement("tr");
      if (row.rank <= 3) tr.className = "top-" + row.rank;
      tr.innerHTML =
        "<td class=\"num\">" +
        row.rank +
        "</td>" +
        "<td class=\"player\">" +
        escapeHtml(row.display_name) +
        "</td>" +
        "<td class=\"module\">" +
        escapeHtml(row.module_title || (mode === "test" ? "—" : "All modules")) +
        "</td>" +
        "<td class=\"num score\">" +
        row.score +
        "</td>" +
        "<td class=\"num\">" +
        row.accuracy_pct +
        "%</td>" +
        "<td class=\"num\">" +
        row.total_attempts +
        "</td>" +
        "<td class=\"num\" title=\"easy / medium / hard levels cleared\">" +
        escapeHtml(formatClearedEMH(row)) +
        "</td>" +
        "<td class=\"num\">" +
        fmtMs(row.median_ms) +
        "</td>" +
        "<td class=\"num\">" +
        row.timeouts +
        "</td>" +
        "<td class=\"num\">Top " +
        (row.top_pct != null ? row.top_pct : Math.max(1, Math.ceil((100 * row.rank) / rows.length))) +
        "%</td>" +
        "<td>" +
        escapeHtml(fmtDate(row.completed_at)) +
        "</td>";
      bodyEl.appendChild(tr);
    });
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function applySort(key, defaultDir) {
    if (sortKey === key) {
      sortDir = sortDir === "asc" ? "desc" : "asc";
    } else {
      sortKey = key;
      sortDir = defaultDir === "asc" ? "asc" : "desc";
    }
    updateSortHeaders();
    renderRows(cachedRows);
  }

  async function loadBoard() {
    metaEl.textContent = "Loading…";
    bodyEl.innerHTML =
      '<tr><td colspan="11" class="board-empty">Loading rankings…</td></tr>';
    const site = await loadSite();
    const url = leaderboardUrl(site, mode);
    if (!url) {
      metaEl.textContent = "Leaderboard endpoint not configured.";
      bodyEl.innerHTML =
        '<tr><td colspan="11" class="board-empty">Set results.endpoint in config/site.json and redeploy the worker.</td></tr>';
      return;
    }
    try {
      const res = await fetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error((data && data.error) || "HTTP " + res.status);
      }
      metaEl.textContent =
        data.count +
        " player" +
        (data.count === 1 ? "" : "s") +
        " · " +
        (mode === "test" ? "short quest" : "full quest") +
        " · updated " +
        fmtDate(data.generated_at);
      if (scoringEl) {
        scoringEl.textContent =
          "Score: " +
          (data.scoring ||
            "1000×(cleared/max) + 100×accuracy − 5×timeouts − median time penalty") +
          ". Best Full Quest run per person; Short Quest keeps best run per person per module. Cleared is easy/medium/hard.";
      }
      cachedRows = data.rows || [];
      updateSortHeaders();
      renderRows(cachedRows);
    } catch (err) {
      console.error(err);
      cachedRows = [];
      metaEl.textContent = "Could not load leaderboard.";
      bodyEl.innerHTML =
        '<tr><td colspan="11" class="board-empty">Failed to reach the results server. Redeploy the worker with GET /leaderboard support, then refresh.</td></tr>';
    }
  }

  if (tableEl) {
    tableEl.querySelectorAll("th[data-sort]").forEach((th) => {
      const btn = th.querySelector(".sort-btn");
      if (!btn) return;
      btn.addEventListener("click", () => {
        applySort(
          th.getAttribute("data-sort"),
          th.getAttribute("data-default-dir") || "desc"
        );
      });
    });
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      mode = btn.getAttribute("data-mode") === "test" ? "test" : "full";
      tabs.forEach((b) => b.classList.toggle("active", b === btn));
      // Reset to official ranking when switching boards.
      sortKey = "score";
      sortDir = "desc";
      loadBoard();
    });
  });

  updateSortHeaders();
  loadBoard();
})();
