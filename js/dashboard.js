/**
 * Public leaderboard page — fetches sanitized rows from the results worker.
 */
(function () {
  const bodyEl = document.getElementById("board-body");
  const metaEl = document.getElementById("board-meta");
  const scoringEl = document.getElementById("scoring-note");
  const tabs = document.querySelectorAll(".mode-tab");
  let mode = "full";

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

  function renderRows(rows) {
    bodyEl.innerHTML = "";
    if (!rows || !rows.length) {
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td colspan="10" class="board-empty">No published results yet for this mode. Complete a quest and claim a certificate with consent to appear here.</td>';
      bodyEl.appendChild(tr);
      return;
    }
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      if (row.rank <= 3) tr.className = "top-" + row.rank;
      tr.innerHTML =
        "<td class=\"num\">" +
        row.rank +
        "</td>" +
        "<td class=\"player\">" +
        escapeHtml(row.display_name) +
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
        "<td class=\"num\">" +
        row.cleared_levels +
        "/" +
        row.max_levels +
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

  async function loadBoard() {
    metaEl.textContent = "Loading…";
    bodyEl.innerHTML =
      '<tr><td colspan="10" class="board-empty">Loading rankings…</td></tr>';
    const site = await loadSite();
    const url = leaderboardUrl(site, mode);
    if (!url) {
      metaEl.textContent = "Leaderboard endpoint not configured.";
      bodyEl.innerHTML =
        '<tr><td colspan="10" class="board-empty">Set results.endpoint in config/site.json and redeploy the worker.</td></tr>';
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
        (mode === "test" ? "test mode" : "full quest") +
        " · updated " +
        fmtDate(data.generated_at);
      if (scoringEl) {
        scoringEl.textContent =
          "Score: " +
          (data.scoring ||
            "1000×(cleared/max) + 100×accuracy − 5×timeouts − median time penalty") +
          ". Best run per person.";
      }
      renderRows(data.rows || []);
    } catch (err) {
      console.error(err);
      metaEl.textContent = "Could not load leaderboard.";
      bodyEl.innerHTML =
        '<tr><td colspan="10" class="board-empty">Failed to reach the results server. Redeploy the worker with GET /leaderboard support, then refresh.</td></tr>';
    }
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      mode = btn.getAttribute("data-mode") === "test" ? "test" : "full";
      tabs.forEach((b) => b.classList.toggle("active", b === btn));
      loadBoard();
    });
  });

  loadBoard();
})();
