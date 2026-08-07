"""Challenge banks for learn_digital modules 02–10: 30×3 difficulties each.

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


def _pick(i: int, options: list[str]) -> str:
    return options[(i - 1) % len(options)]


# ---------------------------------------------------------------------------
# module02 — Two's complement
# ---------------------------------------------------------------------------

def twos_bank() -> dict:
    widths = [4, 5, 6, 7, 8, 16]

    def easy_msb(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "In two’s complement, the MSB is best described as the…",
                "What role does the top bit play in two’s complement?",
                "Two’s-complement encoding treats the MSB as the…",
                "At a fixed width, the most significant bit in two’s complement is the…",
            ]),
            ["Carry bit only", "Sign bit", "Always zero", "Clock enable"],
            1,
            "The MSB is the sign bit in two’s complement.",
            "easy",
        )

    def easy_negate(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "The usual way to negate a two’s-complement value is…",
                "How do you form −X from X in two’s complement?",
                "Standard two’s-complement negation is…",
                "To flip the sign of a two’s-complement number…",
            ]),
            ["Shift left once", "Invert all bits, then add one", "Clear the MSB only", "XOR with zero"],
            1,
            "Invert every bit, then add one.",
            "easy",
        )

    def easy_allones(i: int) -> dict:
        return tf(
            "",
            _pick(i, [
                "All-ones at a fixed width is −1 in two’s complement.",
                "The pattern of all 1-bits means −1 in two’s complement.",
                "Two’s-complement −1 is represented by every bit set.",
                "Unsigned all-ones and signed −1 share the same bit pattern at a fixed width.",
            ]),
            True,
            "All ones is the canonical −1 pattern.",
            "easy",
        )

    def easy_min(i: int) -> dict:
        w = widths[(i - 1) % len(widths)]
        return mcq(
            "",
            f"At width {w}, the two’s-complement minimum is…",
            [str(-(2 ** w - 1)), str(-(2 ** (w - 1))), str(-(2 ** (w - 1) - 1)), "0"],
            1,
            f"{w}-bit two’s complement ranges from −{2 ** (w - 1)} to +{2 ** (w - 1) - 1}.",
            "easy",
        )

    def med_max(i: int) -> dict:
        w = widths[(i - 1) % len(widths)]
        return mcq(
            "",
            f"At width {w}, the two’s-complement maximum is…",
            [str(2 ** (w - 1)), str(2 ** (w - 1) - 1), str(2 ** w - 1), str(2 ** w)],
            1,
            f"Max is 2^{w - 1} − 1 = {2 ** (w - 1) - 1}.",
            "medium",
        )

    def med_sign_only(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Width-8 pattern with only the MSB set means…",
                "Eight-bit 0x80 as two’s complement equals…",
                "What signed value is 10000000₂ at width 8?",
                "Only the sign bit set in 8-bit two’s complement is…",
            ]),
            ["−1", "−128", "128", "0"],
            1,
            "Sign bit alone is the asymmetric minimum (−128).",
            "medium",
        )

    def med_neg_val(i: int) -> dict:
        v = 3 + (i % 5)
        return mcq(
            "",
            f"Negate +{v} in 8-bit two’s complement. You should get…",
            [f"+{v}", f"−{v}", "−128", "0"],
            1,
            f"Invert + 1 maps +{v} to −{v}.",
            "medium",
        )

    def med_asym(i: int) -> dict:
        prompts = [
            ("Two’s-complement range is asymmetric: one more negative value than positive.", True),
            ("At width 8 you can represent −128 but not +128.", True),
            ("The most-negative pattern has no positive counterpart of equal magnitude.", True),
            ("Eight-bit two’s complement max and min have equal absolute values.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Min is −2^(w−1); max is 2^(w−1)−1 — not symmetric.", "medium")

    def hard_adder(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Why can ordinary binary adders still add two’s-complement numbers?",
                "Two’s complement is popular in hardware mainly because…",
                "Addition of signed two’s-complement values uses…",
                "Pick the best reason two’s complement fits ALU adders.",
            ]),
            [
                "It needs a separate signed adder always",
                "Same adder hardware works; wrap interprets signed results",
                "MSB must be stripped before every add",
                "Only subtraction works",
            ],
            1,
            "Ordinary modular add works; interpretation is signed.",
            "hard",
        )

    def hard_sext(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Sign-extending 0b1111 (4-bit, −1) to 8 bits yields…",
                "Widen signed 4-bit all-ones to 8 bits. Hex is…",
                "Two’s-complement sign extension of 1111₂ → 8 bits is…",
                "After signed widen 4→8 from −1 nibble, the byte is…",
            ]),
            ["0x0F", "0xFF", "0xF0", "0x00"],
            1,
            "Negative values fill 1s when sign-extending.",
            "hard",
        )

    def hard_type(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Treating an 8-bit signed wire as unsigned is a pitfall because…",
                "Reading signed 0xFF as unsigned gives…",
                "Same bits, different type: signed −1 vs unsigned is…",
                "Misreading the MSB as magnitude (unsigned) on a negative value…",
            ]),
            [
                "Bits change automatically",
                "Changes the numeric meaning (e.g. −1 → 255)",
                "Never matters in RTL",
                "Only affects clocks",
            ],
            1,
            "Type/signedness changes interpretation of the same pattern.",
            "hard",
        )

    def hard_negmin(i: int) -> dict:
        prompts = [
            ("Negating the most-negative value (−128 at width 8) overflows / wraps.", True),
            ("At width 8, −(−128) cannot be represented as +128.", True),
            ("Invert+1 on 0x80 at width 8 lands back on 0x80.", True),
            ("Every two’s-complement value has a unique positive negation at the same width.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "The asymmetric min has no positive twin; negate wraps.", "hard")

    items = (
        pad("easy", "twos", [easy_msb, easy_negate, easy_allones, easy_min])
        + pad("medium", "twos", [med_max, med_sign_only, med_neg_val, med_asym])
        + pad("hard", "twos", [hard_adder, hard_sext, hard_type, hard_negmin])
    )
    return {"module": "module02-twos-complement", "title": "Two's complement", "items": items}


# ---------------------------------------------------------------------------
# module03 — Overflow / wrap
# ---------------------------------------------------------------------------

def overflow_bank() -> dict:
    wraps = [
        (4, 14, 3, 1),
        (4, 15, 1, 0),
        (4, 12, 5, 1),
        (5, 30, 3, 1),
        (8, 250, 10, 4),
        (8, 200, 100, 44),
    ]

    def easy_wrap(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "At width 4, unsigned 14+3 stores which wrapped result?",
                "Four-bit unsigned 14 + 3 wraps to…",
                "What does 14+3 become modulo 16?",
                "Unsigned wrap of 14+3 in 4 bits leaves…",
            ]),
            ["17", "1", "15", "0"],
            1,
            "17 mod 16 = 1.",
            "easy",
        )

    def easy_carry(i: int) -> dict:
        prompts = [
            ("Carry flag is always the same as signed overflow.", False),
            ("Unsigned carry and signed overflow are identical flags.", False),
            ("If carry is set, signed overflow must also be set.", False),
            ("Carry and signed overflow answer different questions.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Carry tracks unsigned out-of-range; overflow tracks signed.", "easy")

    def easy_sat(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Saturation versus wrap means…",
                "How does saturation differ from modular wrap?",
                "Clamping to min/max instead of modulo is…",
                "Pick the correct contrast of sat vs wrap.",
            ]),
            [
                "They are identical behaviors",
                "Saturation clamps to min/max; wrap uses modular bits",
                "Wrap only happens in floating point",
                "Saturation ignores width",
            ],
            1,
            "Sat clamps; ordinary fixed-width add usually wraps.",
            "easy",
        )

    def easy_counter(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Free-running counters often rely on…",
                "Why do many hardware counters happily wrap?",
                "Counting modulo 2^w on purpose is…",
                "Intentional wrap at full scale is common for…",
            ]),
            ["Never wrapping", "Intentional wrap at the width", "Floating-point add", "Removing the MSB"],
            1,
            "Counters commonly count modulo 2^w.",
            "easy",
        )

    def med_wrap(i: int) -> dict:
        w, a, b, r = wraps[(i - 1) % len(wraps)]
        return mcq(
            "",
            f"At width {w}, unsigned {a}+{b} wraps to…",
            [str(a + b), str(r), str(2 ** w - 1), "0"],
            1,
            f"{a}+{b}={a + b}; mod {2 ** w} → {r}.",
            "medium",
        )

    def med_signed(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "At width 4, signed 7+1 overflows to which pattern meaning?",
                "Four-bit signed 0111 + 0001 yields…",
                "Signed overflow example: 7+1 at width 4 becomes…",
                "What signed result follows 7+1 wrapping in 4-bit two’s complement?",
            ]),
            ["+8", "−8", "0", "+7"],
            1,
            "8 is out of range; pattern 1000 means −8.",
            "medium",
        )

    def med_flags(i: int) -> dict:
        prompts = [
            ("A bit pattern can look fine as unsigned while the signed meaning overflowed.", True),
            ("Signed overflow can occur even when the stored bits are a valid unsigned result.", True),
            ("Checking only the carry flag proves there was no signed overflow.", False),
            ("Unlimited decimal mental math can hide fixed-width wrap.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Signed overflow ≠ carry; width bounds the stored result.", "medium")

    def med_default(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Most simple RTL adders by default…",
                "Without extra sat logic, a fixed-width adder typically…",
                "Ordinary + in hardware at width w usually…",
                "If you do not build clamp logic, overflow tends to…",
            ]),
            ["Saturate to max", "Wrap modulo 2^w", "Grow unlimited bits", "Trap to software always"],
            1,
            "Default is modular wrap unless you build saturation.",
            "medium",
        )

    def hard_detect(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Signed overflow for add is often detected when…",
                "A classic signed-overflow rule for A+B looks at…",
                "Same-sign operands producing opposite-sign result means…",
                "Which condition indicates signed add overflow?",
            ]),
            [
                "Carry into MSB equals carry out of MSB (no overflow)",
                "Carry into MSB differs from carry out of MSB",
                "Any carry out of LSB",
                "Result equals zero",
            ],
            1,
            "XOR of carry-in and carry-out of the MSB flags signed overflow.",
            "hard",
        )

    def hard_borrow(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Unsigned wrap of 0 − 1 at width 8 stores…",
                "Eight-bit unsigned decrement past zero yields…",
                "What is unsigned 0x00 − 1 at width 8?",
                "Borrow wrap: 0−1 in 8-bit unsigned is…",
            ]),
            ["−1", "0xFF (255)", "0x80", "0x01"],
            1,
            "Modular: −1 ≡ 255 mod 256.",
            "hard",
        )

    def hard_policy(i: int) -> dict:
        prompts = [
            ("Waveforms show wrapped bits, not the unlimited mathematical sum.", True),
            ("Saturation and wrap are interchangeable terms in RTL.", False),
            ("You must know width when verifying an adder result.", True),
            ("Free-running timers often depend on intentional wrap.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Sat ≠ wrap; stored bits are modulo the width.", "hard")

    def hard_mix(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Mixing sat and wrap policies across DSP blocks risks…",
                "Why document overflow policy (sat vs wrap)?",
                "Different blocks using sat vs wrap without agreement causes…",
                "Pick the best reason overflow policy matters.",
            ]),
            [
                "Faster synthesis always",
                "Silent numeric disagreement / hard-to-find bugs",
                "Removes the need for width",
                "Only affects ASCII dumps",
            ],
            1,
            "Disagreeing overflow policies corrupt multi-block datapaths.",
            "hard",
        )

    items = (
        pad("easy", "overflow", [easy_wrap, easy_carry, easy_sat, easy_counter])
        + pad("medium", "overflow", [med_wrap, med_signed, med_flags, med_default])
        + pad("hard", "overflow", [hard_detect, hard_borrow, hard_policy, hard_mix])
    )
    return {"module": "module03-overflow-wrap", "title": "Overflow / wrap", "items": items}


# ---------------------------------------------------------------------------
# module04 — ASCII / hex
# ---------------------------------------------------------------------------

def ascii_bank() -> dict:
    letters = [("A", 0x41), ("B", 0x42), ("0", 0x30), ("9", 0x39), ("a", 0x61), ("z", 0x7A)]

    def easy_space(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Printable ASCII typically starts at which hex value (space)?",
                "The ASCII space character is…",
                "Usual start of printable ASCII (space) is hex…",
                "Which byte is the space glyph in ASCII?",
            ]),
            ["0x00", "0x0A", "0x20", "0x7F"],
            2,
            "Space is 0x20.",
            "easy",
        )

    def easy_lf(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Newline (LF) is which byte?",
                "ASCII line feed (LF) equals…",
                "Unix-style newline byte is…",
                "Which code is LF?",
            ]),
            ["0x0D only", "0x0A", "0x20", "0xFF"],
            1,
            "LF is 0x0A (CR is 0x0D).",
            "easy",
        )

    def easy_nul(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "A C string terminator is…",
                "NUL that ends a C string is…",
                "Which byte terminates a classic C string?",
                "C strings end with…",
            ]),
            ["0x20", "0x0A", "0x00", "0xFF"],
            2,
            "NUL (0x00) terminates a C string.",
            "easy",
        )

    def easy_dot(i: int) -> dict:
        prompts = [
            ("Hex dumps often show non-printable bytes as a dot in the ASCII column.", True),
            ("Non-printable bytes in a dump side panel are commonly shown as '.'", True),
            ("Dots keep dump columns aligned when a glyph is unavailable.", True),
            ("Every byte 0x00–0xFF has a unique printable ASCII glyph.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Dots stand in for non-printables so columns stay aligned.", "easy")

    def med_letter(i: int) -> dict:
        ch, code = letters[(i - 1) % len(letters)]
        return mcq(
            "",
            f"ASCII '{ch}' is which hex byte?",
            [f"0x{code - 1:02X}", f"0x{code:02X}", f"0x{code + 1:02X}", "0xFF"],
            1,
            f"'{ch}' = 0x{code:02X} ({code}).",
            "medium",
        )

    def med_cr(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Carriage return (CR) is which byte?",
                "ASCII CR equals…",
                "Classic Mac/old line ending CR is…",
                "Which hex is CR (not LF)?",
            ]),
            ["0x0A", "0x0D", "0x20", "0x00"],
            1,
            "CR is 0x0D.",
            "medium",
        )

    def med_del(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "ASCII DEL (delete) is commonly…",
                "The last 7-bit ASCII control often cited is…",
                "0x7F in ASCII is…",
                "Which byte is DEL?",
            ]),
            ["0x20", "0x7F", "0xFF", "0x01"],
            1,
            "DEL is 0x7F.",
            "medium",
        )

    def med_views(i: int) -> dict:
        prompts = [
            ("Hex on the left and glyphs on the right are two views of the same bytes.", True),
            ("A dump’s ASCII column is independent of the hex bytes shown.", False),
            ("Bytes below 0x20 are typically control codes, not printable glyphs.", True),
            ("0x41 and 'A' name the same byte value.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Dump columns are dual views; controls are not printable.", "medium")

    def hard_digit(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Difference between ASCII '0' and integer 0 is…",
                "'0' as a character byte versus numeric zero…",
                "Digit glyph '5' is not the integer 5 because…",
                "Pick the correct relation of digit characters to values.",
            ]),
            [
                "They are identical bytes",
                "Digit characters are 0x30–0x39, not 0–9 numeric",
                "Digits start at 0x00",
                "Only UTF-16 matters",
            ],
            1,
            "ASCII '0' is 0x30; numeric 0 is 0x00.",
            "hard",
        )

    def hard_high(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Bytes 0x80–0xFF in a classic 7-bit ASCII dump…",
                "How should an ASCII-centric dump treat high bytes?",
                "Values above 0x7F are…",
                "Outside 7-bit ASCII, high bytes typically…",
            ]),
            [
                "Always printable Latin letters",
                "Not standard ASCII printables (often shown as dots)",
                "Equal to space",
                "Terminate C strings",
            ],
            1,
            "7-bit ASCII printables stop at 0x7E; high bytes need another encoding.",
            "hard",
        )

    def hard_lines(i: int) -> dict:
        prompts = [
            ("CRLF line endings use bytes 0x0D 0x0A in that order.", True),
            ("LF alone is never used as a newline on any system.", False),
            ("Reading a ROM dump requires mapping hex ↔ characters carefully.", True),
            ("NUL inside a C string shortens the visible string at that point.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "CRLF is 0D 0A; LF-only also exists; NUL cuts C strings.", "hard")

    def hard_offset(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Offset columns in hex dumps usually count…",
                "The leftmost address in a dump increments by…",
                "If each row shows 16 bytes, the next row offset adds…",
                "Dump addresses refer to…",
            ]),
            [
                "Only printable glyphs",
                "Byte positions in the buffer / memory",
                "Word counts exclusively",
                "Clock cycles",
            ],
            1,
            "Offsets index bytes (often hex), not glyph counts.",
            "hard",
        )

    items = (
        pad("easy", "ascii", [easy_space, easy_lf, easy_nul, easy_dot])
        + pad("medium", "ascii", [med_letter, med_cr, med_del, med_views])
        + pad("hard", "ascii", [hard_digit, hard_high, hard_lines, hard_offset])
    )
    return {"module": "module04-ascii-hex", "title": "ASCII / hex", "items": items}


# ---------------------------------------------------------------------------
# module05 — Gray code
# ---------------------------------------------------------------------------

def gray_bank() -> dict:
    bin_gray = [
        (0b0000, 0b0000),
        (0b0001, 0b0001),
        (0b0010, 0b0011),
        (0b0011, 0b0010),
        (0b0100, 0b0110),
        (0b0101, 0b0111),
        (0b0110, 0b0101),
        (0b0111, 0b0100),
    ]

    def easy_formula(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Binary → Gray is commonly computed as…",
                "A standard binary-to-Gray formula is…",
                "How do you convert binary B to reflected Gray?",
                "Gray from binary typically uses…",
            ]),
            ["B & (B >> 1)", "B ^ (B >> 1)", "B + (B >> 1)", "B << 1"],
            1,
            "Gray = B XOR (B >> 1).",
            "easy",
        )

    def easy_adj(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Adjacent Gray codes flip how many bits?",
                "The defining Gray property for neighbors is…",
                "Hamming distance between successive Gray codes is…",
                "Each Gray step changes…",
            ]),
            ["0", "1", "All bits", "Exactly 2"],
            1,
            "Exactly one bit flips between adjacent codes.",
            "easy",
        )

    def easy_fifo(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Async FIFO pointers often use Gray code because…",
                "Why Gray-encode CDC pointer values?",
                "Single-bit pointer changes help because…",
                "Gray pointers across a synchronizer are safer since…",
            ]),
            [
                "Gray is faster to add",
                "Only one bit changes across a synchronizer",
                "Gray ignores clocks",
                "Gray needs no width",
            ],
            1,
            "One-bit transitions reduce CDC ambiguity.",
            "easy",
        )

    def easy_arith(i: int) -> dict:
        prompts = [
            ("You should do normal arithmetic directly on Gray-encoded bits.", False),
            ("Ordinary +/− on Gray codes gives correct binary sums.", False),
            ("Decode Gray to binary (or use Gray-aware methods) before math.", True),
            ("Gray codes are mainly for adjacency, not for ALU arithmetic.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Do not treat Gray bits as binary integers for normal math.", "easy")

    def med_convert(i: int) -> dict:
        b, g = bin_gray[(i - 1) % len(bin_gray)]
        return mcq(
            "",
            f"Binary 0b{b:04b} converts to Gray…",
            [f"0b{(g ^ 0b0011) & 0xF:04b}", f"0b{g:04b}", f"0b{(b << 1) & 0xF:04b}", "0b1111"],
            1,
            f"Gray = {b:04b} ^ ({b:04b}>>1) = {g:04b}.",
            "medium",
        )

    def med_kmap(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "K-map axes use Gray ordering so neighbors…",
                "Gray on K-map labels ensures…",
                "Why do Karnaugh maps use Gray labels?",
                "Geometric adjacency on a K-map matches…",
            ]),
            [
                "Differ in all variables",
                "Differ by one bit (logic adjacency)",
                "Count in binary order only",
                "Ignore don’t-cares",
            ],
            1,
            "Gray order makes edge-neighbors Hamming distance 1.",
            "medium",
        )

    def med_rev(i: int) -> dict:
        prompts = [
            ("Reflected Gray code is reversible (Gray → binary is possible).", True),
            ("Once in Gray, you can never recover the binary value.", False),
            ("Rotary encoders often output Gray to avoid multi-bit glitches.", True),
            ("Two bits flipping at once is the goal of Gray encoding.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Gray is invertible; encoders prefer single-bit changes.", "medium")

    def med_decode(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Gray → binary for MSB is often…",
                "When converting Gray to binary, the top bit…",
                "First step of Gray decode typically copies…",
                "In Gray→binary, bit[MSB] equals…",
            ]),
            [
                "Always 0",
                "Gray’s MSB (then XOR chain downward)",
                "Always 1",
                "The LSB of Gray only",
            ],
            1,
            "Binary MSB = Gray MSB; lower bits accumulate XORs.",
            "medium",
        )

    def hard_cdc(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "If a synchronizer samples mid-transition of a multi-bit binary counter…",
                "Binary counters across CDC are risky because…",
                "Multi-bit simultaneous flips through flops can cause…",
                "Gray helps CDC pointers mainly by avoiding…",
            ]),
            [
                "Always correct values",
                "Transient illegal intermediate codes",
                "Faster addition",
                "Need for clocks",
            ],
            1,
            "Several bits changing can be sampled as garbage combinations.",
            "hard",
        )

    def hard_next(i: int) -> dict:
        b, g = bin_gray[(i - 1) % (len(bin_gray) - 1)]
        nxt = ((b + 1) ^ ((b + 1) >> 1)) & 0xF
        return mcq(
            "",
            f"Next Gray after binary {b} (Gray 0b{g:04b}) is…",
            [f"0b{g:04b}", f"0b{nxt:04b}", f"0b{(g ^ 0b1111):04b}", "0b1111"],
            1,
            f"Binary {b}+1 → Gray {nxt:04b}.",
            "hard",
        )

    def hard_cmp(i: int) -> dict:
        prompts = [
            ("Pointer comparison after Gray→binary must use the same decode on both sides.", True),
            ("You can compare raw Gray codes with ordinary numeric < and get pointer distance.", False),
            ("FIFO full/empty logic often converts Gray pointers back to binary.", True),
            ("Gray adjacency guarantees arithmetic order without decoding.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Compare after consistent decode; Gray order ≠ binary magnitude.", "hard")

    def hard_len(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "3-bit Gray sequence length (full cycle) is…",
                "How many distinct codes in a 3-bit reflected Gray cycle?",
                "A complete 3-bit Gray tour visits how many values?",
                "2^3 Gray codes means count…",
            ]),
            ["3", "6", "8", "9"],
            2,
            "n-bit Gray has 2^n codes.",
            "hard",
        )

    items = (
        pad("easy", "gray", [easy_formula, easy_adj, easy_fifo, easy_arith])
        + pad("medium", "gray", [med_convert, med_kmap, med_rev, med_decode])
        + pad("hard", "gray", [hard_cdc, hard_next, hard_cmp, hard_len])
    )
    return {"module": "module05-gray-code", "title": "Gray code", "items": items}


# ---------------------------------------------------------------------------
# module06 — BCD
# ---------------------------------------------------------------------------

def bcd_bank() -> dict:
    packed = [(25, 0x25), (42, 0x42), (99, 0x99), (7, 0x07), (30, 0x30), (18, 0x18), (56, 0x56)]

    def easy_bits(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "How many bits does one BCD digit use?",
                "A single BCD digit is stored in…",
                "Packed BCD uses a nibble of how many bits?",
                "Each decimal digit in BCD occupies…",
            ]),
            ["2", "4", "8", "10"],
            1,
            "Each digit is a 4-bit nibble.",
            "easy",
        )

    def easy_max(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Largest valid BCD digit value?",
                "Valid BCD digits run through…",
                "Which is the maximum legal BCD digit?",
                "BCD allows decimal digits up to…",
            ]),
            ["7", "9", "15", "F"],
            1,
            "Digits are 0–9; A–F are invalid.",
            "easy",
        )

    def easy_42(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Decimal 42 as packed BCD (2 digits) is…",
                "Packed BCD for forty-two looks like…",
                "Which hex is packed BCD 42 (not binary 42)?",
                "Nibbles 4 and 2 pack as…",
            ]),
            ["0x2A", "0x42", "0x24", "42 binary bits"],
            1,
            "0x42 is BCD; binary 42 is 0x2A.",
            "easy",
        )

    def easy_invalid(i: int) -> dict:
        prompts = [
            ("Nibble 0xA is a valid BCD digit.", False),
            ("0xB can appear as a legal BCD digit.", False),
            ("Valid BCD nibbles are 0x0–0x9 only.", True),
            ("0xF is acceptable in packed BCD as digit fifteen.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "0xA–0xF are not decimal digits in BCD.", "easy")

    def med_pack(i: int) -> dict:
        dec, hx = packed[(i - 1) % len(packed)]
        distractors = [f"0x{dec:02X}", f"0x{(hx ^ 0x11) & 0xFF:02X}", "0xFF"]
        # Ensure correct answer is unique and at index 1
        choices = [distractors[0], f"0x{hx:02X}", distractors[1], distractors[2]]
        if choices[0] == choices[1]:
            choices[0] = "0x2A"
        return mcq(
            "",
            f"Decimal {dec} as packed BCD is…",
            choices,
            1,
            f"Tens={dec // 10}, ones={dec % 10} → 0x{hx:02X}.",
            "medium",
        )

    def med_vs_bin(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Binary 0x2A versus BCD 0x42 for decimal 42 shows…",
                "Why isn’t binary 42 the same hex as BCD 42?",
                "Packed BCD is not the same as…",
                "Confusing binary magnitude with BCD packing causes…",
            ]),
            [
                "They are always identical",
                "Different encodings of the same decimal quantity",
                "BCD uses 10 bits per digit",
                "Binary forbids digit 2",
            ],
            1,
            "Same decimal, different bit spellings.",
            "medium",
        )

    def med_adjust(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "After BCD digit add that exceeds 9, hardware often…",
                "Decimal adjust / +6 correction is used when…",
                "If a BCD nibble sum is 0xA–0xF, a common fix is…",
                "Invalid BCD after add is repaired by…",
            ]),
            [
                "Ignoring it",
                "Adding 6 (DAA-style) to restore a decimal digit",
                "Shifting left 4",
                "Clearing the carry always",
            ],
            1,
            "Add 6 when the nibble is not a valid digit (or carry).",
            "medium",
        )

    def med_pack_tf(i: int) -> dict:
        prompts = [
            ("Unpacked BCD often stores one digit per byte (low nibble).", True),
            ("Packed BCD places two digits in one byte.", True),
            ("BCD always uses fewer bits than pure binary for the same range.", False),
            ("Displays and RTC chips commonly speak BCD.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "BCD is convenient for digits; denser binary usually wins for math.", "medium")

    def hard_illegal(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Which nibble is illegal in packed BCD?",
                "Pick an invalid BCD digit pattern.",
                "Illegal BCD among these is…",
                "Which value cannot be a BCD digit?",
            ]),
            ["0x3", "0x9", "0xC", "0x0"],
            2,
            "0xC (12) is outside 0–9.",
            "hard",
        )

    def hard_add(i: int) -> dict:
        if i % 2:
            return mcq(
                "",
                "Adding BCD 0x09 + 0x01 without decimal adjust yields nibble…",
                ["0x09", "0x0A (invalid BCD)", "0x10 packed", "0x00"],
                1,
                "9+1=10 → 0xA before +6 adjust → 0x10 BCD.",
                "hard",
            )
        return mcq(
            "",
            "After DAA-style +6 on nibble 0x0A, the corrected BCD digit pair is…",
            ["0x0A", "0x10", "0x16", "0x09"],
            1,
            "0xA + 6 = 0x10 (decimal ten as BCD).",
            "hard",
        )

    def hard_range(i: int) -> dict:
        prompts = [
            ("Packed BCD 0x99 is the largest two-digit packed value.", True),
            ("0x9A is a valid two-digit packed BCD number.", False),
            ("Converting binary to BCD encodes each decimal digit into nibbles.", True),
            ("Seven-segment digit drivers often consume BCD or digit indices.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Both nibbles must stay 0–9; 0x9A is illegal.", "hard")

    def hard_width(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Four packed BCD digits need how many bits minimum?",
                "Width for 4 BCD digits (packed) is…",
                "Packing year digits YYYY in BCD uses…",
                "16 bits of packed BCD hold how many decimal digits?",
            ]),
            ["8", "16", "32", "10"],
            1,
            "4 bits × 4 digits = 16 bits; 16 bits hold 4 digits.",
            "hard",
        )

    items = (
        pad("easy", "bcd", [easy_bits, easy_max, easy_42, easy_invalid])
        + pad("medium", "bcd", [med_pack, med_vs_bin, med_adjust, med_pack_tf])
        + pad("hard", "bcd", [hard_illegal, hard_add, hard_range, hard_width])
    )
    return {"module": "module06-bcd-lab", "title": "BCD", "items": items}


# ---------------------------------------------------------------------------
# module07 — Parity / checksum
# ---------------------------------------------------------------------------

def parity_bank() -> dict:
    patterns = [0b1010, 0b1110, 0b0001, 0b1111, 0b0101, 0b1000, 0b0011, 0b1100]

    def easy_even(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Even parity bit is commonly equal to…",
                "Even P over data bits is typically…",
                "Reduction XOR of data bits gives…",
                "Which operation yields even parity?",
            ]),
            ["OR of all bits", "Reduction XOR of data bits", "AND of all bits", "Bit count divided by 8"],
            1,
            "Even parity bit is the XOR of the data bits.",
            "easy",
        )

    def easy_correct(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Does a single parity bit correct bit errors?",
                "Parity’s job versus ECC correction…",
                "A lone parity bit can…",
                "Pick what single parity provides.",
            ]),
            ["Yes, always", "Yes, for two-bit errors", "No — it detects (many) flips", "Only in odd mode"],
            2,
            "Parity detects many single-bit errors; it does not correct them.",
            "easy",
        )

    def easy_xor(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "A simple multi-byte XOR checksum verifies when the fold is…",
                "XOR of data+checksum bytes equaling zero means…",
                "Successful XOR checksum fold result is…",
                "Check matched for XOR fold when result is…",
            ]),
            ["0xFF", "0", "Equal to the last byte", "Odd"],
            1,
            "XOR fold to zero means the check matched.",
            "easy",
        )

    def easy_flip(i: int) -> dict:
        prompts = [
            ("After a good even-parity verify, flipping one data bit should make verify FAIL.", True),
            ("A single data flip changes ones-parity and fails an even-parity check.", True),
            ("Parity always detects every multi-bit error.", False),
            ("Odd parity forces an odd number of 1s including the parity bit.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Single flips fail parity; some multi-bit errors can sneak through.", "easy")

    def med_even_bit(i: int) -> dict:
        p = patterns[(i - 1) % len(patterns)]
        ans = bin(p).count("1") % 2
        return mcq(
            "",
            f"Even parity bit for data 0b{p:04b} is…",
            ["0", "1", "X", "2"],
            ans,
            f"XOR of bits = {ans} for even parity.",
            "medium",
        )

    def med_odd_bit(i: int) -> dict:
        p = patterns[(i - 1) % len(patterns)]
        ans = 1 - (bin(p).count("1") % 2)
        return mcq(
            "",
            f"Odd parity bit for data 0b{p:04b} is…",
            ["0", "1", "Same as even always", "N/A"],
            ans,
            "Odd parity is the complement of even parity for the same data.",
            "medium",
        )

    def med_limits(i: int) -> dict:
        prompts = [
            ("Two-bit flips can leave even parity unchanged (undetected).", True),
            ("Parity detects all double-bit errors reliably.", False),
            ("Checksums stronger than parity can still miss some corruptions.", True),
            ("XOR checksums are weaker than cryptographic hashes but cheap in hardware.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Even numbers of flips can cancel; simple checks are not crypto.", "medium")

    def med_uart(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "UART framing often includes…",
                "A serial frame may append…",
                "Besides start/stop, links may send…",
                "Which extra bit helps detect line errors?",
            ]),
            ["A parity bit option", "A K-map", "An FSM encoding", "Endian swap only"],
            0,
            "Many UARTs optionally append parity.",
            "medium",
        )

    def hard_codeword(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "If even parity over data||P is checked, a correct frame has…",
                "Verify even parity by XORing all bits including P; success is…",
                "Including the parity bit, even scheme wants XOR fold…",
                "Good even-parity codeword reduction XOR equals…",
            ]),
            ["1", "0", "0xFF", "MSB only"],
            1,
            "Whole codeword has even ones → XOR is 0.",
            "hard",
        )

    def hard_checksum(i: int) -> dict:
        pairs = [(0x12, 0x34, 0x26), (0x01, 0x02, 0x03), (0xFF, 0x0F, 0xF0), (0xAA, 0x55, 0xFF)]
        a, b, c = pairs[(i - 1) % len(pairs)]
        return mcq(
            "",
            f"XOR checksum for bytes 0x{a:02X}, 0x{b:02X} should be…",
            ["0x00", f"0x{c:02X}", "0xFF", f"0x{(c ^ 0x11) & 0xFF:02X}"],
            1,
            f"0x{a:02X} ^ 0x{b:02X} = 0x{c:02X}; that checksum folds to 0.",
            "hard",
        )

    def hard_ecc(i: int) -> dict:
        prompts = [
            ("ECC (e.g. SECDED) can correct single-bit errors; parity alone cannot.", True),
            ("Parity bits locate which bit flipped without extra syndrome bits.", False),
            ("Memory DIMMs may use ECC beyond simple parity.", True),
            ("Checksum mismatch proves exactly which byte is wrong always.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Parity detects; ECC syndromes correct/locate; XOR may not pinpoint.", "hard")

    def hard_2d(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Vertical + longitudinal parity (product codes) mainly improves…",
                "Row and column parity together help…",
                "Adding a parity byte per row and column aims to…",
                "2D parity schemes increase…",
            ]),
            [
                "Clock frequency only",
                "Error detection coverage / occasional location",
                "ASCII glyph count",
                "Endian conversion",
            ],
            1,
            "Extra parity dimensions catch more patterns and can hint at location.",
            "hard",
        )

    items = (
        pad("easy", "parity", [easy_even, easy_correct, easy_xor, easy_flip])
        + pad("medium", "parity", [med_even_bit, med_odd_bit, med_limits, med_uart])
        + pad("hard", "parity", [hard_codeword, hard_checksum, hard_ecc, hard_2d])
    )
    return {"module": "module07-parity-checksum", "title": "Parity / checksum", "items": items}


# ---------------------------------------------------------------------------
# module08 — Fixed-point Qm.n
# ---------------------------------------------------------------------------

def fixed_bank() -> dict:
    decodes = [(4, 8, 0.5), (4, 24, 1.5), (4, 16, 1.0), (4, 4, 0.25), (3, 8, 1.0), (2, 6, 1.5)]

    def easy_div(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Decoding a signed Qm.n raw value divides by…",
                "Real value from Qm.n raw bits scales by…",
                "To decode fixed-point, divide signed_raw by…",
                "The fractional weight uses denominator…",
            ]),
            ["2^m", "2^n", "m+n", "10^n"],
            1,
            "Real ≈ signed_raw / 2^n.",
            "easy",
        )

    def easy_step(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Smallest positive step in Qm.n is…",
                "One LSB in Qm.n equals…",
                "Resolution of Qm.n is…",
                "Fraction LSB weight is…",
            ]),
            ["2^m", "2^-n", "1", "0.1"],
            1,
            "Step size is 2^-n.",
            "easy",
        )

    def easy_width(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "In this lab, total bit width W equals…",
                "Qm.n width W is…",
                "m + n in the lab means…",
                "Bit budget for Qm.n (lab convention) is…",
            ]),
            ["m only", "n only", "m+n", "2^(m+n)"],
            2,
            "W = m + n (m includes sign here).",
            "easy",
        )

    def easy_q44(i: int) -> dict:
        prompts = [
            ("Q4.4 raw 0x18 (decimal 24) decodes to 1.5.", True),
            ("In Q4.4, raw 24 means 24/16 = 1.5.", True),
            ("Changing n with the same raw bits moves the binary point.", True),
            ("Qm.n raw bits are already IEEE floats.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Scale by 2^n; raw ≠ float encoding.", "easy")

    def med_decode(i: int) -> dict:
        n, raw, real = decodes[(i - 1) % len(decodes)]
        return mcq(
            "",
            f"Q with n={n}: raw {raw} decodes to…",
            [str(raw), str(real), str(raw / 2), str(2**n)],
            1,
            f"{raw} / 2^{n} = {real}.",
            "medium",
        )

    def med_encode(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Encoding a real to Qm.n roughly…",
                "To encode, multiply the real by…",
                "Fixed-point encode scales by…",
                "Before storing bits, multiply by…",
            ]),
            ["2^m", "2^n (then round)", "10^n only", "m−n"],
            1,
            "raw ≈ round(real × 2^n).",
            "medium",
        )

    def med_min(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Q4.4 approximate signed minimum is near…",
                "With m=4 including sign, Q4.4 floor is about…",
                "Most-negative Q4.4 raw (−128) as real is…",
                "−8.0 appears as Q4.4 min because…",
            ]),
            ["−1", "−8", "−16", "0"],
            1,
            "−128 / 16 = −8.",
            "medium",
        )

    def med_sat(i: int) -> dict:
        prompts = [
            ("Saturation on encode clamps out-of-range reals to min/max raw.", True),
            ("Saturation and wrap are the same overflow policy.", False),
            ("Same raw with larger n represents a smaller real step / different value.", True),
            ("Forgetting /2^n treats fixed-point as an integer by mistake.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Sat ≠ wrap; scale is mandatory.", "medium")

    def hard_mul(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Multiplying two Q formats: fractional bits…",
                "Qm.a × Qn.b yields fractional width…",
                "Product of Q*.3 and Q*.5 needs how many fraction bits before truncate?",
                "Fraction bits add under multiplication:",
            ]),
            ["Stay max(a,b)", "Add: a+b (before renormalizing)", "Become zero", "Become m+n"],
            1,
            "Fraction widths add; then you shift/round to the target Q.",
            "hard",
        )

    def hard_enc_num(i: int) -> dict:
        if i % 2:
            return mcq(
                "",
                "Encode 0.5 into Q4.4 (n=4). Raw integer is…",
                ["4", "8", "16", "0"],
                1,
                "0.5 × 16 = 8.",
                "hard",
            )
        return mcq(
            "",
            "Encode −1.25 into Q4.4. Closest raw (two’s) is…",
            ["−20", "−16", "−8", "20"],
            0,
            "−1.25 × 16 = −20.",
            "hard",
        )

    def hard_policy(i: int) -> dict:
        prompts = [
            ("Agreed Q formats and rounding modes matter across DSP blocks.", True),
            ("Moving the binary point (changing n) without rescaling keeps the real value.", False),
            ("Fixed-point needs an overflow policy just like integer adders.", True),
            ("m includes the sign bit in this course’s lab convention.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Changing n reinterpretation changes the real; document Q and sat/wrap.", "hard")

    def hard_pitfall(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Pitfall: treating raw bits as a float means…",
                "Reading Q raw in a debugger as unsigned int without scaling…",
                "Forgetting the binary point causes…",
                "Which mistake mis-scales fixed-point?",
            ]),
            [
                "Always correct reals",
                "Wrong magnitude by ~2^n",
                "Removes need for n",
                "Converts to Gray",
            ],
            1,
            "Must divide/multiply by 2^n for real meaning.",
            "hard",
        )

    items = (
        pad("easy", "fixed", [easy_div, easy_step, easy_width, easy_q44])
        + pad("medium", "fixed", [med_decode, med_encode, med_min, med_sat])
        + pad("hard", "fixed", [hard_mul, hard_enc_num, hard_policy, hard_pitfall])
    )
    return {"module": "module08-fixed-point", "title": "Fixed-point Qm.n", "items": items}


# ---------------------------------------------------------------------------
# module09 — Bit-fields
# ---------------------------------------------------------------------------

def bitfields_bank() -> dict:
    slices = [(7, 3, 5), (2, 1, 2), (15, 8, 8), (4, 4, 1), (11, 0, 12), (5, 0, 6), (3, 1, 3)]

    def easy_width(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Field width for [hi:lo] is…",
                "Inclusive slice width equals…",
                "How many bits in field hi downto lo?",
                "w = ? for bits [hi:lo]",
            ]),
            ["hi-lo", "hi-lo+1", "hi+lo", "2^(hi-lo)"],
            1,
            "Inclusive: w = hi − lo + 1.",
            "easy",
        )

    def easy_extract(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Extract typically ends with…",
                "After masking a field, align it by…",
                "To bring [hi:lo] to bit 0…",
                "Field extract shifts…",
            ]),
            ["<< lo", ">> lo", "& lo", "| lo"],
            1,
            "Mask, then >> lo.",
            "easy",
        )

    def easy_insert(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Before OR on insert, clear the old field with…",
                "Insert clears the slice using…",
                "Neighbor bits stay put if you AND with…",
                "Which mask clears a field before OR?",
            ]),
            ["mask", "~mask", "lo", "hi"],
            1,
            "AND with ~mask, then OR new bits.",
            "easy",
        )

    def easy_lsb(i: int) -> dict:
        prompts = [
            ("In this lab, bit 0 is the LSB.", True),
            ("Lab numbering uses LSB = bit 0.", True),
            ("Bit 0 is always the MSB in CSR packs.", False),
            ("hi >= lo for a nonempty field.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "LSB numbering; MSB-as-0 is a different convention.", "easy")

    def med_w(i: int) -> dict:
        hi, lo, w = slices[(i - 1) % len(slices)]
        return mcq(
            "",
            f"Width of field [{hi}:{lo}] is…",
            [str(hi - lo), str(w), str(hi + lo), str(2 * w)],
            1,
            f"{hi}−{lo}+1 = {w}.",
            "medium",
        )

    def med_count(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Word 0xA52D, extract [7:3] (COUNT) yields…",
                "From 0xA52D, bits 7:3 equal…",
                "Starter lab: COUNT in 0xA52D is…",
                "(0xA52D >> 3) & 0x1F equals…",
            ]),
            ["0", "5", "0xA5", "0x2D"],
            1,
            "0xA52D → field 7:3 is 5.",
            "medium",
        )

    def med_mask(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Mask for [hi:lo] is often…",
                "Bit mask covering lo..hi can be written…",
                "((1<<w)-1)<<lo builds…",
                "Which expression makes the field mask?",
            ]),
            [
                "lo alone",
                "((1 << (hi - lo + 1)) - 1) << lo",
                "hi ^ lo",
                "~0 >> hi",
            ],
            1,
            "Width ones, shifted to lo.",
            "medium",
        )

    def med_spill(i: int) -> dict:
        prompts = [
            ("Inserting without masking can spill into neighboring fields.", True),
            ("Overlapping field definitions are harmless in packs.", False),
            ("Clearing a field with insert 0 should leave other fields intact if masked.", True),
            ("Unmasked OR of a wide value corrupts adjacent bits.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Always mask; overlapping specs break packs.", "medium")

    def hard_shift(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Insert value 3 into [5:4] of a cleared byte yields bits…",
                "Field [5:4]=3 means which binary in those positions?",
                "After proper insert of 0b11 at lo=4…",
                "3 << 4 placed in [5:4] contributes…",
            ]),
            ["0x03", "0x30", "0x0C", "0xFF"],
            1,
            "3<<4 = 0x30 for a 2-bit field at lo=4.",
            "hard",
        )

    def hard_csr(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "CSR specs still need beyond pack/unpack…",
                "Real registers also document…",
                "Besides hi/lo, production CSRs specify…",
                "Missing which item breaks SW/HW contract?",
            ]),
            [
                "Only the font in the PDF",
                "Reset values, access types, side effects",
                "Gray code only",
                "UART baud only",
            ],
            1,
            "Reset/access/side effects matter as much as bit indices.",
            "hard",
        )

    def hard_formula(i: int) -> dict:
        prompts = [
            ("Extract is (word & mask) >> lo.", True),
            ("Insert is (word & ~mask) | ((val << lo) & mask).", True),
            ("Using MSB=0 numbering interchangeably with LSB=0 never causes bugs.", False),
            ("Wrong hi/lo off-by-one is a common field bug.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Standard mask formulas; bit-order confusion is costly.", "hard")

    def hard_mask_hex(i: int) -> dict:
        # Vary a few concrete masks
        cases = [
            ([6, 2], "0x7C", "Bits 6..2 → 0b01111100 = 0x7C."),
            ([4, 0], "0x1F", "Bits 4..0 → 0b00011111 = 0x1F."),
            ([7, 4], "0xF0", "Bits 7..4 → 0b11110000 = 0xF0."),
            ([3, 1], "0x0E", "Bits 3..1 → 0b00001110 = 0x0E."),
        ]
        (hi_lo, ans, explain) = cases[(i - 1) % len(cases)]
        hi, lo = hi_lo
        wrong = ["0xFF", "0x01", "0x80"]
        choices = [ans, wrong[0], wrong[1], wrong[2]]
        # rotate so answer index varies but we know index
        rot = (i - 1) % 4
        choices = choices[-rot:] + choices[:-rot] if rot else choices
        answer = choices.index(ans)
        return mcq(
            "",
            f"8-bit mask for bits [{hi}:{lo}] is…",
            choices,
            answer,
            explain,
            "hard",
        )

    items = (
        pad("easy", "bitfields", [easy_width, easy_extract, easy_insert, easy_lsb])
        + pad("medium", "bitfields", [med_w, med_count, med_mask, med_spill])
        + pad("hard", "bitfields", [hard_shift, hard_csr, hard_formula, hard_mask_hex])
    )
    return {"module": "module09-bit-fields", "title": "Bit-fields", "items": items}


# ---------------------------------------------------------------------------
# module10 — Endian packing
# ---------------------------------------------------------------------------

def endian_bank() -> dict:
    words = [
        (0x12345678, 0x78, 0x12),
        (0xAABBCCDD, 0xDD, 0xAA),
        (0x0000FFFF, 0xFF, 0x00),
        (0xDEADBEEF, 0xEF, 0xDE),
        (0x01020304, 0x04, 0x01),
        (0x11223344, 0x44, 0x11),
    ]

    def easy_le(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Little-endian stores at the lowest address the…",
                "In LE, address +0 holds the…",
                "LE puts which byte at the lowest address?",
                "Least significant byte location in little-endian is…",
            ]),
            ["MSB", "LSB", "sign bit only", "middle byte"],
            1,
            "LE stores LSB at +0.",
            "easy",
        )

    def easy_1234(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "For 0x12345678 in little-endian, byte at +0 is…",
                "LE unpack of 0x12345678: first byte is…",
                "Low address byte for 0x12345678 LE…",
                "0x12345678 LE memory starts with…",
            ]),
            ["0x12", "0x34", "0x56", "0x78"],
            3,
            "LE: 78 56 34 12.",
            "easy",
        )

    def easy_net(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Network byte order is usually…",
                "Wire / Internet byte order is conventionally…",
                "Big-endian on the network means…",
                "Protocols typically send multi-byte fields as…",
            ]),
            ["little-endian", "big-endian", "host-dependent only", "random"],
            1,
            "Network order is big-endian by convention.",
            "easy",
        )

    def easy_value(i: int) -> dict:
        prompts = [
            ("Changing endian layout changes the integer value of 0x12345678.", False),
            ("Endianness changes memory byte order, not the abstract integer value.", True),
            ("Same word value can unpack to different address-order bytes in LE vs BE.", True),
            ("Host endian always matches network order.", False),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Value unchanged; only byte placement differs. Host ≠ wire often.", "easy")

    def med_le0(i: int) -> dict:
        w, le0, be0 = words[(i - 1) % len(words)]
        return mcq(
            "",
            f"For 0x{w:08X} little-endian, byte at +0 is…",
            [f"0x{be0:02X}", f"0x{le0:02X}", "0x00", "0xFF"],
            1,
            f"LE LSB = 0x{le0:02X}.",
            "medium",
        )

    def med_be0(i: int) -> dict:
        w, le0, be0 = words[(i - 1) % len(words)]
        return mcq(
            "",
            f"For 0x{w:08X} big-endian, byte at +0 is…",
            [f"0x{le0:02X}", f"0x{be0:02X}", "0x56", "0x00"],
            1,
            f"BE MSB = 0x{be0:02X}.",
            "medium",
        )

    def med_swap(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Byte-swap of 0x12345678 yields…",
                "Reversing four bytes of 0x12345678 gives…",
                "Endian swap word 0x12345678 →…",
                "bswap32(0x12345678) is…",
            ]),
            ["0x12345678", "0x78563412", "0x21436587", "0x00000000"],
            1,
            "78 56 34 12 as a word is 0x78563412.",
            "medium",
        )

    def med_pack(i: int) -> dict:
        prompts = [
            ("Pack LE bytes AA BB CC DD at +0..+3 yields word 0xDDCCBBAA.", True),
            ("BE pack of AA BB CC DD at +0..+3 yields 0xAABBCCDD.", True),
            ("Byte order and bit order inside a byte are the same concept.", False),
            ("Mixing LE and BE across a bus without conversion corrupts multi-byte fields.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Byte order ≠ bit order; conversion is mandatory at boundaries.", "medium")

    def hard_policy(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "DMA / register / frame endian policy must be…",
                "Why SoCs document endianness explicitly?",
                "Assuming host endian matches the wire risks…",
                "Pick the best endian engineering practice.",
            ]),
            [
                "Left implicit always",
                "Specified per interface and converted as needed",
                "Randomized each boot",
                "Only relevant to ASCII",
            ],
            1,
            "Explicit policy + conversion prevents silent corruption.",
            "hard",
        )

    def hard_misread(i: int) -> dict:
        return mcq(
            "",
            _pick(i, [
                "Reading a BE uint32 from a LE CPU without swap…",
                "Casting wire BE bytes as host LE int causes…",
                "Missing ntohl/htonl style conversion yields…",
                "What happens if you interpret BE memory as LE?",
            ]),
            [
                "Correct value always",
                "Scrambled numeric value (byte-reversed interpretation)",
                "Only parity errors",
                "Automatic Gray coding",
            ],
            1,
            "Bytes are reinterpreted → wrong integer.",
            "hard",
        )

    def hard_ops(i: int) -> dict:
        prompts = [
            ("Unpack splits a word into address-ordered bytes for the chosen mode.", True),
            ("Pack rebuilds a word from bytes at +0 through +3.", True),
            ("Endianness never matters for 16- and 32-bit register fields.", False),
            ("Comparing LE vs BE side-by-side is a good literacy check.", True),
        ]
        p, a = prompts[(i - 1) % 4]
        return tf("", p, a, "Multi-byte fields always have an endian story.", "hard")

    def hard_ends(i: int) -> dict:
        w, le0, be0 = words[(i - 1) % len(words)]
        return mcq(
            "",
            f"LE bytes of 0x{w:08X} from +0 to +3 start with 0x{le0:02X} and end with…",
            [f"0x{le0:02X}", f"0x{be0:02X}", "0x00", "0xFF"],
            1,
            f"LE order ends at the MSB 0x{be0:02X}.",
            "hard",
        )

    items = (
        pad("easy", "endian", [easy_le, easy_1234, easy_net, easy_value])
        + pad("medium", "endian", [med_le0, med_be0, med_swap, med_pack])
        + pad("hard", "endian", [hard_policy, hard_misread, hard_ops, hard_ends])
    )
    return {"module": "module10-endian-lab", "title": "Endian packing", "items": items}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_banks() -> list[dict]:
    return [
        twos_bank(),
        overflow_bank(),
        ascii_bank(),
        gray_bank(),
        bcd_bank(),
        parity_bank(),
        fixed_bank(),
        bitfields_bank(),
        endian_bank(),
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
            assert it["type"] in ("multiple_choice", "true_false"), it
            if it["type"] == "multiple_choice":
                assert 0 <= it["answer"] < len(it["choices"]), it
            else:
                assert isinstance(it["answer"], bool), it
        assert counts == {"easy": 30, "medium": 30, "hard": 30}, counts
        print(path.name, counts, "total", len(bank["items"]))


if __name__ == "__main__":
    main()
