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
2. **Question text only on the frame** — no answer choices burned in (choices are spoken, selected in the player).
3. **Always include a related figure** — authored `media/images/<item_id>.png` or auto-generated from the prompt/module (hex nibble, bit-width, K-map, timing sketch, …). Never reuse `*-frame.png` as the figure.
4. **Narrate the question, never the answer** — no correct choice, no `explain`.
5. **Short** — target **15–45 s**; hard cap ~60 s.
6. **Friction, not DRM** — deny easy copy-paste; screenshots still possible.


## Prerequisites

```bash
pip install -r .cursor/skills/question-video/scripts/requirements.txt
# ffmpeg on PATH (Windows: winget/choco; WSL: sudo apt install ffmpeg)
```

Optional figure: place `media/images/<item_id>.png` (or pass `--figure`) before build.

## Workflow

```
Question-Video Progress:
- [ ] 1. Pick course pack + module bank (default content/learn_digital)
- [ ] 2. Inventory items (ids, difficulties, existing media)
- [ ] 3. Resolve authored figure or auto-generate related concept figure
- [ ] 4. Write speech.txt (question + choices labels only; no answer)
- [ ] 5. Build frame + TTS + MP4 via build_question_video.py
- [ ] 6. Patch bank JSON media fields
- [ ] 7. Spot-check 1–2 videos; report paths + remaining items
```

### Step 1–2: Inventory

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module01-radix-converter \
  --list
```

### Step 3: Figures

| Source | When |
|--------|------|
| `media/images/<item_id>.png` | Author-supplied circuit/schematic (preferred) |
| `--figure PATH` | One-off override |
| Auto-generate | Script builds a **related concept figure** from the prompt/module (default) |
| `*-frame.png` | **Full slide poster only — never use as figure input** |

Do **not** put the correct answer on the figure.

Regenerate figures:

```bash
python .cursor/skills/question-video/scripts/build_question_video.py \
  --course content/learn_digital \
  --module module01-radix-converter \
  --item radix_easy_01 \
  --force-figure \
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

`--write-media` patches the bank JSON. Omit it to only generate files.

### Step 7: Packaging report

Tell the user:

- Module + item ids processed  
- Output MP4 paths  
- Whether JSON was patched  
- Player note: `js/quiz-engine.js` may still need video stem rendering  
- Residual risk: screen capture / multimodal models  

## Agent rules

1. Default course: `content/learn_digital` unless user names another pack.
2. Prefer `--limit` / single `--item` before full-bank runs.
3. Never narrate or burn-in the correct answer.
4. Do not commit `media/videos/*.mp4` unless the user asks.
5. If ffmpeg or edge-tts is missing, stop with install hints — do not fake MP4s.
6. For TTS/ffmpeg conventions, you may read sibling  
   `../digital_learning/.cursor/skills/module-slides/` (especially `synthesize_audio.sh`,
   `build_video.sh`) but **run this skill’s scripts** for challenge banks.

## Additional resources

- Schema + speech templates: [reference.md](reference.md)
- Authoring packs: [docs/AUTHORING.md](../../../docs/AUTHORING.md)
- Paper framing: [paper/draft-intro.md](../../../paper/draft-intro.md)
