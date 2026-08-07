/**
 * Challenge controller — variable length; 1 correct per difficulty (max 10).
 * Short Quest: ?test=1|?short=1 → 1 random module, easy+medium (see content.profiles.test).
 * Full Quest: all course modules.
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

  const SHORT_FALLBACK = {
    title: "Digital Foundations Quest (Short)",
    module_count: 1,
    difficulties: ["easy", "medium", "hard"],
    need_correct_per_difficulty: 2,
    max_attempts_per_difficulty: 6,
  };

  function attachShortQuestMeta(session, profileContent) {
    if (session.mode !== "test") return;
    const mods = profileContent.modules || [];
    const difficulties =
      (profileContent.progress && profileContent.progress.difficulties) ||
      SHORT_FALLBACK.difficulties;
    session.short_module_count = mods.length;
    session.short_difficulties = difficulties.slice();
    session.short_need_correct =
      profileContent.progress && profileContent.progress.need_correct_per_difficulty != null
        ? Number(profileContent.progress.need_correct_per_difficulty)
        : SHORT_FALLBACK.need_correct_per_difficulty;
    session.short_max_levels = mods.length * difficulties.length;
    if (mods.length === 1) {
      session.short_module_id = mods[0].id;
      session.short_module_title = mods[0].title;
    } else if (mods.length > 1) {
      session.short_module_id = mods.map((m) => m.id).join(",");
      session.short_module_title = mods.map((m) => m.title).filter(Boolean).join(", ");
    }
  }

  function shuffleIds(ids) {
    const a = ids.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function pickModuleIds(modules, count, lockedIds, preferVideoStems) {
    let pool = modules || [];
    if (preferVideoStems) {
      const withVideo = pool.filter((m) => m && m.video_stems);
      if (withVideo.length) pool = withVideo;
    }
    const all = pool.map((m) => m.id);
    if (Array.isArray(lockedIds) && lockedIds.length) {
      const allow = {};
      all.forEach((id) => {
        allow[id] = true;
      });
      // Locked session may predate video preference; keep lock if still in full course.
      const fullAllow = {};
      (modules || []).forEach((m) => {
        fullAllow[m.id] = true;
      });
      const keptPreferred = lockedIds.filter((id) => allow[id]);
      if (keptPreferred.length) return keptPreferred;
      const keptAny = lockedIds.filter((id) => fullAllow[id]);
      if (keptAny.length) return keptAny;
    }
    const n = Math.max(1, Math.min(Number(count) || 3, all.length));
    return shuffleIds(all).slice(0, n);
  }

  function applyProfile(raw, profileName, opts) {
    const c = JSON.parse(JSON.stringify(raw));
    c.mode = profileName || "full";
    if (!profileName || profileName === "full") {
      return c;
    }

    // Prefer content.profiles.test; always fall back so short quest cannot silently run full.
    const p = Object.assign(
      {},
      SHORT_FALLBACK,
      (c.profiles && c.profiles[profileName]) || {}
    );

    c.title = p.title || c.title;

    const preferVideo = !!p.prefer_video_stems;
    let selectedIds = null;
    if (Array.isArray(p.module_ids) && p.module_ids.length) {
      selectedIds = pickModuleIds(
        c.modules,
        p.module_ids.length,
        p.module_ids,
        preferVideo
      );
    } else {
      const count = p.module_count != null ? Number(p.module_count) : 1;
      selectedIds = pickModuleIds(
        c.modules,
        count,
        opts && opts.module_ids,
        preferVideo
      );
    }

    if (selectedIds && selectedIds.length) {
      const allow = {};
      selectedIds.forEach((id, i) => {
        allow[id] = i + 1;
      });
      c.modules = (c.modules || [])
        .filter((m) => allow[m.id] != null)
        .map((m) => Object.assign({}, m, { order: allow[m.id] }));
      c.selected_module_ids = selectedIds.slice();
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
    // Invalidate stale full-quest sessions when opening short quest.
    c.version = String(c.version || "0") + "-short";
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
    return mode === "test" ? "report.html?short=1" : "report.html";
  }

  function shortQuestQuery() {
    return "short=1";
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
      mediaBase: CONTENT_BASE,
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

  async function showStemPreview(stemId) {
    const modules = content.modules || [];
    let found = null;
    let mod = null;
    for (let i = 0; i < modules.length; i++) {
      const bank = await loadBank(modules[i]);
      const item = (bank.items || []).find((it) => it.id === stemId);
      if (item) {
        found = item;
        mod = modules[i];
        break;
      }
    }
    if (!found) {
      if (els.status) {
        els.status.hidden = false;
        els.status.textContent = "Stem not found: " + stemId;
      }
      return;
    }
    if (els.moduleMeta) {
      els.moduleMeta.hidden = false;
      els.moduleMeta.className = "";
      els.moduleMeta.textContent = "Stem preview · " + mod.id + " · " + stemId;
    }
    if (els.progressTrack) els.progressTrack.hidden = true;
    QCQuiz.renderItem(els.quizRoot, found, {
      feedback: "report_only",
      mediaBase: CONTENT_BASE,
      timeLimitMs: QCQuiz.resolveTimeLimitMs(content, found, found.difficulty),
      warnBeforeMs: QCQuiz.resolveWarnBeforeMs(content),
      onGraded: () => {},
      onContinue: () => {
        if (els.status) {
          els.status.hidden = false;
          els.status.textContent = "Preview only — restart a quest to play for real.";
        }
      },
    });
  }

  function isShortParam(params) {
    return params.get("short") === "1" || params.get("test") === "1";
  }

  async function init() {
    const params = new URLSearchParams(location.search);
    mode = isShortParam(params) ? "test" : "full";
    QCSession.setMode(mode);

    let raw;
    try {
      raw = await loadJson(CONTENT_BASE + "/content.json?v=10");
    } catch (err) {
      if (els.status) {
        els.status.hidden = false;
        els.status.textContent =
          "Could not load content. Serve this folder over HTTP (not file://).";
      }
      console.error(err);
      return;
    }

    if (params.get("restart") === "1") QCSession.clear();

    // Lock short-quest module set from an in-progress session so resume stays stable.
    let lockedIds = null;
    if (mode === "test") {
      const existing = QCSession.load();
      if (
        existing &&
        existing.mode === "test" &&
        !existing.completed_at &&
        Array.isArray(existing.selected_module_ids) &&
        existing.selected_module_ids.length
      ) {
        lockedIds = existing.selected_module_ids;
      } else if (
        existing &&
        existing.mode === "test" &&
        !existing.completed_at &&
        Array.isArray(existing.module_order) &&
        existing.module_order.length
      ) {
        lockedIds = existing.module_order;
      }
    }

    content = applyProfile(raw, mode === "test" ? "test" : "full", {
      module_ids: lockedIds,
    });

    // Safety: short quest must not keep more modules than the profile allows.
    if (mode === "test") {
      const p = Object.assign(
        {},
        SHORT_FALLBACK,
        (raw.profiles && raw.profiles.test) || {}
      );
      const maxN =
        Array.isArray(p.module_ids) && p.module_ids.length
          ? p.module_ids.length
          : Number(p.module_count) || 1;
      if (content.modules && content.modules.length > maxN) {
        content = applyProfile(raw, "test", {
          module_ids: pickModuleIds(
            raw.modules,
            maxN,
            null,
            !!p.prefer_video_stems
          ),
        });
      }
    }

    els.title.textContent = content.title || "Challenge";
    const eyebrow = document.querySelector(".eyebrow");
    if (eyebrow && mode === "test") {
      const mod = (content.modules || [])[0];
      eyebrow.textContent = mod
        ? "Short Quest · " + mod.title
        : "Short Quest · 1 random module";
      if (mod) els.title.textContent = mod.title;
    }

    const restartLink = document.getElementById("restart-link");
    if (restartLink) {
      restartLink.href =
        mode === "test"
          ? "challenge.html?" + shortQuestQuery() + "&restart=1"
          : "challenge.html?restart=1";
    }

    const stemId = params.get("stem");
    if (stemId) {
      if (eyebrow) eyebrow.textContent = "Stem preview";
      els.title.textContent = "Video stem preview";
      await showStemPreview(stemId);
      return;
    }

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
      if (content.selected_module_ids) {
        session.selected_module_ids = content.selected_module_ids.slice();
      }
      attachShortQuestMeta(session, content);
      QCSession.save(session);
    } else if (!session.module_order || !session.module_order.length) {
      session.module_order = QCProgress.buildModuleOrder(content);
      session.mode = mode;
      if (content.selected_module_ids && !session.selected_module_ids) {
        session.selected_module_ids = content.selected_module_ids.slice();
      }
      attachShortQuestMeta(session, content);
      QCSession.save(session);
    } else if (mode === "test" && !session.short_module_title) {
      attachShortQuestMeta(session, content);
      QCSession.save(session);
    }

    console.info(
      "[challenge]",
      mode === "test" ? "short" : "full",
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
