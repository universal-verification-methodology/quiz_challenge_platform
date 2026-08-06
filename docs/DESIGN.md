# Adaptive Quiz Challenge Platform — Design

Status: **variable-length per-difficulty clearance** (v3 content)  
First course target: **`learn_digital`** (demo: 3 modules, 30 items × 3 difficulties each)  
Future home: integrate into [`digital_learning`](../../digital_learning) / GitHub Pages platform

This document captures product and technical decisions so the standalone demo stays consistent with the learning monorepo and can merge back cleanly.

---

## 1. Purpose

Build a **reusable adaptive quiz challenge** layer:

- Under the hood, content maps to **course modules** (for merge-back). During the quest, **module names are not shown** — the run feels like a randomized challenge.
- **Module order is randomized** each session (`ux.module_order: "random"`).
- Within each module, items are served **easy → medium → hard**.
- Advance a module after the learner has **answered all items** in that block (not after mid-quiz retries).
- **No correctness / answer key mid-quest** — grading is silent; the **analytical report** after the full quest explains right/wrong, timing, and path.
- Question stems may use **image / short video** later to raise the cost of casual AI paste.
- The engine is course-agnostic; each course ships as a **content** folder.

This is complementary to existing formative `quiz.json` on lab pages (`DDVQuiz` in `platform/assets/quiz.js`). Lab quizzes remain per-module self-checks with immediate feedback; the challenge platform is a **blind quest** with end-of-run analysis.

---

## 2. Relationship to `digital_learning`

| Concern | `digital_learning` today | This platform |
|---------|--------------------------|---------------|
| Course id | `learn_digital`, `learn_verilog`, … (`catalog.json`) | Same ids under `content/<course_id>/` |
| Module id | `moduleNN-<slug>` (e.g. `module13-kmap`) | Same module ids in manifests and progress |
| Formative quiz | `moduleNN-<slug>/quiz.json` | Source bank; challenge may curate/extend |
| Media | `video.mp4`, slides via CDN / `course-media` | Same naming + URL conventions where possible |
| Lab tools | Browser tools shelf | Out of scope for v1 (optional later “open lab” link) |
| Site | `platform/` on GitHub Pages | Demo standalone → later `platform/challenge/` |

**Consistency rules (non-negotiable for merge-back):**

1. Use existing **course ids** and **module directory names** — do not invent parallel taxonomies.
2. Prefer the existing **quiz item schema** (`type`, `prompt`, `choices`, `answer`, `explain`) so items can round-trip with `quiz.json`.
3. Media paths should resolve the same way as lab pages (`site-config.js` / CDN / local `course-media`) when integrated.
4. Progress keys should be stable: `course_id` + `module_id` + `item_id`.

---

## 3. Progress model

### 3.1 Hidden modules, randomized path

- Content still uses `learn_*` module ids (report + analytics + merge-back).
- **UI during the quest:** anonymous progress only — **do not list module titles**.
- **Session `module_order`:** shuffled module ids at quest start.

### 3.2 Per-difficulty clearance (variable length)

Within each module, climb **easy → medium → hard**. At each difficulty:

| Rule | Value |
|------|--------|
| Need | **1 correct** (`need_correct_per_difficulty`) |
| Cap | **max 10 attempts** (`max_attempts_per_difficulty`) |
| Repeats | **None** — each item used at most once per level |
| Bank size | **≥ 3 × max attempts** per difficulty (`bank_multiplier: 3` → **30** items) so a full worst-case level never reuses a question |

```text
module (shuffled)
  easy:   ask until 1 correct OR 10 tries (unique items)
  medium: same
  hard:   same
→ next module → … → report
```

**Length example (3 modules × 3 difficulties):**

| Case | Questions |
|------|-----------|
| Best | 3 × 3 × 1 = **9** |
| Worst | 3 × 3 × 10 = **90** |

(Not 3×3×100 — the cap is **10** attempts per difficulty.)

If the bank for a level is exhausted without a correct, that level is marked **exhausted** and the quest continues (still silent until the report).

### 3.3 Feedback policy

| When | What the user sees |
|------|--------------------|
| During quest | Prompt + choices; hold selection ~1s → next item (no right/wrong) |
| After quest | Report: correctness, explain, timing, path, module + difficulty breakdown |

`ux.feedback: "report_only"`.

---

## 4. Anti-AI friction (media)

Goals: raise effort for casual ChatGPT paste; not claim DRM-proof security.

| Measure | Approach |
|---------|----------|
| Image / video stems | Prefer schematic, waveform, K-map, timing clip over pure text where it helps |
| No easy download | Disable save-as / download controls; no download button on `<video>` |
| Per-question timeout | Default hard limits: easy **30s**, medium **45s**, hard **60s** (`content.timing`); warn in last 10s; timeout = incorrect + auto-advance. Optional `time_limit_s` on an item. Timer keeps counting if the tab is hidden. |
| Accept residual risk | Screenshots and screen capture still work — intentional remaining path |
| UX care | Do not break accessibility (keyboard, captions when available) |

When integrated, reuse platform media loading; challenge UI adds a thin **media guard** layer on stem media only.

---

## 5. Repository layout (standalone demo)

Folder name for course slices: **`content/`** (not `packs` / `database`).  
Reason: each entry is a challenge-ready content slice keyed by course id; full courses stay in the monorepo course repos.

```text
quiz_challenge_platform/
├── README.md
├── docs/
│   └── DESIGN.md                 # this file
├── index.html                    # start / select quest
├── challenge.html                # runtime UI
├── css/
│   └── challenge.css
├── js/
│   ├── quiz-engine.js            # render item, score, explain
│   ├── adaptive-engine.js        # within-module selection
│   ├── progress.js               # module gate (min_correct_per_module)
│   ├── session-log.js            # per-attempt timing + choice trail
│   ├── report.js                 # post-quest analytical report + diagrams
│   ├── media-guard.js            # download friction
│   └── results.js                # optional submit (later)
├── content/
│   └── learn_digital/
│       ├── content.json          # manifest (modules, gates, media policy)
│       ├── questions/            # curated / extended items (or re-export)
│       │   └── module01-radix-converter.json
│       └── media/                # demo-local media only if not using CDN yet
│           ├── images/
│           └── videos/
└── backend/
    └── api.md                    # results / privacy contract (later)
```

### 5.1 Future layout inside `digital_learning`

Preferred merge shape (keep the same internal split):

```text
digital_learning/platform/
└── challenge/
    ├── index.html
    ├── css/
    ├── js/
    └── content/                  # or load live from course repos + thin manifests
        └── learn_digital/
```

Alternatively, manifests only under `platform/challenge/content/`, with questions/media still fetched from each course module (`quiz.json`, `video.mp4`) like lab pages today.

---

## 6. Manifest schema (`content.json`)

Align identifiers with `catalog.json` / module dirs.

```json
{
  "id": "learn_digital",
  "title": "Digital Foundations Quest",
  "version": 1,
  "source_course": "learn_digital",
  "progress": {
    "unit": "module",
    "min_correct_per_module": 1,
    "advance": "sequential"
  },
  "media_policy": {
    "download": false,
    "screenshot_ok": true
  },
  "modules": [
    {
      "id": "module01-radix-converter",
      "order": 1,
      "title": "Radix & bit width",
      "toolId": "radix-converter",
      "questions": "questions/module01-radix-converter.json",
      "source_quiz": "module01-radix-converter/quiz.json"
    }
  ]
}
```

Notes:

- `id` / module `id` / `toolId` match platform catalog fields where they exist.
- `source_quiz` documents provenance for authors; runtime may load curated `questions/…` or the live course `quiz.json`.
- Example above shows **v0** (`min_correct_per_module: 1`). Flip to `2` when banks grow (v1).

---

## 7. Question schema (compatible with lab `quiz.json`)

Preserve compatibility with `platform/assets/quiz.js`:

```json
{
  "module": "module01-radix-converter",
  "title": "Radix check",
  "items": [
    {
      "id": "q1",
      "type": "multiple_choice",
      "prompt": "…",
      "choices": ["A", "B", "C", "D"],
      "answer": 1,
      "explain": "…",
      "difficulty": "easy",
      "media": {
        "type": "image",
        "src": "media/images/radix-q1.png"
      }
    }
  ]
}
```

| Field | Lab quiz today | Challenge extension |
|-------|----------------|---------------------|
| `type` | `multiple_choice`, `true_false`, `short_answer`, … | Same |
| `prompt` / `choices` / `answer` / `explain` | Yes | Same |
| `difficulty` | — | Optional for adaptivity |
| `media` | — | Optional image/video stem |

Challenge runtime should **ignore unknown fields** gracefully; lab `DDVQuiz` can ignore `difficulty` / `media` until the lab player gains media support.

**Bank size by phase:**

| Phase | Items per module | `min_correct_per_module` |
|-------|------------------|--------------------------|
| **v0 framework spike** | **1** | **1** |
| Target product | ≥2 (preferably ≥4) | **2** |

---

## 8. Session telemetry, analytical report, and progress diagrams

Yes — this is in scope as a first-class product feature. Capture a **session attempt log** during the quest; render a **report page** when the quest completes (and optionally allow revisit from `localStorage`).

### 8.1 Per-question timing

Record for every attempt (including retries):

| Field | Meaning |
|-------|---------|
| `course_id` / `module_id` / `item_id` | Stable ids (merge-back friendly) |
| `attempt_index` | 1st try, 2nd try, … on this item |
| `started_at` / `answered_at` | ISO timestamps |
| `duration_ms` | Time on this attempt (timer keeps running if tab is hidden) |
| `selected` | User’s choice (index / bool / short text); `null` on timeout |
| `correct` | boolean |
| `timed_out` | true when the question limit expired with no locked answer |
| `difficulty` | If tagged on the item |

Quest-level aggregates: total time, time per module, median time per correct vs wrong, slowest items.

**v0:** record `duration_ms` + correct/wrong with **no on-screen reveal**; report UI shows analysis after quest complete.  
**v1+:** richer diagrams / choice rationales / fishbone themes.

### 8.2 Why right / why wrong (analysis)

Be honest about depth by phase:

| Layer | What the user sees | How |
|-------|--------------------|-----|
| **A — Explanation replay** | Item `explain` text; highlight chosen vs correct choice | Deterministic; ship early |
| **B — Pattern summary** | “Missed 2 timing items”; “Fast & wrong on Boolean”; weak module list | Heuristics on the attempt log |
| **C — Deeper narrative** (optional later) | Short coach-style paragraph per miss | Author-written distractor rationales in JSON, or optional LLM assist — **not** required for v0/v1 |

Recommended item extension (optional, for better “why wrong” without AI):

```json
{
  "id": "q1",
  "choices": ["…", "…", "…", "…"],
  "answer": 2,
  "explain": "NAND is functionally complete.",
  "choice_rationales": [
    "AND is not universal by itself.",
    "OR is not universal by itself.",
    "Correct — NAND can implement any Boolean function.",
    "XOR cannot alone implement AND/OR."
  ]
}
```

If `choice_rationales` is absent, fall back to `explain` + “you selected X; correct is Y”.

### 8.3 Progress path diagram

Show **how the user moved** through the quest — not a generic fishbone unless we later do root-cause of errors.

**Primary (recommended): attempt path / tree**

```text
[module01 q1] --wrong (12s)--> [module01 q1 retry] --ok (8s)--> [module02 q1] --ok--> …
```

- Nodes = item attempts (or module milestones).
- Edge labels = correct/wrong + time.
- Color: green = correct, amber/red = wrong.
- Implement with SVG or a small diagram lib (keep Pages-friendly; avoid heavy deps if possible).

**Secondary views (pick what helps; don’t ship all at once):**

| View | Use |
|------|-----|
| **Module spine** | Linear course map with checkmarks + time badges |
| **Attempt tree** | Branches when retries or adaptive alternate items appear |
| **Fishbone (Ishikawa)** | Optional later for “why wrong” themes (timing, Boolean, FSM…) aggregated from misses — good for coaching, weak for literal click-path |

Avoid implying fishbone is the navigation history; use it only as a **theme breakdown** of error causes if we add that view.

### 8.4 Report page outline

After quest complete → `report.html` (or in-page panel):

1. **Summary** — modules cleared, accuracy, total time, median time/item.
2. **Per-module table** — corrects, attempts, time, weak flag.
3. **Per-question detail** — choice, right/wrong, duration, explanation / choice rationale.
4. **Progress diagram** — attempt path (default) + optional module spine.
5. **Suggested next steps** — link to lab `toolId` / module README on the learning site when integrated.

### 8.5 Privacy

- Attempt log stays **local** by default (`localStorage` / export JSON).
- Uploading timing/choices to a backend follows the same privacy rules as results (anonymous UUID; opt-in).
- Do not put personal identity in the client log.

### 8.6 Layout touch

```text
js/session-log.js    # append attempts; compute aggregates
js/report.js         # render tables + SVG path diagram
report.html          # post-quest analytical report
```

---

## 9. Privacy, certificate, and results → GitHub

- Anonymous play remains possible until the user **claims a certificate**.
- Certificate gate collects **name**, **email**, **testimony**, and explicit **consent**.
- Payload (`quiz_challenge_result_v1`) may be POSTed to `config/site.json` → `results.endpoint`.
- That endpoint (e.g. Cloudflare Worker) uses a **server-side** `GITHUB_TOKEN` to open a GitHub Issue or store JSON — never embed the token in Pages JS.
- See `backend/api.md` and `backend/cloudflare-worker.js`.
- **Public leaderboard** (`dashboard.html`): `GET /leaderboard?mode=full|test` returns masked names (`Yxxxxx Lx`), composite score, accuracy, attempts, cleared levels, median time/q, timeouts, top %, and date. Full and test boards are separate; best run per email wins. Email is never exposed.

---

## 10. Phased delivery

### 10.1 Current runtime

- 8 `learn_digital` modules × 3 items (easy/medium/hard)
- Random module order; anonymous progress UI
- `feedback: report_only`; advance on `answered_all`
- End report with timing + path + explanations

### 10.2 Next

1. Media stems + media-guard
2. Optional `choice_rationales` for richer “why wrong”
3. Quiz-bank skill for authoring
4. Fishbone / theme view of misses
5. Merge into `platform/challenge/`

---

## 11. Integration checklist (when merging into `digital_learning`)

- [ ] Place UI under `platform/challenge/` (or agreed path).
- [ ] Reuse `assets/site-config.js` + catalog course/module metadata.
- [ ] Link from Courses / lab pages (“Start quest” / “Challenge mode”) without breaking formative `DDVQuiz`.
- [ ] Prefer loading live `quiz.json` + CDN media; keep curated overrides only when needed.
- [ ] Match existing CSS variables / nav patterns where practical.
- [ ] Document challenge in `platform/README.md` site map.
- [ ] Keep CC BY / attribution aligned with course content licenses.
- [ ] Report links back to module labs / tools where helpful.

---

## 12. Decisions log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Content folder name | `content/` | Clear; not a DB; not a full course mirror |
| Show modules in UI | **No** (during quest) | Feels randomized; syllabus mapping stays internal |
| Module order | Random per session | Harder to memorize a fixed path |
| Within module | easy → medium → hard clearance | Escalating difficulty |
| Clear a difficulty | **1 correct** | Best-case short path |
| Cap per difficulty | **10 attempts**, no repeats | Worst-case bounded |
| Bank size | **3 × max attempts** (30) per difficulty | Avoid repeats in a level |
| Mid-quiz feedback | **None** (`report_only`) | Analysis only after the full quest |
| First course | `learn_digital` | Ready quizzes, visual topics, foundations ladder |
| Media download | Discouraged in UI | Friction vs AI; screenshots remain possible |
| Engine vs content | Split | Reuse for `learn_verilog`, `learn_riscv`, … |
| Timing | Per-attempt `duration_ms` in session log | Needed for end report |
| Post-quest UX | Analytical report + attempt-path diagram | Right/wrong + why lives here |
| Quiz-bank skill | After runtime works | Authoring scale-up without blocking the engine |

---

## 13. Open questions

1. v0 module list: which **5–8** `learn_digital` modules for the framework spike?
2. Runtime source of truth: curated `content/.../questions` only, or fetch course `quiz.json` with a thin overlay?
3. Quest complete: certificate / achievement string only, or also write back to platform progress keys?
4. Wrong-answer policy (v1): unlimited retries until `min_correct` is met, or a max-attempts cap?
5. Skill location: repo `.cursor/skills/` vs personal Cursor skills library?
6. Timing: pause `duration_ms` while the tab is hidden?
7. Default diagram for v1: attempt-path tree only, or also module spine on the same page?

---

## 14. References

- Original concept note: `adaptive_quiz_challenge_platform.md` (Downloads)
- Platform: `digital_learning/platform/README.md`
- Quiz player: `digital_learning/platform/assets/quiz.js`
- Module index: `digital_learning/courses/learn_digital/docs/MODULES.md`
- Live site: https://universal-verification-methodology.github.io/learning/