"""Generate challenge banks: 30 items × 3 difficulties per module (3× max_attempts=10).

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


def radix_bank() -> dict:
    hex_digits = [
        ("A", "10", ["9", "10", "11", "16"]),
        ("B", "11", ["10", "11", "12", "16"]),
        ("C", "12", ["11", "12", "13", "16"]),
        ("D", "13", ["12", "13", "14", "16"]),
        ("E", "14", ["13", "14", "15", "16"]),
        ("F", "15", ["14", "15", "16", "10"]),
    ]
    easy_b = [
        lambda i: mcq(
            "",
            f"Hex digit {hex_digits[(i - 1) % 6][0]} equals which decimal value?",
            hex_digits[(i - 1) % 6][2],
            hex_digits[(i - 1) % 6][2].index(hex_digits[(i - 1) % 6][1]),
            f"{hex_digits[(i - 1) % 6][0]}16 = {hex_digits[(i - 1) % 6][1]}10.",
            "easy",
        ),
        lambda i: mcq(
            "",
            f"How many distinct values can {3 + (i % 5)} bits represent?",
            [
                str(2 ** (3 + (i % 5) - 1)),
                str(2 ** (3 + (i % 5))),
                str(3 + (i % 5)),
                str(10 * (3 + (i % 5))),
            ],
            1,
            "n bits encode 2^n patterns.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Binary 0b1 and hex 0x1 are the same numeric value.",
                "0b10 and 0x2 represent the same quantity.",
                "Writing 5 as 0b101 or 0x5 does not change the value.",
                "Nibble 0xA matches binary 0b1010.",
            ][(i - 1) % 4],
            True,
            "Same quantity, different radix spelling.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "One hex digit corresponds to how many bits?",
                "A nibble is how many bits wide?",
                "Hex packs how many bits per character?",
                "Converting one hex digit uses a group of how many bits?",
            ][(i - 1) % 4],
            ["2", "4", "8", "16"],
            1,
            "16 = 2^4, so one hex digit is 4 bits.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "At width 8, unsigned 0xFF equals...",
                "Eight-bit unsigned all-ones is which decimal?",
                "What is unsigned 255 in hex at width 8?",
                "Width-8 pattern 11111111 as unsigned decimal is...",
            ][(i - 1) % 4],
            ["127", "255", "256", "-1"] if (i - 1) % 4 != 2 else ["0x7F", "0xFF", "0x100", "0x00"],
            1,
            "Unsigned all-ones at 8 bits is 255 / 0xFF.",
            "medium",
        ),
        lambda i: mcq(
            "",
            f"Which is a valid 4-bit binary spelling of decimal {i % 8 + 1}?",
            [
                format((i % 8 + 1) ^ 0xF, "04b"),
                format(i % 8 + 1, "04b"),
                format((i % 8 + 1) + 8, "04b")[-4:],
                "1111",
            ],
            1,
            "Convert the decimal to binary at the stated width.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "0b1010 as unsigned decimal is...",
                "Binary 1010 (4-bit) equals which unsigned value?",
                "What decimal is 0b1010?",
                "Interpret 1010₂ as unsigned decimal.",
            ][(i - 1) % 4],
            ["8", "10", "12", "15"],
            1,
            "8+2 = 10.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Changing bit width can change the meaning of the same typed hex digits.",
                "A fixed width is part of how a bit pattern is interpreted.",
                "Truncating a wider value to fewer bits can change its numeric meaning.",
                "The same hex text can map to different bit budgets at different widths.",
            ][(i - 1) % 4],
            True,
            "Width is part of the value’s interpretation.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "At width 8, 0xFF as two’s-complement signed is...",
                "Eight-bit two’s-complement all-ones equals...",
                "Signed reading of 11111111₂ at width 8 is...",
                "What is signed 0xFF in 8-bit two’s complement?",
            ][(i - 1) % 4],
            ["255", "-1", "128", "0"],
            1,
            "Signed all-ones is -1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Which statement is safest for fixed-width radices?",
                "Binary, hex, and unsigned decimal at one width are best seen as...",
                "Pick the best description of radix views of one pattern.",
                "At a fixed width, different radices mainly provide...",
            ][(i - 1) % 4],
            [
                "Hex and binary never match",
                "They are views of one bit pattern",
                "Width never matters",
                "Only decimal is real",
            ],
            1,
            "Same bits, different spellings.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Sign-extending 0b1111 from 4 bits to 8 bits yields...",
                "Widen signed 0b1111 (4-bit) to 8 bits. The result is...",
                "Two’s-complement sign extension of 1111₂ to 8 bits is...",
                "After signed widen 4→8 from all-ones nibble, hex is...",
            ][(i - 1) % 4],
            ["0x0F", "0xFF", "0xF0", "0x00"],
            1,
            "Negative two’s-complement fills 1s when widening.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Unsigned and signed readings of the same bits can disagree.",
                "0xFF can be read as 255 unsigned or -1 signed at width 8.",
                "Interpretation of a pattern depends on signed vs unsigned view.",
                "Identical bits may mean different integers under different types.",
            ][(i - 1) % 4],
            True,
            "Interpretation depends on the type/radix view.",
            "hard",
        ),
    ]
    items = pad("easy", "radix", easy_b) + pad("medium", "radix", med_b) + pad("hard", "radix", hard_b)
    return {"module": "module01-radix-converter", "title": "Radix & bit width", "items": items}


def kmap_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Adjacent K-map cells differ by how many bits?",
                "In a proper K-map layout, neighbors change how many variables?",
                "Gray-code adjacency means a Hamming distance of...",
                "Two cells that share an edge on a K-map differ in how many bits?",
            ][(i - 1) % 4],
            ["0", "1", "2", "All bits"],
            1,
            "Gray-code neighbors flip one bit.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A 2-variable K-map has how many cells?",
                "How many cells are in a map for inputs A,B only?",
                "2^2 K-map size is...",
                "Smallest common teaching K-map (2 vars) contains...",
            ][(i - 1) % 4],
            ["2", "4", "8", "16"],
            1,
            "2^2 = 4.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "K-map axes use Gray code ordering.",
                "Karnaugh maps arrange labels so neighbors differ by one bit.",
                "Gray ordering is why geometric neighbors are logical neighbors.",
                "Binary counting order on both axes would break single-bit adjacency.",
            ][(i - 1) % 4],
            True,
            "So geometric neighbors are Hamming distance 1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Valid K-map group sizes for 1s are...",
                "When circling 1s, legal group cardinality is...",
                "Which sizes are allowed for a single implicant group?",
                "Power-of-two grouping means sizes like...",
            ][(i - 1) % 4],
            ["3 only", "5 only", "1, 2, 4, 8, ...", "Any odd count"],
            2,
            "Group sizes are powers of two.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "A quad (4 ones) typically eliminates how many literals?",
                "Grouping four adjacent 1s removes about how many variables from the term?",
                "A size-4 group in a K-map usually drops how many literals?",
                "Compared with a single cell, a quad removes how many literals?",
            ][(i - 1) % 4],
            ["0", "1", "2", "4"],
            2,
            "Quad removes two variables.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Don’t-care (X) cells in a K-map...",
                "How may X entries be used while minimizing?",
                "Don’t-cares are allowed to...",
                "Treating an X as 1 is acceptable when...",
            ][(i - 1) % 4],
            [
                "Must be 0",
                "Can join groups if helpful",
                "Force F=1",
                "Break grouping",
            ],
            1,
            "X may be treated as 0 or 1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "K-map edges can wrap for grouping.",
                "Top and bottom rows may be adjacent for groups.",
                "Left and right columns can form a wrap-around pair.",
                "Toroidal adjacency is part of standard K-map grouping.",
            ][(i - 1) % 4],
            True,
            "Top/bottom and left/right are adjacent.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A 3-variable K-map has how many cells?",
                "Map size for A,B,C is...",
                "2^3 cells means which count?",
                "How many minterm slots exist in a 3-input K-map?",
            ][(i - 1) % 4],
            ["4", "6", "8", "9"],
            2,
            "2^3 = 8.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "An essential prime implicant covers a minterm that...",
                "Essential PIs are required because they uniquely cover...",
                "A minterm that forces an implicant into the cover is one that...",
                "Pick the definition closest to an essential prime implicant’s role.",
            ][(i - 1) % 4],
            [
                "No other implicant covers",
                "Is always a don’t-care",
                "Appears twice",
                "Is outside the map",
            ],
            0,
            "It uniquely covers at least one onset minterm.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Largest legal group on a 4-var K-map is size...",
                "A 4-variable map can group at most how many cells at once?",
                "Full coverage of a 4-var K-map is how many cells?",
                "2^4 cells means the maximum single group size is...",
            ][(i - 1) % 4],
            ["8", "12", "16", "3"],
            2,
            "Entire map is 16 cells (2^4).",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Overlapping groups are allowed when minimizing.",
                "The same 1 may belong to more than one implicant group.",
                "Shared onset minterms across groups are acceptable.",
                "Implicants may overlap on 1-cells in a K-map cover.",
            ][(i - 1) % 4],
            True,
            "Shared 1s can belong to multiple implicants.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "SOP minimization from a K-map yields...",
                "Reading groups as products and OR-ing them produces...",
                "A two-level sum-of-products cover is...",
                "Classic K-map output form is...",
            ][(i - 1) % 4],
            [
                "Only NAND gates",
                "A sum of product terms",
                "Only a truth table",
                "A FIFO pointer",
            ],
            1,
            "Each group → product; OR the products.",
            "hard",
        ),
    ]
    items = pad("easy", "kmap", easy_b) + pad("medium", "kmap", med_b) + pad("hard", "kmap", hard_b)
    return {"module": "module13-kmap", "title": "K-maps", "items": items}


def setup_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Setup time (tsu) requires D stable...",
                "Before the capturing edge, data must remain steady for...",
                "The setup window is the time D must be stable...",
                "Violating setup usually means D changed too late relative to...",
            ][(i - 1) % 4],
            [
                "for at least tsu before the capturing edge",
                "only after the edge",
                "only during reset",
                "never",
            ],
            0,
            "Data must settle before the edge.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Hold time (th) requires D stable...",
                "After the capturing edge, D must not change for...",
                "The hold window keeps data steady...",
                "Hold checks care about early data changes...",
            ][(i - 1) % 4],
            [
                "for at least th after the capturing edge",
                "only before power-up",
                "the whole period always",
                "only on negedge forever",
            ],
            0,
            "No early change after the edge.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Flip-flops sample D on a clock edge.",
                "Edge-triggered flops capture input around the active edge.",
                "A FF updates Q based on D at the triggering clock edge.",
                "Level-sensitive latches differ from edge-triggered flip-flops.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Edge-triggered sequential element samples on the clock edge; latches are level-sensitive.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Clock-to-Q (tcq) is...",
                "After the clock edge, Q updates following...",
                "Propagation from clock capture to Q is called...",
                "Which delay starts at the capturing edge and ends when Q is valid?",
            ][(i - 1) % 4],
            [
                "delay from capturing edge until Q updates",
                "the same as setup",
                "an area report",
                "baud period",
            ],
            0,
            "Output propagation after the edge.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "A setup violation means D changed...",
                "Failing setup usually indicates the datapath was...",
                "Late data relative to the clock edge causes...",
                "Which description matches a setup fail?",
            ][(i - 1) % 4],
            [
                "too close before the edge",
                "only after reset",
                "in another clock domain always OK",
                "never matters",
            ],
            0,
            "Insufficient setup margin.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Hold violations are often fixed by...",
                "A common hold fix on a short path is...",
                "To stop D from changing too soon after the edge...",
                "Which change most directly helps hold?",
            ][(i - 1) % 4],
            [
                "adding delay on the data path",
                "removing all clocks",
                "widening the datapath randomly",
                "disabling reset forever",
            ],
            0,
            "Slow the data so it doesn’t change too soon after the edge.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Period must cover logic delay + setup (+ skew/jitter budgets).",
                "Max-delay / setup closure depends on the clock period.",
                "A faster clock tightens setup timing budgets.",
                "Hold checks are primarily a function of clock period length.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Setup relates to period; hold is largely period-independent.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Which pair is most related to sequential timing?",
                "Capture windows are framed by...",
                "Classic FF timing specs include...",
                "tsu pairs most naturally with...",
            ][(i - 1) % 4],
            ["tsu and th", "R and C only", "UART framing only", "K-map quads"],
            0,
            "Setup and hold frame the capture window.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Useful skew can help which constraint?",
                "Intentionally delaying a capture clock may ease...",
                "In some topologies, positive skew helps...",
                "Skew is sometimes used carefully to improve...",
            ][(i - 1) % 4],
            ["Hold on some paths", "Neither setup nor hold", "Only area", "Only power"],
            0,
            "Late clock at capture can ease hold in some topologies (with care).",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Min-delay paths are most associated with...",
                "Short-path timing analysis targets...",
                "Hold checks focus on...",
                "Which analysis worries about data arriving too soon?",
            ][(i - 1) % 4],
            ["Hold checks", "Only DFT", "Only lint", "Hex conversion"],
            0,
            "Hold is a short-path / min-delay problem.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Both setup and hold can fail on the same design for different paths.",
                "Long paths stress setup while short paths stress hold.",
                "A chip can have setup fails and hold fails simultaneously.",
                "Fixing setup always automatically fixes hold.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Long vs short paths; fixes often trade off.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Ignoring clock uncertainty in STA typically...",
                "Leaving out jitter/uncertainty usually...",
                "Optimistic clocks without uncertainty tend to...",
                "What happens if uncertainty is omitted from timing analysis?",
            ][(i - 1) % 4],
            [
                "Overstates margin",
                "Always improves hold",
                "Removes the need for timing",
                "Converts async to sync",
            ],
            0,
            "Jitter/uncertainty consumes margin.",
            "hard",
        ),
    ]
    items = pad("easy", "timing", easy_b) + pad("medium", "timing", med_b) + pad("hard", "timing", hard_b)
    return {"module": "module26-setup-hold", "title": "Setup / hold", "items": items}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    banks = [radix_bank(), kmap_bank(), setup_bank()]
    for bank in banks:
        path = OUT / f"{bank['module']}.json"
        path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        counts = {}
        for it in bank["items"]:
            counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
            assert "(v" not in it["prompt"], it["prompt"]
            assert "variant " not in it["prompt"].lower(), it["prompt"]
        print(path.name, counts, "total", len(bank["items"]))


if __name__ == "__main__":
    main()
