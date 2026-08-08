/**
 * Public leaderboard helpers: name masking + composite benchmark score.
 */
(function (global) {
  function maskName(name) {
    const raw = String(name || "Anonymous").trim() || "Anonymous";
    // "Yongfu Li" → "Yxxxxx Lx" (keep first letter of each word)
    return raw.replace(/[^\s]+/g, (word) => {
      if (word.length <= 1) return word;
      return word[0] + "x".repeat(word.length - 1);
    });
  }

  /** Always report easy/medium/hard for the dashboard Correct E/M/H column. */
  const DISPLAY_DIFFICULTIES = ["easy", "medium", "hard"];

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

  /** Cleared counts per difficulty ladder (defaults to easy / medium / hard). */
  function clearedByDifficulty(levelState, difficulties) {
    const diffs =
      Array.isArray(difficulties) && difficulties.length
        ? difficulties
        : DISPLAY_DIFFICULTIES;
    const counts = diffs.map(() => 0);
    Object.keys(levelState || {}).forEach((mid) => {
      const mod = levelState[mid] || {};
      diffs.forEach((d, i) => {
        if (mod[d] && mod[d].cleared) counts[i] += 1;
      });
    });
    return counts;
  }

  function formatClearedBreakdown(counts) {
    if (!Array.isArray(counts) || !counts.length) return "";
    // Pad/truncate to E/M/H so the board never shows "2/3" total ratios.
    const padded = DISPLAY_DIFFICULTIES.map((_, i) =>
      Number(counts[i]) || 0
    );
    return padded.join("/");
  }

  function countModulesTouched(levelState, modules) {
    if (Array.isArray(modules) && modules.length) {
      return modules.filter((m) => (m.attempts || 0) > 0 || (m.correct || 0) > 0).length;
    }
    return Object.keys(levelState || {}).length;
  }

  function resolveModuleTitle(payload) {
    const quest = (payload && payload.quest) || {};
    if (quest.module_title) return String(quest.module_title);
    const modules = (payload && payload.modules) || [];
    if (modules.length === 1 && modules[0].title) return String(modules[0].title);
    if (modules.length > 1) {
      const titles = modules.map((m) => m && m.title).filter(Boolean);
      if (titles.length) return titles.join(", ");
    }
    const attempts = (payload && payload.attempts) || [];
    if (attempts[0] && attempts[0].module_title) return String(attempts[0].module_title);
    return "";
  }

  function inferMaxLevels(payload) {
    const quest = (payload && payload.quest) || {};
    const bench = (payload && payload.benchmark) || {};
    if (bench.max_levels != null) return Number(bench.max_levels);
    if (quest.max_levels != null) return Number(quest.max_levels);
    if (quest.mode === "test") {
      const nMods = Number(quest.module_count) || 1;
      const diffs = Array.isArray(quest.difficulties) ? quest.difficulties.length : 3;
      return nMods * diffs;
    }
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
    const bench = (payload && payload.benchmark) || {};
    const levelState = payload.level_state || {};
    const cleared = countCleared(levelState);
    const maxLevels = inferMaxLevels(payload);
    // Prefer aggregates when attempts were omitted for GitHub size limits.
    const timeouts =
      attempts.length > 0
        ? countTimeouts(attempts)
        : Number(
            summary.timeouts != null
              ? summary.timeouts
              : bench.timeouts != null
                ? bench.timeouts
                : 0
          ) || 0;
    const med =
      attempts.length > 0
        ? medianMs(attempts)
        : Number(
            summary.median_ms != null
              ? summary.median_ms
              : bench.median_ms != null
                ? bench.median_ms
                : 0
          ) || 0;
    const accuracy = Number(summary.accuracy) || 0;
    // Always E/M/H for the public board column (zeros if a ladder was not played).
    const clearedCounts = clearedByDifficulty(levelState, DISPLAY_DIFFICULTIES);
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
      cleared_by_difficulty: clearedCounts,
      cleared_label: formatClearedBreakdown(clearedCounts),
      modules_touched: countModulesTouched(levelState, payload.modules),
      median_ms: med,
      total_ms: Number(summary.total_ms) || 0,
      timeouts,
      mode: quest.mode || "full",
      module_title: quest.mode === "test" ? resolveModuleTitle(payload) : "",
      module_id:
        quest.mode === "test"
          ? String(
              quest.module_id ||
                (payload.modules && payload.modules[0] && payload.modules[0].module_id) ||
                ""
            )
          : "",
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
    clearedByDifficulty,
    formatClearedBreakdown,
    inferMaxLevels,
    resolveModuleTitle,
    medianMs,
    countTimeouts,
    compositeScore,
    rowFromPayload,
    fmtMs,
    addRanksAndPercentiles,
  };
})(window);
