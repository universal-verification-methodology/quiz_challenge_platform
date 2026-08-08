/**
 * Per-difficulty progress within randomized modules.
 *
 * Rules (from content.progress):
 * - difficulties: easy → medium → hard
 * - need_correct_per_difficulty: 1
 * - max_attempts_per_difficulty: 10 (no question / prompt clones within a level)
 * - advance module when all difficulties are cleared or exhausted
 */
(function (global) {
  const DEFAULT_DIFFICULTIES = ["easy", "medium", "hard"];

  function cfg(content) {
    const p = (content && content.progress) || {};
    return {
      difficulties: p.difficulties || DEFAULT_DIFFICULTIES,
      needCorrect: p.need_correct_per_difficulty != null ? Number(p.need_correct_per_difficulty) : 1,
      maxAttempts: p.max_attempts_per_difficulty != null ? Number(p.max_attempts_per_difficulty) : 10,
      bankMultiplier: p.bank_multiplier != null ? Number(p.bank_multiplier) : 3,
    };
  }

  function recommendedBankSize(content) {
    const c = cfg(content);
    return c.maxAttempts * c.bankMultiplier;
  }

  function catalogModules(content) {
    return (content && content.modules ? content.modules.slice() : []).sort(
      (a, b) => (a.order || 0) - (b.order || 0)
    );
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function buildModuleOrder(content) {
    const ids = catalogModules(content).map((m) => m.id);
    const mode = content && content.ux && content.ux.module_order;
    return mode === "sequential" ? ids : shuffle(ids);
  }

  function modules(content, session) {
    const byId = {};
    catalogModules(content).forEach((m) => {
      byId[m.id] = m;
    });
    const order = (session && session.module_order) || catalogModules(content).map((m) => m.id);
    return order.map((id) => byId[id]).filter(Boolean);
  }

  function currentModule(content, session) {
    const list = modules(content, session);
    return list[session.current_module_index || 0] || null;
  }

  function ensureLevelState(session, moduleId, difficulty) {
    if (!session.level_state) session.level_state = {};
    if (!session.level_state[moduleId]) session.level_state[moduleId] = {};
    if (!session.level_state[moduleId][difficulty]) {
      session.level_state[moduleId][difficulty] = {
        correct: 0,
        attempts: 0,
        used_item_ids: [],
        cleared: false,
        exhausted: false,
      };
    }
    return session.level_state[moduleId][difficulty];
  }

  function levelStats(session, moduleId, difficulty) {
    return ensureLevelState(session, moduleId, difficulty);
  }

  function attemptsAtLevel(session, moduleId, difficulty) {
    return (session.attempts || []).filter(
      (a) => a.module_id === moduleId && a.difficulty === difficulty
    );
  }

  function currentDifficulty(content, session, moduleId) {
    const c = cfg(content);
    for (let i = 0; i < c.difficulties.length; i++) {
      const d = c.difficulties[i];
      const st = levelStats(session, moduleId, d);
      if (!st.cleared && !st.exhausted) return d;
    }
    return null;
  }

  function recordLevelOutcome(content, session, moduleId, difficulty, itemId, correct, bankCountAtDiff) {
    const c = cfg(content);
    const st = ensureLevelState(session, moduleId, difficulty);
    if (st.used_item_ids.indexOf(itemId) === -1) st.used_item_ids.push(itemId);
    st.attempts += 1;
    if (correct) st.correct += 1;
    if (st.correct >= c.needCorrect) {
      st.cleared = true;
    } else if (st.attempts >= c.maxAttempts || st.used_item_ids.length >= bankCountAtDiff) {
      st.exhausted = true;
    }
    global.QCSession.save(session);
    return st;
  }

  function moduleComplete(content, session, moduleId) {
    const c = cfg(content);
    return c.difficulties.every((d) => {
      const st = levelStats(session, moduleId, d);
      return st.cleared || st.exhausted;
    });
  }

  function advance(content, session) {
    const list = modules(content, session);
    const cur = list[session.current_module_index || 0];
    if (!cur || !moduleComplete(content, session, cur.id)) {
      return { advanced: false, complete: false };
    }
    const next = (session.current_module_index || 0) + 1;
    if (next >= list.length) {
      session.completed_at = new Date().toISOString();
      global.QCSession.save(session);
      return { advanced: false, complete: true };
    }
    session.current_module_index = next;
    global.QCSession.save(session);
    return { advanced: true, complete: false, module: list[next] };
  }

  function isComplete(session) {
    return !!session.completed_at;
  }

  /** Bounds for UI: best = modules×diffs×need, worst = modules×diffs×maxAttempts */
  function questBounds(content) {
    const c = cfg(content);
    const nMod = catalogModules(content).length;
    const nDiff = c.difficulties.length;
    return {
      best: nMod * nDiff * c.needCorrect,
      worst: nMod * nDiff * c.maxAttempts,
      recommended_bank_per_difficulty: c.maxAttempts * c.bankMultiplier,
    };
  }

  function progressHint(content, session, bank) {
    const mod = currentModule(content, session);
    if (!mod) return { label: "Complete", detail: "" };
    const diff = currentDifficulty(content, session, mod.id);
    const c = cfg(content);
    const bounds = questBounds(content);
    const answered = (session.attempts || []).length;
    if (!diff) {
      return {
        label: "Moving on…",
        detail: answered + " answered · span " + bounds.best + "–" + bounds.worst,
      };
    }
    const st = levelStats(session, mod.id, diff);
    return {
      label: "Question " + (answered + 1),
      detail:
        "Keep going until this level is cleared (silent) · " +
        answered +
        " done · typical " +
        bounds.best +
        "–" +
        bounds.worst,
      difficulty: diff,
      level_attempts: st.attempts,
      level_max: c.maxAttempts,
    };
  }

  function anonymousDots(content, session) {
    // Variable length — show answered attempts as done dots + one current.
    const attempts = session.attempts || [];
    const dots = attempts.map(() => ({ status: "done" }));
    if (!session.completed_at) dots.push({ status: "current" });
    return dots;
  }

  global.QCProgress = {
    DEFAULT_DIFFICULTIES,
    cfg,
    recommendedBankSize,
    catalogModules,
    buildModuleOrder,
    modules,
    currentModule,
    ensureLevelState,
    levelStats,
    attemptsAtLevel,
    currentDifficulty,
    recordLevelOutcome,
    moduleComplete,
    advance,
    isComplete,
    questBounds,
    progressHint,
    anonymousDots,
  };
})(window);
