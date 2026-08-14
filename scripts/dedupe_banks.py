"""Remove exact duplicate items from learn_digital question banks.

Duplicates were introduced by pad() cycling a few builders to hit TARGET=30.
Keeps the first unique (prompt + choices + answer + type + difficulty); prefers
an item with media when choosing among clones.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_digital" / "questions"


def content_key(it: dict) -> str:
    return json.dumps(
        {
            "d": it.get("difficulty") or "medium",
            "t": it.get("type") or "",
            "p": " ".join(str(it.get("prompt") or "").split()),
            "c": it.get("choices"),
            "a": it.get("answer"),
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def has_media(it: dict) -> bool:
    media = it.get("media")
    return isinstance(media, dict) and bool(media.get("src") or media.get("figure"))


def dedupe_items(items: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    order: list[str] = []
    for it in items:
        key = content_key(it)
        if key not in best:
            best[key] = it
            order.append(key)
            continue
        # Prefer a clone that still has stem media attached.
        if has_media(it) and not has_media(best[key]):
            best[key] = it
    return [best[k] for k in order]


def main() -> None:
    total_before = 0
    total_after = 0
    for path in sorted(OUT.glob("*.json")):
        bank = json.loads(path.read_text(encoding="utf-8"))
        items = bank.get("items") or []
        total_before += len(items)
        unique = dedupe_items(items)
        total_after += len(unique)
        bank["items"] = unique
        path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        counts: dict[str, int] = {}
        for it in unique:
            d = it.get("difficulty") or "medium"
            counts[d] = counts.get(d, 0) + 1
        removed = len(items) - len(unique)
        if removed:
            print(f"{path.name}: {len(items)} -> {len(unique)} (-{removed}) {counts}")
    print(f"total: {total_before} -> {total_after} (-{total_before - total_after})")


if __name__ == "__main__":
    main()
