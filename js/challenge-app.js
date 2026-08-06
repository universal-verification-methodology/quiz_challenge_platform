/**
 * Challenge controller — variable length; 1 correct per difficulty (max 10).
 * Test mode: ?test=1 → 2 modules, 2 difficulties (see content.profiles.test).
 */
(function () {
  const CONTENT_BASE = "content/learn_digital";
  let content = null;
  let session = null;
  let bankCache = {};
  let openAttempt = null;
  let mode = "full";

  const els = {
    title: document.getElementById("quest-title"),
    moduleMeta: document.getElementById("module-meta"),
    progressTrack: document.getElementById("progress-track"),
    quizRoot: document.getElementById("quiz-root"),
    status: document.getElementById("status-line"),
  };

  const TEST_FALLBACK = {
    title: "Digital Foundations Quest (test)",
    module_ids: ["module01-radix-converter", "module13-kmap"],
    difficulties: ["easy", "medium"],
    max_attempts_per_difficulty: 3,
  };

  function applyProfile(raw, profileName) {
    const c = JSON.parse(JSON.stringify(raw));
    c.mode = profileName || "full";
    if (!profileName || profileName === "full") {
      return c;
    }

    // Prefer content.profiles.test; always fall back so ?test=1 cannot silently run full quest.
    const p = Object.assign(
      {},
      TEST_FALLBACK,
      (c.profiles && c.profiles[profileName]) || {}
    );

    c.title = p.title || c.title;
    if (Array.isArray(p.module_ids) && p.module_ids.length) {
      const allow = {};
      p.module_ids.forEach((id, i) => {
        allow[id] = i + 1;
      });
      c.modules = (c.modules || [])
        .filter((m) => allow[m.id] != null)
        .map((m) => Object.assign({}, m, { order: allow[m.id] }));
    }
    if (!c.progress) c.progress = {};
    if (Array.isArray(p.difficulties) && p.difficulties.length) {
      c.progress.difficulties = p.difficulties.slice();
    }
    if (p.max_attempts_per_difficulty != null) {
      c.progress.max_attempts_per_difficulty = Number(p.max_attempts_per_difficulty);
    }
    if (p.need_correct_per_difficulty != null) {
      c.progress.need_correct_per_difficulty = Number(p.need_correct_per_difficulty);
    }
    // Invalidate stale full-quest sessions when opening test.
    c.version = String(c.version || "0") + "-test";
    return c;
  }

  async function loadJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to load " + url);
    return res.json();
  }

  async function loadBank(mod) {
    if (bankCache[mod.id]) return bankCache[mod.id];
    const bank = await loadJson(CONTENT_BASE + "/" + mod.questions);
    bankCache[mod.id] = bank;
    return bank;
  }

  function renderProgress() {
    const dots = QCProgress.anonymousDots(content, session);
    els.progressTrack.innerHTML = "";
    const maxShow = 40;
    const start = Math.max(0, dots.length - maxShow);
    dots.slice(start).forEach((d, i) => {
      const li = document.createElement("li");
      li.className = d.status;
      li.innerHTML = "<span class=\"n\">" + (start + i + 1) + "</span>";
      els.progressTrack.appendChild(li);
    });
  }

  function reportUrl() {
    return mode === "test" ? "report.html?test=1" : "report.html";
  }

  async function showCurrent() {
    if (QCProgress.isComplete(session) || session.completed_at) {
      session.completed_at = session.completed_at || new Date().toISOString();
      QCSession.save(session);
      location.href = reportUrl();
      return;
    }

    const mod = QCProgress.currentModule(content, session);
    if (!mod) {
      if (els.status) {
        els.status.hidden = false;
        els.status.textContent = "No questions available.";
      }
      return;
    }

    const bank = await loadBank(mod);

    if (QCProgress.moduleComplete(content, session, mod.id)) {
      const result = QCProgress.advance(content, session);
      if (result.complete) {
        location.href = reportUrl();
        return;
      }
      return showCurrent();
    }

    let pick = QCAdaptive.pickNext(content, bank, session, mod.id);
    let guard = 0;
    while (!pick && guard++ < 12) {
      const diff = QCProgress.currentDifficulty(content, session, mod.id);
      if (!diff) break;
      const st = QCProgress.levelStats(session, mod.id, diff);
      st.exhausted = true;
      QCSession.save(session);
      if (QCProgress.moduleComplete(content, session, mod.id)) {
        const result = QCProgress.advance(content, session);
        if (result.complete) {
          location.href = reportUrl();
          return;
        }
        return showCurrent();
      }
      pick = QCAdaptive.pickNext(content, bank, session, mod.id);
    }

    if (!pick) {
      if (QCProgress.moduleComplete(content, session, mod.id)) {
        const result = QCProgress.advance(content, session);
        if (result.complete) {
          location.href = reportUrl();
          return;
        }
        return showCurrent();
      }
      if (els.status) els.status.textContent = "";
      return;
    }

    renderProgress();

    openAttempt = QCSession.startAttempt(session, {
      module_id: mod.id,
      module_title: mod.title,
      item_id: pick.item.id,
      attempt_index: pick.attempt_index,
      difficulty: pick.difficulty,
      prompt: pick.item.prompt,
      choices: pick.item.choices || null,
      correct_answer: pick.item.answer,
      explain: pick.item.explain || "",
    });

    QCQuiz.renderItem(els.quizRoot, pick.item, {
      feedback: (content.ux && content.ux.feedback) || "report_only",
      timeLimitMs: QCQuiz.resolveTimeLimitMs(content, pick.item, pick.difficulty),
      warnBeforeMs: QCQuiz.resolveWarnBeforeMs(content),
      onGraded: ({ selected, correct, timedOut }) => {
        QCSession.finishAttempt(session, openAttempt, selected, correct, {
          timedOut: !!timedOut,
        });
        QCProgress.recordLevelOutcome(
          content,
          session,
          mod.id,
          pick.difficulty,
          pick.item.id,
          correct,
          pick.bank_count
        );
        openAttempt = null;
      },
      onContinue: () => {
        showCurrent();
      },
    });
  }

  async function init() {
    const params = new URLSearchParams(location.search);
    mode = params.get("test") === "1" ? "test" : "full";
    QCSession.setMode(mode);

    try {
      const raw = await loadJson(CONTENT_BASE + "/content.json?v=5");
      content = applyProfile(raw, mode === "test" ? "test" : "full");
    } catch (err) {
      if (els.status) {
        els.status.hidden = false;
        els.status.textContent =
          "Could not load content. Serve this folder over HTTP (not file://).";
      }
      console.error(err);
      return;
    }

    // Safety: test mode must never keep the full module list.
    if (mode === "test" && content.modules && content.modules.length > 2) {
      content = applyProfile(
        Object.assign({}, content, {
          modules: content.modules,
          profiles: { test: TEST_FALLBACK },
        }),
        "test"
      );
    }

    els.title.textContent = content.title || "Challenge";
    const eyebrow = document.querySelector(".eyebrow");
    if (eyebrow && mode === "test") eyebrow.textContent = "Test mode · shortened quest";

    const restartLink = document.getElementById("restart-link");
    if (restartLink) {
      restartLink.href =
        mode === "test" ? "challenge.html?test=1&restart=1" : "challenge.html?restart=1";
    }

    if (params.get("restart") === "1") QCSession.clear();

    session = QCSession.load();
    const allowedIds = (content.modules || []).map((m) => m.id);
    const orderInvalid =
      session &&
      Array.isArray(session.module_order) &&
      session.module_order.some((id) => allowedIds.indexOf(id) === -1);
    const modeMismatch = session && session.mode !== mode;

    if (
      !session ||
      modeMismatch ||
      orderInvalid ||
      session.course_id !== content.id ||
      session.completed_at ||
      session.content_version !== content.version
    ) {
      if (
        session &&
        session.completed_at &&
        params.get("restart") !== "1" &&
        session.content_version === content.version &&
        session.mode === mode &&
        !orderInvalid
      ) {
        location.href = reportUrl();
        return;
      }
      session = QCSession.createSession(content.id, content.title, {
        module_order: QCProgress.buildModuleOrder(content),
      });
      session.content_version = content.version;
      session.mode = mode;
      session.level_state = {};
      QCSession.save(session);
    } else if (!session.module_order || !session.module_order.length) {
      session.module_order = QCProgress.buildModuleOrder(content);
      session.mode = mode;
      QCSession.save(session);
    }

    console.info(
      "[challenge]",
      mode,
      "modules",
      (content.modules || []).map((m) => m.id),
      "diffs",
      content.progress.difficulties,
      "maxAttempts",
      content.progress.max_attempts_per_difficulty,
      "bounds",
      QCProgress.questBounds(content)
    );

    await showCurrent();
  }

  init();
})();
