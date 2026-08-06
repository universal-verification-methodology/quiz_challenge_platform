/**
 * Build / submit quest result payloads (GitHub via server endpoint only).
 */
(function (global) {
  function buildPayload(session, identity, site) {
    const agg = global.QCSession.aggregates(session);
    const payload = {
      schema: "quiz_challenge_result_v1",
      submitted_at: new Date().toISOString(),
      identity: {
        name: identity.name || "",
        email: identity.email || "",
        testimony: identity.testimony || "",
        consent: !!identity.consent,
      },
      quest: {
        course_id: session.course_id,
        title: session.title,
        mode: session.mode || "full",
        session_id: session.session_id,
        started_at: session.started_at,
        completed_at: session.completed_at,
      },
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
    }
    return payload;
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
    downloadJson,
    submit,
    storeLocalCopy,
  };
})(window);
