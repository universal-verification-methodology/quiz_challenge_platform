/**
 * Per-attempt session log + localStorage persistence.
 * Full and Short Quest modes use separate keys so they never mix.
 * Keys are also scoped by course_id so packs do not overwrite each other.
 */
(function (global) {
  const KEY_PREFIX = {
    full: "qc_session_v4_full",
    test: "qc_session_v4_test",
  };
  /** @deprecated legacy unscoped keys (pre multi-course) */
  const LEGACY_KEYS = {
    full: "qc_session_v4_full",
    test: "qc_session_v4_test",
  };
  let activeMode = "full";
  let activeCourse = "";

  function storageKey(mode, courseId) {
    const m = mode === "test" ? "test" : "full";
    const base = KEY_PREFIX[m] || KEY_PREFIX.full;
    const c = courseId != null ? courseId : activeCourse;
    return c ? base + "__" + c : base;
  }

  function setMode(mode) {
    activeMode = mode === "test" ? "test" : "full";
  }

  function setCourse(courseId) {
    activeCourse = courseId ? String(courseId) : "";
  }

  function createSession(courseId, title, opts) {
    opts = opts || {};
    return {
      session_id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
      course_id: courseId,
      title: title || courseId,
      mode: activeMode,
      started_at: new Date().toISOString(),
      completed_at: null,
      attempts: [],
      module_correct: {},
      current_module_index: 0,
      module_order: opts.module_order || null,
    };
  }

  function readKey(key) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function loadFrom(mode, courseId) {
    const scoped = readKey(storageKey(mode, courseId));
    if (scoped) return scoped;
    // Migrate legacy unscoped session if it matches this course (or course unknown).
    const legacy = readKey(LEGACY_KEYS[mode === "test" ? "test" : "full"]);
    if (!legacy) return null;
    const want = courseId != null ? courseId : activeCourse;
    if (want && legacy.course_id && legacy.course_id !== want) return null;
    return legacy;
  }

  function load() {
    return loadFrom(activeMode, activeCourse);
  }

  function save(session) {
    if (session && session.course_id) setCourse(session.course_id);
    localStorage.setItem(storageKey(activeMode, activeCourse), JSON.stringify(session));
  }

  function clear() {
    localStorage.removeItem(storageKey(activeMode, activeCourse));
    // Also clear legacy key when it belongs to this course / is empty course.
    try {
      const legacy = readKey(LEGACY_KEYS[activeMode]);
      if (
        legacy &&
        (!activeCourse || !legacy.course_id || legacy.course_id === activeCourse)
      ) {
        localStorage.removeItem(LEGACY_KEYS[activeMode]);
      }
    } catch (_) {}
  }

  function startAttempt(session, meta) {
    return {
      course_id: session.course_id,
      module_id: meta.module_id,
      module_title: meta.module_title || meta.module_id,
      item_id: meta.item_id,
      attempt_index: meta.attempt_index || 1,
      started_at: new Date().toISOString(),
      started_ms: performance.now(),
      difficulty: meta.difficulty || null,
      prompt: meta.prompt || "",
      choices: meta.choices || null,
      correct_answer: meta.correct_answer,
      explain: meta.explain || "",
    };
  }

  function finishAttempt(session, open, selected, correct, extra) {
    extra = extra || {};
    const answered_at = new Date().toISOString();
    const duration_ms = Math.max(0, Math.round(performance.now() - open.started_ms));
    const record = {
      course_id: open.course_id,
      module_id: open.module_id,
      module_title: open.module_title,
      item_id: open.item_id,
      attempt_index: open.attempt_index,
      started_at: open.started_at,
      answered_at: answered_at,
      duration_ms: duration_ms,
      difficulty: open.difficulty,
      prompt: open.prompt,
      choices: open.choices,
      selected: selected,
      correct_answer: open.correct_answer,
      correct: !!correct,
      explain: open.explain,
      timed_out: !!(extra.timed_out || extra.timedOut),
    };
    session.attempts.push(record);
    if (correct) {
      if (!session.module_correct[open.module_id]) session.module_correct[open.module_id] = 0;
      session.module_correct[open.module_id] += 1;
    }
    return record;
  }

  function aggregates(session) {
    const attempts = session.attempts || [];
    const correct = attempts.filter((a) => a && a.correct);
    const wrong = attempts.filter((a) => a && !a.correct);
    const total_ms = attempts.reduce((s, a) => s + (a.duration_ms || 0), 0);
    const byModule = {};
    const byLevel = {};
    attempts.forEach((a) => {
      if (!a) return;
      if (!byModule[a.module_id]) {
        byModule[a.module_id] = {
          id: a.module_id,
          title: a.module_title || a.module_id,
          attempts: 0,
          correct: 0,
          ms: 0,
        };
      }
      byModule[a.module_id].attempts += 1;
      byModule[a.module_id].ms += a.duration_ms || 0;
      if (a.correct) byModule[a.module_id].correct += 1;

      const lvl = a.difficulty || "unknown";
      if (!byLevel[lvl]) {
        byLevel[lvl] = { difficulty: lvl, attempts: 0, correct: 0, ms: 0 };
      }
      byLevel[lvl].attempts += 1;
      byLevel[lvl].ms += a.duration_ms || 0;
      if (a.correct) byLevel[lvl].correct += 1;
    });
    const level_state = session.level_state || {};
    return {
      total_attempts: attempts.length,
      correct_count: correct.length,
      wrong_count: wrong.length,
      total_ms,
      accuracy: attempts.length ? correct.length / attempts.length : 0,
      modules: Object.values(byModule),
      levels: Object.values(byLevel),
      level_state,
    };
  }

  global.QCSession = {
    KEY_PREFIX,
    setMode,
    setCourse,
    createSession,
    load,
    loadFrom,
    save,
    clear,
    startAttempt,
    finishAttempt,
    aggregates,
    storageKey,
  };
})(window);
