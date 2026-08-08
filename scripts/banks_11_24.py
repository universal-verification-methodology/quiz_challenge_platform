"""Challenge banks for modules 11–24 (skip module13-kmap).

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


# ── module11-truth-table ─────────────────────────────────────────────────────


def truth_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "How many rows does a truth table with 3 inputs have?",
                "Three boolean inputs require how many truth-table rows?",
                "2^3 input combinations equal how many rows?",
                "A table for A,B,C lists how many minterm slots?",
            ][(i - 1) % 4],
            ["3", "6", "8", "16"],
            2,
            "2^n rows: 2^3 = 8.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Two-input AND: F = 1 only when…",
                "AND of A and B is high only if…",
                "For F = A·B, which row alone yields 1?",
                "When is a two-input AND output asserted?",
            ][(i - 1) % 4],
            ["A or B is 1", "A and B are both 1", "A and B differ", "both are 0"],
            1,
            "AND is 1 only on the 11 row.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Two-input XOR: F = 1 when…",
                "XOR is high precisely when inputs…",
                "A⊕B equals 1 for which relationship?",
                "Which description matches two-input exclusive-OR?",
            ][(i - 1) % 4],
            ["A and B are equal", "A and B differ", "both are 1", "both are 0"],
            1,
            "XOR is 1 on 01 and 10 rows.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "A truth table must list every input combination exactly once.",
                "Each minterm index appears once in a complete truth table.",
                "Skipping a row leaves an incomplete specification of F.",
                "Duplicate input rows are required for a valid truth table.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Every combination once; duplicates hide bugs.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Two-input OR: F = 0 only when…",
                "When is A+B false?",
                "OR is low only on which pattern?",
                "Which row alone makes two-input OR equal 0?",
            ][(i - 1) % 4],
            ["both inputs are 0", "both are 1", "inputs differ", "A is 1"],
            0,
            "OR is 0 only on 00.",
            "medium",
        ),
        lambda i: mcq(
            "",
            f"How many rows does a truth table with {2 + (i % 3)} inputs have?",
            [
                str(2 + (i % 3)),
                str(2 * (2 + (i % 3))),
                str(2 ** (2 + (i % 3))),
                str(10 * (2 + (i % 3))),
            ],
            2,
            "n inputs → 2^n rows.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Three-input majority: F = 1 when…",
                "Majority of A,B,C asserts when…",
                "A 3-input majority gate is high if…",
                "Which condition matches majority(A,B,C)=1?",
            ][(i - 1) % 4],
            [
                "exactly one input is 1",
                "at least two inputs are 1",
                "all inputs are 0",
                "parity is even",
            ],
            1,
            "Majority needs two or three ones.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "X in a truth-table cell means don't-care, not 'any answer is fine on the quiz'.",
                "An X entry marks a combination that may be treated as 0 or 1 in minimization.",
                "Don't-care cells still appear as rows; they are not simply omitted.",
                "Leaving a row blank is the same as listing every combination.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "X is optional for cover; blank rows are incomplete.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Four variables need how many truth-table rows?",
                "A complete 4-input table has how many combinations?",
                "2^4 minterm slots equal…",
                "How many rows for inputs W,X,Y,Z?",
            ][(i - 1) % 4],
            ["8", "12", "16", "32"],
            2,
            "2^4 = 16.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Full-adder sum S = A⊕B⊕Cin is 1 for how many of the 8 input rows?",
                "Among 8 FA input combinations, how many make sum = 1?",
                "Odd parity of A,B,Cin is true on how many rows?",
                "Count of FA rows with S=1 equals…",
            ][(i - 1) % 4],
            ["2", "3", "4", "8"],
            2,
            "Odd number of ones among three bits: 4 of 8 rows.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If F matches AND on two vars, which minterms are 1?",
                "Two-var F=A·B has onset at…",
                "For A·B, the ON set is…",
                "Which description matches F=A AND B?",
            ][(i - 1) % 4],
            ["only m0", "only m3", "m1 and m2", "all four rows"],
            1,
            "Only AB (row 11 = m3) is 1.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Two functions with identical truth tables are the same Boolean function.",
                "Matching every row means two nets implement the same F.",
                "A correct gate net must match every row of the target table.",
                "Agreeing on three of four rows is enough to prove two-input equivalence.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Complete row agreement defines functional equality.",
            "hard",
        ),
    ]
    items = pad("easy", "truth", easy_b) + pad("medium", "truth", med_b) + pad("hard", "truth", hard_b)
    return {"module": "module11-truth-table", "title": "Truth tables", "items": items}


# ── module12-boolean-laws ────────────────────────────────────────────────────


def bool_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "De Morgan: ~(A·B) equals…",
                "NOT of AND becomes…",
                "Which rewrite is ~(A AND B)?",
                "De Morgan on a product yields…",
            ][(i - 1) % 4],
            ["A'·B'", "A'+B'", "A+B", "A·B"],
            1,
            "NOT over AND becomes OR of the complements.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Absorption: A + A·B simplifies to…",
                "A absorbs the redundant A·B term, leaving…",
                "What does A + AB collapse to?",
                "Absorption law reduces A+AB to…",
            ][(i - 1) % 4],
            ["B", "A·B", "A", "1"],
            2,
            "A absorbs the redundant A·B term.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Complement: A·A' equals…",
                "A AND NOT A is…",
                "What is the product of a literal and its complement?",
                "A·~A evaluates to…",
            ][(i - 1) % 4],
            ["0", "1", "A", "A'"],
            0,
            "A and its complement cannot both be true.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Double negation: ~~A simplifies to A.",
                "Two NOTs cancel: ~~A = A.",
                "Applying NOT twice returns the original literal.",
                "~~A always simplifies to A'.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Two NOTs cancel.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "De Morgan: ~(A+B) equals…",
                "NOT of OR becomes…",
                "Which is ~(A OR B)?",
                "De Morgan on a sum yields…",
            ][(i - 1) % 4],
            ["A'+B'", "A'·B'", "A·B", "A+B"],
            1,
            "NOT over OR becomes AND of complements.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Factor: AB + AC equals…",
                "Common factor A from AB+AC gives…",
                "Distributive factoring of AB+AC yields…",
                "Which factored form matches AB+AC?",
            ][(i - 1) % 4],
            ["A+(B·C)", "A·(B+C)", "B·(A+C)", "(A+B)·C"],
            1,
            "A·(B+C) by distributivity.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A + A' simplifies to…",
                "A OR NOT A equals…",
                "Complement law for sum: A+~A is…",
                "What is the value of A+A'?",
            ][(i - 1) % 4],
            ["0", "1", "A", "A'"],
            1,
            "A or not-A covers every case → 1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Absorption also says A·(A+B) = A.",
                "A·(A+B) collapses to A by absorption.",
                "The dual absorption form uses AND outside a sum.",
                "A·(A+B) simplifies to B, not A.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Dual absorption: A(A+B)=A.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Consensus: AB + A'C + BC — the BC term is…",
                "In AB+A'C, adding BC is called the…",
                "Which role does BC play for AB + A'C?",
                "The bridging product for AB and A'C is…",
            ][(i - 1) % 4],
            [
                "always illegal",
                "a consensus (redundant but useful) term",
                "required for canonical SOP only",
                "the same as De Morgan",
            ],
            1,
            "Consensus BC is redundant algebraically but covers transitions.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Which rewrite is illegal?",
                "Pick the invalid Boolean step.",
                "Which transformation breaks Boolean algebra?",
                "Identify the incorrect identity.",
            ][(i - 1) % 4],
            [
                "~(A·B) → ~A + ~B",
                "~(A+B) → ~A · ~B",
                "~(A·B) → ~A · ~B",
                "A + A·B → A",
            ],
            2,
            "De Morgan flips operator; ~ (A·B) is ~A+~B, not ~A·~B.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Idempotent: A+A equals…",
                "A OR A simplifies to…",
                "What is A+A?",
                "Idempotence for OR yields…",
            ][(i - 1) % 4],
            ["0", "1", "A", "2A"],
            2,
            "A+A = A (idempotent).",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Distributing a NOT over only part of a product is an illegal rewrite.",
                "De Morgan must apply to the whole AND/OR being negated.",
                "Boolean AND/OR are not ordinary arithmetic + and ×.",
                "You may freely drop a NOT from only one literal inside ~(AB).",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Partial De Morgan / arithmetic habits cause illegal steps.",
            "hard",
        ),
    ]
    items = pad("easy", "bool", easy_b) + pad("medium", "bool", med_b) + pad("hard", "bool", hard_b)
    return {"module": "module12-boolean-laws", "title": "Boolean laws", "items": items}


# ── module14-sop-pos ─────────────────────────────────────────────────────────


def sop_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Canonical SOP includes minterms where F equals…",
                "Sum-of-products ORs products for rows where F is…",
                "SOP onset is built from rows with F=…",
                "Which F value feeds canonical SOP minterms?",
            ][(i - 1) % 4],
            ["0", "1", "X", "either"],
            1,
            "SOP ORs products for rows where F is 1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Canonical POS includes maxterms where F equals…",
                "Product-of-sums uses rows where F is…",
                "POS maxterms come from F=…",
                "Which F value feeds canonical POS?",
            ][(i - 1) % 4],
            ["0", "1", "X", "either"],
            0,
            "POS ANDs sums for rows where F is 0.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "2-var minterm m0 is the product…",
                "For A,B, m0 (row 00) is…",
                "Which product is true only on AB=00?",
                "m0 in two variables equals…",
            ][(i - 1) % 4],
            ["AB", "A'B'", "(A+B)", "(A'+B')"],
            1,
            "m0 is the 00 row: A' AND B'.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Canonical SOP is always the minimal expression.",
                "Listing every ON minterm guarantees a minimal gate count.",
                "Canonical forms may still be simplified further.",
                "Sigma notation always equals the smallest SOP cover.",
            ][(i - 1) % 4],
            False if (i - 1) % 4 != 2 else True,
            "Canonical lists every term; minimization may shrink them.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "2-var maxterm M0 is the sum…",
                "Maxterm for row 00 is false only there: …",
                "Which sum is M0 for A,B?",
                "M0 equals which clause?",
            ][(i - 1) % 4],
            ["A'B'", "A+B", "AB", "A'+B'"],
            1,
            "M0 = A+B (false only when A=B=0).",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Two-var XOR canonical SOP uses which minterms?",
                "F=A⊕B is 1 on…",
                "XOR onset in Σm notation is…",
                "Which pair of minterms is two-input XOR?",
            ][(i - 1) % 4],
            ["m0 and m3", "m1 and m2", "only m3", "m0 and m1"],
            1,
            "XOR is 1 on 01 and 10 → m1,m2.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "For two-var AND, which single minterm is 1?",
                "F=AB has onset…",
                "AND of A,B equals which Σm?",
                "Only which minterm is ON for AND?",
            ][(i - 1) % 4],
            ["m0", "m1", "m2", "m3"],
            3,
            "Only m3 (AB) is 1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Sigma-m lists minterm indices; Pi-M lists maxterm indices.",
                "SOP and POS are dual views of the same function.",
                "m0 and M0 are identical expressions.",
                "Canonical POS ANDs a maxterm for each OFF row.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "m0 is a product; M0 is a sum — different shapes.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "If F is identically 0, canonical SOP is…",
                "All-zero truth table yields SOP…",
                "Empty onset means SOP equals…",
                "What is the SOP of a constant-0 function?",
            ][(i - 1) % 4],
            ["1", "0", "A", "A+A'"],
            1,
            "No ON minterms → SOP is 0.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If F is identically 1, both canonical forms…",
                "All-ones table: SOP and POS…",
                "Constant-1 function simplifies canonical views to…",
                "What happens to SOP/POS when every row is 1?",
            ][(i - 1) % 4],
            [
                "remain full of every term forever",
                "collapse to the constant 1",
                "become XOR only",
                "are undefined",
            ],
            1,
            "All ones → both forms are tautology 1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "XOR POS for two vars includes which maxterms?",
                "F=A⊕B is 0 on rows… so POS uses…",
                "Two-var XOR ΠM includes…",
                "OFF rows of XOR feed which maxterms?",
            ][(i - 1) % 4],
            ["M1 and M2", "M0 and M3", "only M0", "M0–M3 all"],
            1,
            "XOR is 0 on 00 and 11 → M0 and M3.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Mixing SOP onset rules with POS offset rules produces wrong covers.",
                "SOP uses F=1 rows; POS uses F=0 rows.",
                "Real synthesis may prefer SOP or POS based on library and timing.",
                "Canonical SOP and POS always use identical product terms.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Don't mix the dual constructions.",
            "hard",
        ),
    ]
    items = pad("easy", "sop", easy_b) + pad("medium", "sop", med_b) + pad("hard", "sop", hard_b)
    return {"module": "module14-sop-pos", "title": "SOP / POS", "items": items}


# ── module15-dont-care-lab ───────────────────────────────────────────────────


def dontcare_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Don't-care rows in a truth table are written as…",
                "Optional output combinations are marked…",
                "Which symbol denotes don't-care in F?",
                "Unspecified/unreachable rows commonly use…",
            ][(i - 1) % 4],
            ["0", "1", "X", "Z"],
            2,
            "X marks combinations that may be treated as 0 or 1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Every SOP cover must include all…",
                "Onset that must be covered is the set of…",
                "Minimization must hit every…",
                "Which minterms are mandatory in an SOP cover?",
            ][(i - 1) % 4],
            ["OFF minterms", "ON minterms", "X minterms only", "maxterms"],
            1,
            "ON (F=1) rows must be covered; OFF rows must not.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Using don't-cares in minimization typically…",
                "Treating helpful X as 1 can…",
                "Optional X entries often…",
                "What is a common benefit of using X?",
            ][(i - 1) % 4],
            [
                "Always increases term count",
                "Can shrink the cover",
                "Forces POS only",
                "Ignores ON rows",
            ],
            1,
            "X can enlarge groups and drop literals.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "A product term must never include an OFF (F=0) minterm.",
                "Covering a hard-zero row would change the function.",
                "Cubes may freely swallow OFF rows if X exists nearby.",
                "OFF rows are forbidden inside any valid implicant.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Never cover a specified 0.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Don't-care minterms in a cover are…",
                "X rows relative to a required cover are…",
                "How must X be treated when building SOP?",
                "Optional X entries…",
            ][(i - 1) % 4],
            [
                "mandatory to cover",
                "forbidden to use",
                "optional — use if they help",
                "always forced to 0",
            ],
            2,
            "X may join groups when helpful.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Sigma notation with don't-cares often writes…",
                "Listing onset and X sets looks like…",
                "Which form separates ON and don't-care indices?",
                "A common shorthand is…",
            ][(i - 1) % 4],
            [
                "only ΠM",
                "Σm(…) + d(…)",
                "only Gray codes",
                "FFT of the table",
            ],
            1,
            "Σm with d(…) lists minterms and don't-cares.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Ignoring all X (treat as 0) versus using X usually…",
                "Compare with-X vs without-X covers: with-X often…",
                "Leaving every X as OFF tends to…",
                "What happens if you never use don't-cares?",
            ][(i - 1) % 4],
            [
                "always gives a smaller cover",
                "can miss a smaller legal cover",
                "forces dynamic hazards",
                "removes all ON rows",
            ],
            1,
            "Treating X as OFF by default can miss a smaller cover.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "X means 'pick whichever helps minimization', not 'skip optimization'.",
                "Don't-cares can enlarge prime implicants.",
                "An X is identical to a hard OFF in every algorithm.",
                "Valid covers may leave some X uncovered.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "X is optional; leaving X uncovered is fine.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "A legal implicant may contain…",
                "Which cell types can sit inside a product cube?",
                "Valid cubes cover ON and optionally…",
                "Pick the allowed contents of one SOP implicant.",
            ][(i - 1) % 4],
            [
                "ON and X, never OFF",
                "OFF only",
                "OFF and ON mixed freely",
                "only X, never ON",
            ],
            0,
            "Cover ON; optionally X; never OFF.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If two covers both hit every ON and avoid OFF, they…",
                "Multiple minimal covers can exist when…",
                "Equally valid SOP covers mean…",
                "Different uses of X can yield…",
            ][(i - 1) % 4],
            [
                "must be bitwise identical expressions",
                "are both functionally acceptable for specified F",
                "imply the truth table was wrong",
                "require POS instead",
            ],
            1,
            "Different X choices can give different but valid covers.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Unreachable vs unused outputs: designers still need…",
                "Marking X requires…",
                "Don't-care justification should come from…",
                "What separates true don't-cares from forgotten rows?",
            ][(i - 1) % 4],
            [
                "a clear spec of what is unreachable or unused",
                "always forcing X=1",
                "deleting the rows from silicon",
                "Gray-code axes only",
            ],
            0,
            "Spec must say what is truly don't-care.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Implementing an X as 1 or 0 changes only unspecified rows.",
                "A cover that hits OFF is illegal even if it uses many X.",
                "Don't-care minimization can reduce both literals and term count.",
                "Once minimized with X, the ON set may legally shrink.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "ON must stay covered; OFF must stay uncovered.",
            "hard",
        ),
    ]
    items = (
        pad("easy", "dontcare", easy_b)
        + pad("medium", "dontcare", med_b)
        + pad("hard", "dontcare", hard_b)
    )
    return {"module": "module15-dont-care-lab", "title": "Don't-care minimization", "items": items}


# ── module16-logic-hazards ───────────────────────────────────────────────────


def hazard_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Output should stay 1 but briefly dips to 0 — this is a…",
                "A glitch low while F should remain 1 is a…",
                "Static-1 hazard means the output…",
                "Which hazard dips toward 0 from a steady 1?",
            ][(i - 1) % 4],
            ["static-0 hazard", "static-1 hazard", "dynamic hazard only", "no hazard"],
            1,
            "A glitch low while F should remain 1 is static-1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Consensus cover for AB + A'C adds which bridging term?",
                "For AB + A'C, the consensus product is…",
                "Which term bridges AB and A'C?",
                "Hazard cover for AB+A'C commonly adds…",
            ][(i - 1) % 4],
            ["AC", "BC", "AB", "A'B'"],
            1,
            "BC covers the cube shared when A changes.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Extra output transitions beyond the ideal single change indicate…",
                "Multiple edges on one input change suggest…",
                "0→1→0→1 on one intended transition is a…",
                "Which hazard adds surplus transitions?",
            ][(i - 1) % 4],
            ["static-1", "static-0", "dynamic hazard", "consensus"],
            2,
            "Multiple edges on one input change = dynamic hazard.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Hazard analysis in this lab typically assumes one input changes at a time.",
                "Single-input transitions isolate path-delay glitches.",
                "Static hazards are about steady F with a momentary wrong level.",
                "Hazards mean the truth table itself is incorrect.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Logic can be correct while timing glitches.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Output should stay 0 but briefly spikes to 1 — this is a…",
                "A glitch high while F should remain 0 is a…",
                "Static-0 hazard means the output…",
                "Which hazard spikes toward 1 from a steady 0?",
            ][(i - 1) % 4],
            ["static-0 hazard", "static-1 hazard", "only metastability", "no hazard"],
            0,
            "Spike high while staying 0 is static-0.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Classic static-1 on AB + A'C appears when…",
                "With B=C=1, changing A from 1→0 can glitch because…",
                "AB and A'C both cover ABC, but when A falls…",
                "Path-delay drop of AB before A'C rises causes…",
            ][(i - 1) % 4],
            [
                "both terms go away briefly under delay skew",
                "the function becomes XOR",
                "Cin is missing",
                "Gray code fails",
            ],
            0,
            "One term drops before the other picks up → static-1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Equal gate delays in simulation can…",
                "Why might a hazard hide in zero-delay sim?",
                "Matched delays often…",
                "Silicon vs equal-delay models: hazards…",
            ][(i - 1) % 4],
            [
                "hide glitches that still occur with real skew",
                "prove silicon is glitch-free forever",
                "remove the need for covers",
                "convert static to dynamic only",
            ],
            0,
            "Equal delays can hide the glitch in sim but not in silicon.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "A consensus term can be algebraically redundant yet remove a static hazard.",
                "Cover terms must bridge the risky single-input transition.",
                "Adding BC to AB+A'C changes the steady-state truth table.",
                "Hazard-free covers still implement the same Boolean function.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Consensus is redundant for F but covers the transition.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Dynamic hazards involve…",
                "Unlike static hazards, dynamic ones…",
                "Which best describes a dynamic hazard?",
                "Dynamic hazard signature is…",
            ][(i - 1) % 4],
            [
                "F should change once but chatters with extra edges",
                "F never changes",
                "only setup violations",
                "only bus contention",
            ],
            0,
            "Extra transitions on an intended 0↔1 change.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Where glitches matter, designers may use…",
                "Practical hazard mitigation includes…",
                "Besides consensus covers, glitch-sensitive logic may need…",
                "Pick a real-world hazard strategy.",
            ][(i - 1) % 4],
            [
                "registers, timing analysis, or hazard-free encodings",
                "deleting all clocks",
                "only hex dumps",
                "unsigned compare only",
            ],
            0,
            "Registers/timing/hazard-free covers where glitches matter.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "AB + A'C with B=C=1: steady F before and after A:1→0 is…",
                "For that transition, ideal steady levels are…",
                "Without delay, F stays… across A falling (B=C=1).",
                "Functionally, F should remain… on that edge.",
            ][(i - 1) % 4],
            ["0 then 0", "1 then 1", "1 then 0", "0 then 1"],
            1,
            "Both cubes require F=1 when B=C=1 regardless of A.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Do not confuse a hazard with wrong combinational logic.",
                "The truth table can be correct while path delays glitch.",
                "Every static-1 hazard is fixed by deleting all product terms.",
                "Single-input-change analysis is the usual teaching model here.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Hazards are timing phenomena on correct F.",
            "hard",
        ),
    ]
    items = pad("easy", "hazard", easy_b) + pad("medium", "hazard", med_b) + pad("hard", "hazard", hard_b)
    return {"module": "module16-logic-hazards", "title": "Logic hazards", "items": items}


# ── module17-gate-composer ───────────────────────────────────────────────────


def gates_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "The starter example implements F as…",
                "A single AND for inputs A,B computes…",
                "F = A & B is which gate?",
                "Starter net F=A·B is…",
            ][(i - 1) % 4],
            ["A OR B", "A AND B", "A XOR B", "NOT A"],
            1,
            "Starter is one AND gate: F = A & B.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Two-input XOR: F = 1 when…",
                "XOR asserts when inputs…",
                "A⊕B is high if…",
                "Which rows make XOR = 1?",
            ][(i - 1) % 4],
            ["A and B are equal", "A and B differ", "both are 1", "both are 0"],
            1,
            "XOR is 1 on rows 01 and 10.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "3-input majority: F = 1 when…",
                "Majority(A,B,C) is high if…",
                "At least how many ones for 3-input majority?",
                "Which condition matches majority?",
            ][(i - 1) % 4],
            [
                "exactly one input is 1",
                "at least two inputs are 1",
                "all inputs are 0",
                "parity is even",
            ],
            1,
            "Majority is 1 when two or three inputs are 1.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "A correct gate net must match every row of the target truth table.",
                "The lab checks all input combinations against F.",
                "NAND is NOT of AND.",
                "Matching half the rows proves the net for all inputs.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Exhaustive row match is the judge.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Half-adder sum is which gate of A,B?",
                "HA sum S equals…",
                "S = A⊕B uses…",
                "Which function is HA sum?",
            ][(i - 1) % 4],
            ["AND", "XOR", "OR", "NAND only"],
            1,
            "Sum is XOR; carry is AND.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Half-adder carry is…",
                "HA carry C equals…",
                "Which gate produces HA carry?",
                "C = A·B is…",
            ][(i - 1) % 4],
            ["XOR", "AND", "NOR", "XNOR"],
            1,
            "Carry is A AND B.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A 2:1 mux selecting B or C under A implements…",
                "With select A, Y = A?C:B means…",
                "Mux under A between B and C is…",
                "Which description matches a 2:1 mux?",
            ][(i - 1) % 4],
            [
                "Y follows B when A=0 and C when A=1 (typical)",
                "Y is always A⊕B",
                "Y ignores select",
                "Y is majority of A,B,C only",
            ],
            0,
            "Select steers one data input to Y.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Every gate input in a composed net must be tied — no floating pins.",
                "Wrong polarity on a reused wire breaks active-high assumptions.",
                "Full-adder sum is A⊕B⊕Cin; Cout is majority.",
                "Leaving an input floating is fine if most rows still pass.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Tie every input; FA sum/carry as stated.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Full-adder Cout is which function of A,B,Cin?",
                "Carry-out equals…",
                "Majority of three adder inputs is…",
                "Which expression is FA carry-out?",
            ][(i - 1) % 4],
            [
                "A⊕B⊕Cin",
                "majority(A,B,Cin)",
                "A·B·Cin only",
                "A+B+Cin without AND terms",
            ],
            1,
            "Cout is majority of A, B, Cin.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Building XOR from AND/OR/NOT typically needs…",
                "A⊕B in SOP is…",
                "Which SOP matches XOR?",
                "XOR as sum of products is…",
            ][(i - 1) % 4],
            ["A·B", "A'B + AB'", "A+B", "A·B'·only"],
            1,
            "A'B + AB' is classic XOR SOP.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "A net that passes 3 of 4 two-input rows…",
                "Partial truth-table success means…",
                "Failing one minterm means the net is…",
                "Which verdict fits a one-row miss?",
            ][(i - 1) % 4],
            [
                "is fully correct",
                "is still wrong for the target F",
                "proves hazard-free design",
                "only affects POS",
            ],
            1,
            "Every row must match.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "NAND-only networks can implement any Boolean function (functionally complete).",
                "NOR alone is also functionally complete.",
                "AND alone without NOT/OR cannot express every function.",
                "AND by itself is enough for all Boolean functions including XOR.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "NAND/NOR are complete; AND alone is not.",
            "hard",
        ),
    ]
    items = pad("easy", "gates", easy_b) + pad("medium", "gates", med_b) + pad("hard", "gates", hard_b)
    return {"module": "module17-gate-composer", "title": "Gate composer", "items": items}


# ── module18-mux-decoder ─────────────────────────────────────────────────────


def mux_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A 4:1 mux needs how many select bits?",
                "Four data inputs require how wide a select field?",
                "2^S = 4 implies S = …",
                "Select width for a 4:1 multiplexer is…",
            ][(i - 1) % 4],
            ["1", "2", "4", "8"],
            1,
            "2^S = 4 inputs → S = 2 select bits.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A binary decoder’s outputs are typically…",
                "Decoder Y lines are usually…",
                "Exactly one output active means…",
                "Which coding do decoder outputs use?",
            ][(i - 1) % 4],
            ["all high at once", "one-hot", "always zero", "Gray coded only"],
            1,
            "Exactly one output active per address.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A 3→8 decoder has how many output lines?",
                "2^3 decoder outputs equal…",
                "How many Y lines on a 3-to-8?",
                "Three address bits decode to how many lines?",
            ][(i - 1) % 4],
            ["3", "6", "8", "16"],
            2,
            "2^3 = 8 one-hot outputs.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "2:1 mux with S=0 passes D0 to Y.",
                "When S=1, a 2:1 mux selects D1.",
                "Starter S=0, D0=1, D1=0 gives Y=1.",
                "Select S=0 always forces Y=0 regardless of D0.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "S chooses which data input reaches Y.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "A 2:1 mux needs how many select bits?",
                "Two data inputs need select width…",
                "2^S=2 ⇒ S=…",
                "Select bits for a 2:1 mux?",
            ][(i - 1) % 4],
            ["0", "1", "2", "4"],
            1,
            "One select bit chooses between two inputs.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A 2→4 decoder has how many outputs?",
                "Two address bits decode to…",
                "2^2 one-hot lines equal…",
                "How many Y lines on a 2-to-4 decoder?",
            ][(i - 1) % 4],
            ["2", "3", "4", "8"],
            2,
            "2^2 = 4.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Encoder role relative to a decoder is roughly to…",
                "A binary encoder compresses…",
                "One-hot input to binary index is an…",
                "Encoders typically produce…",
            ][(i - 1) % 4],
            [
                "expand binary to one-hot",
                "compress one-hot (or sparse) requests to a binary code",
                "add carry bits",
                "only generate clocks",
            ],
            1,
            "Encoder compresses toward a binary code (+ valid).",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Mux select width is not the same as decoder output count.",
                "Confusing S-bit width with 2^n Y lines is a common pitfall.",
                "Priority encoders need a rule when multiple inputs are set.",
                "A decoder should assert every Y line on each address.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "One-hot means one Y; priority resolves conflicts.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "An 8:1 mux needs how many select bits?",
                "Eight data inputs require S = …",
                "2^S=8 ⇒ S=…",
                "Select field width for 8:1 is…",
            ][(i - 1) % 4],
            ["2", "3", "4", "8"],
            1,
            "2^3 = 8 → three select bits.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If all encoder inputs are 0, valid V is typically…",
                "No request active ⇒ V…",
                "Idle encoder usually reports…",
                "With no ones on inputs, V equals…",
            ][(i - 1) % 4],
            ["1", "0", "Z", "the max index"],
            1,
            "All inputs zero ⇒ V=0.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "On a 2→4 decoder, address 10 (binary) lights…",
                "Addr=2 activates which one-hot line (Y0..Y3)?",
                "Binary 10 → which decoder output?",
                "Which Y is high for addr 2?",
            ][(i - 1) % 4],
            ["Y0", "Y1", "Y2", "Y3"],
            2,
            "Address 2 → Y2.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Tying multiple decoder outputs high at once breaks one-hot.",
                "Priority rules (high vs low index first) change encoder answers.",
                "Muxes, decoders, and encoders are three related data-steering blocks.",
                "A 4:1 mux and a 2→4 decoder need the same number of output pins.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "4:1 has 1 Y; 2→4 has 4 Y lines.",
            "hard",
        ),
    ]
    items = pad("easy", "mux", easy_b) + pad("medium", "mux", med_b) + pad("hard", "mux", hard_b)
    return {"module": "module18-mux-decoder", "title": "Mux / decoder / encoder", "items": items}


# ── module19-priority-compare ────────────────────────────────────────────────


def priority_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "4-input, high-index-first: I1=I3=1. Winner index?",
                "High-first with I1 and I3 set picks…",
                "Which request wins when I1 and I3 are both high (high-index-first)?",
                "Priority high-index-first: I1=I3=1 → Y=…",
            ][(i - 1) % 4],
            ["1", "3", "0", "2"],
            1,
            "Higher index wins → I3.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Enable-out (EO) typically asserts when…",
                "EO cascades when…",
                "When does enable-out go high?",
                "EO meaning is closest to…",
            ][(i - 1) % 4],
            [
                "EI is high and no local request is active",
                "any input is high",
                "Y equals zero always",
                "priority is low-index-first",
            ],
            0,
            "EO cascades when V=0 but EI=1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "4-bit: A=1111, B=0001. Unsigned vs signed?",
                "A=0xF vs B=0x1: compare views?",
                "Unsigned 15 vs 1 and signed −1 vs 1…",
                "Which statement matches A=1111, B=0001?",
            ][(i - 1) % 4],
            [
                "Both say A<B",
                "Unsigned A>B, signed A<B",
                "Both say A>B",
                "Unsigned A<B, signed A>B",
            ],
            1,
            "15u > 1u, but −1s < 1s.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "High-index-first with I0=I2=1 picks winner I2.",
                "Low-index-first would pick I0 when I0 and I2 are both set.",
                "Priority direction is a design choice.",
                "High- and low-index-first always name the same winner.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Priority direction changes the answer.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Low-index-first: I1=I3=1. Winner?",
                "With low-priority-first, I1 and I3 set →…",
                "Which index wins low-first when I1=I3=1?",
                "Low-index-first winner for I1|I3 is…",
            ][(i - 1) % 4],
            ["3", "1", "0", "2"],
            1,
            "Lowest active index wins → I1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "With EI=1 and no inputs active, V and EO are…",
                "Idle local encoder with EI high reports…",
                "No requests, EI=1 ⇒ …",
                "Cascade idle case: V and EO?",
            ][(i - 1) % 4],
            ["V=1, EO=0", "V=0, EO=1", "V=1, EO=1", "V=0, EO=0"],
            1,
            "No local winner → V=0, EO=1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Unsigned compare treats bits as…",
                "Signed compare interprets MSB as…",
                "Magnitude-only view is…",
                "Two’s-complement order uses…",
            ][(i - 1) % 4],
            [
                "pure magnitude / sign bit respectively",
                "always identical flags",
                "only Gray codes",
                "parity trees only",
            ],
            0,
            "Unsigned = magnitude; signed = MSB is sign.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Enable-out is not the same as 'any input high'.",
                "EO means no local winner while enable-in is on.",
                "Same bit patterns can disagree under signed vs unsigned compare.",
                "Comparator EQ/GT/LT flags ignore the signed-mode setting.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Check signed mode; EO is cascade idle.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "4-bit A=1000, B=0001 unsigned vs signed?",
                "A=8u/−8s vs B=1: relational split?",
                "Which matches A=1000, B=0001?",
                "MSB-set A versus small positive B…",
            ][(i - 1) % 4],
            [
                "Unsigned A>B, signed A<B",
                "Both A<B",
                "Both A>B",
                "Unsigned A<B, signed A>B",
            ],
            0,
            "8u>1u but −8s<1s.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Cascaded priority blocks rely on…",
                "Chaining encoders uses which pair?",
                "To widen priority encode across chips/blocks…",
                "Which signals cascade priority encoders?",
            ][(i - 1) % 4],
            ["EI/EO", "only Cin/Cout of adders", "SRA/SRL", "only OE of tri-states"],
            0,
            "Enable-in / enable-out cascade the search.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If EI=0, a typical priority block…",
                "Disabled encoder slice usually…",
                "With enable-in low…",
                "EI=0 means the block…",
            ][(i - 1) % 4],
            [
                "still asserts local winners normally",
                "is masked — no local grant / EO path off as designed",
                "forces V=1 always",
                "inverts all request inputs",
            ],
            1,
            "EI gates participation in the cascade.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Assuming unsigned flags match signed without checking mode is a pitfall.",
                "Width agreement matters when cascading compare/priority blocks.",
                "High-index-first and low-index-first are interchangeable without redesign.",
                "Priority & compare labs stress both winner selection and relational views.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Priority direction is not free to ignore.",
            "hard",
        ),
    ]
    items = (
        pad("easy", "priority", easy_b)
        + pad("medium", "priority", med_b)
        + pad("hard", "priority", hard_b)
    )
    return {"module": "module19-priority-compare", "title": "Priority & compare", "items": items}


# ── module20-half-full-adder ─────────────────────────────────────────────────


def adder_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Half-adder sum S is which function of A and B?",
                "HA sum equals…",
                "S = A⊕B means…",
                "Which gate is HA sum?",
            ][(i - 1) % 4],
            ["A AND B", "A XOR B", "A OR B", "NOT A"],
            1,
            "S = A⊕B.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A full adder has how many inputs?",
                "FA input count is…",
                "Besides A and B, FA needs…",
                "How many bits feed a full adder?",
            ][(i - 1) % 4],
            ["2", "3", "4", "1"],
            1,
            "A, B, and Cin.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "HA is missing which input vs a full adder?",
                "Half adder lacks…",
                "What does HA omit that FA includes?",
                "HA vs FA: missing…",
            ][(i - 1) % 4],
            ["A", "B", "Cin", "Cout"],
            2,
            "Half adder has no carry-in.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "HA with A=1, B=1 → S=0, C=1.",
                "Binary 1+1 yields sum 0 with carry 1.",
                "HA carry is A AND B.",
                "HA with A=1, B=1 → S=1, C=0.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "1+1 → sum 0, carry 1.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Full-adder sum is…",
                "FA S equals…",
                "Which expression is FA sum?",
                "S for A,B,Cin is…",
            ][(i - 1) % 4],
            ["A·B·Cin", "A⊕B⊕Cin", "A+B only", "majority(A,B,Cin)"],
            1,
            "Sum is XOR of three inputs.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Full-adder Cout is…",
                "Carry-out equals…",
                "FA Cout function is…",
                "Which describes FA carry?",
            ][(i - 1) % 4],
            ["A⊕B", "majority(A,B,Cin)", "A⊕B⊕Cin", "only Cin"],
            1,
            "Cout is majority of A,B,Cin.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "FA with A=1, B=0, Cin=1 → S,Cout?",
                "1+0+1 gives…",
                "What are S and Cout for A=1,B=0,Cin=1?",
                "Two ones among three inputs → …",
            ][(i - 1) % 4],
            ["S=0, Cout=0", "S=0, Cout=1", "S=1, Cout=0", "S=1, Cout=1"],
            1,
            "Two ones → sum 0, carry 1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Two half adders plus an OR on carries build a full adder.",
                "Compose view: HA(A,B) then HA(S1,Cin); Cout = C1 OR C2.",
                "Ripple-carry chains full adders column by column.",
                "A half adder alone is enough for every column in multi-bit add.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Interior columns need Cin → full adder.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "FA with A=B=Cin=1 → S,Cout?",
                "Three ones into a FA produce…",
                "1+1+1 binary nibble of sum/carry is…",
                "Majority and odd parity of three 1s give…",
            ][(i - 1) % 4],
            ["S=0, Cout=0", "S=1, Cout=1", "S=0, Cout=1", "S=1, Cout=0"],
            1,
            "Three ones → sum 1, carry 1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "2-bit ripple: A=10, B=11, Cin0=0. Result S1 S0 and Cout?",
                "Binary 2+3 with Cin=0 yields…",
                "A=10₂, B=11₂ → sum?",
                "Which is 2+3 in 2-bit ripple?",
            ][(i - 1) % 4],
            ["S=01, Cout=0", "S=01, Cout=1", "S=11, Cout=0", "S=00, Cout=0"],
            1,
            "2+3=5 → bits 01 with Cout=1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "HA carry vs FA Cout when Cin matters…",
                "Why isn't HA carry enough in a multi-bit column?",
                "Majority carry differs from HA carry because…",
                "Pick the accurate statement.",
            ][(i - 1) % 4],
            [
                "They solve different problems; Cin participates in Cout",
                "They are always identical wires",
                "HA carry ignores A and B",
                "FA never produces carry",
            ],
            0,
            "Cin changes Cout vs simple HA carry.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Using a half adder where a column needs carry-in is a design pitfall.",
                "Ripple delay grows with bit width.",
                "Faster adders exist beyond naive ripple (CLA, etc.).",
                "FA Cout equals A⊕B even when Cin=1.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Cout is majority, not XOR.",
            "hard",
        ),
    ]
    items = pad("easy", "adder", easy_b) + pad("medium", "adder", med_b) + pad("hard", "adder", hard_b)
    return {"module": "module20-half-full-adder", "title": "Half / full adder", "items": items}


# ── module21-xor-parity-tree ─────────────────────────────────────────────────


def xorpar_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Parity of ones equals which reduction of all bits?",
                "Reduce-XOR across a vector computes…",
                "Odd/even ones map to which fold?",
                "Which operator reduces to parity?",
            ][(i - 1) % 4],
            ["AND", "XOR", "OR", "NAND"],
            1,
            "Reduce XOR: odd ones → 1.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "4-bit 1010: reduce XOR is…",
                "Two ones in 1010 → reduce XOR…",
                "Even ones in 1010 give…",
                "⊕ of bits 1,0,1,0 equals…",
            ][(i - 1) % 4],
            ["0", "1", "2", "undefined"],
            0,
            "Two ones → even → reduce XOR = 0.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Balanced tree depth for N=4 vs linear chain?",
                "⌈log₂4⌉ vs N−1 for N=4 is…",
                "Tree vs chain depth on 4 bits?",
                "Which pair is tree depth vs chain depth (N=4)?",
            ][(i - 1) % 4],
            ["2 vs 3", "3 vs 2", "4 vs 4", "1 vs 3"],
            0,
            "⌈log₂4⌉=2; chain depth N−1=3.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Even parity bit equals reduce XOR; odd parity is its inverse.",
                "P_even = ⊕; P_odd = ¬⊕.",
                "XOR is associative, so tree and chain agree on the bit.",
                "Even and odd parity bits are always identical.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Odd parity complements even/reduce-XOR.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "4-bit 1101: reduce XOR is…",
                "Three ones in 1101 → …",
                "Odd ones in 1101 give reduce XOR…",
                "⊕ of 1,1,0,1 equals…",
            ][(i - 1) % 4],
            ["0", "1", "3", "undefined"],
            1,
            "Three ones → odd → 1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Tree depth for N=8 vs chain?",
                "⌈log₂8⌉ vs 7 is…",
                "Eight-bit balanced tree depth vs linear?",
                "Which pair matches N=8 tree vs chain?",
            ][(i - 1) % 4],
            ["3 vs 7", "7 vs 3", "8 vs 8", "2 vs 7"],
            0,
            "log₂8=3; chain N−1=7.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Flip any single bit and parity…",
                "Changing one bit in the vector…",
                "Single-bit error effect on parity is…",
                "Reduce XOR after one bit flip…",
            ][(i - 1) % 4],
            ["stays the same", "toggles", "becomes Z", "always clears to 0"],
            1,
            "Any single flip toggles parity.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Hardware parity generators prefer trees for timing.",
                "Tree and chain must agree on the final bit, not on delay.",
                "An odd leftover at a tree level promotes unchanged.",
                "A long XOR chain is always faster than a balanced tree.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Trees shorten critical path.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "If reduce XOR = 1, even parity bit and odd parity bit are…",
                "When ⊕=1, P_even and P_odd equal…",
                "Odd count of ones ⇒ even/odd parity bits…",
                "Which pair is (P_even, P_odd) when reduce XOR is 1?",
            ][(i - 1) % 4],
            ["(1,0)", "(0,1)", "(1,1)", "(0,0)"],
            0,
            "P_even=⊕=1; P_odd=0.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "For N=5, balanced-style depth is about…",
                "⌈log₂5⌉ compared with chain depth 4…",
                "Five-bit tree depth vs chain?",
                "Which is closest for N=5 tree vs chain?",
            ][(i - 1) % 4],
            ["3 vs 4", "5 vs 5", "1 vs 1", "4 vs 3"],
            0,
            "⌈log₂5⌉=3; chain=4.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Level-1 pairs of 1010 yield which two XOR results?",
                "Pair (1⊕0) and (1⊕0) on 1010 → …",
                "First tree level on 1010 produces…",
                "After pairing 10 and 10, bits are…",
            ][(i - 1) % 4],
            ["00", "11", "01", "10"],
            1,
            "1⊕0=1 twice → 11 before final ⊕ → 0.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Do not confuse even parity with odd parity — one complements the other.",
                "Building a long chain when a tree meets timing is a common pitfall.",
                "Real links may need CRC/ECC beyond a single parity bit.",
                "Tree association can change the Boolean result of XOR reduction.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "XOR association preserves the bit; delays differ.",
            "hard",
        ),
    ]
    items = pad("easy", "xorpar", easy_b) + pad("medium", "xorpar", med_b) + pad("hard", "xorpar", hard_b)
    return {"module": "module21-xor-parity-tree", "title": "XOR parity tree", "items": items}


# ── module22-tri-state-bus ───────────────────────────────────────────────────


def tristate_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Enable off — driver disconnected — bus level is…",
                "High-Z means the driver is…",
                "With OE false and no pull, the net reads…",
                "Disconnected tri-state output presents…",
            ][(i - 1) % 4],
            ["Z (high-Z)", "always 0", "always 1", "X"],
            0,
            "High impedance — not driving the net.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Two enabled drivers, A=1 and B=0 → bus is…",
                "Fighting opposite values cause…",
                "Contention on a bus resolves as…",
                "1 fighting 0 yields…",
            ][(i - 1) % 4],
            ["1", "0", "X (contention)", "Z"],
            2,
            "Fighting drivers → unknown/contention.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Safe bus practice: how many drivers enabled at once?",
                "At most how many active drivers?",
                "One-hot OE means…",
                "Safe enable count is…",
            ][(i - 1) % 4],
            ["0 or 1", "exactly 2", "any number", "always 3"],
            0,
            "At most one active driver (or float).",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Only A enabled with data 1 → bus = 1.",
                "Single driver wins cleanly.",
                "All enables off with no pull → bus = Z.",
                "Two opposite drivers still guarantee a valid 0/1.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Opposite drive → contention X.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "All enables low with pull-up on → bus is…",
                "Float with pull-up resolves to…",
                "Idle pulled-up bus reads…",
                "Pull-up on a undriven net yields…",
            ][(i - 1) % 4],
            ["0", "1", "X", "always Z forever"],
            1,
            "Pull-up defines idle as 1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Two drivers enabled with the same data 1 → readout may show 1, but…",
                "Agreeing multi-drive is still…",
                "Same-value overlap is…",
                "Best practice for two enables both driving 1?",
            ][(i - 1) % 4],
            [
                "unsafe practice — violates one-driver discipline",
                "required for speed",
                "identical to high-Z",
                "how pull-downs work",
            ],
            0,
            "Overlapping enables is unsafe even if values match.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Internal FPGA fabrics often prefer… instead of tri-state.",
                "On-chip steering frequently uses…",
                "Which alternative avoids shared tri-state rails inside FPGAs?",
                "Modern fabrics lean toward…",
            ][(i - 1) % 4],
            ["muxes", "more contention", "always analog pads", "removing OE entirely forever"],
            0,
            "Muxes often replace on-chip tri-state.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Pull-down on an undriven net defines idle 0.",
                "X means contention/unknown, not a third valid logic level to use.",
                "Safe protocols often one-hot the output enables.",
                "Any number of drivers may be enabled if the board is short.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Keep ≤1 driver; pulls define idle.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Bus holders / weak keepers primarily…",
                "A bus hold device is meant to…",
                "Which role fits a bus-hold cell?",
                "Keepers on a floated bus…",
            ][(i - 1) % 4],
            [
                "retain the last driven level weakly when undriven",
                "force permanent contention",
                "replace clocks",
                "decode seven-segment glyphs",
            ],
            0,
            "Weak feedback holds the last value.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "OE timing matters because…",
                "Enable overlap during handoff can…",
                "Why carefully break-before-make OE?",
                "Switching drivers without dead time risks…",
            ][(i - 1) % 4],
            [
                "momentary dual-drive contention",
                "only improving setup margin always",
                "removing the need for resets",
                "converting Z to XOR",
            ],
            0,
            "Overlapping OE windows fight the bus.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Resolution table: one driver 0, others Z → bus…",
                "Single active 0 among high-Z peers reads…",
                "Clean drive-0 case yields…",
                "What is the bus with one 0 driver?",
            ][(i - 1) % 4],
            ["0", "1", "X", "Z"],
            0,
            "One driver determines the level.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Do not treat multi-drive same value as safe.",
                "Real boards need OE timing, holders, and protocol rules.",
                "Tri-state is about sharing a wire with disciplined enables.",
                "Contention X is a recommended steady-state operating mode.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Contention is a fault, not a mode.",
            "hard",
        ),
    ]
    items = (
        pad("easy", "tristate", easy_b)
        + pad("medium", "tristate", med_b)
        + pad("hard", "tristate", hard_b)
    )
    return {"module": "module22-tri-state-bus", "title": "Tri-state / bus", "items": items}


# ── module23-barrel-shifter ──────────────────────────────────────────────────


def barrel_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "An 8-bit barrel shifter needs how many mux stages?",
                "⌈log₂8⌉ power-of-two stages equal…",
                "Stage count for width 8 is…",
                "How many binary-weighted stages for 8 bits?",
            ][(i - 1) % 4],
            ["7", "3", "8", "1"],
            1,
            "⌈log₂8⌉ = 3 power-of-two stages.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "0xD2 SLL by 3 → output?",
                "11010010 << 3 equals…",
                "Logical left shift of 0xD2 by 3 is…",
                "Starter SLL3 on 0xD2 yields…",
            ][(i - 1) % 4],
            ["0x90", "0xD2", "0x68", "0xA4"],
            0,
            "11010010 << 3 = 10010000 = 0x90.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Amount 3 enables which shift stages?",
                "3 = 1+2 fires stages…",
                "Which power-of-two enables for amt=3?",
                "Binary 11 on amount selects…",
            ][(i - 1) % 4],
            ["×1 and ×2", "×1 only", "×4 only", "×1, ×2, and ×4"],
            0,
            "3 = 1+2 → stages 1 and 2.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Arithmetic right (SRA) replicates the sign bit into vacated positions.",
                "MSB fills on arithmetic right shifts.",
                "Logical right (SRL) fills with zeros from the left.",
                "SRA and SRL always fill vacated bits with zeros.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "SRA sign-fills; SRL zero-fills.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Amount 5 enables which stages?",
                "5 = 4+1 fires…",
                "Binary amount 101 selects…",
                "Which enables for shift by 5?",
            ][(i - 1) % 4],
            ["×1 and ×4", "×2 only", "×1 and ×2", "×8 only"],
            0,
            "5 = 4+1 → stages ×1 and ×4.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Rotate left differs from SLL because rotate…",
                "ROL vs logical left…",
                "What does rotate preserve that SLL discards?",
                "Rotate mode…",
            ][(i - 1) % 4],
            [
                "wraps bits with no fill loss",
                "always zero-fills",
                "only shifts by 1",
                "ignores amount bits",
            ],
            0,
            "Rotate wraps; SLL shifts in zeros.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Critical path of an 8-bit barrel is about…",
                "Delay scales with…",
                "Barrel timing is dominated by…",
                "Why not N serial 1-bit layers for variable shift?",
            ][(i - 1) % 4],
            [
                "three mux delays, not the shift distance in serial steps",
                "exactly N−1 always",
                "only wire OR",
                "a single AND gate",
            ],
            0,
            "log-depth mux stages beat serial shifting.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Amount N does not mean N serial one-bit layers in a barrel.",
                "Decode the amount into power-of-two stage enables.",
                "SRA and SRL differ only in the fill bit.",
                "A barrel always needs seven stages for any 8-bit shift amount.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Three stages cover amounts 0–7.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "0x80 SRL by 1 → ?",
                "10000000 logical right 1 equals…",
                "Logical right of 0x80 by 1 is…",
                "SRL1 on 0x80 yields…",
            ][(i - 1) % 4],
            ["0x40", "0xC0", "0x00", "0x81"],
            0,
            "Zero fills from the left → 0x40.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "0x80 SRA by 1 → ?",
                "Sign-extending right shift of 0x80…",
                "Arithmetic right of 10000000 by 1 is…",
                "SRA1 on negative 0x80 yields…",
            ][(i - 1) % 4],
            ["0x40", "0xC0", "0x00", "0x01"],
            1,
            "Sign bit 1 fills → 0xC0.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "After ×1 stage on 0xD2 (11010010), intermediate is…",
                "SLL by 1 on 0xD2 gives…",
                "First stage toward SLL3 on 0xD2 yields…",
                "11010010 << 1 equals…",
            ][(i - 1) % 4],
            ["0xA4", "0x90", "0x69", "0xD2"],
            0,
            "11010010<<1 = 10100100 = 0xA4.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Confusing barrel stages with counting single-bit shifts is a pitfall.",
                "Real ALUs still need width rules and flags beyond an 8-bit toy.",
                "Rotate wraps bits; logical shifts use fill constants.",
                "Amount bit for ×4 is unused when shifting by 7.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "7=4+2+1 uses all three stages.",
            "hard",
        ),
    ]
    items = pad("easy", "barrel", easy_b) + pad("medium", "barrel", med_b) + pad("hard", "barrel", hard_b)
    return {"module": "module23-barrel-shifter", "title": "Barrel shifter", "items": items}


# ── module24-seven-segment ───────────────────────────────────────────────────


def sevenseg_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A classic seven-segment digit has how many segments?",
                "Segments a through g total…",
                "How many LED segments form the digit?",
                "Count of segments a–g is…",
            ][(i - 1) % 4],
            ["6", "7", "8", "4"],
            1,
            "Segments a through g.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter A (CC): which segment is off?",
                "Pattern 1110111 has which bit 0 (abcdefg)?",
                "Hex A on common-cathode leaves which segment dark?",
                "For glyph A, segment … is off.",
            ][(i - 1) % 4],
            ["a", "d", "g", "b"],
            1,
            "1110111 — d is 0.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Common-cathode: segment ON is driven at…",
                "CC active level for a lit segment is…",
                "On CC displays, drive 1 means…",
                "Which level lights a CC segment?",
            ][(i - 1) % 4],
            ["0", "1", "Z", "X"],
            1,
            "1 = ON for CC.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Common-anode drive = NOT(common-cathode pattern) for the same glyph.",
                "Polarity inverts the bus between CA and CC.",
                "Digit eight lights all seven segments.",
                "CA and CC use identical drive bit patterns for the same glyph.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "CA inverts the CC pattern.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Digit 1 typically lights which segments?",
                "Glyph '1' uses the right-side pair…",
                "Which segments form digit one?",
                "Classic '1' illuminates…",
            ][(i - 1) % 4],
            ["only b and c", "all seven", "only g", "only a and d"],
            0,
            "Digit one lights b and c on the right.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Digit 0 turns which middle segment off?",
                "Glyph zero leaves … dark.",
                "Which segment is off for '0'?",
                "'0' vs '8' differs mainly by…",
            ][(i - 1) % 4],
            ["g", "a", "b", "c"],
            0,
            "Digit zero turns g off in the middle.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Common-anode: segment ON is typically driven at…",
                "CA active-low lighting means ON is…",
                "On CA parts, lit segments are…",
                "Which level lights a CA segment?",
            ][(i - 1) % 4],
            ["1", "0", "Z only", "X only"],
            1,
            "0 = ON for common-anode.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "The decoder is a lookup (ROM/case), not seven unrelated wires.",
                "Bit order in this lab is abcdefg as the drive string.",
                "Nibble 0xA maps to a fixed segment pattern.",
                "Segment order may be scrambled freely without changing the glyph map.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Keep abcdefg order consistent.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "CC pattern for A is 1110111; CA drive for same glyph is…",
                "Invert 1110111 for common-anode A → …",
                "Bitwise NOT of CC 'A' pattern equals…",
                "CA string for glyph A from CC 1110111 is…",
            ][(i - 1) % 4],
            ["1110111", "0001000", "0000000", "1111111"],
            1,
            "NOT 1110111 = 0001000.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Wiring CC patterns into a CA board without inversion…",
                "Polarity mismatch typically…",
                "What happens if CC codes drive CA hardware raw?",
                "Skipping CA/CC inversion causes…",
            ][(i - 1) % 4],
            [
                "wrong/complement glyphs or mostly inverted lighting",
                "perfect digits always",
                "only faster refresh",
                "removes the need for current limits",
            ],
            0,
            "Must invert for CA vs CC.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Digit 8 CC pattern (abcdefg) is…",
                "All segments on reads as…",
                "Which bit string is '8' on CC?",
                "Seven ones in abcdefg mean…",
            ][(i - 1) % 4],
            ["0000000", "1111111", "0110000", "1110111"],
            1,
            "Eight lights all seven → 1111111.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Real displays still need current limiting and often multiplexing.",
                "Mixed-case hex letters are for readability, not a different encoding.",
                "Four-bit nibbles cover 0–F glyphs in this lab.",
                "A seven-segment digit has eight independent data bits named a–h always lit.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Seven segments a–g; dp is optional extra.",
            "hard",
        ),
    ]
    items = (
        pad("easy", "sevenseg", easy_b)
        + pad("medium", "sevenseg", med_b)
        + pad("hard", "sevenseg", hard_b)
    )
    return {"module": "module24-seven-segment", "title": "Seven-segment", "items": items}


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
        for it in bank["items"]:
            counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
            assert "(v" not in it["prompt"], it["prompt"]
            assert "variant " not in it["prompt"].lower(), it["prompt"]
        print(path.name, counts, "total", len(bank["items"]))


if __name__ == "__main__":
    main()
