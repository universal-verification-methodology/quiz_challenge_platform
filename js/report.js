/**
 * Post-quest report renderer (v0: summary table + attempt path text/SVG).
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

  function render(root, session) {
    if (!root || !session) return;
    const agg = global.QCSession.aggregates(session);
    root.innerHTML = "";

    const summary = document.createElement("section");
    summary.className = "report-summary";
    summary.innerHTML =
      "<h2>Quest summary</h2>" +
      "<ul class=\"stat-list\">" +
      "<li><span>Accuracy</span><strong>" +
      pct(agg.accuracy) +
      "</strong></li>" +
      "<li><span>Attempts</span><strong>" +
      agg.total_attempts +
      "</strong></li>" +
      "<li><span>Correct</span><strong>" +
      agg.correct_count +
      "</strong></li>" +
      "<li><span>Wrong</span><strong>" +
      agg.wrong_count +
      "</strong></li>" +
      "<li><span>Total time</span><strong>" +
      fmtMs(agg.total_ms) +
      "</strong></li>" +
      "</ul>";
    root.appendChild(summary);

    const insights = buildTimeInsights(session);
    const timeSec = document.createElement("section");
    timeSec.innerHTML =
      "<h2>Time analytics</h2>" +
      "<ul class=\"stat-list\">" +
      "<li><span>Average / attempt</span><strong>" + fmtMs(insights.avgMs) + "</strong></li>" +
      "<li><span>Fastest</span><strong>" + (insights.fastest ? fmtMs(insights.fastest.duration_ms) : "-") + "</strong></li>" +
      "<li><span>Slowest</span><strong>" + (insights.slowest ? fmtMs(insights.slowest.duration_ms) : "-") + "</strong></li>" +
      "</ul>";
    root.appendChild(timeSec);

    const modSec = document.createElement("section");
    modSec.innerHTML = "<h2>By module</h2>";
    const table = document.createElement("table");
    table.className = "report-table";
    table.innerHTML =
      "<thead><tr><th>Module</th><th>Correct</th><th>Wrong</th><th>Time</th></tr></thead>";
    const tbody = document.createElement("tbody");
    agg.modules.forEach((m) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" +
        escape(m.title || m.module_id) +
        "</td><td>" +
        m.correct +
        "</td><td>" +
        m.wrong +
        "</td><td>" +
        fmtMs(m.time_ms) +
        "</td>";
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    modSec.appendChild(table);
    modSec.appendChild(renderModuleTimeBars(agg.modules || []));
    root.appendChild(modSec);

    const lvlSec = document.createElement("section");
    lvlSec.innerHTML = "<h2>By difficulty level</h2>";
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
        "</td><td>" +
        status +
        "</td><td>" +
        fmtMs(L.time_ms) +
        "</td>";
      lbody.appendChild(tr);
    });
    lt.appendChild(lbody);
    lvlSec.appendChild(lt);
    root.appendChild(lvlSec);

    const detail = document.createElement("section");
    detail.innerHTML = "<h2>Each attempt</h2>";
    const list = document.createElement("ol");
    list.className = "attempt-list";
    (session.attempts || []).forEach((a) => {
      const li = document.createElement("li");
      li.className = a.correct ? "ok" : "err";
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
        "<div class=\"attempt-head\">" +
        "<strong>" +
        escape(a.module_title || a.module_id) +
        "</strong> · " +
        (a.timed_out ? "Timed out" : a.correct ? "Correct" : "Wrong") +
        " · " +
        fmtMs(a.duration_ms) +
        " · try #" +
        a.attempt_index +
        "</div>" +
        "<p class=\"prompt-sm\">" +
        escape(a.prompt) +
        "</p>" +
        "<p>" +
        (a.timed_out
          ? "No answer within the time limit"
          : "You chose: <em>" + escape(chosen) + "</em>") +
        (a.correct ? "" : " · Correct: <em>" + escape(correctLabel) + "</em>") +
        "</p>" +
        (a.explain ? "<p class=\"explain\">" + escape(a.explain) + "</p>" : "");
      list.appendChild(li);
    });
    detail.appendChild(list);
    root.appendChild(detail);

    const path = document.createElement("section");
    path.innerHTML = "<h2>Progress path</h2>";
    path.appendChild(renderPathSvg(session.attempts || []));
    root.appendChild(path);
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

  function renderModuleTimeBars(modules) {
    const sec = document.createElement("div");
    sec.className = "time-bars";
    if (!modules.length) return sec;
    const maxMs = Math.max.apply(
      null,
      modules.map((m) => m.time_ms || 0)
    ) || 1;

    const title = document.createElement("p");
    title.className = "note";
    title.textContent = "Time spent by module";
    sec.appendChild(title);

    modules.forEach((m) => {
      const row = document.createElement("div");
      row.className = "bar-row";
      const label = document.createElement("div");
      label.className = "bar-label";
      label.textContent = m.title || m.module_id;
      const track = document.createElement("div");
      track.className = "bar-track";
      const fill = document.createElement("div");
      fill.className = "bar-fill";
      fill.style.width = Math.max(4, Math.round(((m.time_ms || 0) / maxMs) * 100)) + "%";
      fill.textContent = fmtMs(m.time_ms || 0);
      track.appendChild(fill);
      row.appendChild(label);
      row.appendChild(track);
      sec.appendChild(row);
    });
    return sec;
  }

  function escape(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function renderPathSvg(attempts) {
    const wrap = document.createElement("div");
    wrap.className = "path-wrap";
    if (!attempts.length) {
      wrap.textContent = "No attempts recorded.";
      return wrap;
    }

    const w = Math.max(640, attempts.length * 120);
    const h = 120;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", "100%");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Attempt path diagram");

    attempts.forEach((a, i) => {
      const x = 40 + i * 120;
      const y = 50;
      if (i > 0) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(x - 120 + 28));
        line.setAttribute("y1", String(y));
        line.setAttribute("x2", String(x - 28));
        line.setAttribute("y2", String(y));
        line.setAttribute("class", "path-edge");
        svg.appendChild(line);
      }
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", String(x));
      circle.setAttribute("cy", String(y));
      circle.setAttribute("r", "18");
      circle.setAttribute("class", a.correct ? "path-node ok" : "path-node err");
      svg.appendChild(circle);

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", String(x));
      label.setAttribute("y", String(y + 5));
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "path-node-label");
      label.textContent = a.correct ? "✓" : "✗";
      svg.appendChild(label);

      const cap = document.createElementNS("http://www.w3.org/2000/svg", "text");
      cap.setAttribute("x", String(x));
      cap.setAttribute("y", String(y + 40));
      cap.setAttribute("text-anchor", "middle");
      cap.setAttribute("class", "path-caption");
      const shortId = (a.module_id || "").replace(/^module\d+-/, "").slice(0, 10);
      cap.textContent = shortId + " " + Math.round((a.duration_ms || 0) / 1000) + "s";
      svg.appendChild(cap);
    });

    wrap.appendChild(svg);
    return wrap;
  }

  global.QCReport = {
    render,
    fmtMs,
  };
})(window);
