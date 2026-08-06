# Adaptive Quiz Challenge Platform

Standalone prototype for a **variable-length**, module-mapped quiz challenge (merge-ready with `digital_learning`).

## Live site

- **Cloudflare:** https://quiz-challenge-platform.digital-design-challenge.workers.dev/
- **GitHub Pages:** https://universal-verification-methodology.github.io/quiz_challenge_platform/ (Actions deploy; may lag while runners are queued)

## Quick start

```bash
cd quiz_challenge_platform
py -3 -m http.server 18080 --bind 127.0.0.1
```

Open http://127.0.0.1:18080/ and use **Start quest** (clears old sessions).

## Certificate + results → GitHub

After a quest, the report asks for **name**, **email**, and **testimony** (consent required) to unlock a printable certificate.

**Automatic GitHub upload** needs a small server (token cannot live in the browser):

1. Deploy `backend/cloudflare-worker.js` with `GITHUB_TOKEN` + repo env vars  
2. Set `config/site.json` → `results.endpoint` to that worker URL  

Until then, claiming a certificate still works and also downloads a local JSON copy of the result. Details: [`backend/api.md`](backend/api.md).

## Test mode (fast)

```text
http://127.0.0.1:18080/challenge.html?test=1&restart=1
```

Or click **Test mode** on the home page.

Uses profile `test` in `content.json`: **2 modules**, **easy + medium** only, max **3** attempts per level (best **4** / worst **12**). Full quest stays the default without `test=1`.

## Rules (full quest)

| | |
|--|--|
| Modules shown mid-quest? | No (randomized blocks) |
| Per difficulty | Need **1 correct**, max **10** unique attempts |
| Difficulties | easy → medium → hard inside each module |
| Bank | **30** items / difficulty (= 3 × 10) |
| Demo size | 3 modules → best **9** / worst **90** questions |
| Feedback | Report only after the quest |

Regenerate banks:

```bash
py -3 scripts/generate_difficulty_banks.py
```

See [docs/DESIGN.md](docs/DESIGN.md).

## Bring your own course

The runtime is **content-agnostic**. Digital foundations is the demo pack; replace or add banks under `content/<course_id>/` and point `CONTENT_BASE` in `js/challenge-app.js`. Step-by-step: [docs/AUTHORING.md](docs/AUTHORING.md).
