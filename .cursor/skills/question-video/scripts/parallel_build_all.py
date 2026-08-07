#!/usr/bin/env python3
"""Launch one build_question_video process per module in parallel."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUILD = Path(__file__).resolve().parent / "build_question_video.py"


def modules_needing_work(course: Path) -> list[str]:
    manifest = json.loads((course / "content.json").read_text(encoding="utf-8"))
    vid = course / "media" / "videos"
    out = []
    for m in manifest.get("modules") or []:
        mid = m["id"]
        qpath = course / "questions" / f"{mid}.json"
        if not qpath.is_file():
            continue
        items = json.loads(qpath.read_text(encoding="utf-8")).get("items") or []
        n = sum(1 for it in items if (vid / f"{it['id']}.mp4").is_file())
        if n < len(items):
            out.append(mid)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--modules", nargs="*", help="Explicit module ids (default: incomplete)")
    ap.add_argument("--reuse-audio", action="store_true")
    ap.add_argument("--skip-existing", action="store_true", default=True)
    ap.add_argument("--max-procs", type=int, default=0, help="0 = all modules at once")
    ap.add_argument("--log-dir", type=Path, default=None)
    args = ap.parse_args()

    course = args.course.resolve()
    mods = args.modules or modules_needing_work(course)
    if not mods:
        print("Nothing to build")
        return 0

    log_dir = args.log_dir or (course / "media" / "_batch_logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"Launching {len(mods)} module builds in parallel -> {log_dir}", flush=True)
    procs: list[tuple[str, subprocess.Popen, Path]] = []
    for mid in mods:
        log = log_dir / f"{mid}.log"
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
        ]
        if args.reuse_audio:
            cmd.append("--reuse-audio")
        lf = open(log, "w", encoding="utf-8")
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
        procs.append((mid, p, log))
        print(f"  started {mid} pid={p.pid} log={log.name}", flush=True)
        if args.max_procs and len(procs) >= args.max_procs:
            # wait for one to finish before starting more
            while True:
                done = [(m, pr, lg) for m, pr, lg in procs if pr.poll() is not None]
                if done:
                    for m, pr, lg in done:
                        print(f"  finished {m} rc={pr.returncode}", flush=True)
                        procs.remove((m, pr, lg))
                    break
                time.sleep(2)

    failed = 0
    while procs:
        time.sleep(5)
        still = []
        for mid, p, log in procs:
            rc = p.poll()
            if rc is None:
                still.append((mid, p, log))
            else:
                print(f"  finished {mid} rc={rc}", flush=True)
                if rc != 0:
                    failed += 1
        procs = still
        if still:
            print(f"  … {len(still)} running", flush=True)

    print(f"All done. failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
