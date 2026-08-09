#!/usr/bin/env python3
"""Force-rebuild every stem video (delete mp4, fresh TTS, no parallel bank writes)."""

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


def all_jobs(course: Path) -> list[tuple[str, str]]:
    manifest = json.loads((course / "content.json").read_text(encoding="utf-8"))
    jobs: list[tuple[str, str]] = []
    for m in manifest.get("modules") or []:
        mid = m["id"]
        qpath = course / "questions" / f"{mid}.json"
        if not qpath.is_file():
            continue
        for it in json.loads(qpath.read_text(encoding="utf-8")).get("items") or []:
            jobs.append((mid, it["id"]))
    return jobs


def rebuild_one(args: tuple[str, str, str]) -> tuple[str, str, int, str]:
    course, mid, iid = args
    mp4 = Path(course) / "media" / "videos" / f"{iid}.mp4"
    if mp4.is_file():
        try:
            mp4.unlink()
        except OSError:
            pass
    # No --write-media: parallel workers must not race on bank JSON.
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


def patch_banks(course: Path) -> None:
    vid = course / "media" / "videos"
    for bpath in sorted((course / "questions").glob("*.json")):
        data = json.loads(bpath.read_text(encoding="utf-8"))
        changed = False
        for it in data.get("items") or []:
            iid = it["id"]
            mp4 = vid / f"{iid}.mp4"
            if not mp4.is_file() or mp4.stat().st_size < 1000:
                continue
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
            bpath.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(f"Patched {bpath.name}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    course = args.course.resolve()
    jobs = all_jobs(course)
    if args.limit and args.limit > 0:
        jobs = jobs[: args.limit]
    print(f"Force rebuild {len(jobs)} videos; workers={args.workers}", flush=True)
    if not jobs:
        return 0

    work = [(str(course), mid, iid) for mid, iid in jobs]
    fail = 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {ex.submit(rebuild_one, job): job for job in work}
        done = 0
        for fut in as_completed(futs):
            mid, iid, rc, out = fut.result()
            done += 1
            if rc == 0:
                print(f"OK [{done}/{len(work)}] {iid}", flush=True)
            else:
                fail += 1
                print(f"FAIL [{done}/{len(work)}] {iid} rc={rc}\n{out}", flush=True)

    print("Patching bank media fields…", flush=True)
    patch_banks(course)
    print(f"Done ok={len(work) - fail} fail={fail} elapsed={time.time() - t0:.0f}s", flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
