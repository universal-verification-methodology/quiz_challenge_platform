"""One-shot generator for expanded banks_11_24.py content — run then delete."""
from pathlib import Path

HEADER = r'''"""Challenge banks for modules 11–24 (skip module13-kmap).

Prompts must NOT include (v1)/(variant N) labels — vary substance or wording instead.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_digital" / "questions"
TARGET = 30  # 3 × max_attempts(10)


def mcq(qid: str, prompt: str, choices: list[str], answer: int, explain: str, difficulty: str) -> dict:
    return {
        "id": qid,
        "type": "multiple_choice",
        "prompt": prompt,
        "choices": choices,
        "answer": answer,
        "explain": explain,
        "difficulty": difficulty,
    }


def tf(qid: str, prompt: str, answer: bool, explain: str, difficulty: str) -> dict:
    return {
        "id": qid,
        "type": "true_false",
        "prompt": prompt,
        "answer": answer,
        "explain": explain,
        "difficulty": difficulty,
    }


def content_key(it: dict) -> str:
    return json.dumps(
        {
            "t": it.get("type") or "",
            "p": " ".join(str(it.get("prompt") or "").split()),
            "c": it.get("choices"),
            "a": it.get("answer"),
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def pad(difficulty: str, prefix: str, builders: list) -> list[dict]:
    """Build unique items only — never pad with clones of the same question."""
    out: list[dict] = []
    seen: set[str] = set()
    max_rounds = max(TARGET * 3, len(builders) * 12)
    for n in range(max_rounds):
        if len(out) >= TARGET:
            break
        it = dict(builders[n % len(builders)](n + 1))
        key = content_key(it)
        if key in seen:
            continue
        seen.add(key)
        it["id"] = f"{prefix}_{difficulty}_{len(out) + 1:02d}"
        it["difficulty"] = difficulty
        out.append(it)
    return out


def _pick(i: int, options: list[str]) -> str:
    return options[(i - 1) % len(options)]


def _slot(i: int) -> int:
    return (i - 1) % 30


def _choices4(correct: str, wrong: list[str]) -> tuple[list[str], int]:
    opts = [correct] + [w for w in wrong if w != correct]
    seen: set[str] = set()
    uniq: list[str] = []
    for o in opts:
        if o not in seen:
            seen.add(o)
            uniq.append(o)
    while len(uniq) < 4:
        uniq.append(str(len(uniq) * 7 + 3))
    return uniq[:4], uniq[:4].index(correct)


'''

FOOTER = r'''

def build_banks() -> list[dict]:
    return [
        truth_bank(),
        bool_bank(),
        sop_bank(),
        dontcare_bank(),
        hazard_bank(),
        gates_bank(),
        mux_bank(),
        priority_bank(),
        adder_bank(),
        xorpar_bank(),
        tristate_bank(),
        barrel_bank(),
        sevenseg_bank(),
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for bank in build_banks():
        path = OUT / f"{bank['module']}.json"
        path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        counts: dict[str, int] = {}
        keys: set[str] = set()
        for it in bank["items"]:
            counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
            k = content_key(it)
            assert k not in keys, f"duplicate in {bank['module']}: {it['prompt'][:60]}"
            keys.add(k)
            assert "(v" not in it["prompt"], it["prompt"]
            assert "variant " not in it["prompt"].lower(), it["prompt"]
        for diff in ("easy", "medium", "hard"):
            assert counts.get(diff, 0) == TARGET, f"{bank['module']} {diff}={counts.get(diff, 0)}"
        print(path.name, counts, "total", len(bank["items"]))


if __name__ == "__main__":
    main()
'''

print("Generator placeholder - use direct file write instead")
