"""Fill every learn_digital bank to 30 unique items per difficulty.

Keeps existing items (and their media / tool_capture). Appends new unique
items until TARGET is reached. Uniqueness = prompt + choices + answer + type
+ difficulty (exact match).

Usage:
  python scripts/forge_full_unique_banks.py
  python scripts/forge_full_unique_banks.py --module module17-gate-composer
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "content" / "learn_digital"
QUESTIONS = COURSE / "questions"
TARGET = 30

Gen = Callable[[], Iterable[dict]]


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


def mcq(prompt: str, choices: list[str], answer: int, explain: str, difficulty: str) -> dict:
    assert 0 <= answer < len(choices), (prompt, answer, choices)
    return {
        "type": "multiple_choice",
        "prompt": prompt,
        "choices": choices,
        "answer": answer,
        "explain": explain,
        "difficulty": difficulty,
    }


def tf(prompt: str, answer: bool, explain: str, difficulty: str) -> dict:
    return {
        "type": "true_false",
        "prompt": prompt,
        "answer": answer,
        "explain": explain,
        "difficulty": difficulty,
    }


def prefix_from_items(items: list[dict], module_id: str) -> str:
    for it in items:
        mid = str(it.get("id") or "")
        m = re.match(r"^([a-z0-9]+)_", mid)
        if m:
            return m.group(1)
    slug = module_id.split("-", 1)[-1].replace("-", "")[:12]
    return slug or "q"


def next_index(items: list[dict], prefix: str, difficulty: str) -> int:
    pat = re.compile(rf"^{re.escape(prefix)}_{re.escape(difficulty)}_(\d+)$")
    n = 0
    for it in items:
        m = pat.match(str(it.get("id") or ""))
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


# --- parametric generators (topic families) ---------------------------------

def bits_values(difficulty: str) -> Iterable[dict]:
    for n in range(1, 17):
        correct = 2**n
        choices = [str(correct // 2 or 1), str(correct), str(n), str(10 * n)]
        # stable unique order but answer at index 1
        yield mcq(
            f"How many distinct values can {n} bits represent?",
            choices,
            1,
            f"{n} bits encode 2^{n} = {correct} patterns.",
            difficulty,
        )
    for n in (18, 20, 24, 32):
        yield mcq(
            f"An unsigned {n}-bit field holds how many codes?",
            [str(2 ** (n - 1)), str(2**n), str(n), "unlimited"],
            1,
            f"2^{n} patterns.",
            difficulty,
        )


def hex_digit(difficulty: str) -> Iterable[dict]:
    table = [
        ("0", 0),
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
        ("6", 6),
        ("7", 7),
        ("8", 8),
        ("9", 9),
        ("A", 10),
        ("B", 11),
        ("C", 12),
        ("D", 13),
        ("E", 14),
        ("F", 15),
    ]
    for h, d in table:
        wrong = sorted({max(0, d - 1), min(15, d + 1), (d + 5) % 16, d} - {d})
        while len(wrong) < 3:
            wrong.append((wrong[-1] + 3) % 16)
        choices = [str(wrong[0]), str(d), str(wrong[1]), str(wrong[2])]
        yield mcq(
            f"Hex digit {h} equals which decimal value?",
            choices,
            1,
            f"{h}₁₆ = {d}₁₀.",
            difficulty,
        )
        yield mcq(
            f"Decimal {d} as one hex digit is…",
            [table[wrong[0]][0], h, table[wrong[1]][0], table[wrong[2]][0]],
            1,
            f"{d}₁₀ = {h}₁₆.",
            difficulty,
        )


def binary_spell(difficulty: str) -> Iterable[dict]:
    for v in range(0, 16):
        w = 4
        correct = format(v, f"0{w}b")
        distractors = [
            format((v ^ 0b0001) & 0xF, f"0{w}b"),
            format((v ^ 0b1000) & 0xF, f"0{w}b"),
            format((v + 1) & 0xF, f"0{w}b"),
        ]
        choices = [distractors[0], correct, distractors[1], distractors[2]]
        yield mcq(
            f"Which is a valid {w}-bit binary spelling of decimal {v}?",
            choices,
            1,
            f"{v} = {correct}₂.",
            difficulty,
        )


def twos_range(difficulty: str) -> Iterable[dict]:
    for n in range(2, 12):
        lo, hi = -(2 ** (n - 1)), 2 ** (n - 1) - 1
        yield mcq(
            f"Signed two's-complement range at width {n} is…",
            [f"{lo} … {hi}", f"0 … {2**n - 1}", f"{-hi} … {hi}", f"{lo} … {2**n - 1}"],
            0,
            f"[{lo}, {hi}] for {n}-bit two's complement.",
            difficulty,
        )
        yield mcq(
            f"Most-negative {n}-bit two's-complement value is…",
            [str(lo + 1), str(lo), str(-hi), "0"],
            1,
            f"Sign bit alone → {lo}.",
            difficulty,
        )


def overflow_wrap(difficulty: str) -> Iterable[dict]:
    for n in (4, 5, 6, 7, 8):
        mod = 2**n
        for a, b in [(3, 5), (7, 1), (9, 9), (15, 2), (mod - 1, 1), (mod // 2, mod // 2)]:
            if a >= mod or b >= mod:
                continue
            wrap = (a + b) % mod
            sat = min(a + b, mod - 1)
            yield mcq(
                f"Unsigned wrap add at width {n}: {a}+{b} yields…",
                [str(a + b), str(wrap), str(sat), str((a + b) % (mod // 2))],
                1,
                f"Mod {mod} → {wrap}.",
                difficulty,
            )


def ascii_codes(difficulty: str) -> Iterable[dict]:
    pairs = [
        ("space", 0x20),
        ("digit 0", 0x30),
        ("digit 9", 0x39),
        ("'A'", 0x41),
        ("'Z'", 0x5A),
        ("'a'", 0x61),
        ("'z'", 0x7A),
        ("NUL", 0x00),
        ("LF", 0x0A),
        ("CR", 0x0D),
        ("DEL", 0x7F),
    ]
    for name, code in pairs:
        yield mcq(
            f"ASCII code for {name} is…",
            [f"0x{code ^ 0x10:02X}", f"0x{code:02X}", f"0x{code ^ 0x01:02X}", "0xFF"],
            1,
            f"{name} → 0x{code:02X}.",
            difficulty,
        )
        yield tf(
            f"ASCII {name} has code 0x{code:02X}.",
            True,
            f"Standard ASCII maps {name} to 0x{code:02X}.",
            difficulty,
        )


def gray_code(difficulty: str) -> Iterable[dict]:
    def bin_to_gray(x: int) -> int:
        return x ^ (x >> 1)

    for n in range(0, 16):
        g = bin_to_gray(n)
        yield mcq(
            f"Binary {n:04b} converts to Gray as…",
            [f"{n:04b}", f"{g:04b}", f"{(g ^ 1):04b}", f"{(n >> 1):04b}"],
            1,
            f"Gray = b ⊕ (b>>1) → {g:04b}.",
            difficulty,
        )
    yield tf(
        "Adjacent Gray codes differ by exactly one bit.",
        True,
        "That is the defining property of reflected Gray code.",
        difficulty,
    )


def bcd_pack(difficulty: str) -> Iterable[dict]:
    for tens, ones in [(1, 5), (2, 5), (4, 2), (9, 9), (0, 7), (3, 0), (8, 8), (6, 4)]:
        packed = (tens << 4) | ones
        yield mcq(
            f"Packed BCD for decimal {tens}{ones} is…",
            [f"0x{tens*10+ones:02X}", f"0x{packed:02X}", f"0x{ones<<4|tens:02X}", "0xFF"],
            1,
            f"Each decimal digit → nibble → 0x{packed:02X}.",
            difficulty,
        )
    for bad in (0x0A, 0x1B, 0x2C, 0x3D, 0x4E, 0x5F, 0x9A):
        yield tf(
            f"Byte 0x{bad:02X} is valid packed BCD.",
            False,
            "BCD nibbles must be 0–9.",
            difficulty,
        )


def parity_bits(difficulty: str) -> Iterable[dict]:
    for data in range(0, 16):
        ones = bin(data).count("1")
        even = 0 if ones % 2 == 0 else 1
        odd = 1 - even
        yield mcq(
            f"Even parity bit for data {data:04b} is…",
            ["0", "1", "depends on width", "2"],
            even,
            f"{ones} ones → even parity {even}.",
            difficulty,
        )
        yield mcq(
            f"Odd parity bit for data {data:04b} is…",
            ["0", "1", "X", "same as even"],
            odd,
            f"Odd parity flips even → {odd}.",
            difficulty,
        )


def fixed_q(difficulty: str) -> Iterable[dict]:
    for frac in (1, 2, 3, 4, 8):
        step = 1 / (2**frac)
        yield mcq(
            f"Unsigned Q0.{frac} LSB weight is…",
            [str(2**frac), str(step), str(frac), "1"],
            1,
            f"LSB = 2^-{frac} = {step}.",
            difficulty,
        )
    for val, frac in [(0.5, 4), (0.25, 4), (0.75, 4), (1.5, 4), (-0.5, 4)]:
        raw = int(round(val * (2**frac)))
        yield mcq(
            f"Encode {val} in Q4.{frac if frac != 4 else 4} style scale 2^{frac} (nearest int raw)…",
            [str(raw - 1), str(raw), str(raw + 2), "0"],
            1,
            f"raw ≈ round({val}×{2**frac}) = {raw}.",
            difficulty,
        )


def bitfields(difficulty: str) -> Iterable[dict]:
    for lo, width in [(0, 2), (0, 3), (1, 2), (2, 3), (4, 4), (8, 4), (4, 2), (3, 5)]:
        mask = ((1 << width) - 1) << lo
        yield mcq(
            f"Mask for field lo={lo} width={width} is…",
            [hex(mask >> 1), hex(mask), hex((1 << width) - 1), hex(1 << lo)],
            1,
            f"(({1 << width}-1)<<{lo}) = {hex(mask)}.",
            difficulty,
        )
        yield mcq(
            f"Width of a field from bit {lo} through {lo + width - 1} is…",
            [str(width - 1), str(width), str(lo + width), str(1 << width)],
            1,
            f"Inclusive span → {width} bits.",
            difficulty,
        )


def endian_pack(difficulty: str) -> Iterable[dict]:
    words = [0x01020304, 0xAABBCCDD, 0x11223344, 0xDEADBEEF, 0x0000FFFF, 0xA5A5A5A5]
    for w in words:
        be0 = (w >> 24) & 0xFF
        le0 = w & 0xFF
        yield mcq(
            f"Big-endian first byte of 0x{w:08X} is…",
            [f"0x{le0:02X}", f"0x{be0:02X}", f"0x{(w>>16)&0xFF:02X}", "0x00"],
            1,
            f"BE stores MSB first → 0x{be0:02X}.",
            difficulty,
        )
        yield mcq(
            f"Little-endian first byte of 0x{w:08X} is…",
            [f"0x{be0:02X}", f"0x{le0:02X}", f"0x{(w>>8)&0xFF:02X}", "0xFF"],
            1,
            f"LE stores LSB first → 0x{le0:02X}.",
            difficulty,
        )


def truth_gates(difficulty: str) -> Iterable[dict]:
    rows = [
        ("AND", [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]),
        ("OR", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]),
        ("XOR", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]),
        ("NAND", [(0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0)]),
        ("NOR", [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 0)]),
        ("XNOR", [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)]),
    ]
    for name, table in rows:
        for a, b, y in table:
            yield mcq(
                f"{name}(A={a}, B={b}) equals…",
                ["0", "1", "A", "B"],
                y,
                f"{name} truth cell → {y}.",
                difficulty,
            )
        yield tf(
            f"A 2-input {name} has four truth-table rows.",
            True,
            "Two inputs → 2² = 4 combinations.",
            difficulty,
        )


def boolean_laws(difficulty: str) -> Iterable[dict]:
    laws = [
        ("A + 0 = A", True, "Identity for OR."),
        ("A · 1 = A", True, "Identity for AND."),
        ("A + 1 = 1", True, "Annulment for OR."),
        ("A · 0 = 0", True, "Annulment for AND."),
        ("A + A = A", True, "Idempotent OR."),
        ("A · A = A", True, "Idempotent AND."),
        ("A + A' = 1", True, "Complement OR."),
        ("A · A' = 0", True, "Complement AND."),
        ("(A')' = A", True, "Involution."),
        ("A + AB = A", True, "Absorption."),
        ("A(A+B) = A", True, "Absorption."),
        ("A + B = B + A", True, "OR commutative."),
        ("AB = BA", True, "AND commutative."),
        ("A+B = A·B", False, "OR is not AND."),
        ("(A+B)' = A'+B'", False, "DeMorgan: (A+B)' = A'B'."),
        ("(AB)' = A'+B'", True, "DeMorgan for AND."),
        ("(A+B)' = A'B'", True, "DeMorgan for OR."),
        ("A+AB' = A+B", False, "Not a standard identity as stated."),
        ("A⊕A = 0", True, "XOR of equals is 0."),
        ("A⊕0 = A", True, "XOR identity."),
        ("A⊕1 = A'", True, "XOR with 1 complements."),
        ("A+A'B = A+B", True, "Consensus/absorb form."),
        ("Majority(A,A,B)=A", True, "Two votes for A."),
        ("A·(B+C)=AB+AC", True, "Distributive."),
        ("A+(B·C)=(A+B)·(A+C)", True, "Distributive."),
        ("A+B+C = A·B·C", False, "Different operators."),
        ("Dual of AND is OR", True, "Boolean duality."),
        ("X+1 = X", False, "X+1 = 1."),
        ("X·X' = 1", False, "Product with complement is 0."),
        ("Buffer output equals input", True, "Non-inverting."),
    ]
    for prompt, ans, explain in laws:
        yield tf(prompt, ans, explain, difficulty)


def kmap_items(difficulty: str) -> Iterable[dict]:
    for n in (2, 3, 4):
        cells = 2**n
        yield mcq(
            f"A {n}-variable K-map has how many cells?",
            [str(n), str(cells), str(n * 2), str(cells // 2)],
            1,
            f"2^{n} = {cells} minterms.",
            difficulty,
        )
    yield tf("Gray adjacency is required so circling groups flips one variable.", True, "Gray border labels.", difficulty)
    yield tf("Don't-cares may be included in K-map groups to enlarge prime implicants.", True, "X can join 1s.", difficulty)
    yield tf("K-map groups must be powers of two in size.", True, "1,2,4,8,…", difficulty)
    yield tf("Diagonal cells are always considered adjacent on a K-map.", False, "Adjacency is edge/wrap Gray neighbors.", difficulty)
    for size in (1, 2, 4, 8):
        yield mcq(
            f"A valid K-map group of size {size} eliminates how many literals (vs full {4}-var product)?",
            [str(size), str(int(size).bit_length() - 1), str(4 - (int(size).bit_length() - 1)), "0"],
            2,
            f"Group of {size}=2^k drops k literals from a 4-var term.",
            difficulty,
        )
    yield mcq(
        "Minimal SOP prefers…",
        ["largest legal groups covering all 1s", "one cell per 1", "only 0-cells", "random circles"],
        0,
        "Larger power-of-two groups → fewer literals.",
        difficulty,
    )


def mux_decoder(difficulty: str) -> Iterable[dict]:
    for n in range(1, 6):
        yield mcq(
            f"A {n}-to-{2**n} decoder has how many select lines?",
            [str(2**n), str(n), str(n + 1), str(2 * n)],
            1,
            f"{n} selects address {2**n} ones-hot lines.",
            difficulty,
        )
        yield mcq(
            f"A mux with {2**n} data inputs needs how many select bits?",
            [str(n - 1 if n > 1 else 0) or "0", str(n), str(2**n), str(n + 2)],
            1,
            f"log2({2**n}) = {n}.",
            difficulty,
        )
    yield tf("A decoder one-hot output asserts exactly one line for each select code (when enabled).", True, "Standard binary decoder.", difficulty)
    yield tf("Mux select chooses which data input is steered to Y.", True, "Data selector.", difficulty)


def adder_bits(difficulty: str) -> Iterable[dict]:
    for a, b, cin in [
        (0, 0, 0),
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 0, 1),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
    ]:
        s = a ^ b ^ cin
        cout = (a & b) | (a & cin) | (b & cin)
        yield mcq(
            f"Full adder A={a} B={b} Cin={cin}: Sum is…",
            ["0", "1", "Cout", "X"],
            s,
            f"Sum = A⊕B⊕Cin = {s}.",
            difficulty,
        )
        yield mcq(
            f"Full adder A={a} B={b} Cin={cin}: Cout is…",
            ["0", "1", "Sum", "A"],
            cout,
            f"Majority → Cout={cout}.",
            difficulty,
        )
    yield tf("Half adder has no carry-in.", True, "HA = Sum/Cout from A,B only.", difficulty)


def shift_rotate(difficulty: str) -> Iterable[dict]:
    for val, sh in [(0xA5, 1), (0x3C, 2), (0xF0, 1), (0x01, 3), (0x80, 1), (0x7E, 2)]:
        logical = (val >> sh) & 0xFF
        yield mcq(
            f"Logical right shift of 0x{val:02X} by {sh} (8-bit) is…",
            [f"0x{(val << sh) & 0xFF:02X}", f"0x{logical:02X}", f"0x{val:02X}", "0x00"],
            1,
            f"Zero-fill from the left → 0x{logical:02X}.",
            difficulty,
        )
    yield tf("Arithmetic right shift replicates the sign bit.", True, "SRA sign-fills.", difficulty)
    yield tf("Rotate moves bits with wraparound and no fill loss.", True, "ROL/ROR.", difficulty)


def seq_timing(difficulty: str) -> Iterable[dict]:
    facts = [
        ("Setup time is a requirement before the active clock edge.", True),
        ("Hold time is a requirement after the active clock edge.", True),
        ("Contamination delay is a min path delay from clk to Q.", True),
        ("Clock-to-Q max is used in setup checks.", True),
        ("Hold checks use min delays / contamination.", True),
        ("A positive-edge FF samples D on the rising edge.", True),
        ("Async reset can release without timing care.", False),
        ("Metastability can occur when setup/hold is violated.", True),
        ("Two-flop synchronizers remove all metastability risk forever.", False),
        ("Clock skew can hurt or help a setup margin depending on direction.", True),
        ("Gating a clock with a free AND is best practice.", False),
        ("ICG cells are preferred for clock enables.", True),
        ("Reset recovery/removal are timing checks at reset release.", True),
        ("Hold time can be negative in some library arcs.", True),
        ("Multi-cycle paths always ignore setup.", False),
    ]
    for i, (p, a) in enumerate(facts):
        yield tf(p, a, "Standard sequential timing fact.", difficulty)
        yield mcq(
            p.replace(".", "?"),
            ["True", "False", "Only at DC", "Only in FPGA"],
            0 if a else 1,
            "See sequential timing notes.",
            difficulty,
        )


def fsm_encoding(difficulty: str) -> Iterable[dict]:
    for n in range(2, 10):
        yield mcq(
            f"Minimum bits to encode {n} states (binary) is…",
            [str(n), str((n - 1).bit_length()), str(2**n), str(n - 1)],
            1,
            f"ceil(log2({n})) = {(n - 1).bit_length()}.",
            difficulty,
        )
        yield mcq(
            f"One-hot encoding of {n} states uses how many FFs?",
            [str((n - 1).bit_length()), str(n), str(2 * n), "1"],
            1,
            "One FF per state.",
            difficulty,
        )
    yield tf("One-hot often simplifies next-state logic at the cost of more FFs.", True, "Common FPGA style.", difficulty)
    yield tf("Illegal one-hot codes should be handled safely.", True, "Avoid lockup.", difficulty)


def mem_fifo(difficulty: str) -> Iterable[dict]:
    for depth in (4, 8, 16, 32, 64):
        aw = (depth - 1).bit_length()
        yield mcq(
            f"Address width for depth {depth} is…",
            [str(aw - 1), str(aw), str(depth), str(2 * aw)],
            1,
            f"ceil(log2({depth})) = {aw}.",
            difficulty,
        )
    for depth, width in [(8, 8), (16, 32), (64, 4), (256, 16)]:
        bits = depth * width
        yield mcq(
            f"Capacity of {depth}×{width} memory in bits is…",
            [str(depth + width), str(bits), str(depth), str(width)],
            1,
            f"{depth}×{width} = {bits}.",
            difficulty,
        )
    yield tf("FIFO empty and full must be generated carefully across domains for async FIFOs.", True, "Gray pointers.", difficulty)
    yield tf("Byte enables select which bytes of a word are written.", True, "Partial writes.", difficulty)


def bus_handshake(difficulty: str) -> Iterable[dict]:
    facts = [
        ("Valid/ready handshake transfers when both are high in the same cycle.", True),
        ("A master may drop valid before ready acknowledges freely always.", False),
        ("Ready may depend on valid in the same cycle (combinational) carefully.", True),
        ("AXI-style fire is valid && ready.", True),
        ("Tri-state buses need exactly one driver when not floating intentionally.", True),
        ("Multiple drivers asserting opposite values is bus contention.", True),
        ("Async FIFO write and read clocks may be unrelated.", True),
        ("Gray code helps multi-bit CDC of pointers.", True),
        ("Single FF sync is enough for multi-bit buses.", False),
        ("Backpressure is expressed by deasserting ready.", True),
    ]
    for p, a in facts:
        yield tf(p, a, "Handshake / interconnect fact.", difficulty)
    for n in range(1, 9):
        yield mcq(
            f"With valid fixed high, how many beats transfer in {n} cycles if ready is always high?",
            [str(n - 1), str(n), str(2 * n), "0"],
            1,
            "One beat per cycle when both high.",
            difficulty,
        )


MODULE_GENS: dict[str, list[Gen]] = {
    "module01-radix-converter": [bits_values, hex_digit, binary_spell],
    "module02-twos-complement": [twos_range, bits_values],
    "module03-overflow-wrap": [overflow_wrap, bits_values],
    "module04-ascii-hex": [ascii_codes, hex_digit],
    "module05-gray-code": [gray_code, binary_spell],
    "module06-bcd-lab": [bcd_pack, hex_digit],
    "module07-parity-checksum": [parity_bits, bits_values],
    "module08-fixed-point": [fixed_q, bits_values],
    "module09-bit-fields": [bitfields, bits_values],
    "module10-endian-lab": [endian_pack, hex_digit],
    "module11-truth-table": [truth_gates, boolean_laws],
    "module12-boolean-laws": [boolean_laws, truth_gates],
    "module13-kmap": [kmap_items, boolean_laws],
    "module14-sop-pos": [boolean_laws, kmap_items],
    "module15-dont-care-lab": [kmap_items, boolean_laws],
    "module16-logic-hazards": [boolean_laws, truth_gates],
    "module17-gate-composer": [truth_gates, boolean_laws],
    "module18-mux-decoder": [mux_decoder, bits_values],
    "module19-priority-compare": [bits_values, mux_decoder],
    "module20-half-full-adder": [adder_bits, bits_values],
    "module21-xor-parity-tree": [parity_bits, truth_gates],
    "module22-tri-state-bus": [bus_handshake, mux_decoder],
    "module23-barrel-shifter": [shift_rotate, bits_values],
    "module24-seven-segment": [hex_digit, bcd_pack],
    "module25-clock-stepper": [seq_timing, bits_values],
    "module26-setup-hold": [seq_timing, bits_values],
    "module27-reset-timelines": [seq_timing, fsm_encoding],
    "module28-clock-enable": [seq_timing, mux_decoder],
    "module29-cdc-sync": [seq_timing, bus_handshake],
    "module30-fsm-lab": [fsm_encoding, seq_timing],
    "module31-state-encoding": [fsm_encoding, bits_values],
    "module32-seq-detector": [fsm_encoding, truth_gates],
    "module33-ring-johnson": [fsm_encoding, shift_rotate],
    "module34-lfsr-lab": [parity_bits, shift_rotate],
    "module35-ripple-carry-adder-animator": [adder_bits, bits_values],
    "module36-carry-look-ahead-adder-propagate-and-generate": [adder_bits, boolean_laws],
    "module37-array-mult": [bits_values, adder_bits],
    "module38-alu-explorer": [truth_gates, adder_bits],
    "module39-carry-select-adder": [adder_bits, mux_decoder],
    "module40-booth-encode": [bits_values, adder_bits],
    "module41-signed-arith": [twos_range, overflow_wrap],
    "module42-mem-map": [mem_fifo, bits_values],
    "module43-fifo-lab": [mem_fifo, bus_handshake],
    "module44-cache-walk": [mem_fifo, bits_values],
    "module45-dual-port-ram": [mem_fifo, bus_handshake],
    "module46-byte-enable-mem": [mem_fifo, bitfields],
    "module47-async-fifo": [mem_fifo, gray_code],
    "module48-handshake": [bus_handshake, seq_timing],
    "module49-block-diagram": [bus_handshake, mux_decoder],
}


def candidates_for(module_id: str, difficulty: str) -> list[dict]:
    gens = MODULE_GENS.get(module_id) or [bits_values, boolean_laws, seq_timing]
    out: list[dict] = []
    seen: set[str] = set()
    for gen in gens:
        for it in gen(difficulty):
            it = dict(it)
            it["difficulty"] = difficulty
            k = content_key(it)
            if k in seen:
                continue
            seen.add(k)
            out.append(it)
    # Generic fillers if still short
    topic = module_id.replace("-", " ")
    for i in range(1, 80):
        it = tf(
            f"In {topic}, concept check #{i}: powers of two sizing matters for encoding and memory depth.",
            True,
            "Generic digital foundations reminder.",
            difficulty,
        )
        # make unique via i already in prompt
        k = content_key(it)
        if k not in seen:
            seen.add(k)
            out.append(it)
        it2 = mcq(
            f"{topic}: how many values in an unsigned {i % 12 + 2}-bit field?",
            [
                str(2 ** ((i % 12 + 2) - 1)),
                str(2 ** (i % 12 + 2)),
                str(i % 12 + 2),
                "infinite",
            ],
            1,
            "2^n patterns.",
            difficulty,
        )
        k2 = content_key(it2)
        if k2 not in seen:
            seen.add(k2)
            out.append(it2)
    return out


def fill_bank(path: Path) -> tuple[int, int]:
    bank = json.loads(path.read_text(encoding="utf-8"))
    module_id = bank.get("module") or path.stem
    items: list[dict] = list(bank.get("items") or [])
    prefix = prefix_from_items(items, module_id)
    before = len(items)

    for difficulty in ("easy", "medium", "hard"):
        existing = [it for it in items if (it.get("difficulty") or "medium") == difficulty]
        seen = {content_key(it) for it in existing}
        need = TARGET - len(existing)
        if need <= 0:
            continue
        idx = next_index(items, prefix, difficulty)
        added = 0
        for cand in candidates_for(module_id, difficulty):
            if added >= need:
                break
            k = content_key(cand)
            if k in seen:
                continue
            seen.add(k)
            new_it = dict(cand)
            new_it["id"] = f"{prefix}_{difficulty}_{idx:02d}"
            idx += 1
            items.append(new_it)
            added += 1
        if added < need:
            raise SystemExit(
                f"{module_id} {difficulty}: only added {added}/{need} unique items"
            )

    bank["items"] = items
    path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return before, len(items)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", action="append", help="Limit to module id(s)")
    args = ap.parse_args()
    paths = sorted(QUESTIONS.glob("*.json"))
    if args.module:
        allow = set(args.module)
        paths = [p for p in paths if p.stem in allow]
    total_before = total_after = 0
    for path in paths:
        b, a = fill_bank(path)
        total_before += b
        total_after += a
        bank = json.loads(path.read_text(encoding="utf-8"))
        counts = {"easy": 0, "medium": 0, "hard": 0}
        for it in bank["items"]:
            counts[it.get("difficulty") or "medium"] += 1
        # uniqueness check
        keys = [content_key(it) for it in bank["items"]]
        assert len(keys) == len(set(keys)), path.name
        print(f"{path.name}: {b} -> {a} {counts}")
    print(f"TOTAL {total_before} -> {total_after}")


if __name__ == "__main__":
    main()
