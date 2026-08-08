/**
 * Build / submit quest result payloads (GitHub via server endpoint only).
 */
(function (global) {
  function buildPayload(session, identity, site) {
    const agg = global.QCSession.aggregates(session);
    const quest = {
      course_id: session.course_id,
      title: session.title,
      mode: session.mode || "full",
      session_id: session.session_id,
      started_at: session.started_at,
      completed_at: session.completed_at,
    };
    if (session.mode === "test") {
      const modTitle =
        session.short_module_title ||
        (agg.modules.length === 1
          ? agg.modules[0].title
          : agg.modules.map((m) => m.title).filter(Boolean).join(", ")) ||
        "";
      const modId =
        session.short_module_id ||
        (agg.modules.length === 1
          ? agg.modules[0].module_id
          : agg.modules.map((m) => m.module_id).filter(Boolean).join(",")) ||
        "";
      const difficulties = session.short_difficulties || ["easy", "medium", "hard"];
      const moduleCount = session.short_module_count || Math.max(1, agg.modules.length || 1);
      quest.module_id = modId;
      quest.module_title = modTitle;
      quest.module_count = moduleCount;
      quest.difficulties = difficulties.slice();
      quest.need_correct_per_difficulty =
        session.short_need_correct != null ? session.short_need_correct : 2;
      quest.max_levels =
        session.short_max_levels != null
          ? session.short_max_levels
          : moduleCount * difficulties.length;
    }
    const payload = {
      schema: "quiz_challenge_result_v1",
      submitted_at: new Date().toISOString(),
      identity: {
        name: identity.name || "",
        email: identity.email || "",
        testimony: identity.testimony || "",
        consent: !!identity.consent,
      },
      quest: quest,
      summary: {
        accuracy: agg.accuracy,
        total_attempts: agg.total_attempts,
        correct_count: agg.correct_count,
        wrong_count: agg.wrong_count,
        total_ms: agg.total_ms,
      },
      modules: agg.modules,
      levels: agg.levels,
      level_state: agg.level_state,
      attempts: session.attempts || [],
      site: {
        issuer: (site && site.certificate && site.certificate.issuer) || "Challenge Platform",
      },
    };
    if (global.QCBenchmark && typeof global.QCBenchmark.rowFromPayload === "function") {
      const row = global.QCBenchmark.rowFromPayload(payload);
      payload.benchmark = {
        score: row.score,
        cleared_levels: row.cleared_levels,
        max_levels: row.max_levels,
        median_ms: row.median_ms,
        timeouts: row.timeouts,
        display_name: row.display_name,
      };
      // Mirror into summary so GitHub/leaderboard can omit the attempts array.
      payload.summary.median_ms = row.median_ms;
      payload.summary.timeouts = row.timeouts;
    } else {
      const attempts = payload.attempts || [];
      const xs = attempts
        .map((a) => Number(a.duration_ms) || 0)
        .filter((n) => n >= 0)
        .sort((a, b) => a - b);
      let med = 0;
      if (xs.length) {
        const mid = Math.floor(xs.length / 2);
        med = xs.length % 2 ? xs[mid] : Math.round((xs[mid - 1] + xs[mid]) / 2);
      }
      payload.summary.median_ms = med;
      payload.summary.timeouts = attempts.filter((a) => a && a.timed_out).length;
    }
    return payload;
  }

  /**
   * Drop per-attempt detail before POSTing to GitHub Issues (65KB body limit).
   * Full quests can exceed that with hundreds of attempts; leaderboard only needs
   * summary + level_state + benchmark aggregates.
   */
  function slimLevelState(levelState) {
    const out = {};
    Object.keys(levelState || {}).forEach((mid) => {
      const mod = levelState[mid] || {};
      out[mid] = {};
      Object.keys(mod).forEach((d) => {
        const st = mod[d] || {};
        out[mid][d] = {
          correct: Number(st.correct) || 0,
          attempts: Number(st.attempts) || 0,
          cleared: !!st.cleared,
          exhausted: !!st.exhausted,
        };
      });
    });
    return out;
  }

  function slimForSubmit(payload) {
    if (!payload || typeof payload !== "object") return payload;
    const slim = Object.assign({}, payload);
    // Per-attempt rows blow past GitHub's ~65KB issue body on Full Quest.
    slim.attempts = [];
    slim.attempts_omitted = Number(
      (payload.summary && payload.summary.total_attempts) ||
        (payload.attempts && payload.attempts.length) ||
        0
    );
    slim.level_state = slimLevelState(payload.level_state);
    if (slim.summary && payload.benchmark) {
      if (slim.summary.median_ms == null) slim.summary.median_ms = payload.benchmark.median_ms;
      if (slim.summary.timeouts == null) slim.summary.timeouts = payload.benchmark.timeouts;
    }
    return slim;
  }

  function downloadJson(payload, filename) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename || "quest-result.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  async function submit(payload, site) {
    const endpoint = site && site.results && site.results.endpoint;
    if (!endpoint) {
      return {
        ok: false,
        skipped: true,
        reason: "No results.endpoint configured in config/site.json",
      };
    }
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    let body = null;
    try {
      body = await res.json();
    } catch (_) {
      body = null;
    }
    return {
      ok: res.ok,
      status: res.status,
      body,
      skipped: false,
    };
  }

  function storeLocalCopy(payload) {
    const key = "qc_submissions_v1";
    let list = [];
    try {
      list = JSON.parse(localStorage.getItem(key) || "[]");
    } catch (_) {
      list = [];
    }
    list.unshift({
      saved_at: new Date().toISOString(),
      session_id: payload.quest && payload.quest.session_id,
      name: payload.identity && payload.identity.name,
      email: payload.identity && payload.identity.email,
      accuracy: payload.summary && payload.summary.accuracy,
    });
    localStorage.setItem(key, JSON.stringify(list.slice(0, 50)));
    localStorage.setItem(
      "qc_last_submission_v1",
      JSON.stringify(payload)
    );
  }

  global.QCResults = {
    buildPayload,
    slimForSubmit,
    downloadJson,
    submit,
    storeLocalCopy,
  };
})(window);
