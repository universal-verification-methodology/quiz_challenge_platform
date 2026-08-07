#!/usr/bin/env python3
"""Capture per-question instrument figures from digital_learning tools.

Reads item['tool_capture'] (from bind_tool_states.py), drives Playwright to that
challenge/state, screenshots the instrument panels, and writes:
  media/images/tools/states/<tool>__<key>.png
  media/images/<item_id>.png  (copy for the stem builder)

So stems differ by question family instead of all sharing one starter PNG.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LIVE = "https://universal-verification-methodology.github.io/learning/tools"

HIDE = [
    ".challenge",
    ".starter-note",
    "#starter-note",
    ".eyebrow",
    ".hero",
    ".site-header",
    ".site-footer",
    ".site-header-crumb",
]

SELECTORS = {
    "radix-converter": "#rc-root",
    "twos-complement": "#tc-root .tool-layout, #tc-root",
    "overflow-wrap": "#ow-root .tool-layout, #ow-root",
    "ascii-hex": "#ah-root .tool-layout, #ah-root",
    "gray-code": "#gc-root .tool-layout, #gc-root",
    "bcd-lab": "#bcd-root .tool-layout, #bcd-root",
    "parity-checksum": "#px-root .tool-layout, #px-root",
    "fixed-point": "#fp-root .tool-layout, #fp-root",
    "bit-fields": "#bf-root .tool-layout, #bf-root",
    "endian-lab": "#en-root .tool-layout, #en-root",
    "truth-table": "#tt-root .tool-layout, #tt-root",
    "boolean-laws": "#bl-root .tool-layout, #bl-root",
    "kmap": ".tool-layout.split-wide",
    "sop-pos": "#sp-root .tool-layout, #sp-root",
    "dont-care-lab": "#dc-root .tool-layout, #dc-root",
    "logic-hazards": "#hz-root .tool-layout, #hz-root",
    "gate-composer": "#gc-root .tool-layout, #gc-root",
    "mux-decoder": "#md-root .panel, #md-root #viz, #md-root",
    "priority-compare": "#pc-root .tool-layout, #pc-root",
    "half-full-adder": "#ha-root .tool-layout, #ha-root",
    "xor-parity-tree": "#xp-root .tool-layout, #xp-root",
    "tri-state-bus": "#ts-root .tool-layout, #ts-root",
    "barrel-shifter": "#bs-root .tool-layout, #bs-root",
    "seven-segment": "#ss-root .tool-layout, #ss-root",
    "clock-stepper": "#cs-root .tool-layout, #cs-root",
    "setup-hold": "#sh-root",
    "reset-timelines": "#rt-root .tool-layout, #rt-root",
    "clock-enable": "#ce-root .tool-layout, #ce-root",
    "cdc-sync": "#cdc-root .tool-layout, #cdc-root",
    "fsm-lab": "#fsm-root .tool-layout, #fsm-root",
    "state-encoding": "#se-root .tool-layout, #se-root",
    "seq-detector": "#sd-root .tool-layout, #sd-root",
    "ring-johnson": "#rj-root .tool-layout, #rj-root",
    "lfsr-lab": "#lfsr-root .tool-layout, #lfsr-root",
    "ripple-carry-adder-animator": "#rca-root .tool-layout, #rca-root",
    "carry-look-ahead-adder-propagate-and-generate": "#cla-root .tool-layout, #cla-root",
    "array-mult": "#am-root .tool-layout, #am-root",
    "alu-explorer": "#alu-root .tool-layout, #alu-root",
    "carry-select-adder": "#csa-root .tool-layout, #csa-root",
    "booth-encode": "#booth-root .tool-layout, #booth-root",
    "signed-arith": "#sa-root .tool-layout, #sa-root",
    "mem-map": "#mm-root .tool-layout, #mm-root",
    "fifo-lab": "#fifo-root .tool-layout, #fifo-root",
    "cache-walk": "#cw-root .tool-layout, #cw-root",
    "dual-port-ram": "#dpr-root .tool-layout, #dpr-root",
    "byte-enable-mem": "#be-root .tool-layout, #be-root",
    "async-fifo": "#af-root .tool-layout, #af-root",
    "handshake": "#hs-root .tool-layout, #hs-root",
    "block-diagram": "#bd-root .tool-layout, #bd-root",
}


def hide_chrome(page) -> None:
    for sel in HIDE:
        page.evaluate(
            """(sel) => {
              document.querySelectorAll(sel).forEach((el) => { el.style.display = 'none'; });
            }""",
            sel,
        )


def run_steps(page, steps: list[dict]) -> None:
    for step in steps or []:
        if "challenge" in step:
            title = step["challenge"]
            # Catalog buttons (kmap / mux / most labs)
            candidates = [
                page.locator(
                    ".challenge button, .challenge-list button, .kbd-row button, .gc-chal-catalog button"
                ).filter(has_text=title),
                page.get_by_role("button", name=title, exact=True),
                page.get_by_role("button", name=title, exact=False),
            ]
            clicked = False
            for loc in candidates:
                try:
                    if loc.count() == 0:
                        continue
                    loc.first.click(timeout=5000)
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                raise RuntimeError(f"challenge button not found: {title}")
            page.wait_for_timeout(500)
            continue
        if "click" in step:
            sel = step["click"]
            page.locator(sel).first.click(timeout=8000)
            page.wait_for_timeout(600)
            continue
        if "select" in step:
            page.locator(step["select"]).select_option(step["value"])
            page.wait_for_timeout(300)
            continue
        if "fill" in step:
            loc = page.locator(step["fill"]).first
            loc.click(timeout=5000)
            loc.fill("")
            loc.fill(str(step["value"]))
            if step.get("enter"):
                loc.press("Enter")
            else:
                loc.press("Tab")
            page.wait_for_timeout(450)
            continue


def capture_state(tool: str, key: str, steps: list[dict], dest: Path, *, base: str) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("pip install playwright && playwright install chromium") from exc

    url = f"{base.rstrip('/')}/{tool}/index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    selector = SELECTORS.get(tool, "main")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=90_000)
        page.wait_for_timeout(1200)
        try:
            run_steps(page, steps)
        except Exception as exc:
            print(f"  setup failed {tool}/{key}: {exc}", file=sys.stderr, flush=True)
            # Still try a chrome-hidden screenshot so we don't block the pipeline
        hide_chrome(page)
        page.wait_for_timeout(350)
        shot = False
        for sel in [s.strip() for s in selector.split(",") if s.strip()]:
            try:
                page.locator(sel).first.wait_for(state="visible", timeout=5000)
                page.locator(sel).first.screenshot(path=str(dest))
                shot = True
                break
            except Exception:
                continue
        if not shot:
            page.screenshot(path=str(dest), full_page=False)
        browser.close()

    ok = dest.is_file() and dest.stat().st_size > 800
    print(f"  {'OK' if ok else 'FAIL'} {tool}__{key} -> {dest.name}", flush=True)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--module", help="module id / questions stem")
    ap.add_argument("--base", default=DEFAULT_LIVE)
    ap.add_argument("--limit-states", type=int, default=0, help="Max unique states (debug)")
    args = ap.parse_args()

    course = args.course.resolve()
    qdir = course / "questions"
    img_dir = course / "media" / "images"
    state_dir = img_dir / "tools" / "states"
    state_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(qdir.glob("*.json"))
    if args.module:
        paths = [p for p in paths if p.stem == args.module]

    jobs: dict[str, dict] = {}
    # (item_id, bank_path, uniq)
    item_refs: list[tuple[str, Path, str]] = []

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for it in data.get("items") or []:
            cap = it.get("tool_capture")
            if not isinstance(cap, dict):
                continue
            tool = cap.get("tool")
            key = cap.get("key")
            if not tool or not key:
                continue
            uniq = f"{tool}__{key}"
            if uniq not in jobs:
                jobs[uniq] = cap
            item_refs.append((str(it["id"]), path, uniq))

    print(f"Unique instrument states: {len(jobs)}")
    keys = list(jobs.keys())
    if args.limit_states and args.limit_states > 0:
        keys = keys[: args.limit_states]
        allowed = set(keys)
        item_refs = [r for r in item_refs if r[2] in allowed]

    ok_map: dict[str, Path] = {}
    for uniq in keys:
        cap = jobs[uniq]
        dest = state_dir / f"{uniq}.png"
        if capture_state(cap["tool"], cap["key"], cap.get("steps") or [], dest, base=args.base):
            ok_map[uniq] = dest

    # Copy state PNGs onto each item image + patch media.figure in banks
    banks: dict[Path, dict] = {}
    for path in {p for _, p, _ in item_refs}:
        banks[path] = json.loads(path.read_text(encoding="utf-8"))

    n_copy = 0
    for item_id, bank_path, uniq in item_refs:
        src = ok_map.get(uniq)
        if not src:
            continue
        dest = img_dir / f"{item_id}.png"
        shutil.copy2(src, dest)
        data = banks[bank_path]
        for it in data.get("items") or []:
            if it.get("id") == item_id:
                it.setdefault("media", {})["figure"] = f"media/images/{item_id}.png"
                break
        n_copy += 1

    for path, data in banks.items():
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Captured {len(ok_map)} states; wrote {n_copy} item figures")
    return 0 if ok_map else 1


if __name__ == "__main__":
    raise SystemExit(main())
