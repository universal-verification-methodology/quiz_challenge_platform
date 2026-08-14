/**
 * Post-quest analytical report — dashboard layout (summary cards, modules, attempt path).
 */
(function (global) {
  function fmtMs(ms) {
    const s = Math.round((ms || 0) / 1000);
    if (s < 60) return s + "s";
    const m = Math.floor(s / 60);
    const r = s % 60;
    return m + "m " + r + "s";
  }

  function pct(n) {
    return Math.round((n || 0) * 100) + "%";
  }

  function escape(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function fmtCompleted(iso) {
    try {
      return new Date(iso || Date.now()).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    } catch (_) {
      return String(iso || "");
    }
  }

  function countTimeouts(session) {
    return (session.attempts || []).filter((a) => a && a.timed_out).length;
  }

  function render(root, session) {
    if (!root || !session) return;
    const agg = global.QCSession.aggregates(session);
    const timeouts = countTimeouts(session);
    const insights = buildTimeInsights(session);
    root.innerHTML = "";
    root.className = "report-dash";

    root.appendChild(renderHeader(session));
    root.appendChild(renderStatCards(agg, timeouts));
    root.appendChild(renderMainGrid(session, agg));
    root.appendChild(renderTimeInsights(insights));
    root.appendChild(renderLevelTable(agg));
    root.appendChild(renderAttemptDetails(session));
  }

  function renderHeader(session) {
    const header = document.createElement("header");
    header.className = "report-dash-header";

    const left = document.createElement("div");
    left.className = "report-dash-heading";

    const h = document.createElement("h1");
    h.className = "report-dash-title";
    h.textContent = "Quest Report";
    left.appendChild(h);

    const sub = document.createElement("p");
    sub.className = "report-dash-sub";
    const title =
      session.title ||
      (session.mode === "test"
        ? session.short_module_title
          ? "Short Quest · " + session.short_module_title
          : "Short Quest"
        : session.course_id === "learn_verilog"
          ? "Verilog RTL Quest"
          : "Digital Foundations Quest");
    const when = fmtCompleted(session.completed_at || session.started_at);
    sub.innerHTML =
      "<span class=\"report-quest-name\">" +
      escape(title) +
      "</span>" +
      '<span class="report-completed"><span class="report-check" aria-hidden="true">✓</span> Completed ' +
      escape(when) +
      "</span>";
    left.appendChild(sub);
    header.appendChild(left);

    const tools = document.createElement("div");
    tools.className = "report-dash-tools no-print";
    tools.innerHTML =
      '<button type="button" class="btn ghost" id="report-print-btn">Print report</button>' +
      '<button type="button" class="btn ghost" id="report-pdf-btn">Download PDF</button>';
    header.appendChild(tools);

    tools.querySelector("#report-print-btn").addEventListener("click", () => {
      window.print();
    });
    tools.querySelector("#report-pdf-btn").addEventListener("click", () => {
      // Browser print dialog → "Save as PDF"
      window.print();
    });

    return header;
  }

  function renderStatCards(agg, timeouts) {
    const grid = document.createElement("section");
    grid.className = "report-stat-cards";
    grid.setAttribute("aria-label", "Quest summary");

    const cards = [
      {
        key: "accuracy",
        label: "Accuracy",
        value: pct(agg.accuracy),
        hint: agg.correct_count + " / " + agg.total_attempts + " correct",
      },
      {
        key: "attempts",
        label: "Attempts",
        value: String(agg.total_attempts),
        hint: "Total questions attempted",
      },
      {
        key: "time",
        label: "Time",
        value: fmtMs(agg.total_ms),
        hint: "Total time taken",
      },
      {
        key: "timeouts",
        label: "Timeouts",
        value: String(timeouts),
        hint: "Questions timed out",
      },
    ];

    cards.forEach((c) => {
      const article = document.createElement("article");
      article.className = "report-stat-card report-stat-" + c.key;
      article.innerHTML =
        '<p class="report-stat-label">' +
        escape(c.label) +
        "</p>" +
        '<p class="report-stat-value">' +
        escape(c.value) +
        "</p>" +
        '<p class="report-stat-hint">' +
        escape(c.hint) +
        "</p>";
      grid.appendChild(article);
    });

    return grid;
  }

  function renderMainGrid(session, agg) {
    const grid = document.createElement("section");
    grid.className = "report-main-grid";

    const mods = document.createElement("div");
    mods.className = "report-panel";
    mods.innerHTML = "<h2>Module breakdown</h2>";
    mods.appendChild(renderModuleTable(agg.modules || []));
    const note = document.createElement("p");
    note.className = "report-formula note";
    note.textContent = "Accuracy = (Correct / Attempts) × 100";
    mods.appendChild(note);
    grid.appendChild(mods);

    const path = document.createElement("div");
    path.className = "report-panel report-path-panel";
    path.innerHTML =
      "<h2>Attempt path</h2>" +
      '<ul class="path-legend" aria-hidden="true">' +
      '<li><span class="dot ok"></span> Correct</li>' +
      '<li><span class="dot err"></span> Incorrect</li>' +
      '<li><span class="dot to"></span> Timeout</li>' +
      "</ul>";
    path.appendChild(renderPathSvg(session.attempts || []));
    grid.appendChild(path);

    return grid;
  }

  function renderModuleTable(modules) {
    const wrap = document.createElement("div");
    wrap.className = "report-table-wrap";
    const table = document.createElement("table");
    table.className = "report-table report-module-table";
    table.innerHTML =
      "<thead><tr>" +
      "<th>Module</th><th>Accuracy</th><th>Attempts</th><th>Correct</th><th>Time</th>" +
      "</tr></thead>";
    const tbody = document.createElement("tbody");

    let totA = 0;
    let totC = 0;
    let totMs = 0;

    modules.forEach((m) => {
      const attempts = m.attempts || m.correct + m.wrong || 0;
      const correct = m.correct || 0;
      const acc = attempts ? correct / attempts : 0;
      totA += attempts;
      totC += correct;
      totMs += m.time_ms || 0;

      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" +
        escape(m.title || m.module_id) +
        '</td><td class="acc-cell">' +
        '<div class="acc-bar" role="img" aria-label="' +
        pct(acc) +
        '">' +
        '<span class="acc-fill" style="width:' +
        Math.round(acc * 100) +
        '%"></span>' +
        '<span class="acc-pct">' +
        pct(acc) +
        "</span></div></td><td>" +
        attempts +
        "</td><td>" +
        correct +
        " / " +
        attempts +
        "</td><td>" +
        fmtMs(m.time_ms) +
        "</td>";
      tbody.appendChild(tr);
    });

    const overallAcc = totA ? totC / totA : 0;
    const foot = document.createElement("tr");
    foot.className = "report-overall-row";
    foot.innerHTML =
      "<td><strong>Overall</strong></td>" +
      '<td class="acc-cell"><div class="acc-bar"><span class="acc-fill" style="width:' +
      Math.round(overallAcc * 100) +
      '%"></span><span class="acc-pct">' +
      pct(overallAcc) +
      "</span></div></td>" +
      "<td><strong>" +
      totA +
      "</strong></td>" +
      "<td><strong>" +
      totC +
      " / " +
      totA +
      "</strong></td>" +
      "<td><strong>" +
      fmtMs(totMs) +
      "</strong></td>";
    tbody.appendChild(foot);

    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function renderTimeInsights(insights) {
    const sec = document.createElement("section");
    sec.className = "report-panel report-secondary";
    sec.innerHTML =
      "<h2>Time analytics</h2>" +
      '<ul class="stat-list compact">' +
      "<li><span>Average / attempt</span><strong>" +
      fmtMs(insights.avgMs) +
      "</strong></li>" +
      "<li><span>Fastest</span><strong>" +
      (insights.fastest ? fmtMs(insights.fastest.duration_ms) : "—") +
      "</strong></li>" +
      "<li><span>Slowest</span><strong>" +
      (insights.slowest ? fmtMs(insights.slowest.duration_ms) : "—") +
      "</strong></li>" +
      "</ul>";
    return sec;
  }

  function renderLevelTable(agg) {
    const sec = document.createElement("section");
    sec.className = "report-panel report-secondary";
    sec.innerHTML = "<h2>By difficulty level</h2>";
    const wrap = document.createElement("div");
    wrap.className = "report-table-wrap";
    const lt = document.createElement("table");
    lt.className = "report-table";
    lt.innerHTML =
      "<thead><tr><th>Module</th><th>Level</th><th>Correct</th><th>Attempts</th><th>Status</th><th>Time</th></tr></thead>";
    const lbody = document.createElement("tbody");
    const state = agg.level_state || {};
    (agg.levels || []).forEach((L) => {
      const st = ((state[L.module_id] || {})[L.difficulty]) || {};
      let status = "in progress";
      if (st.cleared) status = "cleared";
      else if (st.exhausted) status = "exhausted";
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" +
        escape(L.title || L.module_id) +
        "</td><td>" +
        escape(L.difficulty) +
        "</td><td>" +
        L.correct +
        "</td><td>" +
        L.attempts +
        '</td><td><span class="status-pill status-' +
        status.replace(/\s+/g, "-") +
        '">' +
        status +
        "</span></td><td>" +
        fmtMs(L.time_ms) +
        "</td>";
      lbody.appendChild(tr);
    });
    lt.appendChild(lbody);
    wrap.appendChild(lt);
    sec.appendChild(wrap);
    return sec;
  }

  function renderAttemptDetails(session) {
    const detail = document.createElement("section");
    detail.className = "report-panel report-secondary";
    detail.innerHTML = "<h2>Each attempt</h2>";
    const list = document.createElement("ol");
    list.className = "attempt-list";
    (session.attempts || []).forEach((a) => {
      const li = document.createElement("li");
      li.className = a.timed_out ? "timeout" : a.correct ? "ok" : "err";
      const chosen = a.timed_out
        ? "Timed out"
        : a.choices && typeof a.selected === "number"
          ? a.choices[a.selected]
          : a.selected == null
            ? "—"
            : String(a.selected);
      const correctLabel =
        a.choices && typeof a.correct_answer === "number"
          ? a.choices[a.correct_answer]
          : String(a.correct_answer);
      li.innerHTML =
        '<div class="attempt-head">' +
        "<strong>" +
        escape(a.module_title || a.module_id) +
        "</strong> · " +
        (a.timed_out ? "Timed out" : a.correct ? "Correct" : "Wrong") +
        " · " +
        fmtMs(a.duration_ms) +
        " · try #" +
        a.attempt_index +
        "</div>" +
        '<p class="prompt-sm">' +
        escape(a.prompt) +
        "</p>" +
        "<p>" +
        (a.timed_out
          ? "No answer within the time limit"
          : "You chose: <em>" + escape(chosen) + "</em>") +
        (a.correct ? "" : " · Correct: <em>" + escape(correctLabel) + "</em>") +
        "</p>" +
        (a.explain ? '<p class="explain">' + escape(a.explain) + "</p>" : "");
      list.appendChild(li);
    });
    detail.appendChild(list);
    return detail;
  }

  function buildTimeInsights(session) {
    const attempts = session && session.attempts ? session.attempts : [];
    if (!attempts.length) return { avgMs: 0, fastest: null, slowest: null };
    let total = 0;
    let fastest = attempts[0];
    let slowest = attempts[0];
    attempts.forEach((a) => {
      const d = a.duration_ms || 0;
      total += d;
      if (d < (fastest.duration_ms || 0)) fastest = a;
      if (d > (slowest.duration_ms || 0)) slowest = a;
    });
    return { avgMs: total / attempts.length, fastest, slowest };
  }

  /**
   * Vertical attempt path: Y = question index, X = outcome (correct / wrong / timeout).
   */
  function renderPathSvg(attempts) {
    const wrap = document.createElement("div");
    wrap.className = "path-wrap path-wrap-vertical";
    if (!attempts.length) {
      wrap.textContent = "No attempts recorded.";
      return wrap;
    }

    const n = attempts.length;
    const top = 28;
    const bottom = 28;
    const left = 44;
    const right = 16;
    const rowH = Math.max(22, Math.min(36, Math.floor(420 / Math.max(n, 1))));
    const h = top + bottom + n * rowH;
    const w = 220;
    const xCorrect = left + 28;
    const xWrong = left + 88;
    const xTimeout = left + 148;

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", "100%");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Attempt path diagram");

    function outcomeX(a) {
      if (a.timed_out) return xTimeout;
      return a.correct ? xCorrect : xWrong;
    }

    function outcomeClass(a) {
      if (a.timed_out) return "path-node to";
      return a.correct ? "path-node ok" : "path-node err";
    }

    // Axis labels
    ["C", "X", "T"].forEach((lab, i) => {
      const tx = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tx.setAttribute("x", String([xCorrect, xWrong, xTimeout][i]));
      tx.setAttribute("y", "16");
      tx.setAttribute("text-anchor", "middle");
      tx.setAttribute("class", "path-axis-label");
      tx.textContent = lab;
      svg.appendChild(tx);
    });

    let prev = null;
    attempts.forEach((a, i) => {
      const y = top + i * rowH + rowH / 2;
      const x = outcomeX(a);

      const qLab = document.createElementNS("http://www.w3.org/2000/svg", "text");
      qLab.setAttribute("x", "8");
      qLab.setAttribute("y", String(y + 4));
      qLab.setAttribute("class", "path-q-label");
      qLab.textContent = String(i + 1);
      svg.appendChild(qLab);

      if (prev) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(prev.x));
        line.setAttribute("y1", String(prev.y));
        line.setAttribute("x2", String(x));
        line.setAttribute("y2", String(y));
        line.setAttribute("class", "path-edge");
        svg.appendChild(line);
      }

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", String(x));
      circle.setAttribute("cy", String(y));
      circle.setAttribute("r", "9");
      circle.setAttribute("class", outcomeClass(a));
      svg.appendChild(circle);

      prev = { x, y };
    });

    wrap.appendChild(svg);
    return wrap;
  }

  global.QCReport = {
    render,
    fmtMs,
  };
})(window);
