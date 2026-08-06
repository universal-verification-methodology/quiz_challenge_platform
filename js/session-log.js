/**
 * Per-attempt session log + localStorage persistence.
 * Full and test modes use separate keys so they never mix.
 */
(function (global) {
  const KEYS = {
    full: "qc_session_v4_full",
    test: "qc_session_v4_test",
  };
  let activeMode = "full";

  function storageKey() {
    return KEYS[activeMode] || KEYS.full;
  }

  function setMode(mode) {
    activeMode = mode === "test" ? "test" : "full";
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

  function loadFrom(mode) {
    try {
      const raw = localStorage.getItem(KEYS[mode] || KEYS.full);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function load() {
    return loadFrom(activeMode);
  }

  function save(session) {
    localStorage.setItem(storageKey(), JSON.stringify(session));
  }

  function clear() {
    localStorage.removeItem(storageKey());
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
      answered_at,
      duration_ms,
      selected,
      correct: !!correct,
      timed_out: !!extra.timedOut,
      difficulty: open.difficulty,
      prompt: open.prompt,
      choices: open.choices,
      correct_answer: open.correct_answer,
      explain: open.explain,
    };
    session.attempts.push(record);
    if (correct) {
      const mid = open.module_id;
      session.module_correct[mid] = (session.module_correct[mid] || 0) + 1;
    }
    save(session);
    return record;
  }

  function aggregates(session) {
    const attempts = session.attempts || [];
    const total_ms = attempts.reduce((s, a) => s + (a.duration_ms || 0), 0);
    const correct = attempts.filter((a) => a.correct);
    const wrong = attempts.filter((a) => !a.correct);
    const byModule = {};
    const byLevel = {};
    attempts.forEach((a) => {
      if (!byModule[a.module_id]) {
        byModule[a.module_id] = {
          module_id: a.module_id,
          title: a.module_title,
          attempts: 0,
          correct: 0,
          wrong: 0,
          time_ms: 0,
        };
      }
      const m = byModule[a.module_id];
      m.attempts += 1;
      m.time_ms += a.duration_ms || 0;
      if (a.correct) m.correct += 1;
      else m.wrong += 1;

      const lk = a.module_id + "::" + (a.difficulty || "?");
      if (!byLevel[lk]) {
        byLevel[lk] = {
          module_id: a.module_id,
          title: a.module_title,
          difficulty: a.difficulty || "?",
          attempts: 0,
          correct: 0,
          wrong: 0,
          time_ms: 0,
        };
      }
      const L = byLevel[lk];
      L.attempts += 1;
      L.time_ms += a.duration_ms || 0;
      if (a.correct) L.correct += 1;
      else L.wrong += 1;
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
    KEYS,
    setMode,
    createSession,
    load,
    loadFrom,
    save,
    clear,
    startAttempt,
    finishAttempt,
    aggregates,
  };
})(window);
