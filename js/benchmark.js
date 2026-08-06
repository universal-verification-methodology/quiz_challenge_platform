/**
 * Public leaderboard helpers: name masking + composite benchmark score.
 */
(function (global) {
  function maskName(name) {
    const raw = String(name || "Anonymous").trim() || "Anonymous";
    let kept = 0;
    let out = "";
    for (let i = 0; i < raw.length; i++) {
      const ch = raw[i];
      if (/\s/.test(ch)) {
        out += " ";
        continue;
      }
      if (kept < 2) {
        out += ch;
        kept += 1;
      } else {
        out += "X";
      }
    }
    if (kept < 2) out += "X".repeat(2 - kept);
    return out;
  }

  function countCleared(levelState) {
    let n = 0;
    Object.keys(levelState || {}).forEach((mid) => {
      const mod = levelState[mid] || {};
      Object.keys(mod).forEach((d) => {
        if (mod[d] && mod[d].cleared) n += 1;
      });
    });
    return n;
  }

  function countModulesTouched(levelState, modules) {
    if (Array.isArray(modules) && modules.length) {
      return modules.filter((m) => (m.attempts || 0) > 0 || (m.correct || 0) > 0).length;
    }
    return Object.keys(levelState || {}).length;
  }

  function inferMaxLevels(payload) {
    const quest = (payload && payload.quest) || {};
    const bench = (payload && payload.benchmark) || {};
    if (bench.max_levels != null) return Number(bench.max_levels);
    if (quest.mode === "test") return 4;
    const ls = payload.level_state || {};
    let slots = 0;
    Object.keys(ls).forEach((mid) => {
      slots += Object.keys(ls[mid] || {}).length;
    });
    if (slots >= 6) return slots;
    return 9;
  }

  function medianMs(attempts) {
    const xs = (attempts || [])
      .map((a) => Number(a.duration_ms) || 0)
      .filter((n) => n >= 0)
      .sort((a, b) => a - b);
    if (!xs.length) return 0;
    const mid = Math.floor(xs.length / 2);
    return xs.length % 2 ? xs[mid] : Math.round((xs[mid - 1] + xs[mid]) / 2);
  }

  function countTimeouts(attempts) {
    return (attempts || []).filter((a) => a && a.timed_out).length;
  }

  /**
   * Score = 1000×(cleared/max) + 100×accuracy − 5×timeouts − time_penalty
   * Higher is better. time_penalty = min(40, round(median_s)).
   */
  function compositeScore(input) {
    const cleared = Number(input.cleared_levels) || 0;
    const maxLevels = Math.max(1, Number(input.max_levels) || 1);
    const accuracy = Math.max(0, Math.min(1, Number(input.accuracy) || 0));
    const timeouts = Number(input.timeouts) || 0;
    const median = Number(input.median_ms) || 0;
    const timePenalty = Math.min(40, Math.round(median / 1000));
    return Math.round(
      1000 * (cleared / maxLevels) + 100 * accuracy - 5 * timeouts - timePenalty
    );
  }

  function rowFromPayload(payload) {
    const summary = (payload && payload.summary) || {};
    const quest = (payload && payload.quest) || {};
    const identity = (payload && payload.identity) || {};
    const attempts = (payload && payload.attempts) || [];
    const levelState = payload.level_state || {};
    const cleared = countCleared(levelState);
    const maxLevels = inferMaxLevels(payload);
    const timeouts = countTimeouts(attempts);
    const med = medianMs(attempts);
    const accuracy = Number(summary.accuracy) || 0;
    const score = compositeScore({
      cleared_levels: cleared,
      max_levels: maxLevels,
      accuracy,
      timeouts,
      median_ms: med,
    });
    return {
      display_name: maskName(identity.name),
      score,
      accuracy,
      accuracy_pct: Math.round(accuracy * 100),
      total_attempts: Number(summary.total_attempts) || attempts.length || 0,
      correct_count: Number(summary.correct_count) || 0,
      wrong_count: Number(summary.wrong_count) || 0,
      cleared_levels: cleared,
      max_levels: maxLevels,
      modules_touched: countModulesTouched(levelState, payload.modules),
      median_ms: med,
      total_ms: Number(summary.total_ms) || 0,
      timeouts,
      mode: quest.mode || "full",
      course_id: quest.course_id || "",
      completed_at: quest.completed_at || payload.submitted_at || "",
      session_id: quest.session_id || "",
    };
  }

  function fmtMs(ms) {
    const s = Math.round((ms || 0) / 1000);
    if (s < 60) return s + "s";
    const m = Math.floor(s / 60);
    return m + "m " + (s % 60) + "s";
  }

  function addRanksAndPercentiles(rows) {
    const sorted = (rows || []).slice().sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      if (b.accuracy !== a.accuracy) return b.accuracy - a.accuracy;
      return (a.median_ms || 0) - (b.median_ms || 0);
    });
    const n = sorted.length;
    return sorted.map((row, i) => {
      const rank = i + 1;
      const percentile = n <= 1 ? 100 : Math.round((100 * (n - rank)) / (n - 1));
      return Object.assign({}, row, { rank, percentile });
    });
  }

  global.QCBenchmark = {
    maskName,
    countCleared,
    inferMaxLevels,
    medianMs,
    countTimeouts,
    compositeScore,
    rowFromPayload,
    fmtMs,
    addRanksAndPercentiles,
  };
})(window);
