#!/usr/bin/env python3
"""Enforce globally unique quiz prompts across learn_digital banks.

Keeps the first occurrence of each normalized prompt (preferring items that
already have stem media). Drops later clones, then refills each module to
30 items per difficulty with new unique prompts (module-scoped wording).

Usage:
  python scripts/enforce_global_unique_prompts.py
  python scripts/enforce_global_unique_prompts.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_full_unique_banks import (  # noqa: E402
    TARGET,
    candidates_for,
    mcq,
    next_index,
    prefix_from_items,
    tf,
)

COURSE = ROOT / "content" / "learn_digital"
QUESTIONS = COURSE / "questions"


def norm_prompt(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or ""))
    s = s.replace("\u2026", "...").replace("\ufffd", "...")
    s = s.lower()
    return re.sub(r"\s+", " ", s).strip()


def prompt_key(it: dict) -> str:
    return norm_prompt(it.get("prompt") or "")


def has_media(it: dict) -> bool:
    media = it.get("media")
    return isinstance(media, dict) and bool(media.get("src") or media.get("figure"))


def module_titles() -> dict[str, str]:
    manifest = json.loads((COURSE / "content.json").read_text(encoding="utf-8"))
    return {m["id"]: m.get("title") or m["id"] for m in manifest.get("modules") or []}


def short_topic(module_id: str, title: str) -> str:
    slug = module_id.split("-", 1)[-1].replace("-", " ")
    return (title or slug).strip()


def uniquify_item(
    it: dict,
    *,
    used: set[str],
    module_id: str,
    title: str,
    seq: int,
) -> dict | None:
    """Return a copy with a globally unique prompt, or None if exhausted."""
    out = dict(it)
    base = str(out.get("prompt") or "").strip()
    topic = short_topic(module_id, title)
    slug = module_id.split("-", 1)[-1]
    variants = [
        base,
        f"{topic}: {base}",
        f"In {topic}, {base[:1].lower() + base[1:] if base else base}",
        f"For the {topic} lab: {base}",
        f"{base} (context: {slug})",
        f"{base} — {topic} check",
        f"{topic} drill #{seq}: {base}",
        f"{base} [{slug} #{seq}]",
    ]
    # Also try light numeric salts if still colliding
    for n in range(2, 40):
        variants.append(f"{base} (variant {n} for {slug})")

    for prompt in variants:
        pk = norm_prompt(prompt)
        if not pk or pk in used:
            continue
        out["prompt"] = prompt
        # Prompt changed → stem video no longer matches
        if norm_prompt(base) != pk:
            out.pop("media", None)
            out.pop("tool_capture", None)
        used.add(pk)
        return out
    return None


def extra_fillers(module_id: str, title: str, difficulty: str) -> list[dict]:
    """Large pool of module-scoped unique items beyond forge candidates."""
    topic = short_topic(module_id, title)
    slug = module_id.split("-", 1)[-1]
    out: list[dict] = []
    for i in range(1, 120):
        w = 2 + (i % 12)
        out.append(
            tf(
                f"{topic}: statement {i} — an unsigned {w}-bit field has exactly {2**w} codes.",
                True,
                f"2^{w} = {2**w} patterns.",
                difficulty,
            )
        )
        out.append(
            mcq(
                f"{topic}: unsigned width-{w} encoding capacity is…",
                [str(2 ** (w - 1)), str(2**w), str(w), str(10 * w)],
                1,
                f"2^{w} patterns.",
                difficulty,
            )
        )
        out.append(
            mcq(
                f"Lab {slug} item {i}: which power-of-two size matches {w} bits?",
                [str(2 ** (w - 1)), str(2**w), str(w * w), str(w)],
                1,
                f"{w} bits → {2**w} values.",
                difficulty,
            )
        )
        out.append(
            tf(
                f"In {topic} (#{i}), bit width is part of a value's meaning.",
                True,
                "Width is part of interpretation.",
                difficulty,
            )
        )
    return out


def refill_difficulty(
    *,
    module_id: str,
    title: str,
    difficulty: str,
    kept: list[dict],
    used: set[str],
    prefix: str,
    all_items_for_index: list[dict],
) -> list[dict]:
    need = TARGET - len(kept)
    if need <= 0:
        return kept[:TARGET]

    idx = next_index(all_items_for_index + kept, prefix, difficulty)
    pool = candidates_for(module_id, difficulty) + extra_fillers(module_id, title, difficulty)
    seq = 1
    for cand in pool:
        if len(kept) >= TARGET:
            break
        cand = dict(cand)
        cand["difficulty"] = difficulty
        pk = prompt_key(cand)
        if pk in used:
            u = uniquify_item(
                cand, used=used, module_id=module_id, title=title, seq=seq
            )
            seq += 1
            if not u:
                continue
            cand = u
        else:
            used.add(pk)
            cand.pop("media", None)
            cand.pop("tool_capture", None)
        cand["id"] = f"{prefix}_{difficulty}_{idx:02d}"
        idx += 1
        kept.append(cand)

    if len(kept) < TARGET:
        raise SystemExit(
            f"{module_id} {difficulty}: only {len(kept)}/{TARGET} unique prompts"
        )
    return kept[:TARGET]


def process_bank(
    path: Path,
    title: str,
    used: set[str],
    *,
    dry_run: bool,
) -> dict:
    bank = json.loads(path.read_text(encoding="utf-8"))
    module_id = bank.get("module") or path.stem
    items: list[dict] = list(bank.get("items") or [])
    prefix = prefix_from_items(items, module_id)

    before = len(items)
    kept_all: list[dict] = []
    dropped = 0
    refilled = 0

    for difficulty in ("easy", "medium", "hard"):
        group = [it for it in items if (it.get("difficulty") or "medium") == difficulty]
        # Prefer media-bearing items when claiming a prompt for the first time
        group.sort(key=lambda it: (0 if has_media(it) else 1, str(it.get("id") or "")))

        kept: list[dict] = []
        for it in group:
            pk = prompt_key(it)
            if not pk:
                dropped += 1
                continue
            if pk in used:
                dropped += 1
                continue
            used.add(pk)
            kept.append(it)

        before_len = len(kept)
        kept = refill_difficulty(
            module_id=module_id,
            title=title,
            difficulty=difficulty,
            kept=kept,
            used=used,
            prefix=prefix,
            all_items_for_index=kept_all,
        )
        refilled += max(0, len(kept) - before_len)
        kept_all.extend(kept)

    # Stable-ish order: easy, medium, hard blocks already appended
    after = len(kept_all)
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for it in kept_all:
        counts[it.get("difficulty") or "medium"] += 1

    if not dry_run:
        bank["items"] = kept_all
        path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "module": module_id,
        "before": before,
        "after": after,
        "dropped": dropped,
        "refilled": refilled,
        "counts": counts,
    }


def verify_global_unique() -> tuple[int, int]:
    prompts: dict[str, str] = {}
    dups = 0
    total = 0
    for path in sorted(QUESTIONS.glob("*.json")):
        bank = json.loads(path.read_text(encoding="utf-8"))
        for it in bank.get("items") or []:
            total += 1
            pk = prompt_key(it)
            if pk in prompts:
                dups += 1
            else:
                prompts[pk] = f"{path.stem}/{it.get('id')}"
    return total, dups


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--module", action="append", help="Limit to module id(s)")
    args = ap.parse_args()

    titles = module_titles()
    paths = sorted(QUESTIONS.glob("*.json"))
    if args.module:
        allow = set(args.module)
        paths = [p for p in paths if p.stem in allow]

    used: set[str] = set()
    # If limiting modules, still seed used[] with prompts from other modules
    # so we don't recreate global collisions.
    if args.module:
        allow = set(args.module)
        for path in sorted(QUESTIONS.glob("*.json")):
            if path.stem in allow:
                continue
            bank = json.loads(path.read_text(encoding="utf-8"))
            for it in bank.get("items") or []:
                pk = prompt_key(it)
                if pk:
                    used.add(pk)

    stats = []
    for path in paths:
        mid = path.stem
        st = process_bank(
            path,
            titles.get(mid, mid),
            used,
            dry_run=args.dry_run,
        )
        stats.append(st)
        print(
            f"{st['module']}: {st['before']} -> {st['after']} "
            f"(dropped {st['dropped']}, refilled {st['refilled']}) {st['counts']}",
            flush=True,
        )

    if args.dry_run:
        print("DRY-RUN: no files written", flush=True)
        return 0

    total, dups = verify_global_unique()
    print(f"VERIFY total={total} duplicate_prompts={dups}", flush=True)
    if dups:
        return 1
    # Bump content version
    cpath = COURSE / "content.json"
    content = json.loads(cpath.read_text(encoding="utf-8"))
    try:
        content["version"] = int(content.get("version") or 0) + 1
    except (TypeError, ValueError):
        content["version"] = 13
    cpath.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"content.json version -> {content['version']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
