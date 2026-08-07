# Results API → GitHub

The browser **must not** hold a GitHub token. Flow:

```text
Report page (name, email, testimony, consent)
        │
        ▼
POST config/site.json → results.endpoint
        │
        ▼
Cloudflare Worker / serverless function  (GITHUB_TOKEN secret)
        │
        ▼
GitHub Issue (or commit under submissions/)
```

## Configure

1. Follow **[`SETUP_GITHUB.md`](SETUP_GITHUB.md)** — that is where **you** paste `GITHUB_TOKEN` (Cloudflare secret, not this repo).
2. Set `GITHUB_OWNER` / `GITHUB_REPO` in [`wrangler.toml`](wrangler.toml).
3. Put the worker URL in [`../config/site.json`](../config/site.json) → `results.endpoint`.
4. Prefer a **private** results repo; token scope: Issues write only.

## Leaderboard

```text
Dashboard (dashboard.html)
        │
        ▼
GET {results.endpoint}/leaderboard?mode=full|test
        │
        ▼
Worker reads GitHub Issues (labels quest-result + full-mode|test-mode)
        │  (UI: Full Quest / Short Quest; API mode value remains full|test)
        ▼
Public rows only: masked name, score, accuracy, attempts, cleared levels,
median time/q, timeouts, percentile, date — never email
```

Scoring (higher is better):

`1000 × (cleared / max_levels) + 100 × accuracy − 5 × timeouts − min(40, median_seconds)`

Best run per email is kept; names shown as `Yxxxxx Lx` (first letter of each word kept).

Redeploy the worker after pulling these changes so `GET /leaderboard` exists.

## Payload

See `schema: "quiz_challenge_result_v1"` built by `js/results.js` (identity + summary + attempts + optional `benchmark`).

## Without a worker

Certificate + local JSON download still work. Enable GitHub sync when the endpoint is set.
