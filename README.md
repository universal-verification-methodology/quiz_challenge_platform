# quiz_challenge_platform

[![GitHub](https://img.shields.io/badge/GitHub-quiz__challenge__platform-181717?logo=github)](https://github.com/universal-verification-methodology/quiz_challenge_platform)
[![Live](https://img.shields.io/badge/live-Cloudflare%20Workers-F38020?logo=cloudflare)](https://quiz-challenge-platform.digital-design-challenge.workers.dev/)
[![Pages](https://img.shields.io/badge/mirror-GitHub%20Pages-222?logo=githubpages)](https://universal-verification-methodology.github.io/quiz_challenge_platform/)
[![Org](https://img.shields.io/badge/org-universal--verification--methodology-0A9EDC)](https://github.com/universal-verification-methodology)
[![Domain](https://img.shields.io/badge/domain-adaptive%20quiz%20%7C%20digital%20design-purple)](https://github.com/universal-verification-methodology/quiz_challenge_platform)

**quiz_challenge_platform** is a standalone **variable-length**, module-mapped quiz challenge — blind quest, silent grading mid-run, analytical report at the end. Demo packs: Digital Foundations (`learn_digital`) and Verilog RTL (`learn_verilog`); the runtime is content-agnostic and merge-ready with `digital_learning`.

Learners usually **open the live site** or clone and serve locally. Authors edit banks under `content/<course_id>/`, regenerate if needed, and push; Cloudflare / Pages Actions publish from `main`.

## Table of contents

- [Contents](#contents)
- [Browse or clone](#browse-or-clone)
- [Quest modes](#quest-modes)
- [Rules](#rules)
- [Certificate and results](#certificate-and-results)
- [Author: bring your own course](#author-bring-your-own-course)
- [Deploy](#deploy)
- [Docs](#docs)

## Contents

```text
quiz_challenge_platform/
├── README.md
├── index.html              # home — Full / Short Quest
├── challenge.html          # adaptive quest runtime
├── report.html             # end-of-quest analysis + certificate
├── dashboard.html          # leaderboard / results view
├── run.sh                  # local static server (default :18080)
├── config/
│   └── site.json           # certificate labels + results endpoints
├── content/
│   ├── learn_digital/      # Digital Foundations (01–49)
│   └── learn_verilog/     # Verilog RTL Quest (01–17)
│       ├── content.json    # modules, timing, progress, profiles
│       ├── questions/      # one JSON bank per module
│       └── media/          # optional stem images / video
├── css/  js/               # engine (usually leave alone)
├── backend/                # Cloudflare Worker for GitHub results upload
├── scripts/                # bank generators
├── docs/
│   ├── DESIGN.md
│   └── AUTHORING.md
└── paper/                  # related paper (git submodule)
```

## Browse or clone

| Surface | URL |
|---------|-----|
| **Live (Cloudflare)** | https://quiz-challenge-platform.digital-design-challenge.workers.dev/ |
| **Mirror (GitHub Pages)** | https://universal-verification-methodology.github.io/quiz_challenge_platform/ |
| **Org** | [universal-verification-methodology](https://github.com/universal-verification-methodology) |

**Clone and serve locally:**

```bash
git clone https://github.com/universal-verification-methodology/quiz_challenge_platform.git
cd quiz_challenge_platform
./run.sh
```

On Windows (PowerShell), if bash/`run.sh` is unavailable:

```powershell
py -3 -m http.server 18080 --bind 127.0.0.1
```

Open http://127.0.0.1:18080/ and pick a course, then **Full Quest** or **Short Quest** (both clear stale sessions). Optional: `PORT=8080 ./run.sh`.

## Quest modes

| Mode | How to start | What you get |
|------|----------------|--------------|
| **Full Quest** | Home → course → **Full Quest**, or `challenge.html?course=<id>&restart=1` | All modules in that course pack |
| **Short Quest** | Home → course → **Short Quest**, or `challenge.html?course=<id>&short=1&restart=1` | **1 random module**, all 3 levels, **2 correct** per level (max 6 attempts/level) → best **6** / worst **18** questions |

`?test=1` is an alias for Short Quest. Profile `profiles.test` in `content.json` sets `module_count` (demo: **1**). Full and Short boards stay separate on the leaderboard. Course packs: `learn_digital` (49 modules), `learn_verilog` (17 modules).

Recommended path: Short Quest to feel the loop → Full Quest for the complete challenge → report / certificate.

## Rules

| | |
|--|--|
| Modules shown mid-quest? | No (randomized blocks) |
| Per difficulty (Full) | Need **1 correct**, max **10** unique attempts |
| Difficulties | easy → medium → hard inside each module |
| Bank | **30** items / difficulty (= 3 × 10) |
| Demo size | **learn_digital** 49 modules · **learn_verilog** 17 modules · 30 items / difficulty |
| Feedback | Report only after the quest |

Regenerate banks:

```bash
py -3 scripts/generate_difficulty_banks.py          # learn_digital
py -3 scripts/generate_verilog_banks.py             # learn_verilog
py -3 scripts/enrich_verilog_prompts.py             # unique RTL snippets (learn_verilog)
```

Verilog stem videos (see `.cursor/skills/question-video/`):

```bash
py -3 .cursor/skills/question-video/scripts/sync_tool_figures.py --course content/learn_verilog --mode copy
py -3 .cursor/skills/question-video/scripts/parallel_build_all.py --course content/learn_verilog --max-procs 4
py -3 .cursor/skills/question-video/scripts/verify_question_videos.py --course content/learn_verilog
```

## Certificate and results

After a quest, the report asks for **name**, **email**, and **testimony** (consent required) to unlock a printable certificate.

**Automatic GitHub upload** needs a small server (the token cannot live in the browser):

1. Deploy `backend/cloudflare-worker.js` with `GITHUB_TOKEN` + repo env vars  
2. Set `config/site.json` → `results.endpoint` to that worker URL  

Until then, claiming a certificate still works and also downloads a local JSON copy of the result. Details: [`backend/api.md`](backend/api.md).

## Author: bring your own course

The runtime is **content-agnostic**. Digital foundations is the demo pack; replace or add banks under `content/<course_id>/` and point `CONTENT_BASE` in `js/challenge-app.js`.

```text
content/
└── <course_id>/
    ├── content.json
    ├── questions/
    └── media/          # optional
```

Step-by-step (in-place swap vs new pack): [docs/AUTHORING.md](docs/AUTHORING.md).

## Deploy

Workflows: [`.github/workflows/cloudflare-deploy.yml`](.github/workflows/cloudflare-deploy.yml) (static site), [`.github/workflows/cloudflare-results.yml`](.github/workflows/cloudflare-results.yml) (results API), and Pages via [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

Add these repository secrets once:

| Secret | Purpose |
|--------|---------|
| `CLOUDFLARE_API_TOKEN` | Token with Workers edit permission |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account id |

Then push to `main`, or run **Actions → Deploy to Cloudflare Workers → Run workflow**. Local alternative: `wrangler deploy` from the repo root (see [`backend/SETUP_GITHUB.md`](backend/SETUP_GITHUB.md)).

## Docs

| Doc | Purpose |
|-----|---------|
| [docs/DESIGN.md](docs/DESIGN.md) | Product / technical decisions, merge-back rules |
| [docs/AUTHORING.md](docs/AUTHORING.md) | Bring-your-own course packs |
| [backend/api.md](backend/api.md) | Results / certificate upload API |
| [backend/SETUP_GITHUB.md](backend/SETUP_GITHUB.md) | Worker secrets and Wrangler |
