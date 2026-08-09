# Authoring guide: bring your own course

This repo is an **open quiz-challenge platform**. The runtime (adaptive quest, timers, silent grading, report, certificate/leaderboard hooks) is separate from **content packs**. Digital foundations (`content/learn_digital/`) is the reference pack for circuits education—not a hard limit on topics.

**Goal for adopters:** `git clone` or `git pull`, replace (or add) module question banks, serve the site, and run the same challenge UX on your subject.

---

## 1. Mental model

```text
quiz_challenge_platform/
├── *.html, css/, js/          ← engine (usually leave alone)
├── content/
│   └── <course_id>/           ← YOUR pack
│       ├── content.json       ← modules, timing, progress rules, UX
│       ├── questions/         ← one JSON bank per module
│       └── media/             ← optional images/videos for stems
└── docs/AUTHORING.md          ← this file
```

| Layer | Who edits | Examples |
|-------|-----------|----------|
| Engine | Maintainers / rare forks | `js/adaptive-engine.js`, report UI |
| Content pack | **You** | Prompts, choices, difficulties, module list |
| Site config | Optional | `config/site.json` for results endpoint / certificate labels |

---

## 2. Quick path A — replace the demo questions in place

Fastest way to try your own exam items without renaming folders.

1. Pull the latest platform.
2. Edit or overwrite files under `content/learn_digital/`:
   - `content.json` — titles, module list, timing, profiles
   - `questions/*.json` — item banks
3. Keep module `id` values stable if you already have local sessions, or open the quest with `?restart=1`.
4. Serve and open the home page:

```bash
py -3 -m http.server 18080 --bind 127.0.0.1
```

5. Use **Start quest** (clears stale sessions).

You can leave the folder name `learn_digital` even if the subject is no longer digital circuits; update `title` / `id` fields inside `content.json` for display and analytics. For a clean rename, use path B.

---

## 3. Quick path B — add a new course pack (recommended)

1. Copy the demo pack:

```text
content/learn_digital/  →  content/<your_course_id>/
```

Example: `content/learn_signals/`, `content/cs101_midterm/`.

2. Edit `content/<your_course_id>/content.json` (see §4).
3. Replace question files under `content/<your_course_id>/questions/`.
4. Point the runtime at your pack — today the demo hardcodes the path in `js/challenge-app.js`:

```js
const CONTENT_BASE = "content/learn_digital";
```

Change it to:

```js
const CONTENT_BASE = "content/<your_course_id>";
```

5. Optionally update `index.html` hero title/copy so students see your course name.
6. Serve locally and open `challenge.html?restart=1`.

> **Paper / roadmap note:** a future improvement is reading `CONTENT_BASE` from `config/site.json` or a query param so adopters need not edit JS. Until then, one-line path change is the documented switch.

---

## 4. Manifest: `content.json`

Minimal shape:

```json
{
  "id": "my_course",
  "title": "My Course Challenge",
  "version": 1,
  "source_course": "my_course",
  "ux": {
    "reveal_modules_during_quiz": false,
    "feedback": "report_only",
    "module_order": "random",
    "within_module": "easy_to_hard_clearance"
  },
  "timing": {
    "enabled": true,
    "limits_s": { "easy": 30, "medium": 45, "hard": 60 },
    "warn_before_s": 10,
    "on_timeout": "incorrect",
    "keep_counting_when_hidden": true
  },
  "progress": {
    "unit": "module",
    "difficulties": ["easy", "medium", "hard"],
    "need_correct_per_difficulty": 1,
    "max_attempts_per_difficulty": 10,
    "bank_multiplier": 3,
    "advance": "difficulties_cleared_or_exhausted"
  },
  "media_policy": {
    "download": false,
    "screenshot_ok": true
  },
  "modules": [
    {
      "id": "module01-intro",
      "order": 1,
      "title": "Introduction",
      "questions": "questions/module01-intro.json"
    }
  ]
}
```

### Fields that matter for authors

| Field | Meaning |
|-------|---------|
| `modules[].id` | Stable id (report, telemetry). Use slug-style names. |
| `modules[].title` | Shown on the **report** (hidden during quest if `reveal_modules_during_quiz` is false). |
| `modules[].questions` | Relative path to the bank JSON. |
| `progress.max_attempts_per_difficulty` | Cap of unique items tried at one difficulty (default 10). |
| `progress.need_correct_per_difficulty` | Correct answers required to clear a level (default 1). |
| `progress.bank_multiplier` | Guidance: bank size ≥ `max_attempts × multiplier` (default 3 → **30** items per difficulty). |
| `ux.module_order` | `"random"` (recommended) or `"sequential"`. |
| `ux.feedback` | Keep `"report_only"` for the blind-quest integrity model. |
| `ux.embed_tools` | When `true` (default), every module with a `toolId` embeds the live lab tool below the answers. Set `false` to disable. Per-item opt-out: `"embed_tool": false`. |
| `ux.tool_embed_height_px` | Tall iframe height for full-page embeds (default 3600). |
| `timing.limits_s` | Per-difficulty seconds; omit or disable timing only if you accept easier LLM paste. |
| `modules[].toolId` | Maps to `config/site.json` → `tools.base_url` + `/{toolId}/`. |
| `profiles.test` | Optional short run for dry runs (subset of modules / difficulties). |

Bump `version` when you change banks so old `localStorage` sessions are less likely to mismatch (test profile already suffixes the version).

---

## 5. Question bank JSON

One file per module. Compatible types: `multiple_choice`, `true_false`, `short_answer`.

```json
{
  "module": "module01-intro",
  "title": "Introduction",
  "items": [
    {
      "id": "intro_easy_01",
      "type": "multiple_choice",
      "prompt": "Your question text?",
      "choices": ["A", "B", "C", "D"],
      "answer": 1,
      "explain": "Why B is correct (shown on the report).",
      "difficulty": "easy"
    },
    {
      "id": "intro_med_01",
      "type": "true_false",
      "prompt": "A statement students must judge.",
      "answer": false,
      "explain": "Short rationale.",
      "difficulty": "medium"
    },
    {
      "id": "intro_hard_01",
      "type": "short_answer",
      "prompt": "Type the exact expected token.",
      "answer": "expected",
      "explain": "Shown after the quest.",
      "difficulty": "hard",
      "time_limit_s": 90
    }
  ]
}
```

### Rules of thumb

1. **Tag every item** with `"difficulty": "easy" | "medium" | "hard"` (or your `progress.difficulties` list).
2. **Unique `id`s** within the module (and ideally globally).
3. **Unique prompts globally** — after padding/forging, run `python scripts/enforce_global_unique_prompts.py` so the same stem text is not reused across difficulties or modules. Regenerated items drop old `media` and need new stem videos.
4. **MCQ `answer`** is the **0-based index** into `choices`.
5. **Bank size:** aim for ≥ `max_attempts_per_difficulty × bank_multiplier` items **per difficulty** so a worst-case level never repeats a question (demo: 30 × 3).
6. **No mid-quest spoilers** in the prompt; put teaching detail in `explain` (and optional `choice_rationales` later).
7. **Optional media** (video/image hides the prompt text for anti-copy):

```json
"media": {
  "type": "video",
  "src": "media/videos/q1.mp4",
  "poster": "media/images/q1-frame.png"
}
```

Prefer schematics, plots, or short clips over pure text when you want higher friction against casual LLM paste. Tool embeds still appear for every module with a `toolId` even when an item has no video yet.

To **generate stem videos** from bank items (narrated question + on-screen figure/frame), use the project skill [`.cursor/skills/question-video/`](../.cursor/skills/question-video/SKILL.md) — patterned after `digital_learning`’s `module-slides` TTS/ffmpeg pipeline.

8. **Optional per-item timeout:** `"time_limit_s": 45` overrides the difficulty default from `content.json`.
9. **Tool embed opt-out:** `"embed_tool": false`. Optional `"tool_embed_height_px": 4000` if a tall tool is clipped.

---

## 6. Checklist for a new topic (any subject)

Use this when retargeting beyond digital circuits (signals, Verilog, math, chemistry, …).

- [ ] Choose a `course_id` and create `content/<course_id>/`.
- [ ] List 2+ modules that match how you teach (or how you exam).
- [ ] Write banks with easy → medium → hard coverage; pad to recommended size.
- [ ] Set timing limits appropriate to item length (reading a figure ≠ a one-line fact).
- [ ] Set `CONTENT_BASE` in `js/challenge-app.js`.
- [ ] Update landing page title/copy.
- [ ] Run **test profile** or `challenge.html?test=1&restart=1` with a tiny subset first.
- [ ] Complete one full quest; read the report; fix wrong `answer` indices / explains.
- [ ] (Optional) Configure certificate / results worker — see `backend/api.md`.
- [ ] Tell students: screenshots still possible; the design is **friction**, not DRM.

---

## 7. Test mode for authors

In `content.json`, define a short profile (demo pattern):

```json
"profiles": {
  "test": {
    "title": "My Course (test)",
    "module_ids": ["module01-intro"],
    "difficulties": ["easy", "medium"],
    "max_attempts_per_difficulty": 3
  }
}
```

Open:

```text
challenge.html?test=1&restart=1
```

Use this while editing banks so you are not running a 90-question worst case.

---

## 8. What you usually should not change

| Keep stable | Why |
|-------------|-----|
| `ux.feedback: "report_only"` | Core integrity + learning design |
| Non-repeating attempts within a difficulty | Prevents grinding the same stem with an LLM |
| Progress unit = module + difficulty ladder | Matches the published quest model |
| Server-side token for GitHub results | Never put secrets in Pages/JS |

Tuning `need_correct_per_difficulty`, time limits, and bank sizes is encouraged; changing the engine’s clearance semantics should be a deliberate fork.

---

## 9. Mapping from an existing exam or LMS export

1. Split the exam into **modules** (topics or weeks).
2. For each item, assign a difficulty; if unsure, start all as `medium` and rebalance after a pilot.
3. Convert to the JSON schema above (spreadsheet → script is fine).
4. Ensure each difficulty has enough unique items for your `max_attempts` cap.
5. Drop answer keys from any student-facing PDF; explanations live only in the bank for the post-quest report.
6. Pilot with colleagues or TAs using test mode before a graded run.

---

## 10. Related docs

- [`DESIGN.md`](DESIGN.md) — product decisions and anti-AI friction rationale  
- [`../README.md`](../README.md) — quick start  
- [`../backend/api.md`](../backend/api.md) — certificate / results / leaderboard  
- [`../paper/draft-intro.md`](../paper/draft-intro.md) — ISCAS framing (platform + circuits use case)
