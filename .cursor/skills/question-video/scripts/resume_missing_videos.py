#!/usr/bin/env python3
"""Resume missing stem videos with a fixed worker pool (item-level)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUILD = Path(__file__).resolve().parent / "build_question_video.py"


def missing_jobs(course: Path) -> list[tuple[str, str]]:
    manifest = json.loads((course / "content.json").read_text(encoding="utf-8"))
    vid = course / "media" / "videos"
    jobs: list[tuple[str, str]] = []
    for m in manifest.get("modules") or []:
        mid = m["id"]
        qpath = course / "questions" / f"{mid}.json"
        if not qpath.is_file():
            continue
        items = json.loads(qpath.read_text(encoding="utf-8")).get("items") or []
        for it in items:
            iid = it["id"]
            mp4 = vid / f"{iid}.mp4"
            if not mp4.is_file() or mp4.stat().st_size < 1000:
                jobs.append((mid, iid))
    return jobs


def build_one(args: tuple[str, str, str, bool]) -> tuple[str, str, int, str]:
    course, mid, iid, reuse_audio = args
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
        "--skip-existing",
        # Do NOT --write-media here: parallel workers race on the same bank JSON.
    ]
    if reuse_audio:
        cmd.append("--reuse-audio")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = ((r.stdout or "") + (r.stderr or ""))[-500:]
        return mid, iid, r.returncode, out
    except Exception as exc:  # noqa: BLE001
        return mid, iid, 1, str(exc)


def patch_banks(course: Path, touched: set[str]) -> None:
    """Re-run --all --skip-existing --write-media per touched module to persist media fields."""
    for mid in sorted(touched):
        cmd = [
            sys.executable,
            "-u",
            str(BUILD),
            "--course",
            str(course),
            "--module",
            mid,
            "--all",
            "--write-media",
            "--skip-existing",
            "--reuse-audio",
        ]
        # dry: skip-existing will only patch JSON for existing mp4s
        subprocess.run(cmd, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--reuse-audio", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    course = args.course.resolve()
    jobs = missing_jobs(course)
    if args.limit and args.limit > 0:
        jobs = jobs[: args.limit]
    print(f"Missing videos: {len(jobs)}; workers={args.workers}", flush=True)
    if not jobs:
        return 0

    # Stop competing module-level runners? leave to caller.
    work = [(str(course), mid, iid, args.reuse_audio) for mid, iid in jobs]
    ok = fail = 0
    failed: list[tuple[str, str]] = []
    touched: set[str] = set()
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(build_one, w): w for w in work}
        done_n = 0
        for fut in as_completed(futs):
            mid, iid, rc, out = fut.result()
            done_n += 1
            touched.add(mid)
            if rc == 0:
                ok += 1
                print(f"OK [{done_n}/{len(work)}] {iid}", flush=True)
            else:
                fail += 1
                failed.append((mid, iid))
                print(f"FAIL [{done_n}/{len(work)}] {iid} rc={rc}\n{out}", flush=True)

    # Persist media pointers in banks (item-mode already patches one item if write-media)
    # Re-save any bank that was touched by scanning filesystem once more.
    for mid in sorted(touched):
        bpath = course / "questions" / f"{mid}.json"
        data = json.loads(bpath.read_text(encoding="utf-8"))
        changed = False
        for it in data.get("items") or []:
            iid = it["id"]
            mp4 = course / "media" / "videos" / f"{iid}.mp4"
            if mp4.is_file():
                media = it.setdefault("media", {})
                want = {
                    "type": "video",
                    "src": f"media/videos/{iid}.mp4",
                    "poster": f"media/images/{iid}-frame.png",
                    "figure": f"media/images/{iid}.png",
                }
                if media.get("src") != want["src"]:
                    media.update(want)
                    changed = True
        if changed:
            bpath.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Patched {bpath.name}", flush=True)

    elapsed = time.time() - t0
    print(f"Done ok={ok} fail={fail} elapsed={elapsed:.0f}s", flush=True)
    if failed:
        print("Failed items:")
        for mid, iid in failed[:50]:
            print(f"  {mid} {iid}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
