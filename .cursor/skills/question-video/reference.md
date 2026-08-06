# Question-video reference

## Bank item fields used

| Field | Role |
|-------|------|
| `id` | Output basename (`media/videos/<id>.mp4`) |
| `type` | `multiple_choice` / `true_false` / `short_answer` |
| `prompt` | Narrated + shown on frame |
| `choices` | Narrated as A/B/C/… (MCQ); not marked correct |
| `answer` | **Grading only — never spoken or drawn as “correct”** |
| `explain` | Report only — never in stem video |
| `difficulty` | Optional label on frame corner |
| `media` | Written by `--write-media` |
| `time_limit_s` | Unchanged; video length should fit under quest timer |

## Speech template

### Multiple choice

```text
Question. <prompt>
Option A. <choices[0]>.
Option B. <choices[1]>.
…
Select the best answer.
```

If a figure is present, prefix: `Look at the diagram on the screen.`

### True / false

```text
True or false. <prompt>
```

### Short answer

```text
Question. <prompt>
Enter your answer when ready.
```

Do not speak the expected `answer` string.

## Frame layout (1920×1080) — module-slides style

Light slide (not dark “Challenge stem” chrome):

```
┌─────────────────────────────────────────────┐
│  Radix & bit width          challenge stem  │  module title + brand (no difficulty)
│                                             │
│     ┌───────────────────────────────┐       │
│     │  related figure (dominant)    │       │
│     └───────────────────────────────┘       │
│                                             │
│  <prompt text only — no A/B/C/D, no easy>   │
└─────────────────────────────────────────────┘
```

Assets:

| File | Role |
|------|------|
| `media/images/<id>.png` | Related figure only |
| `media/images/<id>-frame.png` | Full slide poster (question + figure) |
| `media/videos/<id>.mp4` | Narrated stem |

Choices are **spoken** and answered in the player — not printed on the slide (harder to screenshot-OCR a full key list with the figure).


## Alignment with digital_learning module-slides

| module-slides | question-video |
|---------------|----------------|
| Unit: module teaching clip | Unit: one quiz item |
| `transcript.md` + PPTX slides | Generated `speech.txt` + single stem frame |
| 3–10 minute target | 15–45 second target |
| Teaches concepts | States the question only |
| `video.mp4` in module root | `media/videos/<item_id>.mp4` in content pack |
| edge-tts + ffmpeg | Same tools via `build_question_video.py` |

Sibling path (typical): `d:/proj/designs/digital_learning/.cursor/skills/module-slides/`.

## DDV platform

Live learning site: https://universal-verification-methodology.github.io/learning/

Keep `module` ids aligned with course modules (e.g. `module01-radix-converter`) so
challenge packs merge cleanly with DDV labs later.

## Player follow-up (not this skill)

Challenge UI should:

1. Play `media.src` when `media.type === "video"`.
2. Avoid exposing a large selectable HTML copy of the full stem when video is present
   (short on-screen choices OK for clicking).
3. Disable download / `controlsList="nodownload"` where supported.
4. Keep report page able to show text `prompt` + `explain` after the quest.
