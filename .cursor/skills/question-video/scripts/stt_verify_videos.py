#!/usr/bin/env python3
"""STT round-trip: transcribe stem audio and compare to the quiz item.

Unlike verify_question_videos.py (script-vs-bank), this checks what was actually
spoken in audio.mp3 / the MP4 against prompt + choices.

Usage:
  py -3 .cursor/skills/question-video/scripts/stt_verify_videos.py --course content/learn_verilog
  py -3 .cursor/skills/question-video/scripts/stt_verify_videos.py --course content/learn_verilog --limit 10
  py -3 .cursor/skills/question-video/scripts/stt_verify_videos.py --course content/learn_verilog --workers 2 --model tiny.en
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ProcessPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
BUILD = SCRIPTS / "build_question_video.py"


def _load_build():
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_question_video", BUILD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_BUILD = None


def speakable(s: str) -> str:
    global _BUILD
    if _BUILD is None:
        _BUILD = _load_build()
    return _BUILD.speakable_verilog(s)

STOP = {
    "a", "an", "the", "of", "to", "in", "on", "at", "for", "and", "or", "is",
    "as", "be", "by", "it", "if", "this", "that", "with", "from", "are", "was",
}

_MODEL = None
_MODEL_NAME = None


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
            yield mid, it


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("\ufffd", " ").replace("\u2026", " ").replace("…", " ")
    s = s.replace("```verilog", " ").replace("```", " ")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str) -> list[str]:
    return [t for t in norm_text(s).split() if t]


def content_tokens(s: str) -> list[str]:
    return [t for t in tokens(s) if t not in STOP and len(t) >= 3]


def strip_code(s: str) -> str:
    return re.sub(r"```.*?```", " ", s or "", flags=re.S)


def recall(expected: list[str], actual_set: set[str]) -> float:
    if not expected:
        return 1.0
    hit = sum(1 for t in expected if t in actual_set)
    return hit / len(expected)


def ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def init_worker(model_name: str, cpu_threads: int) -> None:
    global _MODEL, _MODEL_NAME
    from faster_whisper import WhisperModel

    _MODEL = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        cpu_threads=max(1, cpu_threads),
    )
    _MODEL_NAME = model_name


def transcribe_path(audio: Path) -> str:
    segments, _info = _MODEL.transcribe(
        str(audio),
        language="en",
        beam_size=1,
        vad_filter=False,
        condition_on_previous_text=False,
    )
    return re.sub(r"\s+", " ", " ".join(s.text for s in segments)).strip()


def score_item(item: dict, expected_speech: str, stt: str) -> dict:
    # Score against speakable narration, not raw Verilog punctuation (4'b1110).
    english = speakable(strip_code(str(item.get("prompt") or "")))
    choices = [speakable(str(c)) for c in (item.get("choices") or [])]
    boilerplate = {
        "look", "browser", "lab", "figure", "slide", "question", "given",
        "rtl", "snippet", "option", "select", "best", "answer", "true", "false",
    }

    stt_set = set(tokens(stt))
    eng_toks = [t for t in content_tokens(english) if t not in boilerplate]
    exp_toks = content_tokens(expected_speech)

    eng_recall = recall(eng_toks, stt_set)
    overall_recall = recall(exp_toks, stt_set)
    sim = ratio(norm_text(expected_speech), norm_text(stt))

    choice_hits = 0
    missing_choices: list[int] = []
    for i, ch in enumerate(choices):
        ct = content_tokens(ch)
        cr = recall(ct, stt_set)
        if cr >= 0.5 or (not ct and tokens(ch) and all(t in stt_set for t in tokens(ch))):
            choice_hits += 1
        else:
            missing_choices.append(i)
    choice_cov = (choice_hits / len(choices)) if choices else 1.0

    issues: list[str] = []
    if eng_recall < 0.65:
        issues.append("low_english_recall")
    if choice_cov < 0.5:
        issues.append("low_choice_coverage")
    if overall_recall < 0.35:
        issues.append("low_overall_recall")
    if len(stt) < 20:
        issues.append("stt_too_short")

    return {
        "english_recall": round(eng_recall, 3),
        "overall_recall": round(overall_recall, 3),
        "similarity": round(sim, 3),
        "choice_coverage": round(choice_cov, 3),
        "missing_choices": missing_choices,
        "issues": issues,
        "ok": not issues,
    }


def worker_job(payload: dict) -> dict:
    course = Path(payload["course"])
    iid = payload["item_id"]
    work = course / "media" / "_work" / iid
    stt_path = work / "stt.txt"
    audio = work / "audio.mp3"
    if not audio.is_file():
        audio = course / "media" / "videos" / f"{iid}.mp4"

    t0 = time.time()
    if payload.get("reuse") and stt_path.is_file() and stt_path.stat().st_size > 10:
        stt = stt_path.read_text(encoding="utf-8", errors="replace").strip()
        reused = True
    else:
        if not audio.is_file():
            return {
                "module_id": payload["module_id"],
                "item_id": iid,
                "ok": False,
                "issues": ["missing_audio"],
                "stt": "",
                "elapsed_s": 0.0,
            }
        stt = transcribe_path(audio)
        stt_path.write_text(stt + "\n", encoding="utf-8")
        reused = False

    scored = score_item(payload["item"], payload["expected"], stt)
    scored.update(
        {
            "module_id": payload["module_id"],
            "item_id": iid,
            "stt": stt,
            "reused": reused,
            "elapsed_s": round(time.time() - t0, 2),
        }
    )
    return scored


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--course", type=Path, default=ROOT / "content" / "learn_digital")
    ap.add_argument("--module", action="append", default=[])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--model", default="tiny.en", help="faster-whisper model, e.g. tiny.en / base.en")
    ap.add_argument("--cpu-threads", type=int, default=4)
    ap.add_argument("--reuse", action="store_true", help="Reuse existing _work/<id>/stt.txt")
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()
    course = args.course.resolve()

    jobs = []
    allow = set(args.module) if args.module else None
    for mid, it in iter_items(course):
        if allow and mid not in allow:
            continue
        iid = str(it.get("id") or "")
        speech_path = course / "media" / "_work" / iid / "speech.txt"
        expected = speech_path.read_text(encoding="utf-8", errors="replace") if speech_path.is_file() else str(it.get("prompt") or "")
        jobs.append(
            {
                "course": str(course),
                "module_id": mid,
                "item_id": iid,
                "item": it,
                "expected": expected,
                "reuse": args.reuse,
            }
        )
        if args.limit and len(jobs) >= args.limit:
            break

    print(
        f"STT-verify {len(jobs)} items model={args.model} workers={args.workers} course={course}",
        flush=True,
    )
    t0 = time.time()
    results = []
    workers = max(1, args.workers)
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=init_worker,
        initargs=(args.model, args.cpu_threads),
    ) as ex:
        futs = {ex.submit(worker_job, job): job["item_id"] for job in jobs}
        done = 0
        for fut in as_completed(futs):
            iid = futs[fut]
            done += 1
            try:
                rec = fut.result()
            except Exception as exc:  # noqa: BLE001
                rec = {
                    "module_id": "",
                    "item_id": iid,
                    "ok": False,
                    "issues": [f"stt_error:{exc}"],
                    "stt": "",
                }
            results.append(rec)
            flag = "OK" if rec.get("ok") else "FAIL"
            if done % 25 == 0 or not rec.get("ok"):
                print(
                    f"[{done}/{len(jobs)}] {flag} {iid} "
                    f"eng={rec.get('english_recall')} ch={rec.get('choice_coverage')} "
                    f"{rec.get('issues') or []}",
                    flush=True,
                )

    ok_n = sum(1 for r in results if r.get("ok"))
    bad = [r for r in results if not r.get("ok")]
    by_issue: dict[str, int] = {}
    for r in bad:
        for i in r.get("issues") or []:
            by_issue[i] = by_issue.get(i, 0) + 1

    report = {
        "course": str(course),
        "model": args.model,
        "checked": len(results),
        "ok": ok_n,
        "fail": len(bad),
        "elapsed_s": round(time.time() - t0, 1),
        "by_issue": by_issue,
        "mean_english_recall": round(
            sum(r.get("english_recall") or 0 for r in results) / max(1, len(results)), 3
        ),
        "mean_choice_coverage": round(
            sum(r.get("choice_coverage") or 0 for r in results) / max(1, len(results)), 3
        ),
        "failures": [
            {
                "module_id": r.get("module_id"),
                "item_id": r.get("item_id"),
                "issues": r.get("issues"),
                "english_recall": r.get("english_recall"),
                "choice_coverage": r.get("choice_coverage"),
                "overall_recall": r.get("overall_recall"),
                "similarity": r.get("similarity"),
                "stt": (r.get("stt") or "")[:400],
            }
            for r in bad
        ],
    }
    report_path = args.report or (course / "media" / "_batch_logs" / "stt_verify_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"Checked {len(results)}: ok={ok_n} fail={len(bad)} "
        f"mean_eng={report['mean_english_recall']} mean_choice={report['mean_choice_coverage']} "
        f"elapsed={report['elapsed_s']}s",
        flush=True,
    )
    for k, v in sorted(by_issue.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}", flush=True)
    print(f"Report: {report_path}", flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
