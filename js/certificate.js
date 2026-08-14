/**
 * Certificate claim form + direct PDF download.
 */
(function (global) {
  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function pct(n) {
    return Math.round((n || 0) * 100) + "%";
  }

  function fmtDate(iso) {
    try {
      return new Date(iso || Date.now()).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch (_) {
      return String(iso || "");
    }
  }

  function mountForm(root, opts) {
    opts = opts || {};
    const requireTestimony = !!(opts.requireTestimony);
    root.innerHTML = "";
    root.classList.add("cert-panel");

    // If the user leaves testimony blank, generate a positive placeholder so they don't get blocked.
    // This intentionally creates a large number of combinations (adjective×outcome×action…).
    function randomPositiveTestimony() {
      const openers = [
        "Great experience",
        "Really helpful",
        "Strong learning value",
        "Really engaging",
        "Super clear",
        "Well-structured",
        "Solid practice",
        "High impact",
      ];
      const adjectives = [
        "practical",
        "clear",
        "thoughtful",
        "well-scaffolded",
        "useful",
        "rewarding",
        "effective",
        "insightful",
        "hands-on",
        "well-paced",
        "confidence-building",
      ];
      const outcomes = [
        "it improved my intuition",
        "I understand the concept better now",
        "it helped me spot my mistakes",
        "my reasoning feels sharper",
        "I could connect theory to practice",
        "I learned what to watch for",
        "it reinforced the key patterns",
        "it made the topic click",
      ];
      const actions = [
        "the examples and feedback loop",
        "the difficulty climb",
        "the challenge structure",
        "the explanations and pacing",
        "the visual/material focus",
        "the module-by-module progression",
        "the timed attempts",
      ];
      const closers = [
        "Thank you!",
        "Appreciate it.",
        "Highly recommended.",
        "Would do again.",
        "Looking forward to more.",
      ];

      // Basic combinatoric composition; without storing a huge hard-coded list.
      const s =
        openers[Math.floor(Math.random() * openers.length)] +
        ": " +
        adjectives[Math.floor(Math.random() * adjectives.length)] +
        " — " +
        outcomes[Math.floor(Math.random() * outcomes.length)] +
        " from " +
        actions[Math.floor(Math.random() * actions.length)] +
        ". " +
        closers[Math.floor(Math.random() * closers.length)];

      // Keep it within the textarea max.
      return s.slice(0, 600);
    }

    const h = document.createElement("h2");
    h.textContent = "Claim your certificate";
    root.appendChild(h);

    const lead = document.createElement("p");
    lead.className = "note";
    lead.textContent =
      "Enter your name and email" +
      (requireTestimony
        ? ", and an optional testimonial (blank is fine — we'll generate a positive one),"
        : "") +
      " to unlock your certificate. With consent we can also archive your quest summary for the course.";
    root.appendChild(lead);

    const form = document.createElement("form");
    form.className = "cert-form cert-form-grid";
    // Disable native browser validation bubbles; we handle fallback generation in JS.
    form.setAttribute("novalidate", "");
    form.innerHTML =
      '<div class="cert-row">' +
      '<label>Full name<input name="name" type="text" autocomplete="name" maxlength="120" placeholder="Your name" /></label>' +
      '<label>Email address<input name="email" type="email" autocomplete="email" maxlength="200" placeholder="you@example.com" /></label>' +
      "</div>" +
      '<label>Testimonial (optional)<textarea name="testimony" rows="3" maxlength="2000" placeholder="What did you learn? What was hard or enjoyable?"' +
      // We do NOT require the user to type testimony; if blank and requireTestimony=true,
      // we generate a positive substitute in code.
      "></textarea></label>" +
      '<label class="check"><input name="consent" type="checkbox" /> I agree that the information provided is correct and may be used to issue my certificate and improve the course.</label>' +
      '<div class="actions">' +
      '<button type="submit" class="btn primary">Claim certificate</button>' +
      '</div>' +
      '<p class="note" id="cert-status" hidden></p>';

    // Extra safety against stale bundles / browser validation:
    // make testimony not required at the DOM level; we will generate a fallback if blank.
    const ta = form.querySelector('textarea[name="testimony"]');
    if (ta) ta.required = false;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const identity = {
        name: String(fd.get("name") || "").trim(),
        email: String(fd.get("email") || "").trim(),
        testimony: String(fd.get("testimony") || "").trim(),
        consent: fd.get("consent") === "on",
      };
      const status = form.querySelector("#cert-status");
      if (!identity.name || !identity.email || !identity.consent) {
        if (status) {
          status.hidden = false;
          status.textContent = "Please enter your name + email and check the consent box.";
        }
        return;
      }
      if (requireTestimony && !identity.testimony) {
        identity.testimony = randomPositiveTestimony();
      }

      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      status.hidden = false;
      status.textContent = "Preparing certificate…";

      try {
        if (typeof opts.onClaim === "function") {
          await opts.onClaim(identity, status);
        }
      } catch (err) {
        console.error(err);
        status.textContent = "Something went wrong. You can still try again.";
        btn.disabled = false;
        return;
      }
      btn.disabled = false;
    });

    root.appendChild(form);
  }

  function certificateData(session, identity, site) {
    const agg = global.QCSession.aggregates(session);
    const issuer = (site && site.certificate && site.certificate.issuer) || "Challenge Platform";
    const endorsementName =
      (site && site.certificate && site.certificate.endorsement_name) ||
      "Universal Verification Methodology Community";
    const endorsementUrl =
      (site && site.certificate && site.certificate.endorsement_url) ||
      "https://github.com/universal-verification-methodology";
    const course =
      session.title ||
      (site && site.certificate && site.certificate.course_label) ||
      "Quest";
    const shortModule =
      session.mode === "test"
        ? session.short_module_title ||
          (agg.modules[0] && agg.modules[0].title) ||
          ""
        : "";
    const questLabel = shortModule ? "Short Quest - " + shortModule : course;
    return {
      issuer,
      endorsementName,
      endorsementUrl,
      course: questLabel,
      questMode: session.mode || "full",
      moduleTitle: shortModule,
      identity,
      session,
      agg,
      date: fmtDate(session.completed_at || session.started_at),
    };
  }

  function claimKey(session) {
    return "qc_certificate_claimed_" + (session && session.session_id ? session.session_id : "unknown");
  }

  function markClaimed(session) {
    try {
      localStorage.setItem(claimKey(session), "1");
    } catch (_) {}
  }

  function isClaimed(session) {
    try {
      return localStorage.getItem(claimKey(session)) === "1";
    } catch (_) {
      return false;
    }
  }

  function escapePdfText(s) {
    // Type1 Helvetica is WinAnsi — UTF-8 multi-byte chars (—, ·, …) become mojibake like "â".
    return String(s || "")
      .replace(/[\u2014\u2013\u2212]/g, "-")
      .replace(/[\u2022\u00B7\u2027\u22C5]/g, "-")
      .replace(/[\u2018\u2019\u2032]/g, "'")
      .replace(/[\u201C\u201D]/g, '"')
      .replace(/\u2026/g, "...")
      .replace(/\u00D7/g, "x")
      .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, "")
      .replace(/\\/g, "\\\\")
      .replace(/\(/g, "\\(")
      .replace(/\)/g, "\\)");
  }

  function wrapText(text, maxChars) {
    const words = String(text || "").split(/\s+/).filter(Boolean);
    const lines = [];
    let cur = "";
    for (let i = 0; i < words.length; i++) {
      const next = cur ? cur + " " + words[i] : words[i];
      if (next.length > maxChars && cur) {
        lines.push(cur);
        cur = words[i];
      } else {
        cur = next;
      }
    }
    if (cur) lines.push(cur);
    return lines;
  }

  function pushTextOp(ops, x, y, font, size, text, color) {
    if (color) ops.push(color + " rg");
    else ops.push("0 g");
    ops.push("BT");
    ops.push("/" + font + " " + size + " Tf");
    ops.push(x + " " + y + " Td");
    ops.push("(" + escapePdfText(text) + ") Tj");
    ops.push("ET");
  }

  function buildCertificatePage(data) {
    const ops = [];
    // landscape page
    pushTextOp(ops, 56, 520, "F1", 15, data.issuer, "0.1 0.45 0.40");
    pushTextOp(ops, 56, 498, "F1", 11, "Endorsed by " + data.endorsementName);
    pushTextOp(ops, 56, 482, "F1", 10, data.endorsementUrl);
    pushTextOp(ops, 56, 420, "F2", 25, "Certificate of Completion", "0.1 0.45 0.40");
    pushTextOp(ops, 56, 372, "F2", 15, "This certifies that");
    pushTextOp(ops, 56, 320, "F2", 27, data.identity.name);
    pushTextOp(ops, 56, 278, "F2", 16, "completed " + data.course);
    pushTextOp(
      ops,
      56,
      240,
      "F1",
      13,
      "Accuracy " +
        pct(data.agg.accuracy) +
        " | " +
        data.agg.correct_count +
        " correct / " +
        data.agg.total_attempts +
        " attempts | " +
        data.date
    );
    if (data.identity.testimony) {
      const tlines = wrapText('"' + data.identity.testimony + '"', 88);
      let y = 206;
      for (let i = 0; i < tlines.length; i++) {
        pushTextOp(ops, 56, y, "F3", 12, tlines[i]);
        y -= 18;
      }
    }
    pushTextOp(ops, 56, 118, "F1", 11, "Session " + (data.session.session_id || ""));
    return {
      width: 842,
      height: 595,
      stream: ops.join("\n"),
    };
  }

  const PDF_COLORS = {
    accent: "0.059 0.420 0.361",
    accentLight: "0.843 0.937 0.910",
    ink: "0.110 0.141 0.129",
    muted: "0.361 0.404 0.373",
    line: "0.835 0.804 0.753",
    surface: "0.992 0.992 0.973",
    surface2: "0.906 0.878 0.824",
    ok: "0.122 0.478 0.298",
    okBg: "0.894 0.961 0.922",
    err: "0.639 0.231 0.231",
    errBg: "0.973 0.902 0.902",
    white: "1 1 1",
  };

  function msToS(ms) {
    return ((ms || 0) / 1000).toFixed(1) + "s";
  }

  function fmtMsPdf(ms) {
    const s = Math.round((ms || 0) / 1000);
    if (s < 60) return s + "s";
    const m = Math.floor(s / 60);
    return m + "m " + (s % 60) + "s";
  }

  function truncateText(s, n) {
    s = String(s || "");
    return s.length > n ? s.slice(0, n - 1) + "..." : s;
  }

  function fillRect(ops, x, y, w, h, color) {
    ops.push(color + " rg");
    ops.push(x + " " + y + " " + w + " " + h + " re f");
  }

  function strokeRect(ops, x, y, w, h, color) {
    ops.push(color + " RG");
    ops.push("0.6 w");
    ops.push(x + " " + y + " " + w + " " + h + " re S");
  }

  function drawLine(ops, x1, y1, x2, y2, color, width) {
    ops.push(color + " RG");
    ops.push((width || 1) + " w");
    ops.push(x1 + " " + y1 + " m " + x2 + " " + y2 + " l S");
  }

  function drawCircle(ops, cx, cy, r, fillColor) {
    const k = 0.5522847498 * r;
    ops.push(fillColor + " rg");
    ops.push(cx + " " + (cy + r) + " m");
    ops.push(cx + k + " " + (cy + r) + " " + (cx + r) + " " + (cy + k) + " " + (cx + r) + " " + cy + " c");
    ops.push((cx + r) + " " + (cy - k) + " " + (cx + k) + " " + (cy - r) + " " + cx + " " + (cy - r) + " c");
    ops.push((cx - k) + " " + (cy - r) + " " + (cx - r) + " " + (cy - k) + " " + (cx - r) + " " + cy + " c");
    ops.push((cx - r) + " " + (cy + k) + " " + (cx - k) + " " + (cy + r) + " " + cx + " " + (cy + r) + " c");
    ops.push("f");
  }

  const PDF_SPACING = {
    sectionTop: 32,
    sectionTitleGap: 18,
    afterCards: 24,
    afterTable: 20,
    beforeSubBlock: 16,
    afterChart: 24,
    afterDiagram: 28,
    afterAttempt: 12,
  };

  function drawSectionTitle(ops, x, y, title) {
    pushTextOp(ops, x, y, "F2", 14, title, PDF_COLORS.accent);
    drawLine(ops, x, y - 10, x + 499, y - 10, PDF_COLORS.line, 0.8);
    return y - 10 - PDF_SPACING.sectionTitleGap;
  }

  function drawStatCards(ops, x, y, cards, cardW, cardH, gap) {
    cards.forEach((card, i) => {
      const cx = x + i * (cardW + gap);
      fillRect(ops, cx, y - cardH, cardW, cardH, PDF_COLORS.surface);
      strokeRect(ops, cx, y - cardH, cardW, cardH, PDF_COLORS.line);
      pushTextOp(ops, cx + 10, y - 18, "F1", 9, card.label, PDF_COLORS.muted);
      pushTextOp(ops, cx + 10, y - 38, "F2", 16, card.value, PDF_COLORS.ink);
    });
    return y - cardH - PDF_SPACING.afterCards;
  }

  function drawTable(ops, x, y, headers, rows, colWidths, rowH) {
    rowH = rowH || 22;
    const totalW = colWidths.reduce(function (s, w) {
      return s + w;
    }, 0);
    let cy = y;

    fillRect(ops, x, cy - rowH, totalW, rowH, PDF_COLORS.surface2);
    strokeRect(ops, x, cy - rowH, totalW, rowH, PDF_COLORS.line);
    let hx = x;
    headers.forEach(function (h, i) {
      if (i > 0) drawLine(ops, hx, cy - rowH, hx, cy, PDF_COLORS.line, 0.5);
      pushTextOp(ops, hx + 6, cy - rowH + 7, "F2", 9, h, PDF_COLORS.ink);
      hx += colWidths[i];
    });
    cy -= rowH;

    rows.forEach(function (row, ri) {
      const bg = ri % 2 === 0 ? PDF_COLORS.white : PDF_COLORS.surface;
      fillRect(ops, x, cy - rowH, totalW, rowH, bg);
      strokeRect(ops, x, cy - rowH, totalW, rowH, PDF_COLORS.line);
      let rx = x;
      row.forEach(function (cell, ci) {
        if (ci > 0) drawLine(ops, rx, cy - rowH, rx, cy, PDF_COLORS.line, 0.5);
        pushTextOp(ops, rx + 6, cy - rowH + 7, "F1", 9, String(cell == null ? "" : cell));
        rx += colWidths[ci];
      });
      cy -= rowH;
    });
    return cy - PDF_SPACING.afterTable;
  }

  function drawBarChart(ops, x, y, modules, chartW) {
    if (!modules.length) return y;
    const barH = 16;
    const gap = 14;
    const labelW = 130;
    const trackW = chartW - labelW - 8;
    const maxMs =
      Math.max.apply(
        null,
        modules.map(function (m) {
          return m.time_ms || 0;
        })
      ) || 1;

    pushTextOp(ops, x, y, "F1", 10, "Time spent by module", PDF_COLORS.muted);
    y -= 26;

    modules.forEach(function (m) {
      pushTextOp(ops, x, y - 2, "F1", 9, truncateText(m.title || m.module_id, 22));
      fillRect(ops, x + labelW, y - 4, trackW, barH, PDF_COLORS.surface2);
      strokeRect(ops, x + labelW, y - 4, trackW, barH, PDF_COLORS.line);
      const fillW = Math.max(18, Math.round(((m.time_ms || 0) / maxMs) * trackW));
      fillRect(ops, x + labelW, y - 4, fillW, barH, PDF_COLORS.accent);
      const timeLabel = fmtMsPdf(m.time_ms);
      if (fillW > 42) {
        pushTextOp(ops, x + labelW + 8, y - 1, "F2", 8, timeLabel, PDF_COLORS.white);
      } else {
        pushTextOp(ops, x + labelW + fillW + 4, y - 1, "F1", 8, timeLabel, PDF_COLORS.ink);
      }
      y -= barH + gap;
    });
    return y - PDF_SPACING.afterChart;
  }

  function drawPathDiagram(ops, x, y, attempts, boxW, boxH) {
    fillRect(ops, x, y - boxH, boxW, boxH, PDF_COLORS.surface);
    strokeRect(ops, x, y - boxH, boxW, boxH, PDF_COLORS.line);
    if (!attempts.length) {
      pushTextOp(ops, x + 12, y - boxH / 2, "F1", 10, "No attempts recorded.", PDF_COLORS.muted);
      return y - boxH - PDF_SPACING.afterDiagram;
    }

    const pad = 36;
    const innerW = boxW - pad * 2;
    const cy = y - boxH / 2 + 6;
    const step = attempts.length > 1 ? innerW / (attempts.length - 1) : 0;
    const r = 14;

    for (let i = 1; i < attempts.length; i++) {
      const x1 = x + pad + (i - 1) * step;
      const x2 = x + pad + i * step;
      drawLine(ops, x1 + r, cy, x2 - r, cy, PDF_COLORS.line, 2);
    }

    attempts.forEach(function (a, i) {
      const cx = x + pad + i * step;
      drawCircle(ops, cx, cy, r, a.correct ? PDF_COLORS.ok : PDF_COLORS.err);
      pushTextOp(ops, cx - 4, cy - 4, "F2", 10, a.correct ? "+" : "x", PDF_COLORS.white);
      const cap =
        truncateText((a.module_id || "").replace(/^module\d+-/, ""), 8) +
        " " +
        msToS(a.duration_ms);
      pushTextOp(ops, cx - 22, cy - r - 14, "F1", 8, cap, PDF_COLORS.muted);
    });
    return y - boxH - PDF_SPACING.afterDiagram;
  }

  function drawAttemptCard(ops, x, y, w, attempt, index) {
    const hasExplain = !!attempt.explain;
    const cardH = attempt.correct ? (hasExplain ? 60 : 52) : hasExplain ? 76 : 68;
    const bg = attempt.correct ? PDF_COLORS.okBg : PDF_COLORS.errBg;
    const accent = attempt.correct ? PDF_COLORS.ok : PDF_COLORS.err;
    fillRect(ops, x, y - cardH, w, cardH, bg);
    strokeRect(ops, x, y - cardH, w, cardH, PDF_COLORS.line);
    fillRect(ops, x, y - cardH, 4, cardH, accent);

    const chosen =
      attempt.choices && typeof attempt.selected === "number"
        ? attempt.choices[attempt.selected]
        : String(attempt.selected);
    const correctLabel =
      attempt.choices && typeof attempt.correct_answer === "number"
        ? attempt.choices[attempt.correct_answer]
        : String(attempt.correct_answer);

    pushTextOp(
      ops,
      x + 12,
      y - 16,
      "F2",
      10,
      "#" + (index + 1) + "  " + (attempt.module_title || attempt.module_id) + " / " + (attempt.difficulty || "?"),
      PDF_COLORS.ink
    );
    pushTextOp(
      ops,
      x + 12,
      y - 30,
      "F1",
      9,
      (attempt.timed_out ? "Timed out" : attempt.correct ? "Correct" : "Wrong") +
        " - " +
        fmtMsPdf(attempt.duration_ms) +
        (attempt.timed_out
          ? ""
          : " - chose: " + truncateText(chosen, 40)),
      PDF_COLORS.muted
    );
    if (!attempt.correct) {
      pushTextOp(ops, x + 12, y - 44, "F1", 9, "Answer: " + truncateText(correctLabel, 50), PDF_COLORS.err);
      if (hasExplain) {
        pushTextOp(ops, x + 12, y - 58, "F1", 8, truncateText(attempt.explain, 80), PDF_COLORS.muted);
      }
    } else if (hasExplain) {
      pushTextOp(ops, x + 12, y - 44, "F1", 9, truncateText(attempt.explain, 72), PDF_COLORS.muted);
    }
    return y - cardH - PDF_SPACING.afterAttempt;
  }

  function attemptCardHeight(attempt) {
    const hasExplain = !!attempt.explain;
    if (attempt.correct) return hasExplain ? 68 : 60;
    return hasExplain ? 84 : 76;
  }

  function buildAnalysisPages(data) {
    const agg = data.agg;
    const attempts = data.session.attempts || [];
    const pageW = 595;
    const pageH = 842;
    const marginX = 48;
    const contentW = 499;
    const marginBottom = 48;
    const topY = 790;

    let avgMs = 0;
    let fastest = null;
    let slowest = null;
    if (attempts.length) {
      let total = 0;
      fastest = attempts[0];
      slowest = attempts[0];
      attempts.forEach(function (a) {
        const d = a.duration_ms || 0;
        total += d;
        if (d < (fastest.duration_ms || 0)) fastest = a;
        if (d > (slowest.duration_ms || 0)) slowest = a;
      });
      avgMs = Math.round(total / attempts.length);
    }

    const pages = [];
    let ops = [];
    let y = topY;

    function flushPage() {
      if (ops.length) pages.push({ width: pageW, height: pageH, stream: ops.join("\n") });
      ops = [];
      y = topY;
      fillRect(ops, 0, 0, pageW, pageH, PDF_COLORS.white);
    }

    function ensureSpace(h) {
      if (y - h < marginBottom) flushPage();
    }

    function beginSection(title, reserve) {
      y -= PDF_SPACING.sectionTop;
      ensureSpace((reserve || 0) + PDF_SPACING.sectionTop + 40);
      y = drawSectionTitle(ops, marginX, y, title);
    }

    fillRect(ops, 0, 0, pageW, pageH, PDF_COLORS.white);
    pushTextOp(ops, marginX, y, "F2", 22, "Quiz Analysis", PDF_COLORS.accent);
    pushTextOp(ops, marginX, y - 24, "F1", 10, data.course + " - " + data.date, PDF_COLORS.muted);
    y -= 56;

    beginSection("Quest summary", 70);
    y = drawStatCards(
      ops,
      marginX,
      y,
      [
        { label: "Accuracy", value: pct(agg.accuracy) },
        { label: "Attempts", value: String(agg.total_attempts) },
        { label: "Correct", value: String(agg.correct_count) },
        { label: "Wrong", value: String(agg.wrong_count) },
        { label: "Avg time", value: fmtMsPdf(avgMs) },
      ],
      92,
      48,
      8
    );

    beginSection("Time analytics", 56);
    y = drawStatCards(
      ops,
      marginX,
      y,
      [
        { label: "Average / attempt", value: fmtMsPdf(avgMs) },
        {
          label: "Fastest",
          value: fastest ? fmtMsPdf(fastest.duration_ms) : "-",
        },
        {
          label: "Slowest",
          value: slowest ? fmtMsPdf(slowest.duration_ms) : "-",
        },
      ],
      156,
      48,
      10
    );
    if (fastest) {
      pushTextOp(
        ops,
        marginX,
        y,
        "F1",
        9,
        "Fastest: " + (fastest.module_title || fastest.module_id),
        PDF_COLORS.muted
      );
      y -= 14;
    }
    if (slowest) {
      pushTextOp(
        ops,
        marginX,
        y,
        "F1",
        9,
        "Slowest: " + (slowest.module_title || slowest.module_id),
        PDF_COLORS.muted
      );
      y -= 16;
    }
    y -= 4;

    y -= 4;

    const modRows = (agg.modules || []).map(function (m) {
      return [m.title || m.module_id, m.correct, m.wrong, fmtMsPdf(m.time_ms)];
    });
    beginSection("By module", 22 + modRows.length * 22 + 120);
    y = drawTable(ops, marginX, y, ["Module", "Correct", "Wrong", "Time"], modRows, [220, 60, 60, 70]);
    y -= PDF_SPACING.beforeSubBlock;
    y = drawBarChart(ops, marginX, y, agg.modules || [], contentW);

    const lvlRows = (agg.levels || []).map(function (l) {
      const state = (((agg.level_state || {})[l.module_id] || {})[l.difficulty]) || {};
      const status = state.cleared ? "cleared" : state.exhausted ? "exhausted" : "in progress";
      return [l.title || l.module_id, l.difficulty, l.correct, l.attempts, status, fmtMsPdf(l.time_ms)];
    });
    beginSection("By difficulty level", 22 + lvlRows.length * 22 + 20);
    y = drawTable(
      ops,
      marginX,
      y,
      ["Module", "Level", "Correct", "Attempts", "Status", "Time"],
      lvlRows,
      [130, 52, 52, 62, 68, 55]
    );

    beginSection("Progress path", 110);
    y = drawPathDiagram(ops, marginX, y, attempts, contentW, 96);

    beginSection("Each attempt", attemptCardHeight(attempts[0] || {}));
    attempts.forEach(function (a, i) {
      ensureSpace(attemptCardHeight(a) + PDF_SPACING.sectionTop);
      y = drawAttemptCard(ops, marginX, y, contentW, a, i);
    });

    if (ops.length) pages.push({ width: pageW, height: pageH, stream: ops.join("\n") });
    return pages;
  }

  function buildPdfBytes(data) {
    const pages = [buildCertificatePage(data)].concat(buildAnalysisPages(data));
    const pageCount = pages.length;
    const catalogObj = 1;
    const pagesObj = 2;
    const font1Obj = 3;
    const font2Obj = 4;
    const font3Obj = 5;
    const pageObjStart = 6;
    const contentObjStart = pageObjStart + pageCount;
    const objects = [];
    objects[catalogObj] = "<< /Type /Catalog /Pages 2 0 R >>";
    const kidRefs = [];
    for (let i = 0; i < pageCount; i++) {
      kidRefs.push(pageObjStart + i + " 0 R");
    }
    objects[pagesObj] = "<< /Type /Pages /Kids [" + kidRefs.join(" ") + "] /Count " + pageCount + " >>";
    objects[font1Obj] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>";
    objects[font2Obj] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>";
    objects[font3Obj] = "<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic >>";
    for (let i = 0; i < pageCount; i++) {
      const p = pages[i];
      objects[pageObjStart + i] =
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " +
        p.width +
        " " +
        p.height +
        "] /Resources << /Font << /F1 " +
        font1Obj +
        " 0 R /F2 " +
        font2Obj +
        " 0 R /F3 " +
        font3Obj +
        " 0 R >> >> /Contents " +
        (contentObjStart + i) +
        " 0 R >>";
      objects[contentObjStart + i] =
        "<< /Length " + p.stream.length + " >>\nstream\n" + p.stream + "\nendstream";
    }

    let pdf = "%PDF-1.4\n";
    const offsets = [0];
    for (let i = 1; i < objects.length; i++) {
      if (!objects[i]) continue;
      offsets[i] = pdf.length;
      pdf += i + " 0 obj\n" + objects[i] + "\nendobj\n";
    }
    const xrefStart = pdf.length;
    pdf += "xref\n0 " + objects.length + "\n";
    pdf += "0000000000 65535 f \n";
    for (let i = 1; i < objects.length; i++) {
      pdf += String(offsets[i] || 0).padStart(10, "0") + " 00000 n \n";
    }
    pdf +=
      "trailer\n<< /Size " +
      objects.length +
      " /Root 1 0 R >>\nstartxref\n" +
      xrefStart +
      "\n%%EOF";
    return new TextEncoder().encode(pdf);
  }

  function downloadCertificatePdf(session, identity, site) {
    const data = certificateData(session, identity, site);
    const bytes = buildPdfBytes(data);
    const blob = new Blob([bytes], { type: "application/pdf" });
    const a = document.createElement("a");
    const slug = (identity.name || "quest").replace(/\s+/g, "-").toLowerCase();
    a.href = URL.createObjectURL(blob);
    a.download = "certificate-" + slug + ".pdf";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  global.QCCertificate = {
    claimKey,
    markClaimed,
    isClaimed,
    mountForm,
    downloadCertificatePdf,
    certificateData,
  };
})(window);
