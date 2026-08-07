#!/usr/bin/env python3
"""Sync browser-tool screenshots from digital_learning into challenge media.

Default: Playwright capture of the *instrument* panels only (hide challenge chrome).
K-map → Karnaugh map + Minimal SOP (`.tool-layout.split-wide`).
Optional: copy module `assets/lab-starter.png` (full UI, usually too busy for stems).

eda_learning idea: one visual idea per stem — the real tool surface, not the challenge catalog.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DL = Path("d:/proj/designs/digital_learning")
DEFAULT_LIVE = "https://universal-verification-methodology.github.io/learning/tools"

# toolId → crop + optional prep (click starter, hide challenge chrome)
TOOL_CAPTURE = {
    "radix-converter": {
        # Bit pattern + radix views + ranges/HDL (hide challenge catalog)
        "root": "#rc-root",
        "selector": "#rc-root",
        "hide": [
            ".challenge",
            ".starter-note",
            ".eyebrow",
            ".hero",
            ".site-header",
            ".site-footer",
            ".site-header-crumb",
        ],
        "click": ["#rc-starter"],
        "viewport": (1100, 900),
    },
    "kmap": {
        "selector": ".tool-layout.split-wide",
        "hide": [".challenge", "#starter-note", ".eyebrow", ".hero", ".site-header", ".site-footer"],
        "click": ["#btn-starter"],
        "viewport": (1280, 800),
    },
    "setup-hold": {
        "selector": "#sh-root .tool-layout, #sh-root .panel, #sh-root",
        "hide": [".challenge", ".starter-note.no-print", ".eyebrow", ".hero", ".site-header", ".site-footer"],
        "click": ["button:has-text('Load starter')", "[data-preset='clean']"],
        "viewport": (1280, 900),
    },
}

MODULE_TOOLS = {
    "module01-radix-converter": "radix-converter",
    "module13-kmap": "kmap",
    "module26-setup-hold": "setup-hold",
}


def load_modules(course: Path) -> list[dict]:
    manifest = course / "content.json"
    if not manifest.is_file():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return list(data.get("modules") or [])


def copy_lab_starter(dl: Path, module_id: str, tool_id: str, dest: Path) -> bool:
    src = dl / "courses" / "learn_digital" / module_id / "assets" / "lab-starter.png"
    if not src.is_file():
        alt = dl / "courses" / "learn_digital" / module_id / "frames" / "slide-3.png"
        src = alt if alt.is_file() else src
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"copied {src} -> {dest}")
    return True


def capture_instrument(tool_id: str, dest: Path, *, base: str) -> bool:
    """Capture map/SOP (or equivalent) only — not the challenge catalog."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("pip install playwright && playwright install chromium") from exc

    cfg = TOOL_CAPTURE.get(tool_id) or {
        "selector": "main",
        "hide": [".challenge", ".site-header", ".site-footer"],
        "click": [],
        "viewport": (1280, 800),
    }
    url = f"{base.rstrip('/')}/{tool_id}/index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    vw, vh = cfg.get("viewport") or (1280, 800)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": vw, "height": vh})
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(1500)

        for sel in cfg.get("hide") or []:
            page.evaluate(
                """(sel) => {
                  document.querySelectorAll(sel).forEach((el) => { el.style.display = 'none'; });
                }""",
                sel,
            )

        for sel in cfg.get("click") or []:
            try:
                loc = page.locator(sel).first
                if loc.count() and loc.is_visible():
                    loc.click(timeout=3000)
                    page.wait_for_timeout(800)
                    break
            except Exception:
                continue

        page.wait_for_timeout(500)
        shot = False
        for sel in [cfg.get("selector")] + list(cfg.get("also") or []):
            if not sel:
                continue
            try:
                loc = page.locator(sel).first
                loc.wait_for(state="visible", timeout=8000)
                loc.screenshot(path=str(dest))
                shot = True
                break
            except Exception:
                continue
        if not shot:
            page.screenshot(path=str(dest), full_page=False)
        browser.close()

    ok = dest.is_file() and dest.stat().st_size > 1000
    print(f"{'OK' if ok else 'FAIL'} capture {tool_id} -> {dest} ({url})")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync DDV tool instrument panels into challenge media")
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--digital-learning", type=Path, default=DEFAULT_DL)
    ap.add_argument(
        "--mode",
        choices=("capture", "copy", "copy-then-capture"),
        default="capture",
        help="capture instrument panels (default), copy full lab-starter, or both",
    )
    ap.add_argument("--base", default=DEFAULT_LIVE)
    ap.add_argument("--only", help="Only one toolId, e.g. kmap")
    args = ap.parse_args()

    course = args.course if args.course.is_absolute() else (ROOT / args.course)
    course = course.resolve()
    dl = args.digital_learning.resolve()
    out_dir = course / "media" / "images" / "tools"
    out_dir.mkdir(parents=True, exist_ok=True)

    modules = load_modules(course)
    if not modules:
        modules = [{"id": mid, "toolId": tid} for mid, tid in MODULE_TOOLS.items()]

    ok = 0
    for mod in modules:
        mid = mod.get("id") or ""
        tool_id = mod.get("toolId") or MODULE_TOOLS.get(mid)
        if not tool_id:
            continue
        if args.only and tool_id != args.only:
            continue
        dest = out_dir / f"{tool_id}.png"
        done = False
        if args.mode in ("copy", "copy-then-capture"):
            done = copy_lab_starter(dl, mid, tool_id, dest)
        if args.mode == "capture" or (args.mode == "copy-then-capture" and not done):
            done = capture_instrument(tool_id, dest, base=args.base)
        if done:
            ok += 1
        else:
            print(f"FAILED {mid} / {tool_id}", file=sys.stderr)

    readme = out_dir / "README.md"
    readme.write_text(
        "# Tool figures (stem instruments)\n\n"
        "Captured for quiz stems — **map / converter / timing panels only**, "
        "challenge catalogs hidden.\n\n"
        "- `kmap.png` — Karnaugh map + Minimal SOP (`.tool-layout.split-wide`)\n"
        "- `radix-converter.png` — radix views (+ bit pattern when available)\n"
        "- `setup-hold.png` — timing instrument panel\n\n"
        "Live tools: https://universal-verification-methodology.github.io/learning/tools/\n"
        "Re-capture: `python .cursor/skills/question-video/scripts/sync_tool_figures.py --mode capture`\n",
        encoding="utf-8",
    )

    print(f"Synced {ok} tool figure(s) -> {out_dir}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
