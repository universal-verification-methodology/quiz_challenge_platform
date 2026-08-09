#!/usr/bin/env python3
"""Second-pass accuracy check: stem videos vs current quiz bank items.

Validates for each item:
  - media pointers + MP4/poster/figure files exist and are non-trivial
  - work/speech.txt matches speech regenerated from the current prompt/choices
  - speech does not leak explain / correct answer
  - optional: rebuild stale or broken items (--fix)

Usage:
  py -3 .cursor/skills/question-video/scripts/verify_question_videos.py --course content/learn_digital
  py -3 .cursor/skills/question-video/scripts/verify_question_videos.py --fix --workers 4
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
import unicodedata
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
BUILD = SCRIPTS / "build_question_video.py"


def _load_build():
    spec = importlib.util.spec_from_file_location("build_question_video", BUILD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("\ufffd", "...")  # mojibake / lost ellipsis in JSON
    s = s.replace("\u2026", "...").replace("…", "...")
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def sanitize_prompt(s: str) -> str:
    """Repair common bank encoding damage before TTS / comparison."""
    s = str(s or "")
    s = s.replace("\ufffd", "…")
    return s


def correct_answer_text(item: dict) -> str:
    typ = str(item.get("type") or "multiple_choice")
    ans = item.get("answer")
    if typ in ("true_false", "tf"):
        return "true" if ans is True or ans == "true" or ans == 1 else "false"
    if typ in ("short_answer", "short"):
        return str(ans or "").strip()
    choices = item.get("choices") or []
    try:
        i = int(ans)
    except (TypeError, ValueError):
        return str(ans or "").strip()
    if 0 <= i < len(choices):
        return str(choices[i]).strip()
    return str(ans or "").strip()


def spoiler_hits(speech: str, item: dict) -> list[str]:
    """Return leak phrases if explain / correct choice appear as answer reveals."""
    hits: list[str] = []
    nspeech = norm_text(speech)
    explain = str(item.get("explain") or "").strip()
    if explain and len(explain) >= 12 and norm_text(explain) in nspeech:
        hits.append("explain_in_speech")
    # Do not flag choice text alone (choices are meant to be spoken).
    # Flag only explicit reveal patterns.
    if re.search(r"\b(the answer is|correct answer is|answer:\s*)\b", nspeech):
        hits.append("answer_reveal_phrase")
    return hits


def iter_items(course: Path):
    manifest = json.loads((course / "content.json").read_text(encoding="utf-8"))
    for m in manifest.get("modules") or []:
        mid = m["id"]
        rel = m.get("questions") or f"questions/{mid}.json"
        bpath = course / rel
        if not bpath.is_file():
            continue
        bank = json.loads(bpath.read_text(encoding="utf-8"))
        for it in bank.get("items") or []:
            yield mid, bpath, it


def check_item(course: Path, module_id: str, item: dict, build) -> dict:
    iid = str(item.get("id") or "")
    issues: list[str] = []
    media = item.get("media") or {}
    videos = course / "media" / "videos"
    images = course / "media" / "images"
    work = course / "media" / "_work" / iid

    mp4 = videos / f"{iid}.mp4"
    poster = images / f"{iid}-frame.png"
    figure = images / f"{iid}.png"
    speech_path = work / "speech.txt"

    if not mp4.is_file() or mp4.stat().st_size < 1000:
        issues.append("missing_or_tiny_mp4")
    if not poster.is_file() or poster.stat().st_size < 500:
        issues.append("missing_or_tiny_poster")
    if not figure.is_file() or figure.stat().st_size < 500:
        issues.append("missing_or_tiny_figure")

    if media.get("type") != "video":
        issues.append("media_type_not_video")
    if media.get("src") != f"media/videos/{iid}.mp4":
        issues.append("media_src_mismatch")

    expected = build.speech_for_item(item, has_figure=True)
    # Compare using sanitized prompt view as well (bank may have U+FFFD ellipsis)
    item_sanitized = dict(item)
    item_sanitized["prompt"] = sanitize_prompt(item.get("prompt") or "")
    expected_sanitized = build.speech_for_item(item_sanitized, has_figure=True)
    n_exp = norm_text(expected_sanitized)

    has_video = "missing_or_tiny_mp4" not in issues

    if speech_path.is_file():
        actual = speech_path.read_text(encoding="utf-8", errors="replace")
        n_act = norm_text(actual)
        # Only score speech accuracy when a video exists (otherwise still generating).
        if has_video and n_act != n_exp and n_act != norm_text(expected):
            issues.append("speech_stale_vs_bank")
        if has_video:
            prompt = norm_text(sanitize_prompt(str(item.get("prompt") or "")))
            if prompt and len(prompt) >= 8:
                pcore = prompt.rstrip(" .?")
                if pcore and pcore not in n_act:
                    issues.append("prompt_missing_from_stored_speech")
            issues.extend(spoiler_hits(actual, item))
    elif has_video:
        issues.append("missing_speech_txt")

    accuracy_codes = {
        "speech_stale_vs_bank",
        "prompt_missing_from_stored_speech",
        "missing_speech_txt",
        "explain_in_speech",
        "answer_reveal_phrase",
        "missing_or_tiny_poster",
        "missing_or_tiny_figure",
    }
    has_accuracy_issue = any(i in accuracy_codes for i in issues)

    return {
        "module_id": module_id,
        "item_id": iid,
        "ok": not issues,
        "pending": (not has_video) and not has_accuracy_issue,
        "issues": issues,
        "expected_speech": expected,
    }


def rebuild_one(args: tuple[str, str, str]) -> tuple[str, str, int, str]:
    course, mid, iid = args
    # Force rebuild: remove mp4 so skip-existing does not short-circuit
    mp4 = Path(course) / "media" / "videos" / f"{iid}.mp4"
    if mp4.is_file():
        try:
            mp4.unlink()
        except OSError:
            pass
    # Do not --write-media here: parallel workers race on the same bank JSON.
    # Banks are patched once after all rebuilds complete.
    cmd = [
        sys.executable,
        "-u",
        str(BUILD),
        "--course",
        course,
        "--module",
        mid,
        "--item",
        iid,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = ((r.stdout or "") + (r.stderr or ""))[-400:]
        return mid, iid, r.returncode, out
    except Exception as exc:  # noqa: BLE001
        return mid, iid, 1, str(exc)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--module", action="append", default=[], help="Limit to module id(s)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fix", action="store_true", help="Rebuild items that fail checks")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write JSON report path (default: media/_batch_logs/verify_report.json)",
    )
    ap.add_argument(
        "--issues",
        nargs="*",
        default=None,
        help="Only fix these issue codes (default: all). Example: speech_stale_vs_bank missing_or_tiny_mp4",
    )
    args = ap.parse_args()
    course = args.course.resolve()
    build = _load_build()

    allow_mods = set(args.module) if args.module else None
    results = []
    for mid, _bpath, it in iter_items(course):
        if allow_mods and mid not in allow_mods:
            continue
        results.append(check_item(course, mid, it, build))
        if args.limit and len(results) >= args.limit:
            break

    ok_n = sum(1 for r in results if r["ok"])
    pending_n = sum(1 for r in results if (not r["ok"]) and r.get("pending"))
    bad = [r for r in results if (not r["ok"]) and not r.get("pending")]
    by_issue: dict[str, int] = {}
    for r in results:
        if r["ok"]:
            continue
        for i in r["issues"]:
            by_issue[i] = by_issue.get(i, 0) + 1

    report = {
        "course": str(course),
        "checked": len(results),
        "ok": ok_n,
        "pending_generation": pending_n,
        "accuracy_failures": len(bad),
        "by_issue": by_issue,
        "failures": [
            {"module_id": r["module_id"], "item_id": r["item_id"], "issues": r["issues"]}
            for r in bad
        ],
    }
    report_path = args.report or (course / "media" / "_batch_logs" / "verify_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"Checked {len(results)}: ok={ok_n} pending={pending_n} accuracy_fail={len(bad)}",
        flush=True,
    )
    for k, v in sorted(by_issue.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}", flush=True)
    print(f"Report: {report_path}", flush=True)

    if not args.fix or not bad:
        return 0 if not bad else 1

    issue_filter = set(args.issues) if args.issues else None
    to_fix = []
    for r in bad:
        if issue_filter and not (set(r["issues"]) & issue_filter):
            continue
        to_fix.append((str(course), r["module_id"], r["item_id"]))

    print(f"Rebuilding {len(to_fix)} items with workers={args.workers}", flush=True)
    fail = 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {ex.submit(rebuild_one, job): job for job in to_fix}
        done = 0
        for fut in as_completed(futs):
            mid, iid, rc, out = fut.result()
            done += 1
            if rc == 0:
                print(f"FIXED [{done}/{len(to_fix)}] {iid}", flush=True)
            else:
                fail += 1
                print(f"FAIL [{done}/{len(to_fix)}] {iid} rc={rc}\n{out}", flush=True)

    # Re-patch banks for fixed modules
    touched = {mid for _c, mid, _i in to_fix}
    for mid in sorted(touched):
        bpath = course / "questions" / f"{mid}.json"
        if not bpath.is_file():
            continue
        data = json.loads(bpath.read_text(encoding="utf-8"))
        changed = False
        for it in data.get("items") or []:
            iid = it["id"]
            mp4 = course / "media" / "videos" / f"{iid}.mp4"
            if mp4.is_file() and mp4.stat().st_size > 1000:
                media = it.setdefault("media", {})
                want = {
                    "type": "video",
                    "src": f"media/videos/{iid}.mp4",
                    "poster": f"media/images/{iid}-frame.png",
                    "figure": f"media/images/{iid}.png",
                }
                if media != want:
                    media.clear()
                    media.update(want)
                    changed = True
        if changed:
            bpath.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Patched {bpath.name}", flush=True)

    print(f"Fix done fail={fail} elapsed={time.time() - t0:.0f}s", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
