#!/usr/bin/env python3
"""Bind each quiz item to a digital_learning tool challenge / instrument state.

Adds item['tool_capture'] used by capture_item_figures.py so stems are not
all the same shared starter screenshot.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # quiz_challenge_platform/
COURSE = ROOT / "content" / "learn_digital"


def _click_starter(tool: str, starter: str, key: str = "starter", label: str = "Starter") -> dict:
    return {
        "tool": tool,
        "key": key,
        "label": label,
        "steps": [{"click": starter}],
    }


def _challenge(tool: str, title: str, key: str | None = None, load: str | None = "#chal-load") -> dict:
    steps: list[dict] = [{"challenge": title}]
    if load:
        steps.append({"click": load})
    return {
        "tool": tool,
        "key": key or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40],
        "label": title,
        "steps": steps,
    }


# ---------------------------------------------------------------------------
# module01 — radix-converter
# ---------------------------------------------------------------------------


def radix_capture(item: dict) -> dict:
    p = item.get("prompt") or ""
    pl = p.lower()

    m = re.search(r"hex digit\s+([0-9a-f])\b", pl, re.I)
    if m:
        d = m.group(1).upper()
        return {
            "tool": "radix-converter",
            "key": f"hex-digit-{d}",
            "label": f"Width 4 · hex {d}",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-hex", "value": d},
            ],
        }

    m = re.search(r"(\d+)\s*bits?\s+represent", pl)
    if m:
        n = max(1, min(32, int(m.group(1))))
        steps: list[dict] = [
            {"select": "#rc-width", "value": str(n) if n in (4, 8, 16, 32) else "8"},
        ]
        if n not in (4, 8, 16, 32):
            steps.append({"fill": "#rc-width-custom", "value": str(n), "enter": True})
        steps.append({"fill": "#rc-udec", "value": "0"})
        return {
            "tool": "radix-converter",
            "key": f"width-{n}",
            "label": f"Width {n}",
            "steps": steps,
        }

    if "0b1010" in pl or "what decimal is 0b1010" in pl:
        return {
            "tool": "radix-converter",
            "key": "bin-1010",
            "label": "0b1010",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-bin", "value": "1010"},
            ],
        }

    if "valid 4-bit" in pl and "decimal 3" in pl:
        return {
            "tool": "radix-converter",
            "key": "udec-3-w4",
            "label": "Width 4 · decimal 3",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-udec", "value": "3"},
            ],
        }

    if "valid 4-bit" in pl and "decimal 7" in pl:
        return {
            "tool": "radix-converter",
            "key": "udec-7-w4",
            "label": "Width 4 · decimal 7",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-udec", "value": "7"},
            ],
        }

    if "writing 5 as 0b101" in pl or ("0b101" in pl and "0x5" in pl):
        return {
            "tool": "radix-converter",
            "key": "same-5",
            "label": "Width 8 · 5",
            "steps": [
                {"select": "#rc-width", "value": "8"},
                {"fill": "#rc-udec", "value": "5"},
            ],
        }

    if "hex digit" in pl and "bit" in pl:
        return {
            "tool": "radix-converter",
            "key": "nibble-group",
            "label": "Width 4 nibble",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-hex", "value": "A"},
            ],
        }

    if "0xff" in pl or "ff" in pl:
        if "signed" in pl or "two" in pl:
            return {
                "tool": "radix-converter",
                "key": "signed-ff",
                "label": "Width 8 · 0xFF signed",
                "steps": [
                    {"select": "#rc-width", "value": "8"},
                    {"fill": "#rc-hex", "value": "FF"},
                ],
            }
        return {
            "tool": "radix-converter",
            "key": "hex-ff",
            "label": "Width 8 · 0xFF unsigned",
            "steps": [
                {"select": "#rc-width", "value": "8"},
                {"fill": "#rc-hex", "value": "FF"},
            ],
        }

    if "sign extension" in pl or "1111" in pl:
        return {
            "tool": "radix-converter",
            "key": "sext-nibble",
            "label": "Width 4 all-ones then compare",
            "steps": [
                {"select": "#rc-width", "value": "4"},
                {"fill": "#rc-bin", "value": "1111"},
            ],
        }

    if "msb" in pl or ("sign" in pl and "bit" in pl):
        return {
            "tool": "radix-converter",
            "key": "msb-sign",
            "label": "MSB only",
            "steps": [
                {"select": "#rc-width", "value": "8"},
                {"fill": "#rc-bin", "value": "10000000"},
            ],
        }

    if "identical bits" in pl or "different types" in pl or "different integers" in pl:
        return {
            "tool": "radix-converter",
            "key": "type-view-ff",
            "label": "0xFF signed vs unsigned",
            "steps": [
                {"select": "#rc-width", "value": "8"},
                {"fill": "#rc-hex", "value": "FF"},
            ],
        }

    if "same hex text" in pl or "bit budgets" in pl:
        return {
            "tool": "radix-converter",
            "key": "hex-a-w8",
            "label": "Width 8 · hex A",
            "steps": [
                {"select": "#rc-width", "value": "8"},
                {"fill": "#rc-hex", "value": "A"},
            ],
        }

    if "spellings" in pl or "best seen as" in pl or "readings" in pl:
        return {
            "tool": "radix-converter",
            "key": "same-spellings-2a",
            "label": "Starter 42 / 0x2A",
            "steps": [{"click": "#rc-starter"}],
        }

    return _click_starter("radix-converter", "#rc-starter", "starter-2a", "Starter 42 / 0x2A")


# ---------------------------------------------------------------------------
# module13 — kmap
# ---------------------------------------------------------------------------


def kmap_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()

    if "adjacent" in p or "gray ordering" in p or "geometric neighbors" in p:
        return _challenge("kmap", "XOR (2)", "xor2")

    if "wrap-around" in p or "left and right columns" in p:
        return _challenge("kmap", "Quad group", "wrap-quad")

    if "cells" in p and ("a,b" in p or "a, b" in p or "inputs a" in p):
        return _challenge("kmap", "AND (2)", "and2")

    if "3-input" in p or "3-input k-map" in p or "minterm slots" in p:
        return _challenge("kmap", "Majority (3)", "maj3-slots")

    if "power-of-two" in p or "1, 2, 4" in p or "grouping means" in p:
        return _challenge("kmap", "Quad group", "pow2-quad")

    if "don't care" in p or "dont care" in p or "x entries" in p or ("x " in p and "minimizing" in p):
        return _challenge("kmap", "Don’t cares fill", "dc-fill")

    if "essential" in p or "prime" in p or "shared onset" in p:
        return _challenge("kmap", "Majority (3)", "majority3")

    if "group at most" in p or "4-variable map" in p:
        return _challenge("kmap", "Σm(1,5,9,13)", "4var-sum")

    if "quad" in p and "eliminat" in p:
        return _challenge("kmap", "Quad group", "4var-quad")

    if ("classic" in p and "output" in p) or "sop" in p or "minimal" in p:
        return _challenge("kmap", "Pick SOP: XOR", "sop-xor")

    return _challenge("kmap", "XOR (2)", "xor2")


# ---------------------------------------------------------------------------
# module26 — setup-hold
# ---------------------------------------------------------------------------


def timing_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()

    if "setup violation" in p:
        return {
            "tool": "setup-hold",
            "key": "setup_fail",
            "label": "Setup violation",
            "steps": [{"click": "[data-preset='setup_fail']"}],
        }
    if "hold" in p and ("fix" in p or "short path" in p or "must not change" in p or "after the capturing" in p):
        if "violation" in p or "fix" in p:
            return {
                "tool": "setup-hold",
                "key": "hold_fail",
                "label": "Hold violation",
                "steps": [{"click": "[data-preset='hold_fail']"}],
            }
        return {
            "tool": "setup-hold",
            "key": "clean-hold",
            "label": "Clean · hold window",
            "steps": [{"click": "[data-preset='clean']"}],
        }
    if "setup time" in p or "tsu" in p or "faster clock" in p:
        return {
            "tool": "setup-hold",
            "key": "clean-setup",
            "label": "Clean · setup window",
            "steps": [{"click": "[data-preset='clean']"}],
        }
    if "clock-to-q" in p or "tcq" in p or "q is valid" in p or "updates q" in p:
        return {
            "tool": "setup-hold",
            "key": "clean-tcq",
            "label": "Clean · tcq",
            "steps": [{"click": "[data-preset='clean']"}],
        }
    if "skew" in p or "tight" in p or "simultaneously" in p:
        return {
            "tool": "setup-hold",
            "key": "tight",
            "label": "Tight but legal",
            "steps": [{"click": "[data-preset='tight']"}],
        }
    if "uncertainty" in p:
        return {
            "tool": "setup-hold",
            "key": "clean",
            "label": "Clean pass",
            "steps": [{"click": "[data-preset='clean']"}],
        }
    return {
        "tool": "setup-hold",
        "key": "clean",
        "label": "Clean pass",
        "steps": [{"click": "[data-preset='clean']"}],
    }


# ---------------------------------------------------------------------------
# Remaining modules — prompt → challenge / control recipes
# ---------------------------------------------------------------------------


def twos_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "twos-complement"
    if "msb" in p:
        return _challenge(tool, "Quiz: MSB", "quiz-msb", load=None)
    if "form −x" in p or "form -x" in p or "negate" in p:
        if "+5" in p or "negate +5" in p:
            return {
                "tool": tool,
                "key": "negate-plus5",
                "label": "Negate +5",
                "steps": [{"click": "#tc2-starter"}, {"click": "#btn-negate"}],
            }
        return _challenge(tool, "Quiz: negate", "quiz-negate", load=None)
    if "every bit set" in p or "−1" in p or "-1 is represented" in p:
        return {
            "tool": tool,
            "key": "all-ones",
            "label": "Set −1",
            "steps": [
                {"select": "#width-sel", "value": "8"},
                {"fill": "#signed-in", "value": "-1"},
                {"click": "#btn-apply-signed"},
            ],
        }
    if "0x80" in p:
        return {
            "tool": tool,
            "key": "min-8",
            "label": "8-bit min 0x80",
            "steps": [
                {"select": "#width-sel", "value": "8"},
                {"fill": "#signed-in", "value": "-128"},
                {"click": "#btn-apply-signed"},
            ],
        }
    if "minimum" in p:
        m = re.search(r"width\s+(\d+)", p)
        w = m.group(1) if m and m.group(1) in ("4", "8", "16") else "8"
        steps = [{"select": "#width-sel", "value": w}]
        if w == "8":
            steps.append({"click": "#tc2-starter"})
        else:
            # show most-negative by setting signed min approx via wrap demo path
            steps.extend(
                [
                    {"fill": "#signed-in", "value": str(-(1 << (int(w) - 1)))},
                    {"click": "#btn-apply-signed"},
                ]
            )
        return {
            "tool": tool,
            "key": f"min-w{w}",
            "label": f"Width {w} min",
            "steps": steps,
        }
    if "maximum" in p:
        return _challenge(tool, "Quiz: 8-bit max", "quiz-max", load=None)
    if "wrap" in p or "200" in p:
        return {
            "tool": tool,
            "key": "wrap-200",
            "label": "Wrap 200",
            "steps": [{"click": "#btn-wrap-demo"}],
        }
    if "widen" in p or "all-ones" in p:
        return {
            "tool": tool,
            "key": "widen-ones",
            "label": "Width 4 −1",
            "steps": [
                {"select": "#width-sel", "value": "4"},
                {"fill": "#signed-in", "value": "-1"},
                {"click": "#btn-apply-signed"},
            ],
        }
    return _click_starter(tool, "#tc2-starter", "starter-plus5", "Starter +5")


def overflow_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "overflow-wrap"
    if "14+3" in p or "14 + 3" in p or "unsigned 14" in p:
        return {
            "tool": tool,
            "key": "u-14-plus-3",
            "label": "Unsigned 14+3 @4",
            "steps": [
                {"click": "input[name=mode][value=unsigned]"},
                {"select": "#w-sel", "value": "4"},
                {"fill": "#a-in", "value": "14"},
                {"fill": "#b-in", "value": "3"},
                {"click": "#btn-add"},
            ],
        }
    if "0111 + 0001" in p or "signed 0111" in p or "7+1" in p:
        return {
            "tool": tool,
            "key": "s-7-plus-1",
            "label": "Signed 7+1 @4",
            "steps": [
                {"click": "input[name=mode][value=signed]"},
                {"select": "#w-sel", "value": "4"},
                {"fill": "#a-in", "value": "7"},
                {"fill": "#b-in", "value": "1"},
                {"click": "#btn-add"},
            ],
        }
    if "carry" in p and "overflow" in p:
        return _challenge(tool, "Quiz: flags", "quiz-flags", load=None)
    if "signed overflow" in p:
        return {
            "tool": tool,
            "key": "demo-signed",
            "label": "Demo signed",
            "steps": [{"click": "#btn-demo-s"}],
        }
    if "unsigned" in p or "wrap" in p:
        return {
            "tool": tool,
            "key": "demo-unsigned",
            "label": "Demo unsigned",
            "steps": [{"click": "#btn-demo-u"}],
        }
    return _click_starter(tool, "#ow-starter")


def ascii_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "ascii-hex"
    if "printable" in p or "space" in p:
        return {
            "tool": tool,
            "key": "space",
            "label": "Write space",
            "steps": [{"click": "#btn-sp"}],
        }
    if "line feed" in p or " lf" in p or "lf)" in p:
        return {
            "tool": tool,
            "key": "lf",
            "label": "LF",
            "steps": [{"click": "#btn-lf"}],
        }
    if " cr" in p or "carriage" in p:
        return {
            "tool": tool,
            "key": "cr",
            "label": "CR via text",
            "steps": [
                {"fill": "#text-in", "value": "\r"},
                {"click": "#btn-load-text"},
            ],
        }
    if "nul" in p or "'0'" in p or "integer 0" in p:
        return {
            "tool": tool,
            "key": "nul",
            "label": "NUL",
            "steps": [{"click": "#btn-nul"}],
        }
    if "'a'" in p or "letter" in p:
        return {
            "tool": tool,
            "key": "letter-a",
            "label": "Load A",
            "steps": [
                {"fill": "#text-in", "value": "A"},
                {"click": "#btn-load-text"},
            ],
        }
    return _click_starter(tool, "#ah-starter", "starter-hi", "Starter Hi")


def gray_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "gray-code"
    if "binary → gray" in p or "binary -> gray" in p or "computed as" in p:
        return {
            "tool": tool,
            "key": "formula",
            "label": "Show formula",
            "steps": [{"click": "#gc-starter"}, {"click": "#btn-show-formula"}],
        }
    if "neighbor" in p or "defining gray" in p or "single" in p and "bit" in p:
        return {
            "tool": tool,
            "key": "step-once",
            "label": "Step once",
            "steps": [{"click": "#gc-starter"}, {"click": "#btn-step"}],
        }
    if "k-map" in p or "kmap" in p:
        return {
            "tool": tool,
            "key": "width4-tour",
            "label": "Width 4 tour",
            "steps": [{"click": "#gc-starter"}, {"click": "#btn-step"}, {"click": "#btn-step"}],
        }
    if "synchronizer" in p or "mid-transition" in p or "fifo" in p:
        return _challenge(tool, "Quiz: FIFO", "quiz-fifo", load=None)
    return _click_starter(tool, "#gc-starter")


def bcd_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "bcd-lab"
    if "invalid" in p:
        return {
            "tool": tool,
            "key": "invalid",
            "label": "See invalid",
            "steps": [{"click": "#btn-invalid"}],
        }
    if "42" in p:
        return _click_starter(tool, "#bcd-starter", "starter-42", "Starter 42")
    if "99" in p:
        return {
            "tool": tool,
            "key": "encode-99",
            "label": "Encode 99",
            "steps": [
                {"fill": "#dec-in", "value": "99"},
                {"click": "#btn-encode"},
            ],
        }
    if "digit" in p or "bits" in p:
        return _challenge(tool, "Quiz: bits/digit", "quiz-bits", load=None)
    return _click_starter(tool, "#bcd-starter")


def parity_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "parity-checksum"
    if "odd" in p:
        return {
            "tool": tool,
            "key": "odd",
            "label": "Odd parity",
            "steps": [
                {"click": "#px-starter"},
                {"click": "input[name=mode][value=odd]"},
                {"click": "#btn-compute-p"},
            ],
        }
    if "checksum" in p or "xor" in p:
        return {
            "tool": tool,
            "key": "checksum",
            "label": "XOR checksum",
            "steps": [{"click": "#btn-cs"}],
        }
    if "flip" in p or "detect" in p:
        return {
            "tool": tool,
            "key": "flip-fail",
            "label": "Flip fails",
            "steps": [{"click": "#px-starter"}, {"click": "#btn-attach"}, {"click": "#btn-flip0"}],
        }
    if "even" in p or "parity" in p:
        return {
            "tool": tool,
            "key": "even",
            "label": "Even parity",
            "steps": [{"click": "#px-starter"}, {"click": "#btn-compute-p"}],
        }
    return _click_starter(tool, "#px-starter", "starter-2a", "Starter 0x2A")


def fixed_point_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "fixed-point"
    if "q1.15" in p or "1.15" in p:
        return {
            "tool": tool,
            "key": "q115",
            "label": "Q1.15",
            "steps": [{"click": "#btn-q15"}],
        }
    if "0.5" in p or "half" in p:
        return {
            "tool": tool,
            "key": "half",
            "label": "Encode 0.5",
            "steps": [{"click": "#btn-half"}],
        }
    if "saturat" in p:
        return {
            "tool": tool,
            "key": "sat",
            "label": "Saturate",
            "steps": [{"click": "#btn-sat"}],
        }
    if "scale" in p or "step" in p or "fraction" in p:
        return _click_starter(tool, "#fp-starter", "starter-1.5", "Starter 1.5")
    return _click_starter(tool, "#fp-starter")


def bit_fields_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "bit-fields"
    if "mask" in p:
        return {
            "tool": tool,
            "key": "mask",
            "label": "Show mask",
            "steps": [{"click": "#bf-starter"}, {"click": "#btn-show-mask"}],
        }
    if "extract" in p or "field" in p:
        return {
            "tool": tool,
            "key": "extract",
            "label": "Extract COUNT",
            "steps": [{"click": "#bf-starter"}, {"click": "#btn-extract"}],
        }
    if "insert" in p or "pack" in p:
        return {
            "tool": tool,
            "key": "pack",
            "label": "Pack CSR",
            "steps": [{"click": "#btn-pack"}],
        }
    return _click_starter(tool, "#bf-starter")


def endian_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "endian-lab"
    if "little" in p or " le" in p or "le " in p:
        return {
            "tool": tool,
            "key": "unpack-le",
            "label": "Unpack LE",
            "steps": [
                {"click": "input[name=endian][value=le]"},
                {"click": "#en-starter"},
                {"click": "#btn-unpack"},
            ],
        }
    if "big" in p or "network" in p or " be" in p:
        return {
            "tool": tool,
            "key": "unpack-be",
            "label": "Unpack BE",
            "steps": [
                {"click": "input[name=endian][value=be]"},
                {"click": "#en-starter"},
                {"click": "#btn-unpack"},
            ],
        }
    if "swap" in p:
        return {
            "tool": tool,
            "key": "swap",
            "label": "Byte-swap",
            "steps": [{"click": "#en-starter"}, {"click": "#btn-swap"}],
        }
    return _click_starter(tool, "#en-starter")


def truth_table_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "truth-table"

    def tt_chal(cid: str, key: str, label: str) -> dict:
        return {
            "tool": tool,
            "key": key,
            "label": label,
            "steps": [
                {"select": "#tt-chal-sel", "value": cid},
                {"click": "#tt-chal-start"},
            ],
        }

    if "3 input" in p or "3 inputs" in p or ("three" in p and "row" in p):
        return tt_chal("and3", "and3", "AND (3)")
    if "four variable" in p or "4 variable" in p or "four variables" in p:
        return {
            "tool": tool,
            "key": "n4",
            "label": "4 vars",
            "steps": [{"select": "#tt-n", "value": "4"}, {"click": "#tt-starter"}],
        }
    if "and" in p and "or" not in p:
        return tt_chal("and2", "and2", "AND (2)")
    if "two-input or" in p or (p.startswith("two-input or")) or (" or:" in p):
        return tt_chal("or2", "or2", "OR (2)")
    if "xor" in p:
        return tt_chal("xor2", "xor2", "XOR (2)")
    if "row" in p:
        return tt_chal("and2", "and2-rows", "AND (2) rows")
    return _click_starter(tool, "#tt-starter")


def boolean_laws_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "boolean-laws"
    if "de morgan" in p:
        return _challenge(tool, "Quiz: De Morgan AND", "demorgan", load=None)
    if "absorption" in p:
        return _challenge(tool, "Quiz: absorption", "absorption", load=None)
    if "double negation" in p or "involution" in p:
        return _challenge(tool, "Quiz: double negation", "dneg", load=None)
    if "complement" in p:
        return _challenge(tool, "Quiz: complement", "complement", load=None)
    if "distribut" in p:
        return _challenge(tool, "Quiz: distribute", "distribute", load=None)
    if "idempotent" in p:
        return _challenge(tool, "Quiz: idempotent", "idempotent", load=None)
    return _click_starter(tool, "#btn-starter")


def sop_pos_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "sop-pos"
    if "pos" in p or "product-of-sums" in p or "maxterm" in p:
        return {
            "tool": tool,
            "key": "xor-pos",
            "label": "XOR POS",
            "steps": [{"click": "#sp-starter"}, {"click": "#btn-xor"}],
        }
    if "sop" in p or "minterm" in p or "canonical" in p:
        return {
            "tool": tool,
            "key": "starter-xor",
            "label": "Starter XOR SOP",
            "steps": [{"click": "#sp-starter"}],
        }
    if "and" in p:
        return {
            "tool": tool,
            "key": "preset-and",
            "label": "Preset AND",
            "steps": [{"click": "#btn-and"}],
        }
    return _click_starter(tool, "#sp-starter")


def dont_care_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "dont-care-lab"
    if "without" in p or "ignore" in p:
        return {
            "tool": tool,
            "key": "nodc",
            "label": "Without X",
            "steps": [{"click": "#btn-nodc"}],
        }
    if "minimiz" in p or "cover" in p:
        return {
            "tool": tool,
            "key": "minimize",
            "label": "Minimize",
            "steps": [{"click": "#dc-starter"}, {"click": "#btn-minimize"}],
        }
    if "x" in p or "don't" in p or "dont" in p:
        return {
            "tool": tool,
            "key": "with-x",
            "label": "With X",
            "steps": [{"click": "#btn-starter-preset"}],
        }
    return _click_starter(tool, "#dc-starter")


def logic_hazards_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "logic-hazards"
    if "static-0" in p or "static 0" in p:
        return {
            "tool": tool,
            "key": "static0",
            "label": "Static-0",
            "steps": [{"click": "#btn-static0"}],
        }
    if "dynamic" in p:
        return {
            "tool": tool,
            "key": "dynamic",
            "label": "Dynamic",
            "steps": [{"click": "#btn-dynamic"}],
        }
    if "cover" in p:
        return {
            "tool": tool,
            "key": "cover",
            "label": "Apply cover",
            "steps": [{"click": "#hz-starter"}, {"click": "#btn-cover"}],
        }
    if "static" in p:
        return {
            "tool": tool,
            "key": "static1",
            "label": "Static-1",
            "steps": [{"click": "#hz-starter"}, {"click": "#btn-run"}],
        }
    return _click_starter(tool, "#hz-starter")


def gate_composer_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "gate-composer"
    # Catalog click loads the netlist; no separate #chal-load
    if "nand" in p:
        return _challenge(tool, "NAND (2)", "nand2", load=None)
    if "xor" in p:
        return _challenge(tool, "XOR (2)", "xor2", load=None)
    if "mux" in p:
        return _challenge(tool, "2:1 mux", "mux21", load=None)
    if "majority" in p:
        return _challenge(tool, "Majority (3)", "majority3", load=None)
    if "or" in p and "and" not in p:
        return _challenge(tool, "OR (2)", "or2", load=None)
    if "and" in p or "inverter" in p or "not" in p:
        return _challenge(tool, "AND (2)", "and2", load=None)
    return _click_starter(tool, "#gc-starter")


def mux_decoder_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "mux-decoder"
    if "decoder" in p or "one-hot" in p or "2→4" in p or "2->4" in p:
        return _challenge(tool, "2→4: Y0", "dec-y0")
    if "4:1" in p or "4-to-1" in p:
        return _challenge(tool, "4:1 select D2", "mux41")
    if "2:1" in p or "mux" in p:
        return _challenge(tool, "2:1 pick D0", "mux21")
    return {
        "tool": tool,
        "key": "starter",
        "label": "Starter",
        "steps": [{"click": "#btn-starter"}],
    }


def half_full_adder_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "half-full-adder"
    if "ripple" in p:
        return {
            "tool": tool,
            "key": "ripple",
            "label": "Ripple 1+3",
            "steps": [{"click": "#btn-ripple"}],
        }
    if "full" in p or "cout" in p or "cin" in p:
        return {
            "tool": tool,
            "key": "fa",
            "label": "Preset FA",
            "steps": [{"click": "#btn-fa"}],
        }
    if "half" in p:
        return {
            "tool": tool,
            "key": "ha",
            "label": "Preset HA",
            "steps": [{"click": "#btn-ha"}],
        }
    return _click_starter(tool, "#ha-starter")


def xor_parity_tree_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "xor-parity-tree"
    if "depth" in p or "tree" in p:
        return _challenge(tool, "Depth 4", "depth4", load=None)
    if "0xa5" in p or "a5" in p or "8-bit" in p:
        return _challenge(tool, "8-bit 0xA5", "a5", load=None)
    return _click_starter(tool, "#xp-starter")


def tri_state_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "tri-state-bus"
    if "contention" in p or "conflict" in p:
        return {
            "tool": tool,
            "key": "contention",
            "label": "Contention",
            "steps": [{"click": "#btn-fight"}],
        }
    if "high-z" in p or "high z" in p or "hi-z" in p or "impedance" in p or "float" in p:
        return {
            "tool": tool,
            "key": "see-z",
            "label": "See Z",
            "steps": [{"click": "#btn-float"}],
        }
    return _click_starter(tool, "#ts-starter")


def barrel_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "barrel-shifter"
    if "sra" in p or "arithmetic" in p:
        return {
            "tool": tool,
            "key": "sra",
            "label": "SRA preset",
            "steps": [{"click": "#btn-sra"}],
        }
    if "rol" in p or "rotate" in p:
        return {
            "tool": tool,
            "key": "rol",
            "label": "ROL preset",
            "steps": [{"click": "#btn-rol"}],
        }
    return _click_starter(tool, "#bs-starter")


def seven_seg_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "seven-segment"
    if "all on" in p or "blank" in p or "eight" in p:
        return {
            "tool": tool,
            "key": "all-on",
            "label": "All on",
            "steps": [{"click": "#btn-8"}],
        }
    if "anode" in p:
        return {
            "tool": tool,
            "key": "anode",
            "label": "Anode",
            "steps": [{"click": "#btn-anode"}],
        }
    if "digit" in p or "segment" in p or "hex" in p:
        return {
            "tool": tool,
            "key": "digit-f",
            "label": "Digit F",
            "steps": [{"click": "#btn-f"}],
        }
    return _click_starter(tool, "#ss-starter")


def priority_compare_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "priority-compare"
    # Catalog click selects; no separate load button on many labs
    if "signed" in p:
        return _challenge(tool, "Signed −1 vs 1", "signed-cmp", load=None)
    if "flag" in p:
        return _challenge(tool, "Flags disagree", "flags", load=None)
    if "equal" in p:
        return _challenge(tool, "Compare equal", "equal", load=None)
    if "priority" in p or "wins" in p:
        return _challenge(tool, "High-pri: I2 wins", "pri-i2", load=None)
    return {
        "tool": tool,
        "key": "starter",
        "label": "Starter",
        "steps": [{"click": "#btn-starter"}],
    }

def clock_stepper_capture(item: dict) -> dict:
    p = (item.get("prompt") or "").lower()
    tool = "clock-stepper"
    if "counter" in p:
        return _challenge(tool, "4-bit counter", "counter", load=None)
    if "shift" in p:
        return _challenge(tool, "4-bit shift register", "shift", load=None)
    if "enable" in p or "register" in p:
        return _challenge(tool, "Register + enable", "reg-en", load=None)
    if "pipeline" in p:
        return _challenge(tool, "2-stage pipeline", "pipe", load=None)
    return _click_starter(tool, "#cs-starter")


def generic_starter(tool: str, starter: str):
    def _fn(_item: dict) -> dict:
        return _click_starter(tool, starter)

    return _fn


BINDERS = {
    "module01-radix-converter": radix_capture,
    "module02-twos-complement": twos_capture,
    "module03-overflow-wrap": overflow_capture,
    "module04-ascii-hex": ascii_capture,
    "module05-gray-code": gray_capture,
    "module06-bcd-lab": bcd_capture,
    "module07-parity-checksum": parity_capture,
    "module08-fixed-point": fixed_point_capture,
    "module09-bit-fields": bit_fields_capture,
    "module10-endian-lab": endian_capture,
    "module11-truth-table": truth_table_capture,
    "module12-boolean-laws": boolean_laws_capture,
    "module13-kmap": kmap_capture,
    "module14-sop-pos": sop_pos_capture,
    "module15-dont-care-lab": dont_care_capture,
    "module16-logic-hazards": logic_hazards_capture,
    "module17-gate-composer": gate_composer_capture,
    "module18-mux-decoder": mux_decoder_capture,
    "module19-priority-compare": priority_compare_capture,
    "module20-half-full-adder": half_full_adder_capture,
    "module21-xor-parity-tree": xor_parity_tree_capture,
    "module22-tri-state-bus": tri_state_capture,
    "module23-barrel-shifter": barrel_capture,
    "module24-seven-segment": seven_seg_capture,
    "module25-clock-stepper": clock_stepper_capture,
    "module26-setup-hold": timing_capture,
    # module27–49: starter instrument (unique heuristics can be layered later)
    "module27-reset-timelines": generic_starter("reset-timelines", "#rt-starter"),
    "module28-clock-enable": generic_starter("clock-enable", "#ce-starter"),
    "module29-cdc-sync": generic_starter("cdc-sync", "#cdc-starter"),
    "module30-fsm-lab": generic_starter("fsm-lab", "#btn-starter"),
    "module31-state-encoding": generic_starter("state-encoding", "#btn-starter"),
    "module32-seq-detector": generic_starter("seq-detector", "#btn-starter"),
    "module33-ring-johnson": generic_starter("ring-johnson", "#rj-starter"),
    "module34-lfsr-lab": generic_starter("lfsr-lab", "#lfsr-starter"),
    "module35-ripple-carry-adder-animator": generic_starter(
        "ripple-carry-adder-animator", "#btn-starter"
    ),
    "module36-carry-look-ahead-adder-propagate-and-generate": generic_starter(
        "carry-look-ahead-adder-propagate-and-generate", "#btn-starter"
    ),
    "module37-array-mult": generic_starter("array-mult", "#btn-starter"),
    "module38-alu-explorer": generic_starter("alu-explorer", "#btn-starter"),
    "module39-carry-select-adder": generic_starter("carry-select-adder", "#csa-starter"),
    "module40-booth-encode": generic_starter("booth-encode", "#booth-starter"),
    "module41-signed-arith": generic_starter("signed-arith", "#sa-starter"),
    "module42-mem-map": generic_starter("mem-map", "#btn-starter"),
    "module43-fifo-lab": generic_starter("fifo-lab", "#btn-starter"),
    "module44-cache-walk": generic_starter("cache-walk", "#btn-starter"),
    "module45-dual-port-ram": generic_starter("dual-port-ram", "#dpr-starter"),
    "module46-byte-enable-mem": generic_starter("byte-enable-mem", "#be-starter"),
    "module47-async-fifo": generic_starter("async-fifo", "#af-starter"),
    "module48-handshake": generic_starter("handshake", "#btn-starter"),
    "module49-block-diagram": generic_starter("block-diagram", "#bd-starter"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path, default=COURSE)
    ap.add_argument("--module", help="Only one module id")
    args = ap.parse_args()
    course = args.course.resolve()
    qdir = course / "questions"

    for path in sorted(qdir.glob("*.json")):
        mid = path.stem
        if args.module and mid != args.module:
            continue
        binder = BINDERS.get(mid)
        if not binder:
            print(f"skip {mid}: no binder")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        keys: dict[str, int] = {}
        for it in data.get("items") or []:
            cap = binder(it)
            it["tool_capture"] = cap
            keys[cap["key"]] = keys.get(cap["key"], 0) + 1
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{mid}: {len(data.get('items') or [])} items -> {len(keys)} unique captures")
        for k, n in sorted(keys.items(), key=lambda kv: -kv[1]):
            print(f"  {n:2d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
