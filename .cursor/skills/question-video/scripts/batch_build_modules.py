#!/usr/bin/env python3
"""Batch-build stem videos for one or more modules."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUILD = Path(__file__).resolve().parent / "build_question_video.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--modules", nargs="+", required=True, help="module ids")
    ap.add_argument("--reuse-audio", action="store_true")
    ap.add_argument("--skip-existing", action="store_true", default=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--write-media", action="store_true", default=True)
    args = ap.parse_args()

    for mid in args.modules:
        cmd = [
            sys.executable,
            "-u",
            str(BUILD),
            "--course",
            str(args.course),
            "--module",
            mid,
            "--all",
            "--write-media",
            "--skip-existing",
        ]
        if args.reuse_audio:
            cmd.append("--reuse-audio")
        if args.limit and args.limit > 0:
            cmd.extend(["--limit", str(args.limit)])
        print(f"\n=== BUILD {mid} ===", flush=True)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print(f"FAILED {mid} rc={r.returncode}", file=sys.stderr)
            return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
