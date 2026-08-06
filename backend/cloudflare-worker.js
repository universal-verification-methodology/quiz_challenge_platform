/**
 * Cloudflare Worker: POST results → GitHub Issue; GET /leaderboard → public board.
 *
 * Secrets: GITHUB_TOKEN
 * Vars: GITHUB_OWNER, GITHUB_REPO, ALLOW_ORIGIN (optional)
 */
function corsHeaders(env) {
  const origin = env.ALLOW_ORIGIN || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(data, status, env) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
      ...corsHeaders(env),
    },
  });
}

function maskName(name) {
  const raw = String(name || "Anonymous").trim() || "Anonymous";
  // "Yongfu Li" → "Yxxxxx Lx" (keep first letter of each word)
  return raw.replace(/[^\s]+/g, (word) => {
    if (word.length <= 1) return word;
    return word[0] + "x".repeat(word.length - 1);
  });
}

function countCleared(levelState) {
  let n = 0;
  for (const mid of Object.keys(levelState || {})) {
    const mod = levelState[mid] || {};
    for (const d of Object.keys(mod)) {
      if (mod[d] && mod[d].cleared) n += 1;
    }
  }
  return n;
}

function inferMaxLevels(payload) {
  const quest = (payload && payload.quest) || {};
  const bench = (payload && payload.benchmark) || {};
  if (bench.max_levels != null) return Number(bench.max_levels);
  if (quest.mode === "test") return 4;
  const ls = payload.level_state || {};
  let slots = 0;
  for (const mid of Object.keys(ls)) slots += Object.keys(ls[mid] || {}).length;
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

function extractPayloadFromIssueBody(body) {
  const text = String(body || "");
  const marker = "## Full payload";
  const idx = text.indexOf(marker);
  const slice = idx >= 0 ? text.slice(idx) : text;
  const match = slice.match(/```json\s*([\s\S]*?)```/);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch (_) {
    return null;
  }
}

function publicRow(payload, meta) {
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
  const emailKey = String(identity.email || "")
    .trim()
    .toLowerCase();
  return {
    display_name: maskName(identity.name),
    score: compositeScore({
      cleared_levels: cleared,
      max_levels: maxLevels,
      accuracy,
      timeouts,
      median_ms: med,
    }),
    accuracy,
    accuracy_pct: Math.round(accuracy * 100),
    total_attempts: Number(summary.total_attempts) || attempts.length || 0,
    correct_count: Number(summary.correct_count) || 0,
    wrong_count: Number(summary.wrong_count) || 0,
    cleared_levels: cleared,
    max_levels: maxLevels,
    modules_touched: Object.keys(levelState).length,
    median_ms: med,
    total_ms: Number(summary.total_ms) || 0,
    timeouts,
    mode: quest.mode || "full",
    course_id: quest.course_id || "",
    completed_at: quest.completed_at || payload.submitted_at || meta.created_at || "",
    session_id: quest.session_id || "",
    _email_key: emailKey,
  };
}

async function sha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function fetchIssues(env, labels) {
  const owner = env.GITHUB_OWNER;
  const repo = env.GITHUB_REPO;
  const token = env.GITHUB_TOKEN;
  const url =
    `https://api.github.com/repos/${owner}/${repo}/issues` +
    `?state=all&labels=${encodeURIComponent(labels)}&per_page=100&sort=created&direction=desc`;
  const headers = {
    Accept: "application/vnd.github+json",
    "User-Agent": "quiz-challenge-platform-worker",
  };
  // Token preferred (private repos / higher rate limit). Public repos can list without it.
  if (token) headers.Authorization = `Bearer ${token}`;
  const gh = await fetch(url, { headers });
  const data = await gh.json().catch(() => []);
  if (!gh.ok) {
    const err = new Error("GitHub list failed");
    err.status = gh.status;
    err.detail = data;
    throw err;
  }
  return Array.isArray(data) ? data : [];
}

async function buildLeaderboard(env, mode) {
  const want = mode === "test" ? "test" : "full";
  const label = want === "test" ? "quest-result,test-mode" : "quest-result,full-mode";
  const issues = await fetchIssues(env, label);
  const bestByKey = new Map();

  for (const issue of issues) {
    if (issue.pull_request) continue;
    const payload = extractPayloadFromIssueBody(issue.body);
    if (!payload || payload.schema !== "quiz_challenge_result_v1") continue;
    if (!payload.identity || !payload.identity.consent) continue;
    const questMode = (payload.quest && payload.quest.mode) || "full";
    if (questMode !== want) continue;

    const row = publicRow(payload, { created_at: issue.created_at });
    const key =
      row._email_key ||
      (row.session_id ? "sid:" + row.session_id : "issue:" + issue.number);
    const prev = bestByKey.get(key);
    if (!prev || row.score > prev.score) {
      bestByKey.set(key, row);
    }
  }

  const rows = [];
  for (const row of bestByKey.values()) {
    const emailKey = row._email_key;
    delete row._email_key;
    if (emailKey) {
      row.player_key = (await sha256Hex(emailKey)).slice(0, 12);
    } else {
      row.player_key = (row.session_id || "anon").slice(0, 12);
    }
    rows.push(row);
  }

  rows.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (b.accuracy !== a.accuracy) return b.accuracy - a.accuracy;
    return (a.median_ms || 0) - (b.median_ms || 0);
  });

  const n = rows.length;
  rows.forEach((row, i) => {
    row.rank = i + 1;
    row.top_pct = n <= 0 ? 100 : Math.max(1, Math.ceil((100 * row.rank) / n));
    row.percentile = n <= 1 ? 100 : Math.round((100 * (n - row.rank)) / (n - 1));
  });

  return {
    ok: true,
    mode: want,
    generated_at: new Date().toISOString(),
    count: rows.length,
    scoring:
      "1000×(cleared/max_levels) + 100×accuracy − 5×timeouts − min(40, median_s)",
    rows,
  };
}

async function handlePost(request, env) {
  const token = env.GITHUB_TOKEN;
  const owner = env.GITHUB_OWNER;
  const repo = env.GITHUB_REPO;
  if (!token || !owner || !repo) {
    return json({ ok: false, error: "Server not configured" }, 500, env);
  }

  let payload;
  try {
    payload = await request.json();
  } catch (_) {
    return json({ ok: false, error: "Invalid JSON" }, 400, env);
  }

  if (!payload || payload.schema !== "quiz_challenge_result_v1") {
    return json({ ok: false, error: "Unsupported schema" }, 400, env);
  }
  if (!payload.identity || !payload.identity.consent) {
    return json({ ok: false, error: "Consent required" }, 400, env);
  }

  const name = String(payload.identity.name || "anonymous").slice(0, 120);
  const email = String(payload.identity.email || "").slice(0, 200);
  const accuracy = payload.summary ? Math.round((payload.summary.accuracy || 0) * 100) : 0;
  const mode = (payload.quest && payload.quest.mode) || "full";
  const title = `[quest-result] ${maskName(name)} — ${accuracy}% (${mode})`;

  const body = [
    "## Identity",
    `- Name: ${name}`,
    `- Email: ${email}`,
    `- Consent: yes`,
    "",
    "## Testimony",
    payload.identity.testimony || "_none_",
    "",
    "## Summary",
    "```json",
    JSON.stringify(payload.summary || {}, null, 2),
    "```",
    "",
    "## Benchmark",
    "```json",
    JSON.stringify(
      payload.benchmark ||
        (() => {
          const r = publicRow(payload, {});
          delete r._email_key;
          return r;
        })(),
      null,
      2
    ),
    "```",
    "",
    "## Full payload",
    "```json",
    JSON.stringify(payload, null, 2),
    "```",
  ].join("\n");

  const gh = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "quiz-challenge-platform-worker",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      body,
      labels: ["quest-result", mode === "test" ? "test-mode" : "full-mode"],
    }),
  });

  const ghJson = await gh.json().catch(() => ({}));
  if (!gh.ok) {
    return json(
      { ok: false, error: "GitHub API error", status: gh.status, detail: ghJson },
      502,
      env
    );
  }

  return json(
    { ok: true, issue_url: ghJson.html_url, issue_number: ghJson.number },
    200,
    env
  );
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(env) });
    }

    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "GET" && (path === "/leaderboard" || path.endsWith("/leaderboard"))) {
      if (!env.GITHUB_OWNER || !env.GITHUB_REPO) {
        return json({ ok: false, error: "Server not configured" }, 500, env);
      }
      try {
        const mode = url.searchParams.get("mode") === "test" ? "test" : "full";
        const board = await buildLeaderboard(env, mode);
        return json(board, 200, env);
      } catch (err) {
        return json(
          {
            ok: false,
            error: "Leaderboard fetch failed",
            status: err.status || 500,
            detail: err.detail || String(err.message || err),
          },
          502,
          env
        );
      }
    }

    if (request.method === "GET" && (path === "/health" || path.endsWith("/health"))) {
      const owner = env.GITHUB_OWNER;
      const repo = env.GITHUB_REPO;
      const token = env.GITHUB_TOKEN;
      if (!owner || !repo) {
        return json({ ok: false, error: "GITHUB_OWNER / GITHUB_REPO not set" }, 500, env);
      }
      const headers = {
        Accept: "application/vnd.github+json",
        "User-Agent": "quiz-challenge-platform-worker",
      };
      if (token) headers.Authorization = `Bearer ${token}`;
      const repoRes = await fetch(`https://api.github.com/repos/${owner}/${repo}`, { headers });
      const repoJson = await repoRes.json().catch(() => ({}));
      return json(
        {
          ok: repoRes.ok,
          has_token: !!token,
          owner,
          repo,
          github_status: repoRes.status,
          repo_full_name: repoJson.full_name || null,
          private: repoJson.private ?? null,
          has_issues: repoJson.has_issues ?? null,
          hint: repoRes.ok
            ? "Repo reachable"
            : repoRes.status === 404
              ? "Repo not found OR token cannot see it. Check GITHUB_OWNER/GITHUB_REPO and that the PAT includes this repository with Issues read/write."
              : "GitHub rejected the request. Check token scopes.",
        },
        repoRes.ok ? 200 : 502,
        env
      );
    }

    if (request.method === "POST" && (path === "/" || path === "")) {
      return handlePost(request, env);
    }

    return json({ ok: false, error: "Not found" }, 404, env);
  },
};
