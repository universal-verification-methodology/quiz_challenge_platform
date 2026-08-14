/**
 * Challenge controller — variable length; 1 correct per difficulty (max 10).
 * Short Quest: ?test=1|?short=1 → 1 random module, easy→medium→hard (see content.profiles.test).
 * Full Quest: all course modules.
 * Course pack: ?course=learn_digital|learn_verilog (see config/site.json).
 */
(function () {
  const DEFAULT_COURSE = "learn_digital";
  const DEFAULT_CONTENT_BASE = "content/learn_digital";
  /** Fallback if config/site.json fails so lab embeds still resolve. */
  const DEFAULT_TOOLS_BASE =
    "https://universal-verification-methodology.github.io/learning/tools";
  let content = null;
  let session = null;
  let bankCache = {};
  let openAttempt = null;
  let mode = "full";
  let toolsBase = DEFAULT_TOOLS_BASE;
  let courseId = DEFAULT_COURSE;
  let contentBase = DEFAULT_CONTENT_BASE;
  let siteConfig = null;

  const els = {
    title: document.getElementById("quest-title"),
    moduleMeta: document.getElementById("module-meta"),
    progressTrack: document.getElementById("progress-track"),
    quizRoot: document.getElementById("quiz-root"),
    status: document.getElementById("status-line"),
  };

  const SHORT_FALLBACK = {
    title: "Short Quest",
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

  function resolveCourse(params, site) {
    const allowed = (site && site.courses) || {};
    const fallback =
      (site && site.default_course) || DEFAULT_COURSE;
    let id = (params.get("course") || fallback || DEFAULT_COURSE).trim();
    if (!id) id = DEFAULT_COURSE;
    // If catalog missing (offline/misconfig), honor the query/default id.
    if (!Object.keys(allowed).length) return id;
    if (allowed[id]) return id;
    if (allowed[fallback]) return fallback;
    const keys = Object.keys(allowed);
    if (keys.length) return keys[0];
    return DEFAULT_COURSE;
  }

  function courseMeta(site, id) {
    const entry = (site && site.courses && site.courses[id]) || {};
    return {
      id: id,
      content_base: entry.content_base || "content/" + id,
      label: entry.label || id,
      eyebrow: entry.eyebrow || "",
    };
  }

  function courseQuery() {
    return "course=" + encodeURIComponent(courseId);
  }

  async function loadSite(params) {
    toolsBase = DEFAULT_TOOLS_BASE;
    siteConfig = null;
    try {
      const site = await loadJson("config/site.json?v=9");
      siteConfig = site;
      const fromSite =
        (site.tools && site.tools.base_url) ||
        (site.tools && site.tools.endpoint) ||
        "";
      if (fromSite) toolsBase = String(fromSite).replace(/\/+$/, "");
    } catch (err) {
      console.warn(
        "config/site.json unavailable; using default tools.base_url",
        err
      );
    }
    courseId = resolveCourse(params || new URLSearchParams(), siteConfig);
    const meta = courseMeta(siteConfig, courseId);
    contentBase = meta.content_base || DEFAULT_CONTENT_BASE;
    if (QCSession && QCSession.setCourse) QCSession.setCourse(courseId);
  }

  function quizRenderOpts(mod, item, extra) {
    const embedTools =
      !content.ux || content.ux.embed_tools !== false;
    const toolId = (item && item.tool_id) || (mod && mod.toolId) || "";
    const difficulty =
      (extra && extra.difficulty) || (item && item.difficulty) || null;
    const opts = Object.assign(
      {
        feedback: (content.ux && content.ux.feedback) || "report_only",
        mediaBase: contentBase,
        toolsBase: toolsBase,
        toolId: toolId,
        embedTools: embedTools,
        toolEmbedHeightPx:
          (content.ux && content.ux.tool_embed_height_px) || 3600,
        timeLimitMs: QCQuiz.resolveTimeLimitMs(content, item, difficulty),
        warnBeforeMs: QCQuiz.resolveWarnBeforeMs(content),
      },
      extra || {}
    );
    return opts;
  }

  async function loadBank(mod) {
    if (bankCache[mod.id]) return bankCache[mod.id];
    const bank = await loadJson(contentBase + "/" + mod.questions);
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
    const parts = [courseQuery()];
    if (mode === "test") parts.unshift("short=1");
    return "report.html?" + parts.join("&");
  }

  function shortQuestQuery() {
    return "short=1&" + courseQuery();
  }

  function fullQuestQuery() {
    return courseQuery();
  }

  function rewriteNavForCourse() {
    document.querySelectorAll("a[href*='challenge.html']").forEach((a) => {
      try {
        const url = new URL(a.getAttribute("href"), location.href);
        if (!url.pathname.endsWith("challenge.html")) return;
        url.searchParams.set("course", courseId);
        a.setAttribute(
          "href",
          url.pathname.split("/").pop() + url.search + url.hash
        );
      } catch (_) {}
    });
    document.querySelectorAll("a[href*='report.html']").forEach((a) => {
      try {
        const url = new URL(a.getAttribute("href"), location.href);
        if (!url.pathname.endsWith("report.html")) return;
        url.searchParams.set("course", courseId);
        a.setAttribute(
          "href",
          url.pathname.split("/").pop() + url.search + url.hash
        );
      } catch (_) {}
    });
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

    QCQuiz.renderItem(
      els.quizRoot,
      pick.item,
      quizRenderOpts(mod, pick.item, {
        difficulty: pick.difficulty,
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
      })
    );
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
    QCQuiz.renderItem(
      els.quizRoot,
      found,
      quizRenderOpts(mod, found, {
        onGraded: () => {},
        onContinue: () => {
          if (els.status) {
            els.status.hidden = false;
            els.status.textContent = "Preview only — restart a quest to play for real.";
          }
        },
      })
    );
  }

  function isShortParam(params) {
    return params.get("short") === "1" || params.get("test") === "1";
  }

  async function init() {
    const params = new URLSearchParams(location.search);
    mode = isShortParam(params) ? "test" : "full";
    QCSession.setMode(mode);

    await loadSite(params);
    rewriteNavForCourse();

    let raw;
    try {
      raw = await loadJson(contentBase + "/content.json?v=3");
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
          : "challenge.html?" + fullQuestQuery() + "&restart=1";
    }

    try {
      document.title =
        (mode === "test" ? "Short Quest · " : "Challenge · ") +
        (content.title || courseMeta(siteConfig, courseId).label);
    } catch (_) {}

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
