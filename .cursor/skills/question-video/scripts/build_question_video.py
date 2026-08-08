#!/usr/bin/env python3
"""Build per-question stem videos for challenge banks (anti-copy friction).

Visual style matches digital_learning module-slides PPTX/PDF/video:
  light slide, Calibri-like sans, title #1A1A2E, body #333, footer #666.

Pipeline: item → related figure → question-only slide frame → TTS → ffmpeg MP4.
Never narrates or draws the correct answer / explain.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow required. pip install -r .cursor/skills/question-video/scripts/requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[4]  # quiz_challenge_platform/

# 16:9, same as module-slides 13.333"×7.5" @ 144dpi ≈ 1920×1080
W, H = 1920, 1080
MARGIN = 90

# pptx_theme.py palette
COLOR_BG = (255, 255, 255)
COLOR_TITLE = (0x1A, 0x1A, 0x2E)
COLOR_BODY = (0x33, 0x33, 0x33)
COLOR_PANEL = (0xF4, 0xF4, 0xF4)
COLOR_BORDER = (0xD2, 0xD2, 0xD2)
COLOR_FOOTER = (0x66, 0x66, 0x66)
COLOR_ACCENT = (0x2A, 0x6F, 0x97)  # calm blue for diagram ink (not purple glow)

VOICE_DEFAULT = "en-US-JennyNeural"


def load_bank(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_bank(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bank_path(course: Path, module_id: str) -> Path:
    manifest = course / "content.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for mod in data.get("modules") or []:
            if mod.get("id") == module_id:
                rel = mod.get("questions") or f"questions/{module_id}.json"
                return course / rel
    return course / "questions" / f"{module_id}.json"


def find_item(bank: dict, item_id: str) -> dict | None:
    for it in bank.get("items") or []:
        if it.get("id") == item_id:
            return it
    return None


def speech_for_item(item: dict, *, has_figure: bool) -> str:
    prompt = str(item.get("prompt") or "").strip()
    typ = str(item.get("type") or "multiple_choice")
    parts: list[str] = []
    if has_figure:
        parts.append("Look at the browser lab figure on the slide.")
    if typ in ("true_false", "tf"):
        parts.append(f"True or false. {prompt}")
    elif typ in ("short_answer", "short"):
        parts.append(f"Question. {prompt}")
        parts.append("Enter your answer when ready.")
    else:
        parts.append(f"Question. {prompt}")
        choices = item.get("choices") or []
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, choice in enumerate(choices):
            label = letters[i] if i < len(letters) else str(i + 1)
            parts.append(f"Option {label}. {choice}.")
        parts.append("Select the best answer.")
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    # Prefer Calibri to match pptx_theme FONT_SANS
    candidates = []
    if bold:
        candidates += ["calibrib.ttf", "Calibri Bold.ttf", "arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]
    candidates += ["calibri.ttf", "Calibri.ttf", "arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def module_tool_id(course: Path, module_id: str) -> str | None:
    manifest = course / "content.json"
    if not manifest.is_file():
        return None
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for mod in data.get("modules") or []:
        if mod.get("id") == module_id:
            tid = mod.get("toolId")
            return str(tid) if tid else None
    return None


def resolve_authored_figure(
    course: Path,
    item: dict,
    figure_arg: Path | None,
    *,
    module_id: str = "",
    prefer_tool: bool = True,
) -> Path | None:
    """Return figure path for the stem.

    Priority (unique question state first):
      1. Explicit --figure
      2. Per-item media/images/<id>.(png|jpg|svg) — instrument state for that item
      3. media.figure / media.src when it is a still (not *-frame.png, not shared tools/)
      4. Shared tools/<toolId>.png only as last resort when prefer_tool

    Never reuse *-frame.png (composed stem slides).
    """
    if figure_arg and figure_arg.is_file():
        return figure_arg
    item_id = str(item.get("id") or "item")

    for cand in (
        course / "media" / "images" / f"{item_id}.png",
        course / "media" / "images" / f"{item_id}.jpg",
        course / "media" / "images" / f"{item_id}.svg",
    ):
        if cand.is_file():
            return cand.resolve()

    media = item.get("media") or {}
    for key in ("figure", "src"):
        raw = media.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        p = Path(raw.strip())
        if not p.is_absolute():
            p = course / p
        if (
            p.is_file()
            and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}
            and not p.name.endswith("-frame.png")
            and "/tools/" not in p.as_posix()
        ):
            return p.resolve()

    if prefer_tool:
        tool_id = module_tool_id(course, module_id) if module_id else None
        if tool_id:
            tool_fig = course / "media" / "images" / "tools" / f"{tool_id}.png"
            if tool_fig.is_file():
                return tool_fig.resolve()

    return None


# ---- Related figure generation (question-driven, answer not revealed) ----


def _panel(size: tuple[int, int] = (1400, 620)) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", size, COLOR_PANEL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size[0] - 1, size[1] - 1], outline=COLOR_BORDER, width=2)
    return img, draw


def _hex_digit_decimal_figure(digit: str) -> Image.Image:
    """Show hex digit on the 0..F line — for decimal-value questions (do not reveal the number)."""
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    d = digit.upper()
    draw.text((48, 36), "Hexadecimal digit to decimal value", fill=COLOR_TITLE, font=title)
    draw.text(
        (48, 100),
        "Hex digits run 0-9, then A-F. What decimal number is this digit?",
        fill=COLOR_BODY,
        font=body,
    )
    box = [120, 180, 360, 420]
    draw.rounded_rectangle(box, radius=16, outline=COLOR_ACCENT, width=4, fill=(255, 255, 255))
    draw.text((175, 230), d, fill=COLOR_TITLE, font=_font(120, bold=True))
    draw.text((150, 440), "hex digit", fill=COLOR_FOOTER, font=body)

    digits = list("0123456789ABCDEF")
    x0, y0 = 420, 200
    cell_w, cell_h = 52, 70
    for i, ch in enumerate(digits):
        x = x0 + (i % 8) * (cell_w + 10)
        y = y0 + (i // 8) * (cell_h + 16)
        outline = COLOR_ACCENT if ch == d else COLOR_BORDER
        width = 3 if ch == d else 2
        draw.rounded_rectangle(
            [x, y, x + cell_w, y + cell_h],
            radius=8,
            outline=outline,
            width=width,
            fill=(255, 255, 255),
        )
        draw.text((x + 14, y + 16), ch, fill=COLOR_TITLE, font=_font(28, bold=True))
    draw.text(
        (420, 400),
        "Count from 0 along this row — A is the first letter after 9.",
        fill=COLOR_BODY,
        font=body,
    )
    draw.text(
        (420, 450),
        "Trap: 16 is the base (radix), not the value of digit A.",
        fill=COLOR_FOOTER,
        font=_font(24),
    )
    return img


def _hex_nibble_figure(digit: str) -> Image.Image:
    """Show one hex digit and its 4-bit weight labels (no decimal answer highlighted as key)."""
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    mono = _font(42, bold=True)
    d = digit.upper()
    draw.text((48, 36), "Hex digit and 4-bit nibble", fill=COLOR_TITLE, font=title)
    # Big digit box
    box = [80, 140, 280, 340]
    draw.rounded_rectangle(box, radius=12, outline=COLOR_ACCENT, width=3, fill=(255, 255, 255))
    draw.text((120, 190), d, fill=COLOR_TITLE, font=_font(96, bold=True))
    draw.text((90, 360), "one hex digit", fill=COLOR_FOOTER, font=body)
    # Four bit cells
    weights = ["8", "4", "2", "1"]
    x0 = 400
    for i, w in enumerate(weights):
        x = x0 + i * 160
        draw.rounded_rectangle([x, 160, x + 130, 300], radius=10, outline=COLOR_BODY, width=2, fill=(255, 255, 255))
        # Leave bit cells blank — do not fill the pattern (avoids leaking the decimal answer).
        draw.text((x + 30, 320), f"x{w}", fill=COLOR_BODY, font=body)
    draw.text((400, 420), "Four bits group into one hex digit (weights 8-4-2-1).", fill=COLOR_BODY, font=body)
    draw.text((400, 470), f"Pattern for digit {d} uses those four bit places.", fill=COLOR_BODY, font=body)
    return img


def _bit_width_figure(n_bits: int) -> Image.Image:
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    draw.text((48, 36), f"Bit width = {n_bits}", fill=COLOR_TITLE, font=title)
    # Row of bit boxes
    n = max(1, min(n_bits, 16))
    box_w = min(70, (1200 - 40) // n)
    gap = 8
    total = n * box_w + (n - 1) * gap
    x0 = (1400 - total) // 2
    y = 200
    for i in range(n):
        x = x0 + i * (box_w + gap)
        draw.rounded_rectangle([x, y, x + box_w, y + 90], radius=8, outline=COLOR_ACCENT, width=2, fill=(255, 255, 255))
        draw.text((x + box_w // 2 - 6, y + 28), "0/1", fill=COLOR_FOOTER, font=_font(18))
    draw.text((80, 360), "Each box is one bit in a fixed-width pattern.", fill=COLOR_BODY, font=body)
    draw.text((80, 420), "Distinct patterns grow as two to the power of the width.", fill=COLOR_BODY, font=body)
    draw.text((80, 480), f"Here the hardware budget is {n_bits} bits.", fill=COLOR_BODY, font=body)
    return img


def _hex_group_figure() -> Image.Image:
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    draw.text((48, 36), "Grouping bits into hex", fill=COLOR_TITLE, font=title)
    bits = list("11010110")
    x0 = 120
    for i, b in enumerate(bits):
        x = x0 + i * 90
        draw.rounded_rectangle([x, 180, x + 70, 270], radius=8, outline=COLOR_BODY, width=2, fill=(255, 255, 255))
        draw.text((x + 22, 200), b, fill=COLOR_TITLE, font=_font(36, bold=True))
    # Brackets for nibbles
    draw.rectangle([x0, 300, x0 + 4 * 90 - 20, 308], fill=COLOR_ACCENT)
    draw.rectangle([x0 + 4 * 90, 300, x0 + 8 * 90 - 20, 308], fill=COLOR_ACCENT)
    draw.text((x0 + 80, 330), "4 bits → 1 hex", fill=COLOR_BODY, font=body)
    draw.text((x0 + 4 * 90 + 60, 330), "4 bits → 1 hex", fill=COLOR_BODY, font=body)
    draw.text((80, 420), "One hex digit always maps to a group of four bits.", fill=COLOR_BODY, font=body)
    return img


def _same_value_spellings_figure() -> Image.Image:
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    mono = _font(34, bold=True)
    draw.text((48, 36), "Same quantity, different radix spellings", fill=COLOR_TITLE, font=title)
    cards = [("Binary", "0b…"), ("Hex", "0x…"), ("Decimal", "…")]
    for i, (name, sample) in enumerate(cards):
        x = 100 + i * 400
        draw.rounded_rectangle([x, 160, x + 320, 360], radius=14, outline=COLOR_ACCENT, width=3, fill=(255, 255, 255))
        draw.text((x + 40, 200), name, fill=COLOR_TITLE, font=title)
        draw.text((x + 40, 270), sample, fill=COLOR_BODY, font=mono)
    draw.text((80, 440), "Changing the prefix or digits does not change the stored value.", fill=COLOR_BODY, font=body)
    return img


def _kmap_figure() -> Image.Image:
    img, draw = _panel((1400, 700))
    title = _font(36, bold=True)
    body = _font(26)
    draw.text((48, 28), "Karnaugh map (cells hold minterms)", fill=COLOR_TITLE, font=title)
    # 4x4 grid
    labels_top = ["00", "01", "11", "10"]
    labels_side = ["00", "01", "11", "10"]
    origin_x, origin_y = 280, 120
    cell = 140
    draw.text((origin_x - 60, origin_y - 50), "AB\\CD", fill=COLOR_FOOTER, font=_font(22))
    for i, lab in enumerate(labels_top):
        draw.text((origin_x + i * cell + 45, origin_y - 40), lab, fill=COLOR_BODY, font=_font(24))
    for r, lab in enumerate(labels_side):
        draw.text((origin_x - 70, origin_y + r * cell + 50), lab, fill=COLOR_BODY, font=_font(24))
        for c in range(4):
            x0 = origin_x + c * cell
            y0 = origin_y + r * cell
            draw.rectangle([x0, y0, x0 + cell, y0 + cell], outline=COLOR_BODY, width=2, fill=(255, 255, 255))
    draw.text((80, 640), "Gray-code axis labels make neighboring cells differ by one variable.", fill=COLOR_BODY, font=body)
    return img


def _timing_figure() -> Image.Image:
    img, draw = _panel((1400, 620))
    title = _font(36, bold=True)
    body = _font(26)
    draw.text((48, 28), "Setup / hold timing sketch", fill=COLOR_TITLE, font=title)
    # Axes
    y_clk, y_d = 180, 360
    draw.line([(80, y_clk), (1320, y_clk)], fill=COLOR_BORDER, width=2)
    draw.line([(80, y_d), (1320, y_d)], fill=COLOR_BORDER, width=2)
    draw.text((80, y_clk - 50), "CLK", fill=COLOR_BODY, font=body)
    draw.text((80, y_d - 50), "D", fill=COLOR_BODY, font=body)
    # Clock edge
    edge = 700
    draw.line([(edge, y_clk + 40), (edge, y_clk - 80)], fill=COLOR_ACCENT, width=4)
    draw.line([(edge, y_clk - 80), (edge + 160, y_clk - 80)], fill=COLOR_ACCENT, width=4)
    draw.line([(edge + 160, y_clk - 80), (edge + 160, y_clk + 40)], fill=COLOR_ACCENT, width=4)
    # Setup / hold brackets on D
    draw.line([(edge - 180, y_d + 70), (edge, y_d + 70)], fill=COLOR_TITLE, width=3)
    draw.line([(edge, y_d + 70), (edge + 120, y_d + 70)], fill=(0x8B, 0x45, 0x13), width=3)
    draw.text((edge - 160, y_d + 90), "setup", fill=COLOR_TITLE, font=body)
    draw.text((edge + 20, y_d + 90), "hold", fill=(0x8B, 0x45, 0x13), font=body)
    draw.text((80, 520), "Data must be stable before (setup) and after (hold) the active edge.", fill=COLOR_BODY, font=body)
    return img


def _generic_concept_figure(prompt: str, module_id: str) -> Image.Image:
    img, draw = _panel()
    title = _font(36, bold=True)
    body = _font(28)
    draw.text((48, 36), "Study the concept figure", fill=COLOR_TITLE, font=title)
    draw.rounded_rectangle([120, 140, 1280, 420], radius=16, outline=COLOR_ACCENT, width=3, fill=(255, 255, 255))
    hint = module_id.replace("module", "Module ").replace("-", " ")
    draw.text((160, 200), hint, fill=COLOR_TITLE, font=title)
    # Short cue from prompt (truncated) — still not the answer
    cue = prompt.strip()
    if len(cue) > 90:
        cue = cue[:87] + "…"
    for i, line in enumerate(_wrap(draw, cue, body, 1000)[:3]):
        draw.text((160, 280 + i * 40), line, fill=COLOR_BODY, font=body)
    draw.text((80, 480), "Use the figure with the spoken question — do not copy text into an assistant.", fill=COLOR_FOOTER, font=_font(24))
    return img


def generate_related_figure(item: dict, module_id: str, out_path: Path) -> Path:
    """Create a concept figure from the question text / module. Does not mark the answer."""
    prompt = str(item.get("prompt") or "")
    pl = prompt.lower()
    mid = module_id.lower()

    fig: Image.Image
    if "kmap" in mid or "karnaugh" in pl or "k-map" in pl:
        fig = _kmap_figure()
    elif "setup" in mid or "hold" in mid or "setup" in pl or "hold time" in pl:
        fig = _timing_figure()
    elif re.search(r"hex digit\s+([0-9a-f])\b", pl) and ("decimal" in pl or "equals" in pl or "value" in pl):
        m = re.search(r"hex digit\s+([0-9a-f])\b", pl)
        fig = _hex_digit_decimal_figure(m.group(1) if m else "A")
    elif re.search(r"hex digit\s+([0-9a-f])\b", pl):
        m = re.search(r"hex digit\s+([0-9a-f])\b", pl)
        fig = _hex_nibble_figure(m.group(1) if m else "A")
    elif "hex digit" in pl and "bit" in pl:
        fig = _hex_group_figure()
    elif re.search(r"(\d+)\s*bits?\b", pl) and ("distinct" in pl or "represent" in pl or "values" in pl):
        m = re.search(r"(\d+)\s*bits?\b", pl)
        fig = _bit_width_figure(int(m.group(1)) if m else 4)
    elif "0b" in pl or "0x" in pl or "does not change the value" in pl or "same" in pl and "radix" in pl:
        fig = _same_value_spellings_figure()
    elif "hex" in pl or "radix" in mid or "bit" in pl:
        # Default radix family visual
        if "bit" in pl:
            m = re.search(r"(\d+)\s*bits?\b", pl)
            fig = _bit_width_figure(int(m.group(1)) if m else 8)
        else:
            fig = _hex_group_figure()
    else:
        fig = _generic_concept_figure(prompt, module_id)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.save(out_path, "PNG")
    return out_path


def module_title(course: Path, module_id: str) -> str:
    manifest = course / "content.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for mod in data.get("modules") or []:
            if mod.get("id") == module_id:
                return str(mod.get("title") or module_id)
    return module_id


def render_slide_frame(
    item: dict,
    module_id: str,
    figure: Path,
    out_path: Path,
    *,
    module_name: str | None = None,
) -> Path:
    """Light PPT-style slide: module name + org brand, figure, question only."""
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    title_f = _font(40, bold=True)
    brand_f = _font(22, bold=True)
    body_f = _font(34)

    name = (module_name or module_id).strip() or module_id
    # Header: module name (left) + GitHub org (right) — no difficulty
    draw.text((MARGIN, 48), name, fill=COLOR_TITLE, font=title_f)
    brand = "universal-verification-methodology"
    brand_w = draw.textlength(brand, font=brand_f)
    draw.text((W - MARGIN - brand_w, 58), brand, fill=COLOR_FOOTER, font=brand_f)

    # Figure panel — dominant visual
    fig = Image.open(figure).convert("RGB")
    max_w, max_h = W - 2 * MARGIN, 560
    fig.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    fx = (W - fig.width) // 2
    fy = 120
    pad = 16
    draw.rectangle(
        [fx - pad, fy - pad, fx + fig.width + pad, fy + fig.height + pad],
        fill=COLOR_PANEL,
        outline=COLOR_BORDER,
        width=2,
    )
    img.paste(fig, (fx, fy))
    fig_bottom = fy + fig.height + pad + 28

    # Question text only (no choices, no difficulty)
    prompt = str(item.get("prompt") or "").strip()
    lines = _wrap(draw, prompt, body_f, W - 2 * MARGIN)
    ty = fig_bottom
    for line in lines[:4]:
        draw.text((MARGIN, ty), line, fill=COLOR_BODY, font=body_f)
        ty += 44

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def which_or_die(name: str, hint: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"ERROR: `{name}` not found on PATH.\nHINT: {hint}")
    return path


def run_tts(speech_path: Path, audio_path: Path, voice: str, *, retries: int = 5) -> None:
    which_or_die("edge-tts", "pip install edge-tts")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            subprocess.run(
                [
                    "edge-tts",
                    "--voice",
                    voice,
                    "--file",
                    str(speech_path),
                    "--write-media",
                    str(audio_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            if audio_path.is_file() and audio_path.stat().st_size > 200:
                return
            raise RuntimeError(f"edge-tts produced empty audio: {audio_path}")
        except Exception as exc:  # noqa: BLE001 — retry transient TTS / network
            last = exc
            wait = min(60, 2 ** attempt)
            print(f"TTS retry {attempt}/{retries} in {wait}s: {exc}", flush=True)
            time.sleep(wait)
    raise SystemExit(f"edge-tts failed after {retries} retries: {last}")


def run_ffmpeg(frame: Path, audio: Path, out_mp4: Path, fps: int = 30) -> None:
    which_or_die("ffmpeg", "Install ffmpeg (Windows: winget install ffmpeg; WSL: sudo apt install ffmpeg)")
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(frame),
            "-i",
            str(audio),
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-r",
            str(fps),
            "-movflags",
            "+faststart",
            str(out_mp4),
        ],
        check=True,
    )


def patch_media(item: dict, rel_video: str, rel_poster: str | None, rel_figure: str | None) -> None:
    media = {"type": "video", "src": rel_video.replace("\\", "/")}
    if rel_poster:
        media["poster"] = rel_poster.replace("\\", "/")
    if rel_figure:
        media["figure"] = rel_figure.replace("\\", "/")
    item["media"] = media


def build_one(
    course: Path,
    module_id: str,
    item: dict,
    *,
    figure_arg: Path | None,
    voice: str,
    write_media: bool,
    dry_run: bool,
    force_figure: bool,
    reuse_audio: bool,
    prefer_tool: bool,
    skip_existing: bool = False,
) -> Path:
    item_id = str(item.get("id") or "item")
    work = course / "media" / "_work" / item_id
    videos = course / "media" / "videos"
    images = course / "media" / "images"
    work.mkdir(parents=True, exist_ok=True)

    out_mp4 = videos / f"{item_id}.mp4"
    if skip_existing and out_mp4.is_file() and out_mp4.stat().st_size > 1000:
        if write_media:
            patch_media(
                item,
                f"media/videos/{item_id}.mp4",
                f"media/images/{item_id}-frame.png",
                f"media/images/{item_id}.png",
            )
        print(f"skip-existing {item_id}")
        return out_mp4

    figure_path = images / f"{item_id}.png"
    authored = resolve_authored_figure(
        course,
        item,
        figure_arg,
        module_id=module_id,
        prefer_tool=prefer_tool and not force_figure,
    )
    if authored and not force_figure:
        # Keep a per-item copy when using shared tool capture (stable media/images/<id>.png).
        if authored.resolve() != figure_path.resolve():
            figure_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(authored, figure_path)
    else:
        generate_related_figure(item, module_id, figure_path)

    speech = speech_for_item(item, has_figure=True)
    speech_path = work / "speech.txt"
    frame_path = work / "frame.png"
    poster_path = images / f"{item_id}-frame.png"
    audio_path = work / "audio.mp3"

    speech_path.write_text(speech + "\n", encoding="utf-8")
    render_slide_frame(
        item,
        module_id,
        figure_path,
        frame_path,
        module_name=module_title(course, module_id),
    )
    shutil.copy2(frame_path, poster_path)

    if dry_run:
        print(f"DRY-RUN {item_id}: figure={figure_path.name} frame={frame_path}")
        return frame_path

    if reuse_audio and audio_path.is_file():
        print(f"reuse-audio {item_id}")
    else:
        run_tts(speech_path, audio_path, voice)
    run_ffmpeg(frame_path, audio_path, out_mp4)

    if write_media:
        patch_media(
            item,
            f"media/videos/{item_id}.mp4",
            f"media/images/{item_id}-frame.png",
            f"media/images/{item_id}.png",
        )

    print(f"OK {item_id} -> {out_mp4.relative_to(course)}")
    return out_mp4


def main() -> int:
    ap = argparse.ArgumentParser(description="Build PPT-style quiz stem videos")
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--module", required=True)
    ap.add_argument("--item")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--figure", type=Path, help="Author figure override (not *-frame.png)")
    ap.add_argument("--force-figure", action="store_true", help="Regenerate related figure even if images/<id>.png exists")
    ap.add_argument("--reuse-audio", action="store_true", help="Reuse _work/<id>/audio.mp3 when present (skip TTS)")
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip items that already have media/videos/<id>.mp4",
    )
    ap.add_argument(
        "--no-tool-figure",
        action="store_true",
        help="Do not prefer media/images/tools/<toolId>.png from digital_learning",
    )
    ap.add_argument("--voice", default=VOICE_DEFAULT)
    ap.add_argument("--write-media", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    course = args.course if args.course.is_absolute() else (ROOT / args.course)
    course = course.resolve()
    if not course.is_dir():
        raise SystemExit(f"Course pack not found: {course}")

    bpath = bank_path(course, args.module)
    if not bpath.is_file():
        raise SystemExit(f"Bank not found: {bpath}")

    bank = load_bank(bpath)
    items = list(bank.get("items") or [])

    if args.list:
        for it in items:
            print(f"{it.get('id')}\t{it.get('difficulty')}\t{'media' if it.get('media') else '-'}")
        print(f"# {len(items)} items in {bpath.relative_to(course)}")
        return 0

    if args.item:
        it = find_item(bank, args.item)
        if it is None:
            raise SystemExit(f"Item not found: {args.item}")
        selected = [it]
    elif args.all:
        selected = items[: args.limit] if args.limit and args.limit > 0 else items
    else:
        raise SystemExit("Specify --item ID, --all, or --list")

    for it in selected:
        build_one(
            course,
            args.module,
            it,
            figure_arg=args.figure,
            voice=args.voice,
            write_media=args.write_media,
            dry_run=args.dry_run,
            force_figure=args.force_figure,
            reuse_audio=args.reuse_audio,
            prefer_tool=not args.no_tool_figure,
            skip_existing=args.skip_existing,
        )

    if args.write_media and not args.dry_run:
        save_bank(bpath, bank)
        print(f"Patched {bpath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
