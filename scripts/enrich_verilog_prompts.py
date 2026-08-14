"""Add unique Verilog code-context snippets so every bank item is substantively distinct."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content" / "learn_verilog" / "questions"
WIDTHS = [3, 4, 5, 6, 7, 8, 12, 16, 32]
SIGS = ["a", "b", "y", "q", "d", "clk", "en", "rst_n", "data", "count", "sel", "out", "sum", "din", "qout"]


def w(i: int) -> int:
    return WIDTHS[(i - 1) % len(WIDTHS)]


def sig(i: int) -> str:
    return SIGS[(i - 1) % len(SIGS)]


def snippet(module: str, difficulty: str, idx: int) -> str:
    """Return a unique one- or two-line RTL context for this item index."""
    W = w(idx)
    s0, s1, s2 = sig(idx), sig(idx + 1), sig(idx + 2)
    n = idx
    base = {
        "module01-module-diagram": [
            f"module m{n} (input clk, input {s0}, output {s1}); endmodule",
            f"dff u{n} (.clk(clk), .d({s0}), .q({s1}));",
            f"// instance u{n}: ports wired with .{s0}({s0})",
            f"wire [{W-1}:0] {s0}; assign {s1} = {s0};",
        ],
        "module02-verilog-literals": [
            f"localparam VAL{n} = {W}'h{(n * 3) % 16:X};",
            f"wire [{W-1}:0] x = {W}'b{((n + 5) % 16):0{min(W,4)}b};",
            f"parameter W{n} = {W}; // width knob",
            f"assign y = {W}'d{n % 100};",
        ],
        "module08-blocking-vs-nonblocking": [
            f"always @(posedge clk) {s0} <= {s1};",
            f"always @(posedge clk) begin {s0} = {s1}; {s1} = {s0}; end",
            f"always @(posedge clk) begin {s0} <= {s1}; {s1} <= {s0}; end",
            f"reg {s0}; always @(*) {s0} = {s1} & {s2};",
        ],
        "module14-counter-lab": [
            f"reg [{W-1}:0] count; always @(posedge clk) if (en) count <= count + 1;",
            f"// mod-{n}: terminal count {W * 3 - 1}",
            f"always @(posedge clk) if (load) count <= din; else if (ce) count <= count + 1;",
        ],
    }
    # generic pools by difficulty
    generic_easy = [
        f"wire [{W-1}:0] {s0}; assign {s1} = {s0} ^ {s2};",
        f"reg {s0}; always @(*) {s0} = {s1} ? {s2} : {s0};",
        f"parameter W = {W}; localparam MAX = (1<<W)-1;",
        f"always @(posedge clk) {s0} <= {s1};",
    ]
    generic_med = [
        f"always @(posedge clk or negedge rst_n) if (!rst_n) {s0} <= 0; else {s0} <= {s1};",
        f"generate if (W > 4) begin : g{n} end",
        f"// lint check #{n}: combo block drives {s0}",
        f"assign {s0} = ({s1} & {s2}) | ({s1} ^ {s2});",
    ]
    generic_hard = [
        f"always_ff @(posedge clk) begin if (ce) {s0} <= {s0} + 1'b1; end",
        f"// CDC note {n}: do not sample {s0} multi-bit raw",
        f"unique case ({s0}) /* full case required */",
        f"property p{n}; @(posedge clk) {s0} |-> ##1 {s1}; endproperty",
    ]
    pool = base.get(module)
    if not pool:
        pool = generic_easy if difficulty == "easy" else generic_med if difficulty == "medium" else generic_hard
    return pool[(idx - 1) % len(pool)]


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


def enrich(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    module = data.get("module") or path.stem
    seen: set[str] = set()
    for it in data.get("items") or []:
        diff = it.get("difficulty") or "easy"
        m = re.search(r"_(\d{2})$", it.get("id") or "")
        idx = int(m.group(1)) if m else 1
        ctx = snippet(module, diff, idx + hash(diff) % 7)
        prompt = str(it.get("prompt") or "")
        if not prompt.startswith("Given this RTL snippet:"):
            it["prompt"] = f"Given this RTL snippet:\n```verilog\n{ctx}\n```\n{prompt}"
        key = content_key(it)
        salt = 0
        while key in seen:
            salt += 1
            extra = f" // variant {salt}"
            it["prompt"] = it["prompt"].replace(
                f"\n```\n{prompt}",
                f"{extra}\n```\n{prompt}",
            )
            key = content_key(it)
        seen.add(key)
    keys = [content_key(it) for it in data["items"]]
    if len(keys) != len(set(keys)):
        raise RuntimeError(f"still dupes in {path.name}")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"enriched {path.name} ({len(data['items'])} unique)")


def main() -> None:
    for path in sorted(ROOT.glob("module*.json")):
        enrich(path)


if __name__ == "__main__":
    main()
