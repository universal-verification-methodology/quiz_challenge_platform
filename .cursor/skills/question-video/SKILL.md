---
name: question-video
description: >-
  Converts challenge quiz bank items into short stem videos (narrated question
  plus circuit/figure frame) for anti-copy AI friction. Reads content/<course>/
  question JSON, writes media/videos + audio, patches item.media. Use when the
  user mentions question-video, quiz stem video, convert questions to video,
  learn_digital media stems, anti-AI video stems, or batch narrated quiz clips.
disable-model-invocation: true
---

# Question → Video (challenge stems)

Turn **quiz bank items** into short **stem videos** so learners hear/see the
question (with a circuit or figure) instead of selecting HTML text to paste into
an AI agent.

**Unit of work:** one item, one module bank, or a whole pack under `content/<course_id>/`.  
**Reference pipeline:** sibling repo `digital_learning` skill `module-slides`
(TTS via edge-tts, ffmpeg mux) — adapted here for **per-question stems**, not
module teaching clips.

Work **one module at a time** unless the user asks for a full-pack run.

## Scope

| In | Out |
|----|-----|
| `content/<course>/questions/*.json` | Rewriting `explain` / answers into speech |
| Stem frame PNG (question + figure) | Teaching the correct answer in the video |
| Narration of the **question only** | Full module lecture clips (`module-slides`) |
| `media/videos/<item_id>.mp4` + audio | Committing huge binaries unless asked |
| Patch `item.media` on the bank | Shipping player UX changes unless asked |

## Layout

```
content/<course_id>/
  content.json
  questions/<module>.json
  media/
    images/                 # optional circuit/figure sources
    videos/<item_id>.mp4    # stem videos (this skill)
    _work/<item_id>/        # ephemeral: frame.png, speech.txt, audio.mp3
```

Bank media field after success:

```json
"media": {
  "type": "video",
  "src": "media/videos/<item_id>.mp4",
  "poster": "media/images/<item_id>-frame.png"
}
```

Keep `prompt` / `choices` / `answer` / `explain` in JSON for grading and the
**post-quest report**. During the quest, the player should prefer the video stem
(wire-up may be separate from this skill).

## Design principles

1. **Match module-slides PPT/PDF/video look** — light slide, Calibri-like sans, title `#1A1A2E`, body `#333`, panel `#F4F4F4` (see `digital_learning` `pptx_theme.py`).
2. **Prefer real DDV browser tools** — figures should come from `digital_learning` Track B labs (`radix-converter`, `kmap`, `setup-hold`) via `media/images/tools/<toolId>.png`, not only synthetic posters.
3. **eda_learning stem discipline** — one visual idea per frame; metrics/UI on the figure; speech = question + choices only; pitfalls as distractors; never put the answer on the stem (see `eda_learning` module-slides / STA walkthroughs).
4. **Question text only on the slide chrome** — prompt under the figure; choices stay in the player (and in TTS), not as a burned-in key list.
5. **Brand** — module title left; `universal-verification-methodology` right (no difficulty).
6. **Narrate the question, never the answer** — no correct choice, no `explain`.
7. **Short** — target **15–45 s**; hard cap ~60 s.
8. **Friction, not DRM** — deny easy copy-paste; screenshots still possible.

## Prerequisites

```bash
pip install -r .cursor/skills/question-video/scripts/requirements.txt
# ffmpeg on PATH (Windows: winget/choco; WSL: sudo apt install ffmpeg)
```

Sibling repos (typical Windows paths):

- `d:/proj/designs/digital_learning` — tools + `assets/lab-starter.png` + capture script
- `d:/proj/designs/eda_learning` — pedagogy reference (one idea / frame, shared goldens, no reveal-on-stem)

## Workflow

```
Question-Video Progress:
- [ ] 1. Sync tool figures from digital_learning (sync_tool_figures.py)
- [ ] 2. Pick course pack + module bank (default content/learn_digital)
- [ ] 3. Inventory items (ids, difficulties, existing media)
- [ ] 4. Bind + capture per-question tool states (not one shared tools/*.png)
- [ ] 5. Resolve figure: item png (state) → media.figure → tools/<toolId>.png fallback
- [ ] 6. Write speech.txt (question + choices only; no answer)
- [ ] 7. Build frame + TTS/reuse-audio + MP4
- [ ] 8. Patch bank JSON media fields
- [ ] 9. Spot-check against live tools URL
```

### Step 0: Sync DDV tool UI figures

```bash
# Fast: copy courses/learn_digital/module*/assets/lab-starter.png
python .cursor/skills/question-video/scripts/sync_tool_figures.py \
  --course content/learn_digital \
  --mode copy

# Shared fallback only (one starter UI per tool):
python .cursor/skills/question-video/scripts/sync_tool_figures.py \
  --mode capture --only kmap
# kmap → Karnaugh map + Minimal SOP only (.tool-layout.split-wide)
```

Writes `content/learn_digital/media/images/tools/{radix-converter,kmap,setup-hold}.png`.

**Preferred (unique stems):** bind each item to a challenge/preset, then capture:

```bash
python .cursor/skills/question-video/scripts/bind_tool_states.py
python .cursor/skills/question-video/scripts/capture_item_figures.py
# → media/images/tools/states/<tool>__<key>.png
# → media/images/<item_id>.png (copied per item)
```

Crop selectors (digital_learning): `#rc-root`, `.tool-layout.split-wide`, `#sh-root`.

### Step 1–2: Inventory

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module01-radix-converter \
  --list
```

### Step 3: Figures (priority order)

| Source | When |
|--------|------|
| `media/images/<item_id>.png` | **Default** — instrument state linked to that question family |
| `media.figure` (still, not `tools/` / `*-frame`) | Explicit bank path |
| `media/images/tools/<toolId>.png` | Shared fallback only |
| `--figure PATH` | One-off override |
| `*-frame.png` | **Full slide poster only — never use as figure input** |

Do **not** put the correct answer on the figure. Borrow eda_learning: helpers/UI OK; stem must not be a “reveal golden.”

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module01-radix-converter \
  --item radix_easy_01 \
  --reuse-audio \
  --dry-run
```

### Step 4: Speech rules

Spoken content = question prompt + choice letters/text (for MCQ/TF).  

| Do | Don’t |
|----|--------|
| “Question. How many values can five bits represent? A sixteen. B thirty-two. …” | “The answer is B” / read `explain` |
| Short, clear sentences | Dump JSON or markdown |
| “true or false: …” for TF | Reveal true/false key |
| Mention “look at the circuit on screen” when a figure exists | Read file paths aloud |

### Step 5–6: Build

One item:

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module01-radix-converter \
  --item radix_easy_01 \
  --write-media
```

Whole module (careful: many files):

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module13-kmap \
  --all \
  --limit 5 \
  --write-media
```

Batch several modules:

```bash
python .cursor/skills/question-video/scripts/batch_build_modules.py \
  --modules module02-twos-complement module03-overflow-wrap \
  --reuse-audio   # only after audio already exists
```

`--write-media` patches the bank JSON. Omit it to only generate files.

Binders exist for **module01–module26** (prompt → tool challenge/preset). Modules 27+ still need binders.

### Step 7: Second-pass accuracy check

After a batch build (or anytime banks change), verify speech/files match the current quiz items:

```bash
python .cursor/skills/question-video/scripts/verify_question_videos.py \
  --course content/learn_digital

# Rebuild mismatches (stale speech, missing mp4, etc.)
python .cursor/skills/question-video/scripts/verify_question_videos.py \
  --course content/learn_digital --fix --workers 4
```

Checks: media pointers + file sizes, `speech.txt` vs regenerated speech from prompt/choices, no answer-reveal phrases. Writes `media/_batch_logs/verify_report.json`.

### Step 8: Packaging report

Tell the user:

- Module + item ids processed  
- Output MP4 paths  
- Whether JSON was patched  
- Verify report summary (ok / bad / by_issue)  
- Residual risk: screen capture / multimodal models  

## Agent rules

1. Default course: `content/learn_digital` unless user names another pack.
2. Prefer `--limit` / single `--item` before full-bank runs.
3. Never narrate or burn-in the correct answer.
4. Do not commit `media/videos/*.mp4` unless the user asks.
5. If ffmpeg or edge-tts is missing, stop with install hints — do not fake MP4s.
6. After large batches, run `verify_question_videos.py` and `--fix` stale/broken items.
7. For TTS/ffmpeg conventions, you may read sibling  
   `../digital_learning/.cursor/skills/module-slides/` (especially `synthesize_audio.sh`,
   `build_video.sh`) but **run this skill’s scripts** for challenge banks.

## Additional resources

- Schema + speech templates: [reference.md](reference.md)
- Authoring packs: [docs/AUTHORING.md](../../../docs/AUTHORING.md)
- Paper framing: [paper/draft-intro.md](../../../paper/draft-intro.md)
