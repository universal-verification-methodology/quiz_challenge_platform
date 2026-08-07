# Adaptive Quiz Challenge Platform

Standalone prototype for a **variable-length**, module-mapped quiz challenge (merge-ready with `digital_learning`).

## Live site

- **Cloudflare:** https://quiz-challenge-platform.digital-design-challenge.workers.dev/ (Actions deploy on push to `main`)
- **GitHub Pages:** https://universal-verification-methodology.github.io/quiz_challenge_platform/ (Actions deploy; may lag while runners are queued)

### Cloudflare deploy (GitHub Actions)

Workflows: [`.github/workflows/cloudflare-deploy.yml`](.github/workflows/cloudflare-deploy.yml) (static site) and [`.github/workflows/cloudflare-results.yml`](.github/workflows/cloudflare-results.yml) (results API).

Add these repository secrets once:

| Secret | Purpose |
|--------|---------|
| `CLOUDFLARE_API_TOKEN` | Token with Workers edit permission |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account id |

Then push to `main`, or run **Actions → Deploy to Cloudflare Workers → Run workflow**. Local alternative: `wrangler deploy` from the repo root (see [`backend/SETUP_GITHUB.md`](backend/SETUP_GITHUB.md)).

## Quick start

```bash
./run.sh
```

On Windows PowerShell:

```powershell
.\run.ps1
```

Or manually:

```bash
cd quiz_challenge_platform
py -3 -m http.server 18080 --bind 127.0.0.1
```

Open http://127.0.0.1:18080/ and use **Full Quest** (clears old sessions).
Optional: `PORT=8080 ./run.sh` or `.\run.ps1 -Port 8080`.

## Certificate + results → GitHub

After a quest, the report asks for **name**, **email**, and **testimony** (consent required) to unlock a printable certificate.

**Automatic GitHub upload** needs a small server (token cannot live in the browser):

1. Deploy `backend/cloudflare-worker.js` with `GITHUB_TOKEN` + repo env vars  
2. Set `config/site.json` → `results.endpoint` to that worker URL  

Until then, claiming a certificate still works and also downloads a local JSON copy of the result. Details: [`backend/api.md`](backend/api.md).

## Short Quest / Full Quest

| Mode | How to start | What you get |
|------|----------------|--------------|
| **Full Quest** | Home → **Full Quest**, or `challenge.html?restart=1` | All modules in the course |
| **Short Quest** | Home → **Short Quest**, or `challenge.html?short=1&restart=1` | **1 random module**, all 3 levels, **2 correct** per level (max 6 attempts/level) → best **6** / worst **18** questions |

`?test=1` still works as an alias for Short Quest. Profile `profiles.test` in `content.json` sets `module_count` (default 3). Full and Short boards stay separate on the leaderboard.

## Rules (both modes)

| | |
|--|--|
| Modules shown mid-quest? | No (randomized blocks) |
| Per difficulty | Need **1 correct**, max **10** unique attempts |
| Difficulties | easy → medium → hard inside each module |
| Bank | **30** items / difficulty (= 3 × 10) |
| Demo size | **49** modules (01–49) → best **147** / worst **1470** questions; Short Quest uses 3 random modules |
| Feedback | Report only after the quest |

Regenerate banks:

```bash
py -3 scripts/generate_difficulty_banks.py
```

See [docs/DESIGN.md](docs/DESIGN.md).

## Bring your own course

The runtime is **content-agnostic**. Digital foundations is the demo pack; replace or add banks under `content/<course_id>/` and point `CONTENT_BASE` in `js/challenge-app.js`. Step-by-step: [docs/AUTHORING.md](docs/AUTHORING.md).
