"""Challenge banks for learn_digital modules 35–49 (30 easy + 30 medium + 30 hard each).

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


def pad(difficulty: str, prefix: str, builders: list) -> list[dict]:
    out: list[dict] = []
    n = 0
    while len(out) < TARGET:
        out.append(builders[n % len(builders)](len(out) + 1))
        n += 1
    fixed = []
    for i, it in enumerate(out[:TARGET], start=1):
        it = dict(it)
        it["id"] = f"{prefix}_{difficulty}_{i:02d}"
        it["difficulty"] = difficulty
        fixed.append(it)
    return fixed


def bank(module: str, title: str, prefix: str, easy_b: list, med_b: list, hard_b: list) -> dict:
    items = pad("easy", prefix, easy_b) + pad("medium", prefix, med_b) + pad("hard", prefix, hard_b)
    return {"module": module, "title": title, "items": items}


# --- module35: Ripple-carry adder ---


def rca_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Full-adder sum bit is…",
                "The sum output of a full adder equals…",
                "Which expression yields FA sum?",
                "S from a full adder is best written as…",
            ][(i - 1) % 4],
            ["A ⊕ B ⊕ Cin", "A & B & Cin", "A | B", "A ⊕ B only"],
            0,
            "Three-input XOR.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "In ripple-carry, Cin of bit i comes from…",
                "Where does stage i get its carry-in?",
                "Bit i’s Cin is driven by…",
                "Ripple carry into bit i is…",
            ][(i - 1) % 4],
            ["Cout of bit i−1 (LSB first)", "Cout of the MSB", "Always 1", "The clock"],
            0,
            "Carry chains upward from the LSB.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter 4-bit 5+3, Cin=0 gives sum…",
                "Four-bit unsigned 0101 + 0011 with Cin=0 is…",
                "What is 5 + 3 in a 4-bit RCA with Cin=0?",
                "5+3 on a 4-bit ripple adder (Cin=0) yields…",
            ][(i - 1) % 4],
            ["8, Cout 0", "2, Cout 1", "0, Cout 1", "15, Cout 0"],
            0,
            "0101 + 0011 = 1000.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Worst-case RCA delay grows roughly linearly with bit width.",
                "A ripple-carry adder’s critical path lengthens as N increases.",
                "Carry must walk the FA chain in a classic RCA.",
                "Half adders include a Cin input like full adders.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "RCA delay tracks the carry chain; half adders have no Cin.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Full-adder Cout is 1 when…",
                "Carry-out of a FA asserts if…",
                "Which condition produces Cout=1?",
                "Majority of A, B, Cin being 1 means…",
            ][(i - 1) % 4],
            [
                "At least two of A, B, Cin are 1",
                "Exactly one input is 1",
                "Only A is 1",
                "Clock rises",
            ],
            0,
            "Cout is the majority function of the three inputs.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "4-bit unsigned 15+1, Cin=0 gives…",
                "All-ones plus one in 4 bits (Cin=0) yields…",
                "What happens for 0xF + 1 at width 4?",
                "Unsigned wrap of 1111₂ + 1 is…",
            ][(i - 1) % 4],
            ["0, Cout 1", "1, Cout 0", "15, Cout 0", "16 without Cout"],
            0,
            "Sum 0 with carry out — unsigned wrap.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Critical path of an N-bit RCA is about…",
                "Worst-case delay roughly equals…",
                "Timing bottleneck in ripple-carry is…",
                "Which delay dominates a wide RCA?",
            ][(i - 1) % 4],
            [
                "N full-adder carry delays",
                "One XOR only",
                "A single AND gate forever",
                "Memory access time",
            ],
            0,
            "Carry must propagate through all stages.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Cin=1 is commonly used for two’s-complement subtract (A + ~B + 1).",
                "Treating Cout as signed overflow is always correct.",
                "Bit 1 must wait for bit 0’s Cout in a ripple chain.",
                "Wide adders often prefer lookahead or prefix over pure ripple.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 1 else False,
            "Cout is unsigned wrap; signed overflow is a different flag.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Why is pure ripple rarely used at 64 bits?",
                "Main drawback of a long RCA is…",
                "At large N, ripple-carry suffers from…",
                "Architects replace wide RCAs mainly because of…",
            ][(i - 1) % 4],
            [
                "Carry delay grows ~linearly with N",
                "It cannot add at all",
                "It needs no gates",
                "It only works in Gray code",
            ],
            0,
            "Lookahead / prefix shorten the carry path.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Half adder vs full adder — key difference?",
                "What does a full adder have that a half adder lacks?",
                "HA and FA differ because FA includes…",
                "Pick the accurate HA/FA distinction.",
            ][(i - 1) % 4],
            [
                "FA has Cin; HA does not",
                "HA has three inputs; FA has two",
                "Only HA produces Cout",
                "They are identical",
            ],
            0,
            "Full adders take A, B, and Cin.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "For 4-bit 7+9 with Cin=0, the unsigned result is…",
                "0111 + 1001 at width 4 (Cin=0) yields…",
                "What are sum and Cout for 7+9 in 4 bits?",
                "7 + 9 unsigned 4-bit RCA output is…",
            ][(i - 1) % 4],
            ["0, Cout 1", "16, Cout 0", "7, Cout 0", "15, Cout 0"],
            0,
            "16 wraps to 0000 with Cout=1.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Browser labs teach literacy; real RTL still needs timing analysis.",
                "An RCA always meets timing at any clock rate by construction.",
                "Cout of the MSB can feed Cin of a wider extended adder.",
                "Ripple order is MSB-first by definition.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 in (0, 2) else False,
            "Ripple is LSB→MSB; timing is not automatic.",
            "hard",
        ),
    ]
    return bank(
        "module35-ripple-carry-adder-animator",
        "Ripple-carry adder",
        "rca",
        easy_b,
        med_b,
        hard_b,
    )


# --- module36: Carry-lookahead G/P ---


def cla_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Generate Gᵢ is…",
                "Bit generate equals…",
                "Which expression is generate?",
                "Gᵢ forces a carry when both inputs are 1 — Gᵢ is…",
            ][(i - 1) % 4],
            ["Aᵢ · Bᵢ", "Aᵢ ⊕ Bᵢ", "Aᵢ + Bᵢ (OR only)", "Cᵢ alone"],
            0,
            "G = A AND B forces carry out.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Propagate Pᵢ (XOR form) is…",
                "XOR-style propagate equals…",
                "Which is Pᵢ in the common CLA teaching form?",
                "P passes Cin when G=0; P is…",
            ][(i - 1) % 4],
            ["Aᵢ ⊕ Bᵢ", "Aᵢ · Bᵢ", "Always 0", "Cᵢ ⊕ Cᵢ₊₁"],
            0,
            "P = A XOR B.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Recursive CLA carry is…",
                "Cᵢ₊₁ from G and P is…",
                "The CLA recurrence for next carry is…",
                "Generate-or-propagate carry rule is…",
            ][(i - 1) % 4],
            ["Cᵢ₊₁ = Gᵢ + Pᵢ·Cᵢ", "Cᵢ₊₁ = Aᵢ ⊕ Bᵢ", "Cᵢ₊₁ = Gᵢ · Pᵢ", "Cᵢ₊₁ = Cᵢ only"],
            0,
            "Generate or propagate path.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "If Gᵢ=1, then Cᵢ₊₁ is 1 regardless of Cᵢ.",
                "Generate dominates propagate when G=1.",
                "Sum in CLA teaching form is often P ⊕ Cin.",
                "CLA always uses a longer carry chain than ripple.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "G wins; CLA shortens carry delay vs ripple.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "For 5+3 bit0 (A=B=1): G₀ and P₀ are…",
                "LSBs both 1 in 0101+0011 means…",
                "Bit 0 of starter 5+3: generate/propagate?",
                "At bit0 of 5+3, which G/P pair is correct?",
            ][(i - 1) % 4],
            ["G=1, P=0", "G=0, P=1", "G=1, P=1", "G=0, P=0"],
            0,
            "Both 1 → generate; XOR is 0.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "If G=0 and P=1, the carry…",
                "Propagate with no generate means…",
                "When only P is asserted…",
                "P=1, G=0 does what to Cin?",
            ][(i - 1) % 4],
            [
                "Passes Cin through to Cout",
                "Forces Cout=1 always",
                "Kills carry always",
                "Ignores Cin and A",
            ],
            0,
            "Propagate path: Cout = Cin.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "If G=0 and P=0, carry is…",
                "Neither generate nor propagate means…",
                "G=P=0 implies Cout…",
                "Kill case for carry is…",
            ][(i - 1) % 4],
            ["Killed (Cout=0)", "Forced to 1", "Equal to Cin always", "Undefined forever"],
            0,
            "No generate and no propagate → kill.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Expanded C₂ includes terms like G₁ + P₁·G₀ + …",
                "CLA trades area (more G/P logic) for shorter carry delay.",
                "P=0 kills carry regardless of Cin when G=0.",
                "Confusing G with P never causes sum errors.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Expanded AND-OR paths; G/P mix-ups break results.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Wide adders usually implement lookahead as…",
                "Beyond flat expansion, industry uses…",
                "Prefix/Ladner-Fischer style trees replace…",
                "One giant flat CLA expansion for 64 bits is…",
            ][(i - 1) % 4],
            [
                "Prefix trees / grouped CLA, not one flat mega-OR",
                "Only pure ripple forever",
                "Software loops only",
                "ROM lookup of every sum",
            ],
            0,
            "Practical CLA uses hierarchy/prefix.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "CLA vs RCA: main speed win comes from…",
                "Why can CLA be faster than ripple?",
                "Parallel carry computation helps because…",
                "CLA shortens path by…",
            ][(i - 1) % 4],
            [
                "Computing carries from G/P in parallel",
                "Removing all adders",
                "Using fewer bits always",
                "Ignoring Cin",
            ],
            0,
            "Carries from G, P, C₀ without long ripple.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Given G₀=1, C₀=0, what is C₁?",
                "Generate at bit0 with C₀=0 yields C₁=…",
                "If G₀=1, C₁ equals…",
                "Force-carry case: G₀=1 ⇒ C₁…",
            ][(i - 1) % 4],
            ["1", "0", "Equal to P₀", "Undefined"],
            0,
            "C₁ = G₀ + P₀·C₀ = 1.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Each term in an expanded CLA equation is a real AND-OR path.",
                "G=1 always wins over propagate.",
                "Sum still needs the local Cin even in CLA.",
                "CLA eliminates the need for any timing on carry paths.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Still analyze timing; literacy ≠ free STA.",
            "hard",
        ),
    ]
    return bank(
        "module36-carry-look-ahead-adder-propagate-and-generate",
        "Carry-lookahead G/P",
        "cla",
        easy_b,
        med_b,
        hard_b,
    )


# --- module37: Array multiplier ---


def arrmult_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Each cell Aᵢ·Bⱼ in an unsigned array multiplier is…",
                "Partial-product bits come from…",
                "The basic PP bit function is…",
                "Aᵢ AND Bⱼ produces…",
            ][(i - 1) % 4],
            ["AND of one A bit and one B bit", "XOR only", "A flip-flop", "A carry lookahead cell"],
            0,
            "Partial-product bit from AND.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Row for Bⱼ is shifted left by…",
                "Partial-product row j is aligned by…",
                "How many positions does row j shift?",
                "Bit weight of Bⱼ requires a left shift of…",
            ][(i - 1) % 4],
            ["j bit positions", "Always zero", "N bits always", "2N bits"],
            0,
            "Matches bit weight of Bⱼ.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter 4-bit 5×3 gives product…",
                "Unsigned 0101 × 0011 equals…",
                "What is 5 × 3 in the array-mult starter?",
                "4-bit 5 times 3 product is…",
            ][(i - 1) % 4],
            ["15", "8", "5", "225"],
            0,
            "0101 × 0011 = 1111.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "N-bit × N-bit unsigned product needs up to 2N bits.",
                "Partial products are summed (with shifts) to form the product.",
                "Array multipliers never use adders.",
                "Each B bit enables one shifted copy of A (or zeros).",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Double width for full product; PP rows feed an array of adders.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "How many AND terms in an N×N unsigned array?",
                "Partial-product bit count for N×N is…",
                "Number of Aᵢ·Bⱼ cells for width N is…",
                "N×N array has how many PP bits?",
            ][(i - 1) % 4],
            ["N²", "N", "2N", "N/2"],
            0,
            "Every bit pair contributes one AND.",
            "medium",
        ),
        lambda i: mcq(
            "",
            f"Unsigned 4-bit {6 + (i % 3)}×{2 + (i % 2)} product is…",
            [
                str((6 + (i % 3)) * (2 + (i % 2))),
                str((6 + (i % 3)) + (2 + (i % 2))),
                str((6 + (i % 3)) << 1),
                "0",
            ],
            0,
            "Multiply the two unsigned values.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "If Bⱼ=0, that PP row contributes…",
                "A zero multiplier bit means the row is…",
                "When Bⱼ is clear, shifted A becomes…",
                "Disabled PP row equals…",
            ][(i - 1) % 4],
            ["All zeros", "All ones", "A unshifted", "Carry-only"],
            0,
            "AND with 0 clears the row.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Unsigned array multiply is not the same as signed Booth without recoding.",
                "Product width 2N covers the worst-case unsigned magnitude.",
                "Shifting PP rows implements place value of Bⱼ.",
                "Array height is unrelated to multiplier bit count.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Rows track B bits; signed needs different treatment.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Critical path in a large array mult often involves…",
                "Delay bottleneck tends to be…",
                "What dominates timing in a deep PP array?",
                "Array mult speed is limited by…",
            ][(i - 1) % 4],
            [
                "Long adder/carry chains through the array",
                "A single AND forever",
                "Only ROM decode",
                "UART baud",
            ],
            0,
            "PP reduction / carry propagate through rows.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Max unsigned product of two 4-bit numbers is…",
                "15×15 fits in how many bits minimum?",
                "Worst-case 4×4 unsigned magnitude is…",
                "0xF × 0xF equals…",
            ][(i - 1) % 4],
            ["225 (needs 8 bits)", "15", "30", "255 always"],
            0,
            "15×15=225 < 256 → 8 bits.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Compared with shift-add sequential multiply, an array…",
                "Combinational array vs iterative multiply:",
                "Array multiplier typically offers…",
                "Area/latency trade for array vs sequential is…",
            ][(i - 1) % 4],
            [
                "More area, lower latency (one cycle combinational)",
                "Less area, more cycles always identical",
                "No partial products",
                "Only works for odd widths",
            ],
            0,
            "Parallel PP vs multi-cycle shift-add.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Truncating a 2N-bit product to N bits can lose high bits.",
                "Signed × signed needs care beyond plain AND arrays.",
                "PP alignment mistakes shift the numeric weight.",
                "N² ANDs alone finish the multiply with no addition.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "ANDs make PPs; adders reduce them.",
            "hard",
        ),
    ]
    return bank("module37-array-mult", "Array multiplier", "arrmult", easy_b, med_b, hard_b)


# --- module38: ALU explorer ---


def alu_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "An ALU opcode primarily selects…",
                "Opcode / op field chooses…",
                "What does the ALU control word pick?",
                "Datapath function is selected by…",
            ][(i - 1) % 4],
            [
                "Which arithmetic/logic function to apply",
                "The clock frequency",
                "A memory address only",
                "Reset polarity",
            ],
            0,
            "Control picks the datapath op.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter ADD 5+3: Y equals…",
                "ALU ADD of 0101 and 0011 yields…",
                "5 + 3 through the ALU explorer is…",
                "Result Y for starter ADD is…",
            ][(i - 1) % 4],
            ["8 (1000₂)", "2", "15", "0"],
            0,
            "0101 + 0011 = 1000.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Flag Z is set when…",
                "Zero flag asserts if…",
                "When is Z true?",
                "Z indicates…",
            ][(i - 1) % 4],
            ["Y is zero", "Carry occurred", "MSB is 1", "Opcode is SUB"],
            0,
            "Zero result flag.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Flag V indicates signed overflow on ADD/SUB.",
                "Flag C is the unsigned carry / borrow sense.",
                "AND/OR/XOR typically ignore arithmetic overflow V.",
                "ALU flags are unrelated to the result Y.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Flags summarize Y and arithmetic properties.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "SUB often implemented as…",
                "A − B in two’s complement is…",
                "How do many ALUs subtract?",
                "Hardware subtract commonly uses…",
            ][(i - 1) % 4],
            ["A + ~B + 1", "A AND B", "A XOR 0", "Shift B left"],
            0,
            "Add bitwise complement plus one.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Bitwise AND of 0b1100 and 0b1010 is…",
                "1100₂ ∧ 1010₂ equals…",
                "ALU AND 12 & 10 yields…",
                "What is 0xC & 0xA at 4 bits?",
            ][(i - 1) % 4],
            ["0b1000", "0b1110", "0b0110", "0b0000"],
            0,
            "Bitwise AND → 1000₂.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "N flag (if present) usually tracks…",
                "Negative flag commonly mirrors…",
                "Sign/N flag is often…",
                "Which bit feeds a typical N flag?",
            ][(i - 1) % 4],
            ["MSB of Y (sign bit)", "LSB only", "Carry only", "Opcode LSB"],
            0,
            "N ≈ signed negative when MSB=1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "V and C can disagree on the same ADD.",
                "Logical ops still update Z based on Y.",
                "Opcode must match the intended arithmetic vs logic view of flags.",
                "Changing opcode never changes Y for fixed A,B.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Different ops → different Y; C≠V possible.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Signed overflow V on ADD is typically…",
                "Classic V detection for A+B looks at…",
                "When do same-sign operands overflow signed add?",
                "V=1 on ADD when…",
            ][(i - 1) % 4],
            [
                "Carry into MSB ≠ carry out of MSB (same-sign case)",
                "Z is 1",
                "Y equals A",
                "Opcode is OR",
            ],
            0,
            "Signed overflow ≠ unsigned Cout alone.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "ALU result bus Y width usually matches…",
                "Datapath width for Y is…",
                "If operands are N bits, Y is typically…",
                "Flags are derived from an N-bit Y where N is…",
            ][(i - 1) % 4],
            [
                "The operand datapath width N",
                "Always 1 bit",
                "Always 2N for every op",
                "Independent of A/B width",
            ],
            0,
            "ALU Y is N-bit for N-bit ops (multiply may differ).",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "XOR of A with all-ones is…",
                "A ⊕ 0xFF (8-bit) equals…",
                "Bitwise complement via XOR mask is…",
                "Inverting all bits of A can be done with…",
            ][(i - 1) % 4],
            ["Bitwise NOT of A", "A + 1", "A AND 0", "A unchanged"],
            0,
            "XOR with ones flips every bit.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Exploring flags per opcode builds intuition for ISA condition codes.",
                "Unsigned wrap and signed overflow are the same flag.",
                "A good check is hand-computing Y and Z for one ADD and one AND.",
                "ALUs never feed status into branch decisions in CPUs.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 in (0, 2) else False,
            "C≠V; flags often steer branches.",
            "hard",
        ),
    ]
    return bank("module38-alu-explorer", "ALU explorer", "alu", easy_b, med_b, hard_b)


# --- module39: Carry-select adder ---


def csa_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "An adder that muxes dual Cin paths is a…",
                "Speculate-then-select on carry describes a…",
                "Which adder runs two upper sums and muxes?",
                "Carry-select architecture is…",
            ][(i - 1) % 4],
            ["Carry-select adder", "Lookahead multiplier", "Ring counter", "ALU flag decoder"],
            0,
            "Speculate then select on carry.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "The upper block computes how many speculative sums?",
                "How many Cin hypotheses does the upper CSA block use?",
                "Dual parallel upper adds means…",
                "Upper CSA paths are…",
            ][(i - 1) % 4],
            ["2 (Cin=0 and Cin=1)", "1", "4", "8"],
            0,
            "Dual parallel upper adds.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "C4 from the lower nibble selects…",
                "Real carry into the mux picks…",
                "What does the select signal choose?",
                "Lower-block Cout steers…",
            ][(i - 1) % 4],
            [
                "Which upper speculative path the mux uses",
                "The clock edge",
                "ROM contents",
                "Reset only",
            ],
            0,
            "Real carry picks Cin=0 vs Cin=1 sum.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "C4 from the lower nibble selects which upper path the mux uses.",
                "Carry-select trades area (dual adders) for less wait on late carry.",
                "Only one upper sum is ever computed in CSA.",
                "Starter idea: lower finishes, then mux picks upper.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Two speculative uppers; mux on real carry.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Starter A5+3C style CSA aims for sum…",
                "Example teaching sum 0xA5+0x3C is…",
                "0xA5 + 0x3C equals…",
                "Hex A5+3C result is…",
            ][(i - 1) % 4],
            ["0xE1", "0xA5", "0x3C", "0xFF"],
            0,
            "165+60=225 → 0xE1.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Relative to pure ripple, CSA typically…",
                "Main CSA benefit vs RCA is…",
                "Why use carry-select?",
                "CSA reduces…",
            ][(i - 1) % 4],
            [
                "Shortens wait for upper bits once lower Cout arrives",
                "Removes all adders",
                "Uses zero multiplexers",
                "Only works for 1-bit widths",
            ],
            0,
            "Upper work overlaps; mux when carry ready.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Cost of CSA compared with a single RCA is…",
                "Area penalty of carry-select is…",
                "Extra hardware in CSA includes…",
                "What do you pay for speculation?",
            ][(i - 1) % 4],
            [
                "Roughly duplicate upper adder + muxes",
                "No extra gates",
                "Only a slower clock",
                "Removing the lower adder",
            ],
            0,
            "Dual paths plus select muxes.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Both speculative upper sums are computed before select resolves.",
                "If lower Cout=1, the mux chooses the Cin=1 upper result.",
                "CSA and CLA are identical circuits.",
                "Block size choice trades area vs delay in CSA designs.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "CSA ≠ CLA; block sizing matters.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Multi-level CSA cascades by…",
                "Larger widths often use…",
                "Hierarchical carry-select means…",
                "Beyond two blocks, architects…",
            ][(i - 1) % 4],
            [
                "Selecting among more blocks / nested select stages",
                "Abandoning muxes entirely always",
                "Using only software add",
                "Forbidding speculation",
            ],
            0,
            "Nested or multi-block select.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "If both speculative uppers were identical always…",
                "Useless speculation would mean…",
                "When is the dual-path mux wasted?",
                "Mux adds value only if…",
            ][(i - 1) % 4],
            [
                "Paths can differ — Cin changes upper sum/Cout",
                "Cin never affects upper bits",
                "Lower Cout is unused",
                "Area is free",
            ],
            0,
            "Cin hypothesis changes the upper result.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Delay sketch: lower ripple + mux vs full N-bit ripple…",
                "First-order CSA timing insight is…",
                "Critical path often becomes…",
                "CSA hopes the path is closer to…",
            ][(i - 1) % 4],
            [
                "max(lower delay, upper delay) + mux, not full N ripple",
                "Always slower than RCA",
                "Independent of block size",
                "Equal to memory latency",
            ],
            0,
            "Overlap upper with lower; pay mux.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Wrong mux select reproduces a wrong upper sum.",
                "CSA still needs correct lower Cout as select.",
                "Teaching CSA builds intuition before prefix adders.",
                "Carry-select removes the need for any carry at all.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Select still depends on real carry.",
            "hard",
        ),
    ]
    return bank("module39-carry-select-adder", "Carry-select adder", "csa", easy_b, med_b, hard_b)


# --- module40: Booth encode ---


def booth_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Radix-4 Booth recodes the multiplier into digits…",
                "Booth digits (radix-4) are from the set…",
                "Allowed radix-4 Booth digit values are…",
                "Recoding yields digits…",
            ][(i - 1) % 4],
            ["0, ±1, or ±2", "0 through 3 only", "Binary 0–15 nibbles", "Carry propagate bits"],
            0,
            "Signed recoding, not ±3.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Triplet 011 encodes to digit…",
                "Booth table: bits 011 map to…",
                "What digit does 011 produce?",
                "Standard radix-4 encoding of 011 is…",
            ][(i - 1) % 4],
            ["+2", "0", "−2", "+1"],
            0,
            "Standard radix-4 Booth table.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "8-bit Y yields how many radix-4 Booth digits?",
                "For n=8, number of radix-4 digits is…",
                "Each digit covers two bits, so 8-bit →…",
                "n/2 partial products for n=8 means…",
            ][(i - 1) % 4],
            ["4", "8", "2", "16"],
            0,
            "Each digit covers two multiplier bits.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "8-bit Y yields four radix-4 Booth digits (n/2 partial products).",
                "Booth aims to reduce the number of partial products.",
                "Digit ±2 means shift multiplicand left by one then add/sub.",
                "Booth digits are always unsigned 0..3 with no signs.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Signed digits 0,±1,±2.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Starter 0x0C×0x1A (12×26) product is…",
                "12 × 26 equals…",
                "Booth sum for 12×26 should match…",
                "What product should Booth give for 12 and 26?",
            ][(i - 1) % 4],
            ["312", "26", "12", "0x1A"],
            0,
            "Booth sum matches signed/unsigned product here.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Triplet 000 encodes to…",
                "Booth digit for 000 is…",
                "All-zero window means digit…",
                "000 → which digit?",
            ][(i - 1) % 4],
            ["0", "+1", "−1", "+2"],
            0,
            "No operation for that PP.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Triplet 111 encodes to…",
                "Booth digit for 111 is…",
                "111 → digit…",
                "What does 111 map to?",
            ][(i - 1) % 4],
            ["0", "+2", "−2", "+1"],
            0,
            "Adjacent 1s can cancel to 0 in radix-4 Booth.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Overlapping triplets examine yᵢ₊₁ yᵢ yᵢ₋₁ with y₋₁=0 initially.",
                "Digit −1 means subtract the multiplicand (aligned).",
                "Radix-4 Booth never uses overlapping bit windows.",
                "Correct recoding must match the mathematical product.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Overlapping windows are the method.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Triplet 010 encodes to…",
                "Booth: 010 → digit…",
                "What digit is 010?",
                "010 maps to…",
            ][(i - 1) % 4],
            ["+1", "0", "−1", "+2"],
            0,
            "Classic table: 010 → +1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Triplet 101 encodes to…",
                "Booth: 101 → digit…",
                "101 maps to…",
                "What is digit for 101?",
            ][(i - 1) % 4],
            ["−1", "0", "+2", "+1"],
            0,
            "101 → −1 in standard radix-4 Booth.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Why prefer Booth over naive array for some designs?",
                "Booth’s practical motivation is…",
                "Fewer PPs help because…",
                "Main Booth win is…",
            ][(i - 1) % 4],
            [
                "Fewer partial products → less reduction work",
                "It removes the multiplicand",
                "It forbids negative numbers",
                "It needs no shifters",
            ],
            0,
            "n/2 PPs vs n for binary.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Hard part is aligning signed digits (±1, ±2) with correct shifts.",
                "Verifying Booth against a known product catches encoding bugs.",
                "±3 is a standard radix-4 Booth digit.",
                "Sign extension of PP rows matters for signed multiply.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Digits are 0,±1,±2 only.",
            "hard",
        ),
    ]
    return bank("module40-booth-encode", "Booth encode", "booth", easy_b, med_b, hard_b)


# --- module41: Signed arithmetic ---


def signed_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "8-bit two’s complement signed range is…",
                "Signed width-8 spans…",
                "What range does 8-bit two’s complement cover?",
                "Pick the correct 8-bit signed range.",
            ][(i - 1) % 4],
            ["−128 … +127", "0 … 255", "−255 … +255", "−64 … +63"],
            0,
            "MSB is sign bit.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Flag V indicates…",
                "V means…",
                "Signed overflow flag is…",
                "Which flag tracks signed overflow?",
            ][(i - 1) % 4],
            ["Signed overflow", "Unsigned carry only", "Result is zero", "MSB is zero"],
            0,
            "Distinct from C.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "100+100 in 8-bit signed add wraps to…",
                "Signed 8-bit 100+100 yields…",
                "True sum 200 in 8-bit signed becomes…",
                "What happens for 100+100 at width 8 signed?",
            ][(i - 1) % 4],
            ["−56 with V=1", "+200 with V=0", "0 with Z=1", "+100 unchanged"],
            0,
            "True sum 200 out of signed range.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "200+100 can set C=1 while V=0.",
                "Unsigned carry ≠ signed overflow.",
                "Same bits can be read signed or unsigned differently.",
                "V is identical to C on every ADD.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "C and V answer different questions.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Two’s-complement negate of X is…",
                "How do you form −X?",
                "Negation algorithm is…",
                "−X equals…",
            ][(i - 1) % 4],
            ["~X + 1", "X << 1", "X & 0", "X XOR X"],
            0,
            "Invert and add one.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "8-bit pattern 0x80 as signed is…",
                "Signed reading of 10000000₂ is…",
                "What decimal is signed 0x80?",
                "MSB-only set at width 8 signed equals…",
            ][(i - 1) % 4],
            ["−128", "128", "−1", "0"],
            0,
            "Most-negative value.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "−1 as 8-bit two’s complement is…",
                "Signed −1 hex is…",
                "All-ones pattern signed means…",
                "0xFF signed 8-bit equals…",
            ][(i - 1) % 4],
            ["0xFF (−1)", "0x01", "0x80", "0x7F"],
            0,
            "All ones = −1.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Adding two positive numbers that yield MSB=1 often signals V.",
                "Sign-extending before a wider add preserves signed value.",
                "Unsigned 200 + 100 fits in 8 bits without wrap.",
                "Borrow/carry rules differ in meaning for signed vs unsigned views.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "200+100 = 300 needs wrap in 8 bits.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "−128 negated in 8-bit two’s complement…",
                "What is special about negating 0x80 at width 8?",
                "Most-negative negate problem is…",
                "−(−128) in 8 bits…",
            ][(i - 1) % 4],
            [
                "Overflows / stays 0x80 — no positive counterpart",
                "Becomes +128 cleanly",
                "Becomes 0",
                "Becomes 0x7F",
            ],
            0,
            "Asymmetric range: −128 has no +128.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Signed 127+1 at 8 bits gives…",
                "0x7F + 1 signed yields…",
                "Overflow of max positive is…",
                "What are Y and V for 127+1?",
            ][(i - 1) % 4],
            ["−128 with V=1", "128 with V=0", "0 with Z=1", "127 with V=0"],
            0,
            "Wraps to 0x80, signed overflow.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Comparing C vs V after ADD, best summary is…",
                "Pick the accurate C/V statement.",
                "Unsigned vs signed overflow flags…",
                "C and V differ because…",
            ][(i - 1) % 4],
            [
                "C tracks unsigned wrap; V tracks signed range break",
                "They are always equal",
                "Only Z matters",
                "V replaces the need for width",
            ],
            0,
            "Different interpretations of the same add.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Hand-checking one wrapping and one non-wrapping add cements C vs V.",
                "Sign extension of 0xF0 from 8→16 bits yields 0xFFF0.",
                "Zero-extending 0xF0 from 8→16 bits yields 0x00F0.",
                "Signed and unsigned addition use different XOR gates for the sum bits.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Sum bits identical; flags/interpretation differ.",
            "hard",
        ),
    ]
    return bank("module41-signed-arith", "Signed arithmetic", "signed", easy_b, med_b, hard_b)


# --- module42: RAM / ROM map ---


def memmap_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "In this lab, ROM mode means…",
                "ROM behavior for runtime writes is…",
                "How does ROM differ from RAM here?",
                "ROM mode rejects…",
            ][(i - 1) % 4],
            [
                "Runtime writes are rejected; init via readmemh load",
                "Reads are illegal",
                "Addresses are decimal only",
                "DEPTH must be 1",
            ],
            0,
            "ROM blocks runtime writes.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter read at address 0 returns…",
                "First byte of DE AD BE EF is…",
                "mem[0] after DEADBEF load is…",
                "Address 0 starter data is…",
            ][(i - 1) % 4],
            ["0xDE", "0xEF", "0x00", "0xAD"],
            0,
            "First byte of DE AD BE EF.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A 16-word memory needs how many address bits?",
                "log₂(16) address width is…",
                "DEPTH=16 ⇒ ADDR_W=…",
                "How wide is the address for 16 locations?",
            ][(i - 1) % 4],
            ["4", "8", "16", "2"],
            0,
            "log₂(16) = 4.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "RAM mode allows both read and write at runtime.",
                "Address width must cover DEPTH.",
                "ROM init often uses a hex image (readmemh-style).",
                "ROM and RAM use different address math for the same DEPTH.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Same map math; permission differs.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            f"A {2 ** (3 + (i % 3))}-word memory needs how many address bits?",
            [
                str(3 + (i % 3)),
                str(2 ** (3 + (i % 3))),
                str(8),
                str((3 + (i % 3)) * 2),
            ],
            0,
            "ADDR_W = log₂(DEPTH).",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Out-of-range address access should be…",
                "If addr ≥ DEPTH, a careful model…",
                "Bounds check on the map means…",
                "Illegal address handling is…",
            ][(i - 1) % 4],
            [
                "Detected / rejected rather than silently wrapping unchecked",
                "Always written as success",
                "Converted to opcode",
                "Ignored as a feature",
            ],
            0,
            "Teach map bounds.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Word vs byte addressing confusion causes…",
                "If CPU is byte-addressed but mem is word-addressed…",
                "Map bugs often come from…",
                "Address unit mismatch leads to…",
            ][(i - 1) % 4],
            [
                "Wrong location selection / misaligned views",
                "Faster clocks",
                "Automatic ECC",
                "No need for DEPTH",
            ],
            0,
            "Know the address granularity.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Writing in ROM mode should fail or be ignored by policy.",
                "Reading RAM and ROM both return stored data when legal.",
                "DEPTH and DATA width are independent parameters.",
                "readmemh is required for every RAM write in hardware.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Init image ≠ runtime store path.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Sparse map with base+offset decoding…",
                "Chip-select style maps use…",
                "Address decode for multiple slaves needs…",
                "A memory map integrator relies on…",
            ][(i - 1) % 4],
            [
                "Comparing high bits / ranges to select a device",
                "Only the LSB forever",
                "Gray code only",
                "Removing addresses",
            ],
            0,
            "Decode selects the target region.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Endianness when viewing multi-byte words affects…",
                "Byte order on a mapped word changes…",
                "0xDEADBEEF display depends on…",
                "Map dumps can look wrong because of…",
            ][(i - 1) % 4],
            [
                "Which byte appears at the low address",
                "The clock frequency",
                "Reset polarity only",
                "ALU opcode",
            ],
            0,
            "Endianness is a map/view concern.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Capacity in bits for DEPTH×WIDTH is…",
                "Total storage bits equal…",
                "Mem size formula is…",
                "DEPTH words × WIDTH bits =…",
            ][(i - 1) % 4],
            ["DEPTH × WIDTH", "DEPTH + WIDTH", "DEPTH only", "2^WIDTH"],
            0,
            "Product of depth and width.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Overlapping decode ranges cause bus conflicts / ambiguity.",
                "Hole in the map means some addresses hit no device.",
                "Teaching ROM vs RAM is about write permission and init path.",
                "Address bits below log₂(DEPTH) are never used in a dense array.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Low bits index; statement 3 inverted is false.",
            "hard",
        ),
    ]
    return bank("module42-mem-map", "RAM / ROM map", "memmap", easy_b, med_b, hard_b)


# --- module43: FIFO pointers ---


def fifo_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "FIFO means…",
                "Queue ordering in a FIFO is…",
                "First-In First-Out means…",
                "Unlike a stack, a FIFO…",
            ][(i - 1) % 4],
            [
                "First-In First-Out — oldest entry read next",
                "First-In Last-Out (stack)",
                "Random access like RAM",
                "Only a clock generator",
            ],
            0,
            "Order-preserving queue.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter push 0xA5 on empty depth-4 FIFO: count becomes…",
                "One push into empty FIFO yields count…",
                "After first push, occupancy is…",
                "Empty → push once ⇒ count…",
            ][(i - 1) % 4],
            ["1 (wr=1, rd=0)", "4 (full)", "0 (empty)", "2 always"],
            0,
            "One entry stored at slot 0.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Full is true when…",
                "FIFO full condition is…",
                "When are all slots occupied?",
                "count == DEPTH means…",
            ][(i - 1) % 4],
            ["count == DEPTH", "count == 0", "wr == 0 only", "rd == wr always"],
            0,
            "All slots occupied.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Pop while empty is blocked in this lab.",
                "Empty means count == 0.",
                "Push while full should be blocked / flagged.",
                "FIFO is random-access by address like RAM.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Queue discipline, not RAM addressing.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Write pointer advances on…",
                "Successful push updates…",
                "wr pointer increments when…",
                "Which event moves the write pointer?",
            ][(i - 1) % 4],
            ["Accepted push / write", "Every clock unconditionally", "Only on reset", "Only on pop"],
            0,
            "wr tracks next write slot.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Read pointer advances on…",
                "Successful pop updates…",
                "rd increments when…",
                "Which event moves the read pointer?",
            ][(i - 1) % 4],
            ["Accepted pop / read", "Every push", "Only when full", "Never"],
            0,
            "rd tracks oldest entry.",
            "medium",
        ),
        lambda i: mcq(
            "",
            f"Depth-{4 + (i % 4)} FIFO after {1 + (i % 3)} pushes from empty: count is…",
            [
                str(1 + (i % 3)),
                str(4 + (i % 4)),
                "0",
                str((1 + (i % 3)) * 2),
            ],
            0,
            "Count tracks occupancy.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Pointers wrap modulo DEPTH in a circular buffer FIFO.",
                "count can be derived from wr/rd with care for full vs empty.",
                "Underflow and overflow are both hazards to prevent.",
                "rd and wr are allowed to index beyond DEPTH without wrap.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Circular indexing uses modulo DEPTH.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Classic full vs empty ambiguity when wr==rd is solved by…",
                "Distinguishing full/empty with equal pointers needs…",
                "Extra count bit / MSB trick helps because…",
                "When pointers match, status might be…",
            ][(i - 1) % 4],
            [
                "Extra state (count or pointer MSB) to tell full from empty",
                "Ignoring full forever",
                "Using no memory",
                "Clearing the clock",
            ],
            0,
            "wr==rd alone is ambiguous.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Back-to-back push then pop on depth≥1 from empty ends with…",
                "Push A5 then pop once: FIFO is…",
                "After one push and matching pop…",
                "Net zero transactions leave…",
            ][(i - 1) % 4],
            ["Empty again (count 0)", "Full", "Count 2", "Stuck"],
            0,
            "Balanced push/pop restore empty.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "FWFT vs standard FIFO differs in…",
                "First-word fall-through affects…",
                "Data timing at the read port depends on…",
                "Which topic is FWFT about?",
            ][(i - 1) % 4],
            [
                "When the next data appears on dout relative to empty",
                "Gray coding only",
                "Byte enables only",
                "ALU opcodes",
            ],
            0,
            "Read latency / data validity style.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Sync FIFO uses one clock; async FIFO crosses clocks (later module).",
                "Occupancy histogram helps debug sticky full/empty bugs.",
                "Push without advancing wr corrupts the queue contract.",
                "DEPTH=1 FIFOs cannot exist.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Depth-1 is valid; pointer updates matter.",
            "hard",
        ),
    ]
    return bank("module43-fifo-lab", "FIFO pointers", "fifo", easy_b, med_b, hard_b)


# --- module44: Cache walk ---


def cache_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A cache address is commonly split into…",
                "Three-field cache decode is…",
                "Address fields are…",
                "Tag / index / offset means…",
            ][(i - 1) % 4],
            [
                "Tag, index (set), and offset (within line)",
                "Opcode and funct only",
                "Row and column of DRAM only",
                "Byte enable alone",
            ],
            0,
            "Three-field decode.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "A hit requires…",
                "Cache hit means…",
                "Valid + tag match yields…",
                "When is access a hit?",
            ][(i - 1) % 4],
            [
                "Valid set and stored tag equals address tag",
                "Only offset zero",
                "Empty cache",
                "Write-back always",
            ],
            0,
            "Valid plus tag match.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter addr 0x14 (2 index / 2 offset bits): tag, index, offset…",
                "0x14 with 2+2 low bits splits as…",
                "Binary 0001_01_00 fields are…",
                "For 0x14, (tag,index,offset) teaching answer is…",
            ][(i - 1) % 4],
            ["1, 1, 0", "0, 0, 0", "2, 1, 0", "1, 0, 4"],
            0,
            "0001 01 00 binary split.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Two addresses with the same index but different tags can conflict in direct-mapped cache.",
                "Offset selects the byte/word within a cache line.",
                "Index selects which set/line to check.",
                "Tag compare is unnecessary on a miss fill.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Tag still stored/compared; conflict misses thrash.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Direct-mapped means…",
                "One line per set describes…",
                "Associativity=1 is…",
                "Each index maps to how many lines in direct-mapped?",
            ][(i - 1) % 4],
            ["Exactly one line per index/set", "Fully associative only", "No tags", "Infinite ways"],
            0,
            "One candidate line per index.",
            "medium",
        ),
        lambda i: mcq(
            "",
            f"With {1 + (i % 3)} offset bits, line size in bytes (byte-addressed) is…",
            [
                str(2 ** (1 + (i % 3))),
                str(1 + (i % 3)),
                str(8),
                str(2 * (1 + (i % 3))),
            ],
            0,
            "2^offset_bits bytes per line.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A compulsory miss happens when…",
                "Cold miss means…",
                "First reference to a block causes…",
                "Compulsory misses occur because…",
            ][(i - 1) % 4],
            [
                "Line was never fetched before",
                "Cache is infinite",
                "Tags always match",
                "Offset is zero",
            ],
            0,
            "First touch / cold start.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Conflict misses arise when blocks map to the same set.",
                "Capacity misses occur when working set exceeds cache size.",
                "Write-through vs write-back changes when memory updates.",
                "Index bits are taken from the high end of the address only.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Index is mid-field; offset is low.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Set-associative caches reduce…",
                "More ways mainly help…",
                "2-way vs direct-mapped eases…",
                "Associativity fights…",
            ][(i - 1) % 4],
            ["Conflict misses", "Clock uncertainty", "ROM init", "UART framing"],
            0,
            "Multiple ways per set.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "LRU / replacement policy matters when…",
                "Choosing which way to evict is…",
                "On a miss to a full set you need…",
                "Victim selection is…",
            ][(i - 1) % 4],
            [
                "A set is full and a new line must enter",
                "Only on hits",
                "Only for ROM",
                "Never in hardware",
            ],
            0,
            "Replacement on capacity/conflict fill.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Dirty bit is used with…",
                "Write-back caches track…",
                "Why store dirty?",
                "Dirty means…",
            ][(i - 1) % 4],
            [
                "Write-back — line differs from memory",
                "Read-only ROMs",
                "Gray FIFO pointers",
                "Opcode decode",
            ],
            0,
            "Evict must write memory if dirty.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Walking an address bit-field by hand is the point of this lab.",
                "Same index + different tag ⇒ potential conflict in direct-mapped.",
                "Larger lines raise offset width and can improve spatial locality.",
                "Tag bits are never stored in the cache.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Tags are stored and compared.",
            "hard",
        ),
    ]
    return bank("module44-cache-walk", "Cache walk", "cache", easy_b, med_b, hard_b)


# --- module45: Dual-port RAM ---


def dpram_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Dual-port RAM provides…",
                "True dual-port means…",
                "Two ports on one array give…",
                "DPRAM offers…",
            ][(i - 1) % 4],
            [
                "Two independent addr/we/din ports on one array",
                "Two separate clock domains always",
                "Read-only access on both ports",
                "No address lines",
            ],
            0,
            "Shared memory, two ports.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter has ports on different addresses — that means…",
                "A=0, B=1 with no same-addr clash is…",
                "Independent addresses imply…",
                "Different port addresses ⇒…",
            ][(i - 1) % 4],
            [
                "Independent access (no collision)",
                "Automatic X on both dout",
                "Both ports must write",
                "Memory clears to zero",
            ],
            0,
            "A=0, B=1 in starter.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "write_first policy on W/R collision means read port sees…",
                "Read-new behavior returns…",
                "Write-first collision read yields…",
                "Under write_first, same-addr read gets…",
            ][(i - 1) % 4],
            ["New (written) data", "Always old data only", "Always X", "The write pointer"],
            0,
            "Read-new after write.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Same address, both reading (R/R) is OK in this lab.",
                "Collision policies matter when both ports touch one address with a write.",
                "Dual-port always implies two clock domains.",
                "Independent ports can read and write different addresses concurrently.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Simple dual/true dual may share a clock; async is separate.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "read_first (write-after-read) collision returns…",
                "Old-data policy means dout shows…",
                "read_first on W/R same addr yields…",
                "Opposite of write_first is…",
            ][(i - 1) % 4],
            ["Previous stored data", "Always the new din", "Always 0", "The address"],
            0,
            "Read-old behavior.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "W/W same address collision is…",
                "Two writes to one location in one cycle…",
                "Dangerous dual write means…",
                "Undefined / priority needed when…",
            ][(i - 1) % 4],
            [
                "Hazard — need priority or avoid",
                "Always safe like R/R",
                "Forced empty FIFO",
                "A cache miss only",
            ],
            0,
            "Two writers conflict.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Simple dual-port often means…",
                "One write port + one read port describes…",
                "SDP vs TDP: SDP typically…",
                "Many FPGA block RAMs offer…",
            ][(i - 1) % 4],
            [
                "1W1R rather than two fully symmetric R/W ports",
                "No addresses",
                "Only ROM",
                "Four write ports minimum",
            ],
            0,
            "SDP ≠ true dual R/W+R/W.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Documenting collision policy avoids sim vs hardware surprises.",
                "R/R same address is generally fine.",
                "Port A and Port B can use different widths in some DPRAM modes.",
                "Collision never occurs if addresses are equal.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Equal addresses are when collisions happen.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "no_change collision policy means…",
                "On conflict, no_change dout…",
                "What does no_change do?",
                "no_change read during write…",
            ][(i - 1) % 4],
            [
                "Read output holds prior dout (doesn’t update that cycle)",
                "Always X",
                "Always new din",
                "Clears memory",
            ],
            0,
            "Hold previous read data.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Why do CDC concerns appear with dual clocks on DPRAM?",
                "Async dual-clock BRAM needs care because…",
                "Two clocks on one array raise…",
                "Metastability / coherency issues when…",
            ][(i - 1) % 4],
            [
                "Write domain and read domain are asynchronous",
                "AND gates glow",
                "Tags disappear",
                "Gray code is illegal",
            ],
            0,
            "Cross-clock memory needs sync discipline.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Best lab check for collision literacy is…",
                "To verify write_first, you should…",
                "Hands-on DPRAM test…",
                "Prove policy by…",
            ][(i - 1) % 4],
            [
                "Same addr W+R and observe dout vs policy",
                "Only reading empty addresses",
                "Ignoring we",
                "Changing DEPTH randomly mid-cycle",
            ],
            0,
            "Force the hazard and watch dout.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Sim models may differ from device BRAM collision behavior if unconstrained.",
                "True dual-port can implement ping-pong and FIFO-like structures.",
                "Avoiding same-addr W/W is a common safe coding rule.",
                "Dual-port means byte enables are impossible.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Byte enables are orthogonal.",
            "hard",
        ),
    ]
    return bank("module45-dual-port-ram", "Dual-port RAM", "dpram", easy_b, med_b, hard_b)


# --- module46: Byte-enable memory ---


def byteen_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Byte-enable bits on write…",
                "BE mask purpose is…",
                "Partial store uses BE to…",
                "What do byte enables gate?",
            ][(i - 1) % 4],
            [
                "Gate which byte lanes update; others keep old data",
                "Always clear the full word to zero",
                "Select the CPU opcode",
                "Disable the clock",
            ],
            0,
            "Partial store mask.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter word0 DDCCBBAA with be=0001 patches byte0 to…",
                "BE=0001 updates which lane?",
                "Only LSB enable from din → word becomes…",
                "be=0001 on DDCCBBAA with din …55 yields…",
            ][(i - 1) % 4],
            ["0x55 (word becomes DDCCBB55)", "0xAA unchanged", "Full word 88776655", "All zeros"],
            0,
            "Only LSB lane from din.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "be=0011 stores…",
                "Mask 0011 means…",
                "Which lanes does be=0011 write?",
                "0011 byte enables update…",
            ][(i - 1) % 4],
            ["Low halfword (two bytes)", "MSB byte only", "No bytes", "All four words"],
            0,
            "Lanes 0 and 1.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "we=1 with be=0000 changes no byte lanes.",
                "Disabled lanes retain previous bytes.",
                "BE is a per-byte write mask.",
                "be=1111 clears the word to zero without din.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "1111 writes all lanes from din; does not auto-zero.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "be=1000 updates…",
                "MSB-only enable means…",
                "Which byte does 1000 touch?",
                "Lane 3 enable is…",
            ][(i - 1) % 4],
            ["The most-significant byte lane", "Only lane 0", "All lanes", "No lanes"],
            0,
            "One-hot high lane.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Sub-word store of a byte into a word memory needs…",
                "CPU sb/sh style ops rely on…",
                "Partial writes are implemented with…",
                "Without BE, byte store would…",
            ][(i - 1) % 4],
            [
                "Byte enables (or read-modify-write)",
                "Only full-word writes forever",
                "Gray pointers",
                "ALU V flag",
            ],
            0,
            "Mask lanes or RMW.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "For a 32-bit word, be width is typically…",
                "How many byte-enable bits for a 4-byte word?",
                "One enable per byte means width…",
                "32-bit data path uses how many BE bits?",
            ][(i - 1) % 4],
            ["4", "32", "8", "1"],
            0,
            "One bit per byte lane.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Endianness affects which BE bit maps to which address byte.",
                "we=0 should leave memory unchanged regardless of be.",
                "Merged BE across bursts can describe lane activity over time.",
                "BE=1100 always means little-endian halfword at LSB.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Lane mapping depends on endianness.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Word was 0xDDCCBBAA; be=0100, din byte=0x77 →…",
                "Update only lane 2 of DDCCBBAA with 77…",
                "After be=0100 patch, word is…",
                "Lane-2 write of 77 into DDCCBBAA yields…",
            ][(i - 1) % 4],
            ["0xDD77BBAA", "0x77CCBBAA", "0xDDCC77AA", "0xDDCCBB77"],
            0,
            "Lane 2 is the 0xCC position → DD77BBAA.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "ECC / parity complications with BE arise because…",
                "Partial writes and ECC often need…",
                "Why is BE+ECC tricky?",
                "Masked store with ECC may require…",
            ][(i - 1) % 4],
            [
                "Read-modify-write to recompute check bits",
                "No stores allowed",
                "Disabling clocks",
                "Removing din",
            ],
            0,
            "Check bits cover the whole word.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "be=1111 with we=1 means…",
                "Full-word store is…",
                "All lanes enabled ⇒…",
                "What does be all-ones do?",
            ][(i - 1) % 4],
            [
                "Entire word replaced by din",
                "No write",
                "Only byte0 writes",
                "Memory reset async",
            ],
            0,
            "All lanes take din.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Verifying unchanged lanes is as important as checking written ones.",
                "BE bugs often corrupt adjacent bytes silently.",
                "Teaching model: mask then merge with old word.",
                "Byte enables replace the need for addresses.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Address still selects the word.",
            "hard",
        ),
    ]
    return bank("module46-byte-enable-mem", "Byte-enable memory", "byteen", easy_b, med_b, hard_b)


# --- module47: Async FIFO (Gray) ---


def asyncfifo_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Why use Gray-coded pointers for CDC in an async FIFO?",
                "Gray pointers help because…",
                "Safer CDC counting uses Gray since…",
                "Multi-bit binary CDC is risky; Gray…",
            ][(i - 1) % 4],
            [
                "Only one bit changes per count—safer to synchronize",
                "Gray is faster than binary always",
                "Gray removes the need for memory",
                "Binary pointers are illegal in Verilog",
            ],
            0,
            "Avoid multi-bit CDC glitches.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter FIFO state is…",
                "Cold async FIFO begins…",
                "Initial empty flag is…",
                "At reset, typical async FIFO is…",
            ][(i - 1) % 4],
            ["empty=1 (no data to read)", "full=1", "Both full and empty", "Depth zero"],
            0,
            "Cold empty FIFO.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Remote Gray pointers typically cross domains through…",
                "CDC path for pointers uses…",
                "How are Gray pointers synchronized?",
                "Metastability hardening for pointers is…",
            ][(i - 1) % 4],
            [
                "Two flip-flop synchronizers (2FF)",
                "A single XOR gate",
                "Direct combinational wire",
                "No synchronization",
            ],
            0,
            "Metastability hardening.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Write and read ports use independent clocks (wclk and rclk).",
                "Async FIFO definition includes two clock domains.",
                "Gray coding makes multi-bit sync safer.",
                "Async FIFO needs no memory array.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Still a dual-clock memory + pointers.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Full is detected in the write domain using…",
                "Comparing wr ptr to synced rd ptr yields…",
                "Write-side full flag comes from…",
                "To assert full you compare…",
            ][(i - 1) % 4],
            [
                "Local write pointer vs synchronized read pointer",
                "Only rclk edges",
                "Opcode decode",
                "Byte enables",
            ],
            0,
            "Synced remote pointer + local pointer.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Empty is detected in the read domain using…",
                "Read-side empty compares…",
                "empty flag uses…",
                "To assert empty you compare…",
            ][(i - 1) % 4],
            [
                "Local read pointer vs synchronized write pointer",
                "Only wclk",
                "Cache tags",
                "ALU Y",
            ],
            0,
            "Symmetric to full, other domain.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Binary to Gray conversion is typically…",
                "gray = binary ^ (binary >> 1) is…",
                "How encode pointer for CDC?",
                "Classic bin→Gray formula is…",
            ][(i - 1) % 4],
            [
                "XOR of bit with its neighbor (shift-xor)",
                "Add one only",
                "Multiply by 3",
                "OR-reduction only",
            ],
            0,
            "Standard Gray encode.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Synchronizer latency makes full/empty slightly pessimistic — that’s OK for safety.",
                "Never sample multi-bit binary counts with a single 2FF without Gray/handshake.",
                "wclk and rclk may be unrelated frequencies.",
                "Gray pointers eliminate the need for 2FF synchronizers.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Still synchronize Gray bits.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Pointer width often uses an extra MSB so that…",
                "Extra pointer bit helps…",
                "Why DEPTH and pointer width relationship…",
                "Full/empty distinction with wrapping pointers needs…",
            ][(i - 1) % 4],
            [
                "Full vs empty can be distinguished after wrap",
                "Faster AND gates",
                "Removing Gray code",
                "Byte enables",
            ],
            0,
            "Classic n+1 pointer style.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Which is unsafe for async FIFO CDC?",
                "Bad practice is…",
                "Avoid which pointer transfer?",
                "Hazardous CDC choice…",
            ][(i - 1) % 4],
            [
                "Sending raw multi-bit binary pointers through one FF",
                "Gray + 2FF per bit",
                "Comparing in the correct domain",
                "Asserting reset",
            ],
            0,
            "Multi-bit binary tear / skew.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Memory write port is clocked by…",
                "Read port array timing follows…",
                "Dual-clock FIFO RAM ports use…",
                "wclk vs rclk for the array…",
            ][(i - 1) % 4],
            [
                "wclk for writes, rclk for reads",
                "Only wclk for both always",
                "No clocks",
                "Scan clock only",
            ],
            0,
            "Each port in its domain.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Pessimistic full can leave a slot unused — safer than overflow.",
                "Pessimistic empty can delay a read — safer than underflow.",
                "Async FIFO is a canonical CDC pattern.",
                "Gray coding alone fixes metastability without synchronizers.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Gray reduces multi-bit risk; 2FF still needed.",
            "hard",
        ),
    ]
    return bank("module47-async-fifo", "Async FIFO (Gray)", "asyncfifo", easy_b, med_b, hard_b)


# --- module48: Handshake (valid/ready) ---


def handshake_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A beat transfers when…",
                "When does fire happen?",
                "Transfer occurs if…",
                "valid/ready handshake completes when…",
            ][(i - 1) % 4],
            [
                "valid and ready are both 1 in the same cycle",
                "only valid is 1",
                "only ready is 1",
                "the clock stops",
            ],
            0,
            "fire = valid && ready.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter preset on cycle 0…",
                "Initial teaching beat shows…",
                "Preset valid=ready=1 with data 0xA5 means…",
                "Cycle-0 starter transfer is…",
            ][(i - 1) % 4],
            [
                "valid=ready=1, data 0xA5 — one transfer",
                "no signals asserted",
                "ready only, no valid",
                "three back-to-back beats",
            ],
            0,
            "Both assert preset.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "If valid=1 but ready=0, a well-behaved source usually…",
                "Backpressure rule for the source is…",
                "When sink is not ready…",
                "Stable data while waiting means…",
            ][(i - 1) % 4],
            [
                "holds valid and data stable until ready rises",
                "drops valid immediately every cycle",
                "loses the beat forever",
                "drives high-Z on the bus",
            ],
            0,
            "Backpressure stability rule.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Transfer fire is written as fire = valid && ready.",
                "ready low means the sink applies backpressure.",
                "valid means the source offers a beat.",
                "A transfer needs only ready without valid.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Both must be high.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Bubble cycle means…",
                "No transfer this cycle when…",
                "Idle beat on the interface is…",
                "When fire=0…",
            ][(i - 1) % 4],
            [
                "No beat — valid or ready (or both) deasserted",
                "Always a transfer",
                "Reset only",
                "Memory full always",
            ],
            0,
            "Not every cycle transfers.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "AXI-stream style ready may…",
                "Combinational ready paths risk…",
                "Registered ready helps…",
                "Timing of ready relative to valid matters because…",
            ][(i - 1) % 4],
            [
                "Depend on valid (with care) or be registered — know the rule set",
                "Ignore valid forever",
                "Stop the clock",
                "Replace data",
            ],
            0,
            "Protocol variants constrain ready timing.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Skid buffer / elasticity is used to…",
                "Decoupling valid/ready timing often needs…",
                "Why insert a skid stage?",
                "Pipeline handshake breaks cycles via…",
            ][(i - 1) % 4],
            [
                "Break ready combinational loops / absorb one beat",
                "Remove all data",
                "Force full always",
                "Disable valid",
            ],
            0,
            "Common ready/valid plumbing.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Changing data while valid=1 and ready=0 violates common stability rules.",
                "Sink can lower ready to stall the stream.",
                "Source can lower valid when it has no data.",
                "fire can be 1 when valid=0.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "fire requires both.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Registered-output source that must not drop a beat under backpressure…",
                "Holding pattern under ready=0 requires…",
                "If you already asserted valid, you typically…",
                "Correct stall behavior is…",
            ][(i - 1) % 4],
            [
                "Keep valid/data until fire",
                "Toggle data each cycle anyway",
                "Clear valid immediately always",
                "Ignore ready",
            ],
            0,
            "Hold until accepted.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Throughput of a perfect 1-beat/cycle stream needs…",
                "Sustained full rate requires…",
                "Max throughput when…",
                "Bubbles reduce rate because…",
            ][(i - 1) % 4],
            [
                "valid and ready both stay high every cycle",
                "valid only half the time always",
                "ready always 0",
                "No clock",
            ],
            0,
            "fire each cycle.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Connecting two modules with opposite ready/valid polarity mistakes…",
                "Interface mismatch often shows up as…",
                "Deadlock can occur if…",
                "Classic handshake bug is…",
            ][(i - 1) % 4],
            [
                "No fires / deadlock or lost beats",
                "Faster addition",
                "Automatic Gray coding",
                "Bigger caches",
            ],
            0,
            "Both sides must speak the same protocol.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Counting fires in simulation is a good throughput check.",
                "valid/ready is the backbone of many streaming IP interfaces.",
                "Backpressure propagates upstream when ready falls.",
                "Handshake replaces the need for clocks.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Still synchronous to a clock usually.",
            "hard",
        ),
    ]
    return bank(
        "module48-handshake",
        "Handshake (valid/ready)",
        "handshake",
        easy_b,
        med_b,
        hard_b,
    )


# --- module49: Block-diagram integrator ---


def blkdiag_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A legal wire in this lab goes…",
                "Connection rule is…",
                "Ports connect…",
                "Valid edge direction is…",
            ][(i - 1) % 4],
            [
                "from an output to an input of the same type",
                "from any input to any input",
                "only between identical block titles",
                "without types ever",
            ],
            0,
            "out → in, matching addr/data/ctrl/instr.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter preset already wires…",
                "Initial diagram includes…",
                "What is pre-connected?",
                "Preset datapath covers…",
            ][(i - 1) % 4],
            [
                "ALU + RegFile datapath (CPU control to ALU/RF)",
                "CPU ↔ Memory completely",
                "Only the system bus",
                "Nothing — blank canvas",
            ],
            0,
            "Four CPU↔Memory links still missing.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "To finish the starter you must add CPU↔Memory links for…",
                "Missing fetch/load-store wires are…",
                "Complete the map with…",
                "CPU–Memory needs…",
            ][(i - 1) % 4],
            [
                "addr, wdata, rdata, and instr",
                "only the clock",
                "Gray pointers",
                "valid and ready only",
            ],
            0,
            "Fetch and load/store paths.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Connecting an addr port to a data port is rejected in this teaching model.",
                "Types must match on a legal wire.",
                "Outputs drive inputs, not the reverse.",
                "Any port may connect to any other port freely.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Typed out→in only.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "instr path is typically…",
                "Fetch uses which link?",
                "Instruction memory read returns…",
                "CPU←Memory instruction side is…",
            ][(i - 1) % 4],
            [
                "Memory → CPU instruction/data-for-fetch",
                "Only ALU→RegFile",
                "Reset only",
                "Baud rate",
            ],
            0,
            "Fetch path.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "wdata vs rdata direction…",
                "Store data flows…",
                "Load data flows…",
                "Which way does wdata go?",
            ][(i - 1) % 4],
            [
                "wdata: CPU→Mem; rdata: Mem→CPU",
                "Both always CPU→Mem",
                "Both always Mem→CPU",
                "Neither connects",
            ],
            0,
            "Write vs read data directions.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "addr on a memory interface is usually…",
                "Who drives the address for a CPU load/store?",
                "Address port direction in the lab model…",
                "addr wire goes…",
            ][(i - 1) % 4],
            ["CPU output → Memory input", "Memory → CPU always", "Floating", "Only Gray"],
            0,
            "CPU issues addresses.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Integration diagrams make dataflow and control ownership visible.",
                "Type mismatches catch many student wiring errors early.",
                "Block diagrams replace the need to understand protocols.",
                "Leaving rdata unwired breaks loads.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Diagrams teach structure; protocols still matter.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "A dangling required input means…",
                "Unconnected mandatory port implies…",
                "Incomplete integrator solution has…",
                "Checker fails when…",
            ][(i - 1) % 4],
            [
                "The design is incomplete — that port needs a driver",
                "Automatic success",
                "Faster timing always",
                "ROM mode",
            ],
            0,
            "Every required input needs a source.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Fan-out of one output to multiple inputs is…",
                "Driving two sinks from one out…",
                "When is multi-sink wiring OK?",
                "One output may feed…",
            ][(i - 1) % 4],
            [
                "Often OK if types match and protocol allows broadcast",
                "Never allowed in any HDL",
                "Only for clocks in this lab’s typed model without thinking",
                "Only for Gray pointers",
            ],
            0,
            "Broadcast can be legal; watch protocols.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Two outputs driving one input is…",
                "Contended drivers mean…",
                "Illegal multi-driver case is…",
                "What happens with two outs → one in?",
            ][(i - 1) % 4],
            [
                "Conflict — not legal in this teaching model",
                "Required for ROM",
                "Same as fan-out",
                "Always Gray-coded",
            ],
            0,
            "Single driver per input.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "System integration stitches ALU, RF, mem, and control into one story.",
                "Matching port types is necessary but not always sufficient for correct protocols.",
                "The starter’s remaining work is specifically the CPU↔Memory bundle.",
                "Block-diagram literacy removes the need for RTL forever.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Still need RTL/courses beyond the lab.",
            "hard",
        ),
    ]
    return bank(
        "module49-block-diagram",
        "Block-diagram integrator",
        "blkdiag",
        easy_b,
        med_b,
        hard_b,
    )


def build_banks() -> list[dict]:
    return [
        rca_bank(),
        cla_bank(),
        arrmult_bank(),
        alu_bank(),
        csa_bank(),
        booth_bank(),
        signed_bank(),
        memmap_bank(),
        fifo_bank(),
        cache_bank(),
        dpram_bank(),
        byteen_bank(),
        asyncfifo_bank(),
        handshake_bank(),
        blkdiag_bank(),
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for bank_data in build_banks():
        path = OUT / f"{bank_data['module']}.json"
        path.write_text(json.dumps(bank_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        counts: dict[str, int] = {}
        for it in bank_data["items"]:
            counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
            assert "(v" not in it["prompt"], it["prompt"]
            assert "variant " not in it["prompt"].lower(), it["prompt"]
        assert counts.get("easy") == TARGET and counts.get("medium") == TARGET and counts.get("hard") == TARGET
        assert len(bank_data["items"]) == 3 * TARGET
        print(path.name, counts, "total", len(bank_data["items"]))


if __name__ == "__main__":
    main()
