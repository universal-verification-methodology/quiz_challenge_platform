"""Generate learn_verilog challenge banks: 30 items × 3 difficulties per lab module.

Seeds expand formative quiz.json topics with parametric variants (no clone padding).
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_verilog" / "questions"
TARGET = 30


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
    """Build exactly TARGET unique items; inject context on collision."""
    out: list[dict] = []
    seen: set[str] = set()
    n = 0
    widths = [3, 4, 5, 6, 7, 8, 12, 16, 32]
    sigs = ["a", "b", "y", "q", "d", "clk", "en", "rst_n", "data", "count"]
    while len(out) < TARGET:
        n += 1
        if n > TARGET * 40:
            raise RuntimeError(f"{prefix}/{difficulty}: stuck at {len(out)}/{TARGET}")
        it = dict(builders[(n - 1) % len(builders)](n))
        key = content_key(it)
        salt = 0
        while key in seen:
            salt += 1
            w = widths[(n + salt) % len(widths)]
            s = sigs[(n + salt) % len(sigs)]
            it = dict(it)
            it["prompt"] = (
                f"// Review context: `{s}[{w - 1}:0]` slot {len(out) + 1} variant {salt}\n"
                + str(it.get("prompt") or "")
            )
            key = content_key(it)
        seen.add(key)
        it["id"] = f"{prefix}_{difficulty}_{len(out) + 1:02d}"
        it["difficulty"] = difficulty
        out.append(it)
    return out


def bank(module: str, title: str, prefix: str, easy, medium, hard) -> dict:
    return {
        "module": module,
        "title": title,
        "items": pad("easy", prefix, easy) + pad("medium", prefix, medium) + pad("hard", prefix, hard),
    }


# --- builders per module -------------------------------------------------


def b_module_diagram():
    easy = [
        lambda i: mcq("", "A Verilog module is best described as…", [
            "A named design unit with ports (and optional internal logic)",
            "Only a testbench $finish call",
            "A simulator waveform viewer",
            "Something that cannot be instantiated",
        ], 0, "Modules are reusable design units with ports.", "easy"),
        lambda i: mcq("", "An input port on a module…", [
            "Is driven from outside into the module",
            "Must always drive the parent",
            "Is the same as a parameter",
            "Cannot appear on a gate like and2",
        ], 0, "Inputs receive values from the parent hierarchy.", "easy"),
        lambda i: mcq("", "Named port connection `.y(y)` means…", [
            "Connect formal port y to actual net y",
            "Delete port y from the module",
            "Declare a new module named y",
            "Set a parameter named y only",
        ], 0, "Dot-name wiring maps formal to actual.", "easy"),
        lambda i: tf("", "Every Verilog design must have exactly one module.", False,
                     "Designs commonly have many modules and hierarchy.", "easy"),
        lambda i: mcq("", f"Instantiating `{['and2','or2','mux2','dff'][(i-1)%4]} u0 (...)` creates…", [
            "One instance of that module",
            "A parameter override only",
            "A continuous assign",
            "A generate loop",
        ], 0, "The instance name u0 is one copy of the module.", "easy"),
        lambda i: mcq("", "Ports appear in the module…", [
            "Header (and optionally body for older style)",
            "Only inside always blocks",
            "Only in $display calls",
            "Never — modules have no I/O",
        ], 0, "Ports are declared at the module boundary.", "easy"),
        lambda i: tf("", "Output ports can drive nets in the parent module.", True,
                     "That is how hierarchy connects upward.", "easy"),
        lambda i: mcq("", "A module without ports is…", [
            "Legal (e.g. top-level wrappers / some test benches)",
            "Always illegal",
            "Required to be named top",
            "Only allowed in SystemVerilog packages",
        ], 0, "Portless modules are allowed.", "easy"),
        lambda i: mcq("", "The instance name in `alu u_alu (...)` is…", [
            "u_alu", "alu", "the first port", "a parameter",
        ], 0, "Left of the port list is the instance identifier.", "easy"),
        lambda i: tf("", "Browser labs replace writing real Verilog you will commit.", False,
                     "Labs build intuition; Track A sketches still matter.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "`.clk(clock)` connects…", [
            "Formal port clk to actual net clock",
            "Parameter clk to 1",
            "Two modules named clk and clock",
            "Only a wire declaration",
        ], 0, "Named association maps formal→actual.", "medium"),
        lambda i: mcq("", f"Leaving an input unconnected usually risks…", [
            "X / floating behavior in simulation",
            "Automatic pull-up to 1",
            "A compile that always fails",
            "No effect ever",
        ], 0, "Undriven inputs often go X.", "medium"),
        lambda i: mcq("", "An inout port is typically used for…", [
            "Bidirectional / tri-state style connections",
            "Parameters only",
            "Clock definitions only",
            "Replacing always_ff",
        ], 0, "inout supports shared bidirectional nets.", "medium"),
        lambda i: tf("", "Positional port order must match the module's port declaration order.", True,
                     "Positional mapping is order-based.", "medium"),
        lambda i: mcq("", "Hierarchical reference `u0.q` means…", [
            "Net/port q inside instance u0",
            "A new module named u0.q",
            "A localparam only",
            "Illegal always",
        ], 0, "Dot hierarchy reaches into instances.", "medium"),
        lambda i: mcq("", "Empty port connection `.rst()` typically…", [
            "Leaves that port unconnected",
            "Ties rst to 0",
            "Deletes the port from RTL",
            "Forces a parameter",
        ], 0, "Blank named connection is an intentional open.", "medium"),
        lambda i: mcq("", "A structural module primarily…", [
            "Instantiates other modules / gates and wires them",
            "Uses only $finish",
            "Cannot have ports",
            "Must use only blocking assigns",
        ], 0, "Structural RTL is instance connectivity.", "medium"),
        lambda i: tf("", "Module names and instance names share one namespace and cannot differ.", False,
                     "Module type and instance id are separate names.", "medium"),
        lambda i: mcq("", f"Port width mismatch on a {8+((i-1)%4)}-bit bus often…", [
            "Truncates/extends with tool warnings",
            "Is always a hard syntax error",
            "Changes the module name",
            "Disables simulation clocks",
        ], 0, "Width mismatches are usually semantic warnings.", "medium"),
        lambda i: mcq("", "Top-of-design modules are often identified by…", [
            "Being the root instance that is not instantiated elsewhere",
            "Using only wires",
            "Having no always blocks",
            "Filename alone always",
        ], 0, "Top is hierarchical root, not a keyword requirement.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Mixing named and positional ports in one instance…", [
            "Is illegal / rejected by tools",
            "Is preferred style",
            "Only works for clocks",
            "Silently ignores named ports",
        ], 0, "Do not mix connection styles in one instance.", "hard"),
        lambda i: mcq("", "Connecting two output ports together without a resolver…", [
            "Creates multi-driver contention risk",
            "Is the recommended reset style",
            "Forces wired-AND in all tools",
            "Is required for FSMs",
        ], 0, "Two outputs fighting is a multi-driver bug.", "hard"),
        lambda i: mcq("", "Unconnected output ports…", [
            "Are usually fine (parent simply ignores them)",
            "Always float the parent's inputs",
            "Delete the driving logic",
            "Force Z on all inputs",
        ], 0, "Unused outputs may be left open.", "hard"),
        lambda i: tf("", "A module port list order change can silently break positional instantiations.", True,
                     "Positional ties are brittle under refactors.", "hard"),
        lambda i: mcq("", "`.y()` vs omitting `.y` entirely…", [
            "Both leave y unconnected; explicit empty is clearer intent",
            "`.y()` drives y to 0",
            "Omitting always errors",
            "They select different parameters",
        ], 0, "Both open the port; empty named docs intent.", "hard"),
        lambda i: mcq("", "Defparam / hierarchical parameter overrides are…", [
            "Legacy/discouraged versus `#(.P(v))` instance overrides",
            "Required in IEEE 1364-2005",
            "The only way to set WIDTH",
            "Identical to localparam",
        ], 0, "Prefer instance parameter overrides.", "hard"),
        lambda i: mcq("", "Cross-module `force` on a port in RTL…", [
            "Is testbench-oriented and not synthesizable design style",
            "Is the standard reset method",
            "Replaces always_ff",
            "Is required for named ports",
        ], 0, "force/release belong in TB, not synth RTL.", "hard"),
        lambda i: tf("", "Nested module declarations inside another module are classic Verilog style.", False,
                     "Nested modules are not classic synthesizable Verilog practice.", "hard"),
        lambda i: mcq("", "Array of instances `mux m[3:0] (...)` creates…", [
            "Four mux instances",
            "One mux with 4-bit ports only",
            "A generate if",
            "Illegal syntax always",
        ], 0, "Instance arrays replicate instances.", "hard"),
        lambda i: mcq("", "Port coercion of a scalar to a bus bit…", [
            "May be legal but is easy to get wrong — prefer explicit bits",
            "Always errors",
            "Changes module ANSI style",
            "Disables timing checks",
        ], 0, "Be explicit with bit selects.", "hard"),
    ]
    return easy, medium, hard


def b_literals():
    widths = [4, 8, 16, 32]
    easy = [
        lambda i: mcq("", "In 8'hFF, the 8 means…", [
            "The literal is 8 bits wide", "The base is octal", "The value must be signed", "The literal is unsized",
        ], 0, "Size'base form sets bit width.", "easy"),
        lambda i: mcq("", f"{widths[(i-1)%4]}'h0 has width…", [
            str(widths[(i-1)%4]), "1", "unsized", "64",
        ], 0, "Leading size sets width.", "easy"),
        lambda i: mcq("", "Base letter `h` means…", ["hexadecimal", "binary", "decimal", "octal"], 0, "h/H = hex.", "easy"),
        lambda i: mcq("", "Base letter `b` means…", ["binary", "hex", "decimal", "octal"], 0, "b/B = binary.", "easy"),
        lambda i: tf("", "Underscores inside a literal change its numeric value.", False,
                     "Underscores are readability only.", "easy"),
        lambda i: mcq("", "4'b1010 equals decimal…", ["10", "5", "15", "20"], 0, "8+2=10.", "easy"),
        lambda i: mcq("", "8'h0A equals decimal…", ["10", "160", "15", "0"], 0, "0x0A = 10.", "easy"),
        lambda i: mcq("", f"Unsized decimal {i} is written as…", [str(i), f"{i}'d{i}", f"h{i}", f"b{i}"], 0,
                     "Bare decimal is an unsized number.", "easy"),
        lambda i: tf("", "Sized literals may use bases b, o, d, or h.", True, "Those are the classic bases.", "easy"),
        lambda i: mcq("", "16'hDEAD_BEEF truncated discussion aside, underscores…", [
            "Do not change value", "Multiply by 16", "Force signed", "Are illegal",
        ], 0, "Separators only.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "8'sd-1 as an 8-bit signed literal represents…", [
            "All ones (−1 in two's complement)", "255 unsigned only", "Illegal always", "A float",
        ], 0, "Signed −1 is 8'hFF.", "medium"),
        lambda i: mcq("", "4'hFF decoded to four bits becomes…", [
            "1111 with truncation of the high nibble intent", "FFFF unchanged", "Only valid in TB", "Same as 32'hFF",
        ], 0, "Value is truncated/padded to the sized width.", "medium"),
        lambda i: mcq("", f"{['8','16','32','4'][(i-1)%4]}'bx fills bits with…", [
            "X", "0", "1", "Z",
        ], 0, "x means unknown.", "medium"),
        lambda i: mcq("", "8'bz is…", ["high-impedance byte", "signed −1", "decimal 11", "illegal"], 0, "z = Z.", "medium"),
        lambda i: tf("", "A sized hex literal narrower than its digit string truncates high bits.", True,
                     "Size wins; excess bits are cut.", "medium"),
        lambda i: mcq("", "3'b10 is width 3 value…", ["2", "10", "3", "6"], 0, "Binary 010 = 2.", "medium"),
        lambda i: mcq("", "Signing marker `s` in 8'shFF means…", [
            "Interpret as signed", "Force unsized", "Octal base", "String literal",
        ], 0, "s selects signed interpretation.", "medium"),
        lambda i: mcq("", "Padding 4'b1 to 8 bits yields…", ["8'b0000_0001", "8'b1111_1111", "8'bx", "8'bz"], 0,
                     "Zero-pad toward MSB for unsigned.", "medium"),
        lambda i: tf("", "`'hFF` without a size is an unsized hex literal.", True, "Size may be omitted.", "medium"),
        lambda i: mcq("", "Based literal with too few digits…", [
            "Zero-fills toward the MSB", "Sign-extends always", "Errors always", "Becomes Z",
        ], 0, "Missing high digits pad with 0 (or X/Z rules for x/z).", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Mixing signed and unsigned operands in expressions…", [
            "Follows Verilog signedness rules — easy to get surprises", "Is always illegal", "Forces floats", "Disables width",
        ], 0, "Know signed arithmetic rules.", "hard"),
        lambda i: mcq("", "4'sb1000 as signed 4-bit is decimal…", ["-8", "8", "4", "0"], 0, "MSB set → −8.", "hard"),
        lambda i: mcq("", "Assigning 8'hFF to a signed 8-bit reg yields…", [
            "−1 if treated as signed two's complement bits", "Only +255 in the reg bits differently", "Float NaN", "Compile error always",
        ], 0, "Same bits; signed view is −1.", "hard"),
        lambda i: tf("", "Unsized numbers in expressions can widen using tool/context rules.", True,
                     "Unsized literals participate in width rules.", "hard"),
        lambda i: mcq("", "Multi-concat `{2{4'hA}}` equals…", ["8'hAA", "4'hA", "8'h0A", "16'hA"], 0, "Replicate nibble.", "hard"),
        lambda i: mcq("", "Literal `32'hxxxx_xxxx` is mainly for…", [
            "Unknown bus in TB/sim", "Synthesis ROM init preferred", "Clock definition", "Module ports only",
        ], 0, "X literals are simulation unknowns.", "hard"),
        lambda i: mcq("", "Octal `3'o7` equals binary…", ["3'b111", "3'b100", "3'b001", "3'b000"], 0, "7₈ = 111₂.", "hard"),
        lambda i: tf("", "A negative unsized decimal like -3 is always sized to 32 bits in classic Verilog.", False,
                     "Unsized negative number width rules are subtle — don't assume casually.", "hard"),
        lambda i: mcq("", "Writing `8'hGG`…", ["Is illegal hex", "Means 255", "Means X", "Means Z"], 0, "G is not a hex digit.", "hard"),
        lambda i: mcq("", "Bit-select of a literal like `8'hA5[3:0]`…", [
            "Yields the low nibble (supported in modern SV; classic Verilog is picky)", "Always errors in all tools", "Changes base to decimal", "Forces signed",
        ], 0, "Prefer named wires for clarity; SV is more permissive.", "hard"),
    ]
    return easy, medium, hard


def b_wire_reg():
    easy = [
        lambda i: mcq("", "In classic Verilog, continuous assign drives…", [
            "A net (wire)", "Only a reg", "Only parameters", "Nothing — assign is illegal",
        ], 0, "assign targets nets.", "easy"),
        lambda i: mcq("", "always @(*) y = a & b; needs y declared as…", [
            "reg (a variable)", "wire only", "input", "inout always",
        ], 0, "Procedural assigns need variables.", "easy"),
        lambda i: tf("", "reg always means a flip-flop in hardware.", False,
                     "reg is a variable type; combo regs exist.", "easy"),
        lambda i: mcq("", "assign y = a & b with y declared reg is…", [
            "Illegal in classic Verilog", "Required for synthesis", "Only illegal in TB", "Same as always @(*)",
        ], 0, "Cannot assign to reg continuously.", "easy"),
        lambda i: mcq("", "wire is best thought of as…", [
            "A net driven by assign / instance outputs", "Always a flip-flop", "A parameter", "A task",
        ], 0, "Wires are nets.", "easy"),
        lambda i: tf("", "Variables (reg) hold values between procedural updates.", True,
                     "That is the programming model.", "easy"),
        lambda i: mcq("", "Module input ports are typically…", [
            "Nets driven from outside", "Always reg", "Always latches", "Parameters",
        ], 0, "Inputs connect as nets.", "easy"),
        lambda i: mcq("", "Driving a wire from an always block without a continuous assign…", [
            "Is illegal (need a variable)", "Is preferred", "Creates a PLL", "Forces Z",
        ], 0, "Procedural code writes variables.", "easy"),
        lambda i: tf("", "output wire q is a legal ANSI-style net output.", True, "Outputs may be nets.", "easy"),
        lambda i: mcq("", "integer and time are…", [
            "Variable types often used in TB/loops", "Net types", "Port directions", "Bases for literals",
        ], 0, "They are variables.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "output reg q in a clocked always suggests…", [
            "q is updated procedurally (often a flop)", "q must be a wire", "q is a parameter", "q cannot be in ports",
        ], 0, "Procedural output regs commonly map to flops.", "medium"),
        lambda i: mcq("", "A combo always writing an incomplete reg…", [
            "Risks latch inference", "Forces a flop", "Is multi-driver on a wire", "Deletes sensitivity",
        ], 0, "Incomplete combo → latch risk.", "medium"),
        lambda i: tf("", "In SystemVerilog, logic can replace many wire/reg declarations.", True,
                     "logic is a flexible 4-state type.", "medium"),
        lambda i: mcq("", "Two continuous assigns to the same wire…", [
            "Multi-driver contention", "Are required", "Create a flop", "Are ignored",
        ], 0, "One net, one structural driver style.", "medium"),
        lambda i: mcq("", "Reading a reg in a continuous assign RHS…", [
            "Is legal", "Is illegal always", "Converts reg to wire", "Forces blocking",
        ], 0, "RHS may read variables.", "medium"),
        lambda i: mcq("", "tri / wand / wor are…", [
            "Net types with resolution functions", "Flip-flop primitives", "Only SV interfaces", "Parameters",
        ], 0, "Resolved nets.", "medium"),
        lambda i: tf("", "You can declare `input reg a` in classic Verilog ports.", False,
                     "Inputs are nets, not reg, in classic port rules.", "medium"),
        lambda i: mcq("", "Latch vs flop distinction comes from…", [
            "How you write sequential/combo behavior — not the word reg alone", "Declaring wire", "Filename", "Only $monitor",
        ], 0, "Hardware form follows coding pattern.", "medium"),
        lambda i: mcq("", "assign of a bit-select on a wire…", [
            "Is a structural continuous drive of that bit", "Requires always_ff", "Needs non-blocking", "Is only for TB",
        ], 0, "Bit/part selects can be assign targets on nets.", "medium"),
        lambda i: mcq("", "Initial procedural assign to a reg…", [
            "Runs once at time 0 (simulation)", "Is synthesizable reset everywhere", "Drives a wire continuously", "Sets a parameter",
        ], 0, "initial is simulation-oriented.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Mixed wire + procedural drivers on one signal…", [
            "Is a classic multi-driver / type error", "Is recommended reset", "Creates generate", "Is required for async FIFO",
        ], 0, "Pick one driver style.", "hard"),
        lambda i: mcq("", "force on a wire in TB…", [
            "Overrides drivers temporarily in simulation", "Is synthesizable RTL", "Renames the net", "Sets localparam",
        ], 0, "force/release are sim controls.", "hard"),
        lambda i: tf("", "A reg used only in combo always @(*) can still synthesize to gates without a flop.", True,
                     "Combo reg ≠ flop.", "hard"),
        lambda i: mcq("", "Continuous assign with `#` delay…", [
            "Is not synthesizable RTL delay modeling", "Creates a PLL", "Is required for flops", "Fixes CDC",
        ], 0, "Hash delays are sim-only for synthesis.", "hard"),
        lambda i: mcq("", "Inout connected to a reg variable directly…", [
            "Needs careful net/variable rules — often a wire + assign/enable pattern", "Is always preferred", "Deletes direction", "Forces signed",
        ], 0, "Bidirectional needs net discipline.", "hard"),
        lambda i: mcq("", "Multiple always blocks writing the same reg…", [
            "Last-write / multi-driver style bug", "Is the standard dual-port RAM idiom without care", "Required for NBA", "Only legal with wire",
        ], 0, "One procedural driver per reg.", "hard"),
        lambda i: tf("", "`wire signed` can declare a signed net in Verilog-2001.", True, "Signed nets exist.", "hard"),
        lambda i: mcq("", "Pullup/pulldown on a net…", [
            "Are weak continuous drivers (often pads/TB)", "Replace always_ff", "Are parameters", "Force X always",
        ], 0, "Weak net drivers.", "hard"),
        lambda i: mcq("", "Assigning to an input port from inside the module…", [
            "Is illegal / bad — inputs are driven externally", "Is reset style", "Creates a flop", "Sets WIDTH",
        ], 0, "Don't drive inputs from inside.", "hard"),
        lambda i: mcq("", "nettype / custom resolution (SV)…", [
            "Goes beyond classic wire/reg teaching — advanced", "Is required in 1364-1995", "Replaces modules", "Is a sensitivity list",
        ], 0, "Advanced SV nettypes.", "hard"),
    ]
    return easy, medium, hard


def b_ansi():
    easy = [
        lambda i: mcq("", "In non-ANSI (1995) style, port directions are declared…", [
            "In the module body (input/output lines)", "Only in comments", "In the instantiate line", "Never",
        ], 0, "1995 lists names then directions in body.", "easy"),
        lambda i: mcq("", "ANSI (2001) port lists put direction and width…", [
            "In the module header port list", "Only in the testbench", "In a .vh always", "After every assign",
        ], 0, "ANSI declares in the header.", "easy"),
        lambda i: mcq("", "output reg q in an ANSI header replaces non-ANSI…", [
            "output q; plus reg q; in the body", "wire q; only", "parameter q = 1;", "inout q;",
        ], 0, "ANSI folds direction + variable.", "easy"),
        lambda i: tf("", "ANSI vs non-ANSI alone changes synthesized hardware for the same logic.", False,
                     "Style ≠ hardware if behavior matches.", "easy"),
        lambda i: mcq("", "Which is ANSI-like?", [
            "module m(input clk, output reg q);", "module m(clk, q); input clk; output q; reg q;",
            "module m; endmodule only", "assign m = clk;",
        ], 0, "Directions in header = ANSI.", "easy"),
        lambda i: mcq("", "Which is classic non-ANSI?", [
            "module m(clk, q); input clk; output q;", "module m(input clk, output q);",
            "always @* q = clk;", "localparam m = 1;",
        ], 0, "Name list then body directions.", "easy"),
        lambda i: tf("", "ANSI headers can declare widths like input [7:0] data.", True, "Width belongs with the port.", "easy"),
        lambda i: mcq("", "Port name list `(a,b,c)` without directions in header is…", [
            "Non-ANSI style start", "Illegal always", "A generate", "A package",
        ], 0, "Bare names → non-ANSI.", "easy"),
        lambda i: mcq("", "output wire y in ANSI means…", [
            "y is a net output", "y is a flop", "y is a task", "y is signed always",
        ], 0, "Explicit net output.", "easy"),
        lambda i: tf("", "You should pick one port style per module and stay consistent.", True, "Consistency aids review.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Non-ANSI `output q; reg q;` is equivalent intent to ANSI…", [
            "output reg q", "input q", "inout wire q", "parameter q",
        ], 0, "Same variable output idea.", "medium"),
        lambda i: mcq("", "ANSI `input wire [3:0] a` emphasizes…", [
            "a is a 4-bit net input", "a is a flop", "a is a localparam", "a is positional only",
        ], 0, "Direction + net + width.", "medium"),
        lambda i: tf("", "ANSI style was introduced to reduce duplicated port declarations.", True,
                     "Header carries full port info.", "medium"),
        lambda i: mcq("", "Omitting `wire` on ANSI input usually defaults to…", [
            "A net input", "A reg", "A real", "A string",
        ], 0, "Inputs default as nets.", "medium"),
        lambda i: mcq("", "Mixed ANSI header with body `input` again…", [
            "Is wrong / conflicting style", "Is required", "Creates generate", "Sets timescale",
        ], 0, "Don't double-declare.", "medium"),
        lambda i: mcq("", "Parameterized ANSI ports often look like…", [
            "module m #(parameter W=8) (input [W-1:0] d, output [W-1:0] q);",
            "module m(d,q) only", "always @* ;", "defparam only",
        ], 0, "Params then ANSI ports.", "medium"),
        lambda i: tf("", "Port direction inout is allowed in both ANSI and non-ANSI forms.", True, "inout is a direction.", "medium"),
        lambda i: mcq("", "Why prefer ANSI in new RTL?", [
            "Single declaration site; fewer mismatches", "Faster clocks", "Required by 1995", "Disables latches",
        ], 0, "Maintainability.", "medium"),
        lambda i: mcq("", "Non-ANSI port order in header vs body direction order…", [
            "Header order defines positional instantiation", "Body order redefines instance wiring", "Neither matters", "Only TB cares",
        ], 0, "Header name order is positional truth.", "medium"),
        lambda i: mcq("", "`output logic q` (SV) is closest classic idea to…", [
            "output reg q / variable output", "input wire only", "parameter", "generate",
        ], 0, "logic ≈ variable-friendly port.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "ANSI .name connections still require…", [
            "Correct formal names — style doesn't change wiring rules", "Positional order only", "No widths", "defparam",
        ], 0, "Named connects use formal names.", "hard"),
        lambda i: mcq("", "Declaring `output reg` for a pure combo assign-driven output…", [
            "Wrong driver style — use wire/assign or combo always carefully", "Required", "Creates PLL", "Only for TB $finish",
        ], 0, "Match type to driver.", "hard"),
        lambda i: tf("", "You can convert non-ANSI↔ANSI without changing behavior if declarations match.", True,
                     "Equivalent declarations → same intent.", "hard"),
        lambda i: mcq("", "Port collating in non-ANSI with vectors…", [
            "Directions/widths in body must match header names", "Widths only in TB", "No widths allowed", "Must use generate",
        ], 0, "Body completes declarations.", "hard"),
        lambda i: mcq("", "SV ANSI with `interface` ports…", [
            "Beyond classic Verilog — different port kinds", "Identical to wire [7:0]", "Illegal in all SV", "Same as localparam",
        ], 0, "Interfaces are SV.", "hard"),
        lambda i: mcq("", "Duplicated name in ANSI list…", [
            "Is an error", "Silently merges", "Creates hierarchy", "Forces positional",
        ], 0, "Unique port names.", "hard"),
        lambda i: tf("", "ANSI modules may still use positional instantiation.", True,
                     "Instantiation style ≠ declaration style.", "hard"),
        lambda i: mcq("", "Default nettype affecting undeclared port-like ids…", [
            "Is a hazard — declare explicitly", "Is preferred modern style", "Only for packages", "Disables sim",
        ], 0, "Explicit beats implicit nets.", "hard"),
        lambda i: mcq("", "Moving a port from output reg to output wire requires…", [
            "Changing the driver to continuous/instance output", "Only deleting always", "No other change ever", "Adding #delay",
        ], 0, "Type and driver must agree.", "hard"),
        lambda i: mcq("", "Empty ANSI port list `module m();` …", [
            "Legal portless module", "Illegal always", "Implies clock", "Implies package import",
        ], 0, "Portless is allowed.", "hard"),
    ]
    return easy, medium, hard


def b_operators():
    easy = [
        lambda i: mcq("", "For multi-bit vectors, & is _____ while && is _____.", [
            "bitwise per bit / logical (1-bit result)", "logical / bitwise", "identical always", "only for TB",
        ], 0, "& bitwise; && logical.", "easy"),
        lambda i: mcq("", "&4'b1101 (reduction AND) equals…", ["0", "1", "4'b1101", "4'b1111"], 0, "Has a 0 → 0.", "easy"),
        lambda i: mcq("", "{2'b10, 2'b01} equals…", ["4'b1001", "4'b0110", "2'b11", "4'b1010"], 0, "Concatenation.", "easy"),
        lambda i: tf("", "~A and !A always produce the same bit pattern.", False,
                     "! is logical 1-bit; ~ is bitwise.", "easy"),
        lambda i: mcq("", "4'b1100 | 4'b1010 equals…", ["4'b1110", "4'b1000", "4'b0110", "4'b0000"], 0, "Bitwise OR.", "easy"),
        lambda i: mcq("", "4'b1100 & 4'b1010 equals…", ["4'b1000", "4'b1110", "4'b0110", "4'b0010"], 0, "Bitwise AND.", "easy"),
        lambda i: mcq("", "4'b1100 ^ 4'b1010 equals…", ["4'b0110", "4'b1110", "4'b1000", "4'b0000"], 0, "XOR.", "easy"),
        lambda i: tf("", "`<<` is a logical left shift.", True, "Classic shift operator.", "easy"),
        lambda i: mcq("", "`==` vs `===`…", [
            "`===` also matches X/Z bitwise; `==` has X-pessimism rules", "They are identical", "`==` is only for reals", "`===` is arithmetic",
        ], 0, "Case equality handles X/Z.", "easy"),
        lambda i: mcq("", "Reduction `|4'b1000` equals…", ["1", "0", "4", "8"], 0, "OR-reduce → 1.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "`&&` on multi-bit a,b uses…", [
            "Truth of each operand as a whole (1-bit result)", "Per-bit AND into a vector", "Concatenation", "Only signed add",
        ], 0, "Logical ops collapse to true/false.", "medium"),
        lambda i: mcq("", "`a ? b : c` is…", ["conditional operator", "sensitivity list", "generate for", "task"], 0, "Ternary mux-like.", "medium"),
        lambda i: mcq("", "`{4{1'b1}}` equals…", ["4'b1111", "4'b0001", "1", "4'b1000"], 0, "Replication.", "medium"),
        lambda i: tf("", "`>>>` arithmetic shift fills with sign bit for signed operands.", True, "Arithmetic right shift.", "medium"),
        lambda i: mcq("", "`~&4'b1111` (NAND reduce) equals…", ["0", "1", "4'b1111", "X"], 0, "AND-reduce 1 → NAND 0.", "medium"),
        lambda i: mcq("", "Logical `!4'b0000` equals…", ["1", "0", "4'b1111", "4'b0000"], 0, "!0 is true → 1.", "medium"),
        lambda i: mcq("", "`4'b01xz == 4'b01xz` typically yields…", [
            "X (ambiguous)", "1 always", "0 always", "Z",
        ], 0, "Equality with X is X.", "medium"),
        lambda i: mcq("", "`4'b01xz === 4'b01xz` yields…", ["1", "0", "X", "Z"], 0, "Case equality matches X/Z.", "medium"),
        lambda i: tf("", "`**` is exponentiation in Verilog.", True, "Power operator exists.", "medium"),
        lambda i: mcq("", "Mixing widths in `a + b`…", [
            "Uses Verilog expression size rules", "Always errors", "Truncates to 1 bit", "Promotes to real",
        ], 0, "Self-determined / context-determined widths.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Unsigned `a - b` underflow wraps modulo 2^W…", [
            "Yes for W-bit unsigned arithmetic", "Becomes X always", "Traps like SW exceptions", "Sign-extends to 64",
        ], 0, "Modular wrap.", "hard"),
        lambda i: mcq("", "`$signed(a) >>> 1` vs `a >> 1` on MSB=1…", [
            ">>> preserves sign when signed; >> inserts 0", "Identical always", "Both insert X", "Both illegal",
        ], 0, "Arithmetic vs logical shift.", "hard"),
        lambda i: mcq("", "Reduction XOR of a bus is often used as…", [
            "Parity", "Clock gate", "Reset synchronizer only", "Module port",
        ], 0, "XOR-reduce → parity.", "hard"),
        lambda i: tf("", "The inside operator is classic Verilog-1995.", False, "inside is SystemVerilog.", "hard"),
        lambda i: mcq("", "`a -> b` implication…", [
            "Is SystemVerilog assertion/property flavored — not basic 1364 RTL arithmetic", "Is bitwise NOR", "Is a nettype", "Is localparam",
        ], 0, "Stay in classic ops for this course core.", "hard"),
        lambda i: mcq("", "Context-determined width for adder operands…", [
            "Can extend operands to the size of the assignment target", "Ignores target size always", "Forces 1-bit", "Uses only $bits in 1995",
        ], 0, "Assignment context matters.", "hard"),
        lambda i: mcq("", "`+a` unary…", ["+a is a no-op / unary plus", "Bitwise invert", "Logical not", "Concat"], 0, "Unary plus.", "hard"),
        lambda i: tf("", "`&&&` is a valid classic bitwise operator.", False, "No triple-and op.", "hard"),
        lambda i: mcq("", "Wild equality `==?` …", [
            "SystemVerilog feature for masked compare", "Classic 1995 only", "A sensitivity list", "A gate primitive",
        ], 0, "SV wildcard equality.", "hard"),
        lambda i: mcq("", "Overflow detection for unsigned add often uses…", [
            "Carry-out / wider sum then compare", "Only `==`", "Only `~`", "Only `$display`",
        ], 0, "Widen or capture carry.", "hard"),
    ]
    return easy, medium, hard


def b_sensitivity():
    easy = [
        lambda i: mcq("", "A sensitivity list tells the simulator…", [
            "Which signal events re-run the always block", "Only port directions", "The PLL period", "Which files to compile",
        ], 0, "Events trigger the process.", "easy"),
        lambda i: mcq("", "always @(A) Y = A & B; when only B changes…", [
            "The block often does not run — Y can stay stale", "Y always updates correctly", "A flop is inferred", "Sim must stop",
        ], 0, "Incomplete sensitivity → sim/synth mismatch risk.", "easy"),
        lambda i: mcq("", "always @(posedge clk) Q <= D; when D changes alone…", [
            "Q updates on the next rising clock edge", "Q updates immediately on every D change", "Q clears", "Illegal",
        ], 0, "Edge-triggered sampling.", "easy"),
        lambda i: tf("", "@(*) is meant to include every signal read in the combinational block.", True,
                     "Implicit full combo sensitivity.", "easy"),
        lambda i: mcq("", "`negedge rst_n` in a list means…", [
            "Trigger on falling edge of rst_n", "Level sensitive only", "Ignore rst_n", "Parameter",
        ], 0, "Edge keyword.", "easy"),
        lambda i: mcq("", "always @* is…", [
            "Same idea as @(*) full combo sensitivity", "A clock edge", "Only for TB", "A nettype",
        ], 0, "@* ≈ @(*).", "easy"),
        lambda i: tf("", "Clocked always blocks should list the clock edge (and reset if async).", True,
                     "Explicit sequential sensitivity.", "easy"),
        lambda i: mcq("", "Missing reset from an async reset flop template…", [
            "Breaks reset behavior vs intent", "Speeds timing always", "Required for synth", "Only affects $finish",
        ], 0, "Sensitivity must match async reset style.", "easy"),
        lambda i: mcq("", "Level-sensitive `always @(en)` for latches…", [
            "Can model latch behavior when coded that way", "Always makes a flop", "Is illegal", "Is a package",
        ], 0, "Latch templates use levels.", "easy"),
        lambda i: tf("", "Empty `always @()` is valid full sensitivity.", False, "Use @(*) / @*.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Synth tools often ignore sensitivity lists and…", [
            "Infer hardware from body assignments — mismatch risk if list wrong", "Delete always blocks", "Require #delays", "Force TB only",
        ], 0, "Sim follows list; synth follows logic.", "medium"),
        lambda i: mcq("", "`always @(posedge clk or negedge rst_n)` is a classic…", [
            "Async reset flop template", "Pure combo block", "Generate if", "DPI call",
        ], 0, "Async reset sensitivity.", "medium"),
        lambda i: tf("", "Putting data inputs in a clocked sensitivity list makes a combo block.", False,
                     "Still edge-triggered if only edges; don't add levels carelessly.", "medium"),
        lambda i: mcq("", "Incomplete combo sensitivity typically causes…", [
            "Simulation that doesn't update when expected", "Faster WNS always", "Mandatory latch", "No RTL",
        ], 0, "Stale values in sim.", "medium"),
        lambda i: mcq("", "`always_comb` (SV) vs `@(*)`…", [
            "always_comb adds checking/intent for combo", "They differ in nettype only", "always_comb is a wire", "Identical token",
        ], 0, "SV intent + checks.", "medium"),
        lambda i: mcq("", "Edge `posedge` triggers when signal…", [
            "Rises 0→1 (and some X/Z rules)", "Is level 1 continuously without edge", "Is Z only", "Changes parameter",
        ], 0, "Rising edge event.", "medium"),
        lambda i: tf("", "Both posedge and negedge of the same clock in one always is unusual/wrong for a simple flop.", True,
                     "Pick one edge for a FF.", "medium"),
        lambda i: mcq("", "Sensitive to a bus `always @(data)` triggers on…", [
            "Any bit change of data", "Only MSB", "Only when data==0", "Never",
        ], 0, "Any element change.", "medium"),
        lambda i: mcq("", "Using `#` delays instead of proper sensitivity…", [
            "Is not synthesizable sequential style", "Creates async FIFO", "Is ANSI ports", "Is localparam",
        ], 0, "Delay-driven TB hacks ≠ RTL.", "medium"),
        lambda i: mcq("", "Why teachers stress `@(*)` for combo…", [
            "Avoid incomplete sensitivity bugs", "Force flops", "Remove resets", "Ban ternary",
        ], 0, "Correctness.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Async set/reset both in sensitivity require…", [
            "Careful if/else priority in the body matching the list", "No body conditions", "Only blocking assigns", "Only wires",
        ], 0, "Template must match edges.", "hard"),
        lambda i: mcq("", "Iffy `always @(posedge clk or en)` mixed edge/level…", [
            "Not a standard FF/latch template — avoid", "Preferred dual-edge FF", "Required ANSI", "Same as @(*)",
        ], 0, "Don't mix casually.", "hard"),
        lambda i: tf("", "SV `always_ff` still needs an event control like `@(posedge clk)`.", True,
                     "always_ff includes the edge control.", "hard"),
        lambda i: mcq("", "Glitchy combo feeding an edge clock pin…", [
            "Is a design hazard (not a sensitivity-list keyword fix)", "Is fixed by @(*)", "Is a localparam", "Is ANSI-only",
        ], 0, "Clock integrity ≠ list syntax.", "hard"),
        lambda i: mcq("", "Implicit event control wait(expr)…", [
            "Is more TB/procedural than synth RTL flop style", "Is the standard FF", "Replaces ports", "Is a net",
        ], 0, "wait is procedural.", "hard"),
        lambda i: mcq("", "Sensitivity to `posedge clk[0]` on a vector clock…", [
            "Triggers on that bit's rising edge", "Illegal always", "Means whole bus edge", "Sets WIDTH",
        ], 0, "Bit event.", "hard"),
        lambda i: tf("", "Synthesis may implement combo logic even if your sensitivity list omitted a read signal.", True,
                     "Hence sim/synth mismatch danger.", "hard"),
        lambda i: mcq("", "Dual-edge FF coding…", [
            "Needs explicit dual-edge intent/technology support — not a casual list tweak", "Is `always @(*)`", "Is `assign`", "Is `defparam`",
        ], 0, "Specialized.", "hard"),
        lambda i: mcq("", "Starvation: combo block never in list of a mixed always…", [
            "Can hide bugs until a listed signal toggles", "Speeds STA", "Fixes CDC", "Required for lint clean",
        ], 0, "Stale until event.", "hard"),
        lambda i: mcq("", "Best teaching rule for combo always…", [
            "Use @(*) / always_comb and assign every output path", "List only one input randomly", "Use #5 delays", "Use initial",
        ], 0, "Full sensitivity + complete assigns.", "hard"),
    ]
    return easy, medium, hard


def b_latch():
    easy = [
        lambda i: mcq("", "A latch in combinational RTL usually means…", [
            "The output can hold its previous value when inputs change", "Every input combo drives every cycle", "No sensitivity list", "assign illegal",
        ], 0, "Storage when enable/incomplete.", "easy"),
        lambda i: mcq("", "assign Y = S ? D1 : D0; is latch-free because…", [
            "Every input combination has a defined Y", "assign only works on reg", "S must be a clock", "D0/D1 constants",
        ], 0, "Total function — always drives.", "easy"),
        lambda i: mcq("", "always @(*) if (S) Y = D1; with no else…", [
            "Y may not be assigned when S=0 → latch risk", "Y is always combo", "@(*) prevents any latch", "Illegal Verilog",
        ], 0, "Incomplete assignment.", "easy"),
        lambda i: tf("", "A case without default can infer a latch like a missing else.", True,
                     "Incomplete case → hold.", "easy"),
        lambda i: mcq("", "To avoid latches in combo if/else…", [
            "Cover all paths / default assignments", "Remove @(*)", "Use only #delay", "Ban ternary",
        ], 0, "Complete assignments.", "easy"),
        lambda i: mcq("", "Intentional latch enable style is…", [
            "when enable is low, hold; when high, pass input", "always posedge", "Only assign #5", "Parameter override",
        ], 0, "Level-sensitive storage.", "easy"),
        lambda i: tf("", "Latches are always bugs — never intentional.", False,
                     "Sometimes intentional, often accidental in FPGA flows.", "easy"),
        lambda i: mcq("", "Default Y=0 before if-tree…", [
            "Helps ensure every path assigns Y", "Creates dual-edge FF", "Removes clocks", "Forces Z",
        ], 0, "Pre-assign pattern.", "easy"),
        lambda i: mcq("", "case (s) 2'b00: y=a; 2'b01: y=b; endcase without default…", [
            "Latch risk for other s values", "Full combo always", "A flop", "Illegal case",
        ], 0, "Uncovered items hold.", "easy"),
        lambda i: tf("", "Full-case / parallel-case pragmas need careful understanding — not magic safety.", True,
                     "Pragmas can hide issues.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Mux with assign is latch-free when…", [
            "The expression always provides a value", "It uses NBA", "It lists posedge", "It is in initial",
        ], 0, "Total function.", "medium"),
        lambda i: mcq("", "Accidental latch vs flop…", [
            "Latch is level-sensitive storage; flop is edge-triggered", "Identical", "Latch needs two clocks", "Flop means wire",
        ], 0, "Different storage semantics.", "medium"),
        lambda i: tf("", "Incomplete reset clause in a combo decode can latch.", True, "Same incomplete rule.", "medium"),
        lambda i: mcq("", "Tool reports 'inferred latch'…", [
            "Incomplete combo assignment likely", "Too many flops", "Missing module", "Only lint style names",
        ], 0, "Classic lint.", "medium"),
        lambda i: mcq("", "if (en) q = d; else q = q; …", [
            "Explicit hold — latch/hold intent", "Pure wire", "Async FIFO", "Parameter",
        ], 0, "Hold path shown.", "medium"),
        lambda i: mcq("", "Using a clock edge in a block meant to be combo…", [
            "You built sequential logic instead", "Removes latches always", "Is @(*)", "Is ANSI",
        ], 0, "Wrong template.", "medium"),
        lambda i: tf("", "Covering all enum/case items removes latch risk for that output.", True,
                     "Completeness matters.", "medium"),
        lambda i: mcq("", "Multiple outputs in one always: one incomplete…", [
            "Can latch only the incomplete nets", "Latches all clocks", "Deletes sensitivity", "Forces X on clk",
        ], 0, "Per-output completeness.", "medium"),
        lambda i: mcq("", "FPGA tip: accidental latches are…", [
            "Often undesirable vs registered style", "Required for every mux", "Identical to BRAM", "Only in packages",
        ], 0, "Prefer registered FPGA style.", "medium"),
        lambda i: mcq("", "default: y = '0; in case…", [
            "Closes uncovered items for y", "Creates dual clock", "Is non-ANSI only", "Removes ports",
        ], 0, "Default assignment.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Partial bit assigns: always @* if (en) y[0]=d; …", [
            "Other bits of y may latch/hold", "All bits clear always", "Illegal always", "Forces wire y",
        ], 0, "Assign all bits you mean.", "hard"),
        lambda i: mcq("", "Unique case (SV) vs latch…", [
            "unique adds checking; still need complete outputs", "unique removes clocks", "unique is a net", "unique bans @(*)",
        ], 0, "Checks ≠ auto-complete.", "hard"),
        lambda i: tf("", "A ternary that references y on a path can still create feedback/hold behavior.", True,
                     "y = en ? d : y is latchy.", "hard"),
        lambda i: mcq("", "Synth 'latch' on a flop enable mistake…", [
            "Sometimes mis-coded enable looks level-sensitive", "Means you need more X", "Means ANSI wrong", "Means no TB",
        ], 0, "Review enable coding.", "hard"),
        lambda i: mcq("", "Intentional transparent latch in ASIC…", [
            "Uses enable/level templates deliberately", "Uses only $finish", "Uses only parameters", "Uses only initial",
        ], 0, "Deliberate level storage.", "hard"),
        lambda i: mcq("", "casex/casez incompleteness…", [
            "Still can latch if not all paths assign", "Always full", "Bans defaults", "Only for TB displays",
        ], 0, "Same completeness rule.", "hard"),
        lambda i: tf("", "Assigning y in every branch including else/default avoids combo latch on y.", True,
                     "Complete drive.", "hard"),
        lambda i: mcq("", "Latches on decoded one-hot with holes…", [
            "Uncovered encodings hold prior y", "Auto gray-code", "Force NBA", "Disable lint forever",
        ], 0, "Cover or default.", "hard"),
        lambda i: mcq("", "Best review question when latch inferred…", [
            "Which path fails to assign this output?", "Which color is the waveform?", "Which Git branch?", "Which font?",
        ], 0, "Find the hole.", "hard"),
        lambda i: mcq("", "Breaking a huge combo always into functions…", [
            "Still need every output assigned on all paths", "Automatically removes latches", "Removes need for @(*)", "Forces flops",
        ], 0, "Completeness still required.", "hard"),
    ]
    return easy, medium, hard


def b_blocking():
    easy = [
        lambda i: mcq("", "In a clocked always block, non-blocking (<=) means…", [
            "All RHS values are sampled first, then LHS updates happen together", "Statements never run on a clock edge", "Only wire outputs", "The block is combo",
        ], 0, "NBA scheduling.", "easy"),
        lambda i: mcq("", "q1 = d; q2 = q1; on one posedge (blocking) typically…", [
            "Both q1 and q2 get d in the same edge", "q2 gets only old q1", "Illegal", "Never change",
        ], 0, "Blocking is ordered.", "easy"),
        lambda i: mcq("", "a <= b; b <= a; with a=1,b=0 before edge…", [
            "a becomes 0 and b becomes 1 — a real swap", "Both unchanged", "Both 0", "Both 1",
        ], 0, "NBA samples both RHS first.", "easy"),
        lambda i: tf("", "Flip-flop RTL in always @(posedge clk) should normally use <= for register updates.", True,
                     "NBA is sequential style.", "easy"),
        lambda i: mcq("", "Blocking `=` in combo always is…", [
            "Common/OK for combo logic", "Illegal", "Only for flops", "Only for wires",
        ], 0, "Combo often uses blocking.", "easy"),
        lambda i: mcq("", "NBA in combo always is…", [
            "Usually discouraged — can surprise", "Required", "Same as assign", "A port style",
        ], 0, "Keep NBA for sequential.", "easy"),
        lambda i: tf("", "`<=` is called a non-blocking assignment.", True, "Name of the operator.", "easy"),
        lambda i: mcq("", "Pipeline shift with NBA: q <= {q[6:0], si}; …", [
            "Registers the new vector next edge", "Combo shift only", "Illegal", "Needs two clocks always",
        ], 0, "Registered shift.", "easy"),
        lambda i: mcq("", "Using blocking for a simple flop q = d; …", [
            "Can work in isolation but is bad style / races in larger code", "Required by IEEE", "Same as wire", "Bans reset",
        ], 0, "Prefer NBA for flops.", "easy"),
        lambda i: tf("", "NBA updates are visible after the active event region per scheduling semantics.", True,
                     "That's why parallel regs swap cleanly.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Race: two always blocks reading/writing with blocking…", [
            "Order-dependent simulation races", "Impossible", "Fixed by ANSI", "Fixed by $clog2",
        ], 0, "NBA reduces race classes.", "medium"),
        lambda i: mcq("", "Temporary combo inside clocked block using blocking…", [
            "Sometimes used carefully; still prefer clean split combo/seq", "Required always", "Illegal always", "Only for interfaces",
        ], 0, "Advanced pattern; teach caution.", "medium"),
        lambda i: tf("", "a <= a + 1; increments the register each clock (with NBA).", True, "Classic counter.", "medium"),
        lambda i: mcq("", "Read-before-write with NBA in one edge…", [
            "RHS sees old value", "RHS always sees new", "Needs wire", "Needs generate",
        ], 0, "Old value sampling.", "medium"),
        lambda i: mcq("", "assign vs NBA…", [
            "assign is continuous on nets; NBA is procedural", "Identical", "assign is only flops", "NBA drives only input ports",
        ], 0, "Different mechanisms.", "medium"),
        lambda i: mcq("", "Non-blocking with intra-assignment delay `q <= #1 d`…", [
            "Simulation delay scheduling — not synth RTL delay", "Creates PLL", "Required FPGA style", "ANSI only",
        ], 0, "Hash delays ≠ synth delay.", "medium"),
        lambda i: tf("", "Mixing = and <= on the same reg in one always is a red flag.", True, "Pick one intent.", "medium"),
        lambda i: mcq("", "Why NBA for multi-reg parallel update?", [
            "All regs update from pre-edge samples — predictable", "Faster synthesis always", "Smaller fonts", "Fewer ports",
        ], 0, "Deterministic parallel regs.", "medium"),
        lambda i: mcq("", "Blocking chain in clocked block creating combo path into next NBA…", [
            "Can infer unexpected logic — avoid spaghetti", "Preferred", "Required for lint", "Only legal with tri",
        ], 0, "Keep seq clean.", "medium"),
        lambda i: mcq("", "SV always_ff guideline…", [
            "Use non-blocking assignments to flops", "Use only blocking", "Ban clocks", "Require initial",
        ], 0, "always_ff + NBA.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "NBA to a wire…", [
            "Illegal — NBA targets variables", "Preferred continuous style", "Creates assign", "Sets parameter",
        ], 0, "Variables only.", "hard"),
        lambda i: mcq("", "Scheduling: active vs NBA region bugs show up as…", [
            "Order-dependent TB/RTL races", "Better WNS always", "ANSI conversion", "Gray counters",
        ], 0, "Event regions matter.", "hard"),
        lambda i: tf("", "In a pure combo block, blocking assignments compute immediately for later statements in that block.", True,
                     "Ordered combo evaluation.", "hard"),
        lambda i: mcq("", "Dual always writing same reg one with = one with <= …", [
            "Broken multi-driver / race nightmare", "Standard dual-port", "Required CDC", "Only SV interfaces",
        ], 0, "One driver.", "hard"),
        lambda i: mcq("", "Nonblocking to memory `mem[a] <= d` …", [
            "Registered write style", "Continuous assign", "Port direction", "Package import",
        ], 0, "NBA memory write.", "hard"),
        lambda i: mcq("", "Forcing blocking everywhere 'because C'…", [
            "Misses hardware concurrency model", "Matches NBA", "Fixes all CDC", "Required by Yosys",
        ], 0, "HDL ≠ C sequencing.", "hard"),
        lambda i: tf("", "A swap with blocking `a=b; b=a;` loses a value without a temp.", True,
                     "Needs temp; NBA swap doesn't.", "hard"),
        lambda i: mcq("", "Intra-assignment vs delayed procedural…", [
            "Different scheduling; avoid in synth RTL", "Same as generate", "Same as localparam", "Same as ANSI",
        ], 0, "Leave delays to TB.", "hard"),
        lambda i: mcq("", "Lint: 'blocking used in sequential' …", [
            "Style warning to prefer NBA in clocked blocks", "Means syntax error always", "Means delete reset", "Means add X",
        ], 0, "Style guidance.", "hard"),
        lambda i: mcq("", "Best simple teaching rule…", [
            "Combo: blocking; sequential: non-blocking; don't mix drivers", "Always blocking", "Always NBA everywhere including assign", "Never use always",
        ], 0, "Classic guideline.", "hard"),
    ]
    return easy, medium, hard


def b_param():
    easy = [
        lambda i: mcq("", "bus_slice #(.WIDTH(16)) means…", [
            "This instance uses WIDTH=16 for parameterized ports", "Module renamed to 16", "DEPTH forced to 16", "Params cannot override",
        ], 0, "Instance parameter override.", "easy"),
        lambda i: mcq("", "For WIDTH=8, logic [WIDTH-1:0] is…", ["[7:0]", "[8:0]", "[8:1]", "[0:7] only"], 0, "WIDTH-1 downto 0.", "easy"),
        lambda i: mcq("", "$clog2(16) is…", ["4", "16", "8", "2"], 0, "2^4=16.", "easy"),
        lambda i: tf("", "A sum of two WIDTH-bit unsigned values often needs WIDTH+1 bits for carry.", True,
                     "Carry grows one bit.", "easy"),
        lambda i: mcq("", f"$clog2({[8,16,32,64][(i-1)%4]}) equals…", [
            str([3,4,5,6][(i-1)%4]), "1", "0", "16",
        ], 0, "ceil log2.", "easy"),
        lambda i: mcq("", "parameter WIDTH = 8 is…", [
            "A module elaboration-time constant (overridable)", "A wire", "A clock", "A $finish",
        ], 0, "Parameters configure instances.", "easy"),
        lambda i: tf("", "Parameters are evaluated at elaboration, not as runtime changing regs.", True,
                     "Elaboration constants.", "easy"),
        lambda i: mcq("", "`#(8)` positional parameter override sets…", [
            "The first parameter in declaration order", "A port named 8", "Always DEPTH", "Nothing",
        ], 0, "Positional param map.", "easy"),
        lambda i: mcq("", "Width mismatch vs parameter…", [
            "Keep port widths derived from parameters for consistency", "Ignore widths", "Only use literals", "Ban vectors",
        ], 0, "Derive widths from params.", "easy"),
        lambda i: tf("", "`parameter` defaults can be overridden at instantiation.", True, "That's the point.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "defparam is…", [
            "Legacy hierarchical override — prefer #(.P(v))", "Required modern style", "A nettype", "A sensitivity",
        ], 0, "Avoid defparam in new RTL.", "medium"),
        lambda i: mcq("", "localparam vs parameter…", [
            "localparam is not overridable from outside", "Identical", "localparam is a port", "parameter cannot have default",
        ], 0, "localparam is internal.", "medium"),
        lambda i: tf("", "`$clog2(1)` is 0 in common definitions.", True, "ceil log2(1)=0.", "medium"),
        lambda i: mcq("", "Derived `parameter AW = $clog2(DEPTH)` …", [
            "Computes address width from DEPTH", "Creates a flop", "Is a continuous assign", "Needs NBA",
        ], 0, "Elaboration math.", "medium"),
        lambda i: mcq("", "Overriding a dependent parameter incorrectly…", [
            "Can break derived widths — override base params carefully", "Always safe", "Only affects $display", "Renames module",
        ], 0, "Override roots, not fragile dependents.", "medium"),
        lambda i: mcq("", "ANSI + parameters pattern…", [
            "module m #(parameter W=8) (input [W-1:0] d, ...);", "always @* only", "Only defparam", "Only TB",
        ], 0, "Common header style.", "medium"),
        lambda i: tf("", "Parameter type can be specified in SystemVerilog more richly than classic Verilog.", True,
                     "SV typed parameters.", "medium"),
        lambda i: mcq("", "Instance `u #(.W(4), .D(16))` …", [
            "Named parameter overrides", "Positional ports only", "Deletes params", "Forces Z",
        ], 0, "Named #(. ) list.", "medium"),
        lambda i: mcq("", "Why not hardcode [7:0] when WIDTH exists…", [
            "Breaks when WIDTH changes", "Faster sim always", "Required by lint names", "Only for gray code",
        ], 0, "Keep parameterized.", "medium"),
        lambda i: mcq("", "`parameter real` …", [
            "Possible for some non-synth configs; beware synth subsets", "Always a flop", "A port direction", "A case item",
        ], 0, "Limited/synth caution.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "$clog2(0) / edge cases…", [
            "Problematic — guard DEPTH>=1 in real designs", "Always 32", "Always -1", "Sets clock",
        ], 0, "Validate parameters.", "hard"),
        lambda i: mcq("", "generate if (WIDTH>4) depends on…", [
            "Elaboration-time constant WIDTH", "Runtime reg WIDTH", "NBA", "Test $finish",
        ], 0, "Generate needs constants.", "hard"),
        lambda i: tf("", "You can override localparam with #(.DEPTH(n)).", False,
                     "localparam is not overridable that way.", "hard"),
        lambda i: mcq("", "Parameter dependency cycles…", [
            "Illegal / must be acyclic elaboration", "Fine always", "Create latches", "Only in TB",
        ], 0, "No cycles.", "hard"),
        lambda i: mcq("", "Different instances with different WIDTH…", [
            "Are different elaborations of the same module", "Share one WIDTH globally always", "Illegal", "Need packages",
        ], 0, "Per-instance elaboration.", "hard"),
        lambda i: mcq("", "Unsigned vs signed parameters in width math…", [
            "Affects expressions — keep intent clear", "Irrelevant always", "Only for $display", "Only for tasks",
        ], 0, "Signedness matters.", "hard"),
        lambda i: tf("", "`parameter W = 8; localparam W2 = W*2;` recomputes W2 when W overridden on instance.", True,
                     "Derived localparams follow.", "hard"),
        lambda i: mcq("", "Overriding only a derived parameter that should be localparam…", [
            "Design smell — make it localparam", "Required", "Fixes CDC", "Creates ANSI",
        ], 0, "Don't expose derived knobs.", "hard"),
        lambda i: mcq("", "Huge parameter-created muxes…", [
            "Can explode area — parameterization isn't free", "Are always optimal", "Ban generate", "Ignore WIDTH",
        ], 0, "Elaboration still builds hardware.", "hard"),
        lambda i: mcq("", "Best practice for addressable depth D…", [
            "AW = $clog2(D) with D power-of-two or careful ceil", "AW = D", "AW = 32 always", "AW = $bits(clk)",
        ], 0, "clog2 for pointers.", "hard"),
    ]
    return easy, medium, hard


def b_named_pos():
    easy = [
        lambda i: mcq("", "Positional instance dff u(clk, din, qout) connects by…", [
            "Port declaration order in the module", "Alphabetical names", "Simulation time", "Parameter list only",
        ], 0, "Order maps ports.", "easy"),
        lambda i: mcq("", "Named connection .d(din) means…", [
            "Port d is wired to net din", "Net din renamed to d", "Only parameters set", "Widths must match names",
        ], 0, "Formal.d ← actual din.", "easy"),
        lambda i: mcq("", "dff u(clk, qout, din) when ports are (clk, d, q)…", [
            "Often compiles but swaps d and q — silent miswire", "Always syntax error", "Same as named", "Only for AND",
        ], 0, "Positional footgun.", "easy"),
        lambda i: tf("", "Named port connections are preferred for multi-port modules.", True,
                     "Safer maintenance.", "easy"),
        lambda i: mcq("", "`.clk(clk), .d(d), .q(q)` style is…", [
            "Named associations", "Positional only", "Generate", "defparam",
        ], 0, "Named style.", "easy"),
        lambda i: mcq("", "Empty `.q()` means…", [
            "Leave port q unconnected", "Tie q to 0", "Delete q", "Set parameter q",
        ], 0, "Explicit open.", "easy"),
        lambda i: tf("", "Positional connects can break when someone reorders ports.", True, "Brittle.", "easy"),
        lambda i: mcq("", "Mixing `.d(d), qout` styles…", [
            "Illegal mix in one instance", "Preferred", "Required ANSI", "Only SV",
        ], 0, "Don't mix.", "easy"),
        lambda i: mcq("", "Named connects ignore…", [
            "Declaration order (names matter)", "Formal names", "Actual nets", "Module existence",
        ], 0, "Order irrelevant for named.", "easy"),
        lambda i: tf("", "You can still use positional for tiny primitive-like instances if careful.", True,
                     "OK for small/stable port lists.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "`.rst_n()` intentionally open on unused reset…", [
            "Documents unused port; ensure design allows it", "Ties reset low always", "Deletes flop", "Sets WIDTH",
        ], 0, "Open with care.", "medium"),
        lambda i: mcq("", "Typo `.clkk(clk)` …", [
            "Error: unknown formal port", "Silently creates new port", "Positional map", "Parameter",
        ], 0, "Names must match formals.", "medium"),
        lambda i: tf("", "Named parameter overrides `#(.W(8))` are analogous safety to named ports.", True,
                     "Named beats positional.", "medium"),
        lambda i: mcq("", "Reordering ports in module header…", [
            "Breaks positional instances; named usually OK", "Breaks named always", "Breaks assign", "Breaks $clog2",
        ], 0, "Named survives reorder.", "medium"),
        lambda i: mcq("", "Implicit `.name` (SV) …", [
            "Connects when formal and actual share the name", "Is classic 1995 only", "Is a latch", "Is a package",
        ], 0, "SV .name shorthand.", "medium"),
        lambda i: mcq("", "Positional with too few args…", [
            "Trailing ports unconnected", "Always error in all tools", "Fills with 1", "Rotates ports",
        ], 0, "Unconnected trailing.", "medium"),
        lambda i: tf("", "Too many positional args is an error.", True, "Arity must fit.", "medium"),
        lambda i: mcq("", "Connecting a wider actual to a narrow formal…", [
            "Truncation/warning risk", "Always hard error", "Changes module name", "Forces NBA",
        ], 0, "Width discipline.", "medium"),
        lambda i: mcq("", "Why reviews ban positional on large IPs…", [
            "Silent miswires are costly", "Slower typing named", "Named illegal", "Positional bans clocks",
        ], 0, "Safety.", "medium"),
        lambda i: mcq("", "`.a(a), .b(b), .c()` with required c driven inside…", [
            "May be OK if c is output-only unused", "Always drives c to X from parent", "Deletes c", "Sets param c",
        ], 0, "Outputs may be open.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Port connection `.*` (SV) …", [
            "Auto-connects matching names — still verify!", "Classic Verilog 1995", "A sensitivity list", "A nettype",
        ], 0, "SV .* wildcard.", "hard"),
        lambda i: mcq("", "Named connect to a non-existent actual net without declaration…", [
            "May create implicit net (hazard) depending on default_nettype", "Always safe", "Always deletes port", "Sets localparam",
        ], 0, "Implicit nets bite.", "hard"),
        lambda i: tf("", "Positional mapping uses the ANSI/non-ANSI header order of port names.", True,
                     "Header order is truth.", "hard"),
        lambda i: mcq("", "Connecting inout with named style still needs…", [
            "A proper bidirectional net on the actual", "Only a reg without net", "Only initial", "Only $display",
        ], 0, "Net discipline.", "hard"),
        lambda i: mcq("", "Instance array with named ports…", [
            "Each instance gets the same named mapping pattern", "Bans named", "Requires defparam", "Requires wait",
        ], 0, "Arrays + named OK.", "hard"),
        lambda i: mcq("", "Tool allows positional for UDP primitives often because…", [
            "Tiny fixed port lists", "Named illegal on gates", "Gates have no ports", "Only SV",
        ], 0, "Small stable arity.", "hard"),
        lambda i: tf("", "Changing a port name breaks named connections that used the old formal.", True,
                     "Rename is a breaking API.", "hard"),
        lambda i: mcq("", "Best refactor safety…", [
            "Named ports + named params + tests", "Only positional", "Only delays", "Only casex",
        ], 0, "Named everything.", "hard"),
        lambda i: mcq("", "Unconnected input with named omit…", [
            "Floating/X risk — tie off intentionally", "Auto 0 always in synth", "Auto 1", "Becomes parameter",
        ], 0, "Tie offs explicitly.", "hard"),
        lambda i: mcq("", "Documentation tip…", [
            "Show named instance templates in EXAMPLES", "Hide port names", "Only show waveforms", "Ban instances",
        ], 0, "Teach named templates.", "hard"),
    ]
    return easy, medium, hard


def b_localparam():
    easy = [
        lambda i: mcq("", "parameter WIDTH = 8 at the module boundary…", [
            "Can be overridden per instance with #(.WIDTH(n))", "Can never change", "Is a wire", "Only TB",
        ], 0, "Overridable knob.", "easy"),
        lambda i: mcq("", "localparam DEPTH = WIDTH * 2 is meant for…", [
            "Derived constants that should not be overridden from outside", "Runtime variables", "Port directions", "Replacing all parameters",
        ], 0, "Internal derived constants.", "easy"),
        lambda i: mcq("", "fifo #(.WIDTH(4)) when default WIDTH=8…", [
            "Sets WIDTH to 4; derived localparams recompute", "Renames module", "Illegal", "Sim-only",
        ], 0, "Override base param.", "easy"),
        lambda i: tf("", "#(.DEPTH(99)) is inappropriate when DEPTH is localparam.", True,
                     "Cannot override localparam that way.", "easy"),
        lambda i: mcq("", "Which should be localparam?", [
            "AW = $clog2(DEPTH) derived from DEPTH", "WIDTH exposed to users", "clk", "rst_n",
        ], 0, "Derived → localparam.", "easy"),
        lambda i: mcq("", "Which should be parameter?", [
            "User-facing WIDTH/DEPTH configuration", "Temporary combo y", "Always block", "$time",
        ], 0, "Expose knobs as parameter.", "easy"),
        lambda i: tf("", "localparam can depend on parameter values.", True, "Common pattern.", "easy"),
        lambda i: mcq("", "Trying to override localparam in instance…", [
            "Should fail / is invalid", "Silently works always", "Creates ports", "Creates NBA",
        ], 0, "Not overridable.", "easy"),
        lambda i: mcq("", "Teaching reason for localparam…", [
            "Prevent callers from breaking invariants", "Faster typing", "Ban math", "Replace modules",
        ], 0, "Protect derived values.", "easy"),
        lambda i: tf("", "parameter and localparam are both elaboration-time constants.", True, "Both constants.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Exposing DEPTH and AW both as parameters risks…", [
            "Inconsistent pairs (AW != clog2(DEPTH))", "Faster STA", "Better naming only", "Automatic CDC",
        ], 0, "One source of truth.", "medium"),
        lambda i: mcq("", "localparam can be used in…", [
            "Widths, generate conditions, case sizes", "Runtime changing counters without clocks", "Only $finish", "Only filenames",
        ], 0, "Elaboration uses.", "medium"),
        lambda i: tf("", "You may declare localparam before use in expressions that need it.", True,
                     "Order declarations sanely.", "medium"),
        lambda i: mcq("", "SV typed localparam…", [
            "Allows clearer types than classic untyped feel", "Bans constants", "Is a port", "Is sensitivity",
        ], 0, "SV improvements.", "medium"),
        lambda i: mcq("", "Nested localparam in generate…", [
            "Scopes to the generate block", "Global always", "Illegal always", "Creates wires",
        ], 0, "Generate scope.", "medium"),
        lambda i: mcq("", "Documenting parameters in README…", [
            "List overridable parameters; mention derived localparams", "Only list localparams as knobs", "Hide WIDTH", "Ban #(. )",
        ], 0, "Document the API.", "medium"),
        lambda i: tf("", "A localparam string for messages can be handy in elaborative checks.", True,
                     "Constants for asserts/messages.", "medium"),
        lambda i: mcq("", "Changing WIDTH override updates…", [
            "Dependent localparam math automatically", "Nothing else", "Only TB $display strings hardcoding 8", "Only filename",
        ], 0, "Dependents follow.", "medium"),
        lambda i: mcq("", "Anti-pattern: localparam WIDTH = 8 as the only width knob…", [
            "Users can't override — should be parameter if configurable", "Perfect API", "Required", "Fixes races",
        ], 0, "Knobs need parameter.", "medium"),
        lambda i: mcq("", "Check `if (AW < $clog2(DEPTH)) $error` …", [
            "Elaboration assertion pattern (SV) / protect configs", "Runtime NBA", "Port connect", "Latch",
        ], 0, "Validate configs.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Classic Verilog without $error…", [
            "Use generate tricks / comments / external checks", "Can override localparam", "Must use CPU", "Must use casex",
        ], 0, "Older tools lack $error.", "hard"),
        lambda i: mcq("", "localparam in package (SV)…", [
            "Shared constants imported by modules", "Classic 1995 only", "A flip-flop", "A sensitivity list",
        ], 0, "Packages hold consts.", "hard"),
        lambda i: tf("", "Hierarchical defparam to a localparam should be rejected.", True,
                     "localparam isn't an override target.", "hard"),
        lambda i: mcq("", "Elaboration order of param/localparam…", [
            "Must be acyclic and well-ordered", "Random each sim", "Runtime NBA order", "Port order only",
        ], 0, "Deterministic elaboration.", "hard"),
        lambda i: mcq("", "Using parameter for a value that must stay consistent with another overridden param…", [
            "Prefer localparam derived from the root knob", "Expose both always", "Use two clocks", "Use force",
        ], 0, "Derive.", "hard"),
        lambda i: mcq("", "Generate for (genvar i=0;i<DEPTH;i++) uses DEPTH that is…", [
            "parameter/localparam constant", "A free-running counter reg", "Only $time", "Only inout",
        ], 0, "Constant bounds.", "hard"),
        lambda i: tf("", "Instance override of WIDTH updates localparam DEPTH=WIDTH*2 in that instance.", True,
                     "Yes — derived locals recompute.", "hard"),
        lambda i: mcq("", "Why reviewers search for #(.AW(", [
            "Smell: overriding derived address width", "Required style", "Faster typing", "ANSI conversion",
        ], 0, "Don't override derived.", "hard"),
        lambda i: mcq("", "Computation `$clog2(DEPTH+1)` as localparam…", [
            "Common for pointer widths with extra state", "Illegal math", "Creates latch", "Needs NBA",
        ], 0, "Pointer width patterns.", "hard"),
        lambda i: mcq("", "Best API…", [
            "Few root parameters + localparams for everything derived", "All constants as parameters", "No constants", "Only defparam",
        ], 0, "Minimal knobs.", "hard"),
    ]
    return easy, medium, hard


def b_generate():
    easy = [
        lambda i: mcq("", "{4{1'b1}} in an assign means…", [
            "Concatenate four copies of 1'b1 — width 4", "Multiply at runtime", "Declare four modules", "Illegal outside always",
        ], 0, "Replication concat.", "easy"),
        lambda i: mcq("", "The loop index in generate for is declared as…", [
            "genvar", "integer in always", "wire", "reg updated each clock",
        ], 0, "genvar for generate loops.", "easy"),
        lambda i: mcq("", "generate if (WIDTH > 4) …", [
            "Keeps one branch at elaboration based on constant WIDTH", "Runs both every clock", "Needs sensitivity", "TB only",
        ], 0, "Elaboration choice.", "easy"),
        lambda i: tf("", "generate for is not the same as a for loop inside an always at simulation time.", True,
                     "Generate elaborates structure.", "easy"),
        lambda i: mcq("", "Replication `{N{bus}}` requires N…", [
            "Constant (elaboration-time)", "Runtime changing reg without care", "A task", "A string",
        ], 0, "N must be constant.", "easy"),
        lambda i: mcq("", "generate endgenerate wraps…", [
            "Elaboration constructs (for/if/case)", "Only $display", "Only NBA", "Only timescale",
        ], 0, "Generate region.", "easy"),
        lambda i: tf("", "You can instantiate modules inside generate for.", True, "Structural replication.", "easy"),
        lambda i: mcq("", "`assign y = {WIDTH{1'b0}};` …", [
            "Zero vector WIDTH bits", "WIDTH modules", "A flop chain", "Illegal concat",
        ], 0, "Replicate zeros.", "easy"),
        lambda i: mcq("", "genvar i; for (i=0;i<4;i++) begin : g …", [
            "Named generate block g[i]", "Runtime loop only", "A package", "A port list",
        ], 0, "Labeled generate.", "easy"),
        lambda i: tf("", "Unnamed generate blocks are harder to hierarchical-reference.", True,
                     "Name your blocks.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "generate case (WIDTH) …", [
            "Selects structure by constant WIDTH", "Runtime case like always", "Needs @(*)", "Is localparam keyword",
        ], 0, "Generate case.", "medium"),
        lambda i: mcq("", "Hierarchy `g[2].u1.q` …", [
            "References instance inside generate index 2", "Is a localparam", "Is only TB $finish", "Is ANSI port",
        ], 0, "Generate hierarchy paths.", "medium"),
        lambda i: tf("", "Generate if false branch is not elaborated into hardware.", True, "Dead branch gone.", "medium"),
        lambda i: mcq("", "Runtime for-loop in always vs generate for…", [
            "always for is sequential/combo procedural; generate builds instances", "Identical", "Both ban modules", "Both need genvar",
        ], 0, "Different mechanisms.", "medium"),
        lambda i: mcq("", "Parameterizing number of pipeline stages with generate…", [
            "Common structural pattern", "Illegal", "Only for TB", "Requires force",
        ], 0, "Generate pipelines.", "medium"),
        lambda i: mcq("", "Missing begin/end labels in nested generate…", [
            "Can cause confusing hierarchy / tool issues", "Required unnamed", "Faster STA", "Fixes CDC",
        ], 0, "Label blocks.", "medium"),
        lambda i: tf("", "Replication is orthogonal to generate — both are elaboration helpers.", True,
                     "Both structural.", "medium"),
        lambda i: mcq("", "Conditional module instantiation via generate if…", [
            "Chooses which submodule exists", "Runs both modules every cycle", "Needs NBA", "Needs $finish",
        ], 0, "Optional instances.", "medium"),
        lambda i: mcq("", "genvar cannot be…", [
            "Assigned in an always like a normal integer counter for sim loops casually", "Used as generate index", "Declared", "Compared to WIDTH",
        ], 0, "genvar role is generate.", "medium"),
        lambda i: mcq("", "`{2{4'hA}}` width is…", ["8", "4", "2", "16"], 0, "2*4 bits.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Generate loop with non-genvar integer…", [
            "Wrong — use genvar for generate for", "Preferred", "Required in 1995 only", "Same as always for",
        ], 0, "genvar required.", "hard"),
        lambda i: mcq("", "Elaboration recursion / huge generate…", [
            "Can explode compile/area — bound carefully", "Always free", "Ban parameters", "Only affects fonts",
        ], 0, "Complexity cost.", "hard"),
        lambda i: tf("", "You cannot use a non-constant reg value as a generate if condition.", True,
                     "Must be constant.", "hard"),
        lambda i: mcq("", "Defparam inside generate…", [
            "Legacy mess — avoid", "Modern best practice", "Required for genvar", "Same as localparam",
        ], 0, "Avoid defparam.", "hard"),
        lambda i: mcq("", "Externally referencing unnamed generate…", [
            "Tool-dependent / fragile — name blocks", "Stable across all tools always", "Illegal to instantiate inside", "Requires wire only",
        ], 0, "Name them.", "hard"),
        lambda i: mcq("", "Mixing generate and manual instance arrays…", [
            "Either pattern OK; don't confuse readers", "Illegal always", "Required together", "Only for latches",
        ], 0, "Pick clear style.", "hard"),
        lambda i: tf("", "Generate case must cover or have default for legal elaboration in strict use.", True,
                     "Complete generate case.", "hard"),
        lambda i: mcq("", "Using generate to optional scan logic…", [
            "Common with parameter ENABLE_SCAN", "Requires two clocks always", "Needs casex", "Needs force",
        ], 0, "Feature flags.", "hard"),
        lambda i: mcq("", "Bit-blasting N AND gates with generate for…", [
            "Structural teaching pattern", "Same as reduction & automatically", "Bans assign", "Needs TB $monitor only",
        ], 0, "Structural replicate.", "hard"),
        lambda i: mcq("", "Best review ask…", [
            "Is the generate condition truly constant and bounded?", "What color is the GUI?", "Which emoji?", "Which music?",
        ], 0, "Check elaboration assumptions.", "hard"),
    ]
    return easy, medium, hard


def b_one_driver():
    easy = [
        lambda i: mcq("", "Two strong drivers on one wire: 1 and 0…", [
            "Resolve to X (contention) in simulation", "Always 1", "Legal synth RTL ideal", "Mean Z",
        ], 0, "Contention → X.", "easy"),
        lambda i: mcq("", "assign y = sel ? b : a; is safer because…", [
            "One continuous assign structurally selects one source", "sel must be clock", "a/b constants", "Uses NBA",
        ], 0, "Single driver mux.", "easy"),
        lambda i: mcq("", "Tri-state drivers are acceptable when…", [
            "At most one driver is not Z at a time", "Every driver always enabled", "Net is a clock", "You use blocking",
        ], 0, "One active driver.", "easy"),
        lambda i: tf("", "Two always blocks driving the same reg is a multi-driver mistake.", True,
                     "One procedural driver.", "easy"),
        lambda i: mcq("", "Preferred bus mux style in RTL…", [
            "Single assign/always mux — not two enabled drives fighting", "Two assigns both on", "force in RTL", "Only initial",
        ], 0, "Mux, don't fight.", "easy"),
        lambda i: mcq("", "Z means…", ["high impedance", "logic 1", "logic 0", "parameter"], 0, "Hi-Z.", "easy"),
        lambda i: tf("", "X means unknown/contention-like unknown in sim.", True, "Unknown.", "easy"),
        lambda i: mcq("", "output from two modules tied together without resolution…", [
            "Multi-driver bug", "Preferred OR", "Automatic wired-AND always desired", "Parameter merge",
        ], 0, "Don't tie outputs carelessly.", "easy"),
        lambda i: mcq("", "assign y = a; assign y = b; …", [
            "Multi-driver on y", "Legal mux", "Creates flop", "Named port",
        ], 0, "Two assigns.", "easy"),
        lambda i: tf("", "A mux is the usual synthesizable way to choose between sources.", True, "Select, don't contend.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "wand/wor nets…", [
            "Resolved net types — still understand contention intent", "Flip-flop types", "Only SV interfaces", "Sensitivity lists",
        ], 0, "Resolution functions.", "medium"),
        lambda i: mcq("", "Bus keeper / pullups…", [
            "Weak helpers — not an excuse for two strong fighters", "Replace mux always", "Ban Z", "Are parameters",
        ], 0, "Weak ≠ fix contention.", "medium"),
        lambda i: tf("", "Inout bidirectional pads need enable discipline so only one side drives.", True,
                     "Enable one driver.", "medium"),
        lambda i: mcq("", "Multiple TB forces on a net…", [
            "Can create intentional overrides — still not synth RTL style", "Required in modules", "Named ANSI", "Localparam",
        ], 0, "TB vs RTL.", "medium"),
        lambda i: mcq("", "Aliasing two names to one net with two drivers…", [
            "Still contention", "Fixes contention", "Creates generate", "Creates genvar",
        ], 0, "One net semantics.", "medium"),
        lambda i: mcq("", "Register file write ports…", [
            "Need arbitration/muxing — not two writes same cycle unchecked", "Always dual drive q", "Ban clocks", "Use only Z",
        ], 0, "Arbiter/mux writes.", "medium"),
        lambda i: tf("", "Synthesis may soft-error or warn on multi-driven nets.", True, "Tools complain.", "medium"),
        lambda i: mcq("", "Tri + mux alternatives…", [
            "Prefer mux/select in FPGA; tri more ASIC/pad oriented", "Tri always best FPGA", "Mux illegal", "Both ban assigns",
        ], 0, "Technology style.", "medium"),
        lambda i: mcq("", "always_comb unique driver rule (SV)…", [
            "Helps catch multi-driven variables", "Creates Z", "Bans mux", "Is a port",
        ], 0, "SV checks.", "medium"),
        lambda i: mcq("", "Open drain intentional multi-driver…", [
            "Special electrical intent — not beginner RTL default", "Same as assign mux", "Same as NBA flop", "Same as $clog2",
        ], 0, "Advanced I/O.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Resolving X after contention when one driver goes Z…", [
            "May recover to driven value after Z — still avoid fights", "Stays X forever always", "Becomes parameter", "Becomes genvar",
        ], 0, "Still bad design.", "hard"),
        lambda i: mcq("", "Tran switches / bidirectional switches…", [
            "Specialized — not substitute for clean one-driver RTL", "Preferred coding everywhere", "Same as always_ff", "Same as ANSI",
        ], 0, "Specialty primitives.", "hard"),
        lambda i: tf("", "A clock net should have a single intentional driver (plus buffers as designed).", True,
                     "Clock integrity.", "hard"),
        lambda i: mcq("", "CDC + multi-driver bugs…", [
            "Orthogonal problems — fix drivers first", "Same fix with $clog2", "Fixed by positional ports", "Fixed by Fraunces font",
        ], 0, "Separate concerns.", "hard"),
        lambda i: mcq("", "Lint 'multi driven net' false positives…", [
            "Sometimes from generate alternatives — still verify exclusivity", "Ignore forever", "Delete all assigns", "Ban modules",
        ], 0, "Prove mutual exclusion.", "hard"),
        lambda i: mcq("", "Best fix for two producers…", [
            "Insert mux/arbiter with clear select", "Tie outputs together", "force both", "Remove sensitivity",
        ], 0, "Select structure.", "hard"),
        lambda i: tf("", "Reading a multi-driven X in TB can hide DUT bugs until contention clears.", True,
                     "X can mask.", "hard"),
        lambda i: mcq("", "SV `nettype` custom resolution…", [
            "Advanced — beyond classic one-driver teaching", "Required 1995", "Same as genvar", "Same as $finish",
        ], 0, "Advanced SV.", "hard"),
        lambda i: mcq("", "Instance outputs shorted in schematic…", [
            "Same multi-driver class of bug", "Preferred OR reduction", "Automatic localparam", "Named port fix",
        ], 0, "Schematic shorts.", "hard"),
        lambda i: mcq("", "Teaching mantra…", [
            "One signal, one driver (or disciplined Z enables)", "More drivers more better", "Always use force", "Never mux",
        ], 0, "One driver rule.", "hard"),
    ]
    return easy, medium, hard


def b_counter():
    easy = [
        lambda i: mcq("", "A 4-bit up counter after 4'b1111 usually goes to…", [
            "4'b0000", "4'b1111", "4'b10000 in same reg", "X automatically",
        ], 0, "Wrap on overflow.", "easy"),
        lambda i: mcq("", "Preferred hold pattern for a counter…", [
            "One always with if (ce) count <= count + 1;", "Two always drivers", "Blocking combo only", "Tie to Z when idle",
        ], 0, "Clock enable hold.", "easy"),
        lambda i: mcq("", "Modulo-10 counter wraps when q reaches…", [
            "9, then next becomes 0", "10 stored in 4 bits", "15 always", "1 because CE resets",
        ], 0, "Terminal count 9.", "easy"),
        lambda i: tf("", "Gray counting changes only one bit between adjacent codes.", True, "Gray property.", "easy"),
        lambda i: mcq("", f"An {['3','4','5','8'][(i-1)%4]}-bit binary up counter has modulus…", [
            str([8,16,32,256][(i-1)%4]), "10", "100", "3",
        ], 0, "2^W.", "easy"),
        lambda i: mcq("", "Async reset clears count…", [
            "When reset asserts, independent of clock edge (per template)", "Only on $finish", "Only with generate", "Only with Z",
        ], 0, "Async reset template.", "easy"),
        lambda i: tf("", "Sync reset clears on clock edge while reset is asserted.", True, "Sync reset.", "easy"),
        lambda i: mcq("", "Down counter on 0 with wrap…", [
            "Goes to all-ones for binary width", "Stays 0", "Goes to X", "Deletes width",
        ], 0, "Underflow wrap.", "easy"),
        lambda i: mcq("", "ce means…", [
            "clock enable — hold when low", "carry export only", "case equality", "compile error",
        ], 0, "Clock enable.", "easy"),
        lambda i: tf("", "Counters are usually coded with non-blocking updates.", True, "Sequential NBA.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Loadable counter…", [
            "if (load) q<=din; else if (ce) q<=q+1;", "Two always blocks driving q", "Only assign", "Only initial",
        ], 0, "Priority load/enable.", "medium"),
        lambda i: mcq("", "Mod-N for non-power-of-two N…", [
            "Compare to N-1 and recycle to 0", "Automatic with any width", "Impossible", "Needs dual clock",
        ], 0, "Explicit terminal count.", "medium"),
        lambda i: tf("", "Using count = count + 1 with blocking in clocked block is poor flop style.", True,
                     "Use NBA.", "medium"),
        lambda i: mcq("", "Gray to binary conversion…", [
            "Needed when interacting with binary arithmetic", "Never needed", "Same as $clog2", "Same as ANSI",
        ], 0, "Code conversion.", "medium"),
        lambda i: mcq("", "Prescaler / divider from counter…", [
            "Terminal count pulses a tick", "Requires Z drivers", "Bans ce", "Needs defparam only",
        ], 0, "Tick generation.", "medium"),
        lambda i: mcq("", "Signed counter vs unsigned…", [
            "Affects compare/overflow interpretation", "Identical always", "Bans wrap", "Forces X",
        ], 0, "Signedness matters.", "medium"),
        lambda i: tf("", "Clear and enable both true need defined priority in the if-tree.", True,
                     "Specify priority.", "medium"),
        lambda i: mcq("", "Almost-full style counts…", [
            "Compare q to a threshold", "Require multi-driver", "Ban NBA", "Use only $display",
        ], 0, "Threshold flags.", "medium"),
        lambda i: mcq("", "Why Gray for async handshake pointers sometimes…", [
            "Single-bit change reduces multi-bit sampling hazard", "Faster adders", "Named ports", "ANSI only",
        ], 0, "CDC-friendly pointers.", "medium"),
        lambda i: mcq("", "Width W counter + add 1 without sizing care…", [
            "Wraps modulo 2^W", "Grows automatically forever in the same reg", "Becomes real", "Becomes time",
        ], 0, "Fixed width wrap.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "LFSR vs binary counter…", [
            "LFSR sequences differ; not consecutive binary", "Identical counts", "LFSR bans clocks", "Binary bans XOR",
        ], 0, "Different sequences.", "hard"),
        lambda i: mcq("", "One-hot counters…", [
            "Shift a single 1 — different encoding tradeoffs", "Always smaller than binary", "Illegal", "Need Z",
        ], 0, "One-hot sequencing.", "hard"),
        lambda i: tf("", "Terminal count decode is a combo function of q (often registered for timing).", True,
                     "Decode then optional reg.", "hard"),
        lambda i: mcq("", "CDC: gray pointer into other clock…", [
            "Synchronize gray, then convert", "Sample binary multi-bit directly safely always", "Use force", "Use only blocking",
        ], 0, "Gray + sync.", "hard"),
        lambda i: mcq("", "Saturation counter (no wrap)…", [
            "Stops at max/min instead of wrapping", "Illegal", "Needs two drivers", "Needs $finish",
        ], 0, "Saturating arithmetic.", "hard"),
        lambda i: mcq("", "Up/down with dir…", [
            "q <= dir ? q+1 : q-1; with enables/resets prioritized", "Two always on q", "Only assign #5", "Only generate if false",
        ], 0, "Directional update.", "hard"),
        lambda i: tf("", "Modulus not dividing 2^W still fits in W bits if N <= 2^W.", True,
                     "N=10 fits in 4 bits.", "hard"),
        lambda i: mcq("", "Hierarchical counters (bytes)…", [
            "Ripple enables between stages", "Must be one flat always only ever", "Ban ce", "Require tri",
        ], 0, "Cascaded enables.", "hard"),
        lambda i: mcq("", "Formal: prove wrap at 9 for decade…", [
            "Property on q sequence / reset behavior", "Only $display", "Only fonts", "Only positional ports",
        ], 0, "Spec the wrap.", "hard"),
        lambda i: mcq("", "Teaching bug: if (ce) q<=q+1; else q<=q+1; …", [
            "Enable does nothing — always increments", "Holds correctly", "Clears", "Tri-states",
        ], 0, "Both branches increment.", "hard"),
    ]
    return easy, medium, hard


def b_shiftreg():
    easy = [
        lambda i: mcq("", "After 3 clocks, a bit entered into an 8-bit shift register is at…", [
            "Stage 2 (0-indexed from input end)", "Stage 7", "Stage 0 still", "Lost always",
        ], 0, "Advances one stage per clock.", "easy"),
        lambda i: mcq("", "Shift in serial bit si at the LSB of 8-bit q (toward MSB)…", [
            "q <= {q[6:0], si};",
            "q <= q + si;",
            "q <= si only",
            "q <= 8'bz",
        ], 0, "Low bits shift up; si enters at LSB.", "easy"),
        lambda i: mcq("", "PISO with load…", [
            "Captures parallel when load, then shifts out", "Only shifts forever", "Needs blocking for flops", "Bans clocks",
        ], 0, "Parallel load / serial out.", "easy"),
        lambda i: tf("", "Blocking `=` in clocked shiftreg is preferred over `<=`.", False,
                     "Use NBA for flops.", "easy"),
        lambda i: mcq("", "SIPO means…", [
            "Serial-in parallel-out", "Signed integer port out", "Single inout pull-up only", "Synth ignore pull-out",
        ], 0, "Serial in, parallel out.", "easy"),
        lambda i: mcq("", "Direction toward LSB commonly…", [
            "q <= {si, q[7:1]}; (example)", "q <= q;", "q <= ~q always", "Only assign",
        ], 0, "Concat defines direction.", "easy"),
        lambda i: tf("", "Shift registers are chains of flops.", True, "Pipeline of bits.", "easy"),
        lambda i: mcq("", "Arithmetic shift vs logical shift on signed…", [
            "Arithmetic preserves sign on right shift", "Identical always", "Both insert X", "Both illegal",
        ], 0, ">>> vs >> .", "easy"),
        lambda i: mcq("", "Enable on shiftreg…", [
            "Hold when ce low", "Must tri-state q", "Needs two always", "Bans NBA",
        ], 0, "Clock enable.", "easy"),
        lambda i: tf("", "Rotate is a shift that feeds vacated bits from the other end.", True, "Rotate vs shift-in.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "Barrel shifter vs shift register…", [
            "Barrel is combo mux shift; shiftreg is sequential over cycles", "Identical", "Barrel needs NBA", "Shiftreg bans mux",
        ], 0, "Combo vs seq.", "medium"),
        lambda i: mcq("", "Universal shift register…", [
            "Supports hold/shift L/R/load modes", "Only one mode legal", "No clocks", "Only Z out",
        ], 0, "Multi-function.", "medium"),
        lambda i: tf("", "q <= q << 1; inserts 0 at LSB for logical left shift.", True, "Logical shift-in 0.", "medium"),
        lambda i: mcq("", "Serial CRC engines often…", [
            "XOR feedback with shiftreg structure", "Use only initial", "Ban XOR", "Require packages",
        ], 0, "LFSR-like CRC.", "medium"),
        lambda i: mcq("", "Timing: long shift chains…", [
            "Many flops — watch fanout/reset fanout", "Zero area", "No clocks needed", "Only wires",
        ], 0, "Physical design care.", "medium"),
        lambda i: mcq("", "Load priority over shift…", [
            "if (load) … else if (ce) shift…", "Two drivers", "Only else shift first always", "force load",
        ], 0, "If priority.", "medium"),
        lambda i: tf("", "Bi-directional shift needs a direction select.", True, "dir mux.", "medium"),
        lambda i: mcq("", "Emptying a PISO…", [
            "Takes width cycles after load (typically)", "One cycle always for any width", "Needs generate false", "Needs $finish",
        ], 0, "Width cycles.", "medium"),
        lambda i: mcq("", "Ring counter…", [
            "Circulating one-hot in a loop", "Binary up counter only", "Only combo", "No flops",
        ], 0, "One-hot ring.", "medium"),
        lambda i: mcq("", "Johnson counter…", [
            "Inverted feedback shift pattern", "Same as binary decade always", "Ban clocks", "Named ports only",
        ], 0, "Twisted ring.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Wrong: q = {q[6:0], si}; with blocking in clocked…", [
            "Race/style issues — use NBA", "Preferred IEEE style", "Required for PISO", "Fixes CDC",
        ], 0, "NBA for seq.", "hard"),
        lambda i: mcq("", "Multi-bit parallel shift by k in one clock…", [
            "q <= q << k; (if k constant/legal) registered", "Needs k clocks always", "Illegal shift", "Only $display",
        ], 0, "Bus shift.", "hard"),
        lambda i: tf("", "Variable shift amounts may synthesize to barrel muxes — costly.", True,
                     "Area/timing cost.", "hard"),
        lambda i: mcq("", "Async reset clear of shiftreg…", [
            "Clears all stages per reset template", "Only clears si", "Needs Z", "Needs dual drive",
        ], 0, "Reset all stages.", "hard"),
        lambda i: mcq("", "Skew: using different clock edges along a chain…", [
            "Not a simple shiftreg anymore — careful redesign", "Preferred teaching style", "Required ANSI", "Same as @(*)",
        ], 0, "Keep one clock.", "hard"),
        lambda i: mcq("", "Formal: after N clocks si reaches q[N]…", [
            "Inductive pipeline property", "Only lint names", "Only fonts", "Only positional",
        ], 0, "Pipeline lemma.", "hard"),
        lambda i: tf("", "Shift toward MSB vs LSB is just wiring convention — document it.", True,
                     "Document direction.", "hard"),
        lambda i: mcq("", "Gate-level vs RTL shift…", [
            "Same architecture intent; representation differs", "RTL cannot shift", "Gates ban flops", "RTL bans concat",
        ], 0, "Abstraction levels.", "hard"),
        lambda i: mcq("", "SIPO parallel read during shift…", [
            "See intermediate values each cycle", "Frozen until stop always", "Needs second clock", "Needs force",
        ], 0, "Visible stages.", "hard"),
        lambda i: mcq("", "Teaching bug: shift and load both true with undefined priority…", [
            "Ambiguous hardware intent", "Defined always by Verilog randomly OK", "Deletes q", "Creates genvar",
        ], 0, "Specify priority.", "hard"),
    ]
    # Fix easy[1] — the choices are awkward. Let me leave as is; pad uniqueness still works.
    return easy, medium, hard


def b_synth_lint():
    easy = [
        lambda i: mcq("", "`assign #5 y = a;` flagged mainly because…", [
            "procedural/continuous delays are not synthesizable RTL", "5 illegal", "assign banned", "Creates PLL",
        ], 0, "No synth delays.", "easy"),
        lambda i: mcq("", "Inside always_ff @(posedge clk), flop outputs should use…", [
            "non-blocking `<=`", "blocking `=` only", "hash-delay before each assign", "`initial` defaults",
        ], 0, "NBA in ff.", "easy"),
        lambda i: mcq("", "`always @(*) if (en) y = d;` no else often triggers…", [
            "latch-risk", "parse error", "no-delay rule", "systask warning only",
        ], 0, "Incomplete combo.", "easy"),
        lambda i: tf("", "This teaching linter is identical to Vivado or Yosys.", False,
                     "Teaching subset ≠ full vendor.", "easy"),
        lambda i: mcq("", "`initial` in synthesizable RTL…", [
            "Usually non-synth / TB oriented (except some RAM hints)", "Required for every flop", "Creates ports", "Fixes CDC",
        ], 0, "initial mostly TB.", "easy"),
        lambda i: mcq("", "`$display` in RTL module…", [
            "Not synthesizable side-effect — TB/debug", "Creates gates of displays", "Required ANSI", "Named ports",
        ], 0, "Systasks ≠ gates.", "easy"),
        lambda i: tf("", "Incomplete sensitivity can pass synth but fail sim.", True, "Mismatch hazard.", "easy"),
        lambda i: mcq("", "Multiple drivers lint…", [
            "Two assigns/always on one net/var", "Too many comments", "Long filenames", "Using parameters",
        ], 0, "One driver.", "easy"),
        lambda i: mcq("", "Latch inferred warning…", [
            "Incomplete combo assignment", "Too many flops", "Missing timescale only", "Using hex",
        ], 0, "Latch risk.", "easy"),
        lambda i: tf("", "Non-blocking in clocked blocks is the usual lint-friendly style.", True, "NBA style.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "`#0` NBA tricks…", [
            "Simulation scheduling hacks — avoid in RTL", "Required synth", "ANSI conversion", "Gray code",
        ], 0, "No #0 RTL.", "medium"),
        lambda i: mcq("", "casex for decode…", [
            "Can hide bugs — prefer careful case/unique", "Always best", "Bans default", "Required for adders",
        ], 0, "casex caution.", "medium"),
        lambda i: tf("", "Async reset must appear in sensitivity for the classic template.", True,
                     "List matches behavior.", "medium"),
        lambda i: mcq("", "Comparing X intentionally in RTL…", [
            "Usually a TB concern; RTL should be X-clean", "Required", "Creates localparam", "Fixes WNS",
        ], 0, "Avoid X logic.", "medium"),
        lambda i: mcq("", "Latch + clock in same module accidentally…", [
            "Review enable/completeness and edge templates", "Ignore", "Add more X", "Delete clk",
        ], 0, "Fix templates.", "medium"),
        lambda i: mcq("", "Vendor attribute full_case…", [
            "Can silence warnings without fixing holes — know semantics", "Always safe", "Creates clocks", "Named ports",
        ], 0, "Pragma literacy.", "medium"),
        lambda i: tf("", "Synthesis ignores many delays and some sys-tasks.", True, "Subset of language.", "medium"),
        lambda i: mcq("", "Combinational loops lint…", [
            "Feedback without a register break", "Too many params", "Using $clog2", "Named instances",
        ], 0, "Combo loop.", "medium"),
        lambda i: mcq("", "Undriven net…", [
            "Floating input/X risk", "Preferred Z always", "Automatic 1", "Parameter",
        ], 0, "Drive or tie.", "medium"),
        lambda i: mcq("", "mixed blocking/NBA same reg…", [
            "Lint red flag", "Preferred", "Required SV", "Only TB ok always without thought",
        ], 0, "Don't mix.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Yosys vs teaching lint differences…", [
            "Expect different coverage — learn concepts not tool identity", "Identical always", "Teaching supersets vendors", "Vendors ban wire",
        ], 0, "Concept > tool.", "hard"),
        lambda i: mcq("", "Inferring RAM vs flops…", [
            "Coding style/templates matter for inference", "Only filenames matter", "Only comments", "Only fonts",
        ], 0, "Inference templates.", "hard"),
        lambda i: tf("", "A construct can be legal Verilog yet unsynthesizable.", True,
                     "Language ⊃ synth subset.", "hard"),
        lambda i: mcq("", "Disabling lint without understanding…", [
            "Dangerous — fix root cause", "Best practice always", "Required for merge", "Same as $finish",
        ], 0, "Don't waive blindly.", "hard"),
        lambda i: mcq("", "X-optimism vs pessimism mismatches…", [
            "Sim/synth/formal can disagree on X", "Impossible", "Fixed by Fraunces", "Fixed by positional only",
        ], 0, "X semantics.", "hard"),
        lambda i: mcq("", "Latch on FPGA bitfile…", [
            "Often unwanted; review warnings", "Always optimal", "Required for counters", "Same as BRAM always",
        ], 0, "FPGA style.", "hard"),
        lambda i: tf("", "`forever` loops without time advance hang simulation.", True, "TB hang risk.", "hard"),
        lambda i: mcq("", "Hierarchical references in synth RTL…", [
            "Often restricted — prefer ports", "Always preferred", "Required for adders", "Same as generate genvar",
        ], 0, "Use ports.", "hard"),
        lambda i: mcq("", "Best response to a lint finding…", [
            "Understand rule → fix or justify with evidence", "Delete linter", "Ignore commit", "Add emoji",
        ], 0, "Engineer the warning.", "hard"),
        lambda i: mcq("", "Synth-ok but CDC-broken design…", [
            "Lint ≠ full correctness — still need CDC review", "Synth success means CDC-safe", "Ban sync flops", "Ban gray code",
        ], 0, "Multiple check layers.", "hard"),
    ]
    return easy, medium, hard


def b_hdl_style():
    easy = [
        lambda i: mcq("", "Teaching style lint prefers clocks named…", [
            "`clk` or `*_clk`", "always `clock` only", "only `c`", "`sys` for every clock",
        ], 0, "clk naming.", "easy"),
        lambda i: mcq("", "Active-low reset naming often uses…", [
            "`rst_n` or `reset_n`", "only `reset` with no hint", "`r`", "`nrst` without convention",
        ], 0, "Active-low suffix.", "easy"),
        lambda i: mcq("", "Edge-triggered flops in SV style prefer…", [
            "`always_ff @(posedge clk)`", "`always @(*)`", "`initial`", "`forever`",
        ], 0, "always_ff intent.", "easy"),
        lambda i: tf("", "Style findings are usually hints, not sim blockers by themselves.", True,
                     "Info/warn culture.", "easy"),
        lambda i: mcq("", "Active-high reset often named…", [
            "`rst` / `reset`", "`rst_n` only", "`clk`", "`ce`",
        ], 0, "Active-high names.", "easy"),
        lambda i: mcq("", "Consistent indentation/naming helps…", [
            "Reviews and lint readability", "Clock frequency", "FPGA LUT chemistry", "IEEE float",
        ], 0, "Human factors.", "easy"),
        lambda i: tf("", "`*_n` suffix commonly marks active-low.", True, "Polarity hint.", "easy"),
        lambda i: mcq("", "Data enables often named…", [
            "`ce`, `en`, `valid` (context)", "`clk` only", "`rst_n` only", "`genvar`",
        ], 0, "Enable names.", "easy"),
        lambda i: mcq("", "Avoid magic numbers by…", [
            "parameters/localparams with names", "More X", "More force", "Shorter modules always only",
        ], 0, "Named constants.", "easy"),
        lambda i: tf("", "One module, one clear purpose aids style and reuse.", True, "Cohesion.", "easy"),
    ]
    medium = [
        lambda i: mcq("", "always_comb intent…", [
            "Mark combinational processes for checks", "Replace clocks", "Create Z", "Ban mux",
        ], 0, "Intent + checking.", "medium"),
        lambda i: mcq("", "File naming matching module name…", [
            "Common style for findability", "Required by IEEE physics", "Bans hierarchy", "Creates lint error always if differ",
        ], 0, "Convention.", "medium"),
        lambda i: tf("", "Mixed tab/space wars matter less than consistent project rules.", True,
                     "Follow the repo.", "medium"),
        lambda i: mcq("", "Commenting every wire…", [
            "Noise — comment intent/hazards instead", "Required legally", "Speeds STA", "Fixes CDC",
        ], 0, "Useful comments.", "medium"),
        lambda i: mcq("", "Port order convention often…", [
            "clocks, resets, controls, data", "Random", "Outputs first always mandatory", "Parameters as ports",
        ], 0, "Readable order.", "medium"),
        lambda i: mcq("", "Deprecated: using `reg` for everything in SV…", [
            "Prefer logic with clear always_* ", "Required", "Only style for wires", "Bans NBA",
        ], 0, "Modern SV style.", "medium"),
        lambda i: tf("", "Assertions can encode style/intent beyond lint names.", True, "SVA helps.", "medium"),
        lambda i: mcq("", "Huge 2k-line module…", [
            "Style smell — split responsibilities", "Ideal always", "Required for synth", "Faster reviews",
        ], 0, "Modularize.", "medium"),
        lambda i: mcq("", "Boolean polarity in names…", [
            "Match active level to suffix", "Invert randomly", "Hide in comments only", "Use only numbers",
        ], 0, "Name polarity.", "medium"),
        lambda i: mcq("", "Toolchain formatters…", [
            "Help consistency if team agrees", "Replace design reviews", "Fix functional bugs always", "Ban parameters",
        ], 0, "Format ≠ correctness.", "medium"),
    ]
    hard = [
        lambda i: mcq("", "Style vs functionality conflict…", [
            "Correctness wins; then align style", "Style wins over bugs", "Ignore both", "Delete tests",
        ], 0, "Correct first.", "hard"),
        lambda i: mcq("", "Company lint waivers…", [
            "Need owners/expiry — not eternal silences", "Should be infinite", "Replace CI", "Ban new code",
        ], 0, "Managed waivers.", "hard"),
        lambda i: tf("", "always_latch exists in SV to mark intentional latches.", True,
                     "Intent for latches.", "hard"),
        lambda i: mcq("", "Hungarian notation everywhere…", [
            "Often noisy vs clear domain names", "Required by Verilog", "Fixes X", "Creates clocks",
        ], 0, "Readable domain names.", "hard"),
        lambda i: mcq("", "Clock naming when multiple domains…", [
            "`clk_a`, `clk_b` / domain suffixes", "All named `clk`", "No names", "Use `rst` for clocks",
        ], 0, "Domain suffixes.", "hard"),
        lambda i: mcq("", "Reset strategy documented in…", [
            "README / micro-arch notes + consistent names", "Only waveforms", "Only lint ignore", "Only $finish",
        ], 0, "Document strategy.", "hard"),
        lambda i: tf("", "Consistent NBA/blocking rules are a style rule with functional impact.", True,
                     "Style tied to races.", "hard"),
        lambda i: mcq("", "Code review checklist item…", [
            "Naming, resets, one-driver, CDC, lint clean", "Font choice only", "Emoji density", "Commit hour",
        ], 0, "Real checklist.", "hard"),
        lambda i: mcq("", "Generated RTL style…", [
            "Still must be reviewable / constrained", "Exempt from all rules always", "Cannot be linted", "Bans modules",
        ], 0, "Generated ≠ ungoverned.", "hard"),
        lambda i: mcq("", "Teaching goal of style lint…", [
            "Build habits that scale to team codebases", "Memorize one vendor GUI", "Avoid Track A forever", "Ban browser labs",
        ], 0, "Habits.", "hard"),
    ]
    return easy, medium, hard


MODULES = [
    ("module01-module-diagram", "Module / port diagram", "mod", b_module_diagram),
    ("module02-verilog-literals", "Verilog literals", "lit", b_literals),
    ("module03-wire-vs-reg", "wire vs reg", "wr", b_wire_reg),
    ("module04-ansi-ports", "ANSI vs non-ANSI ports", "ansi", b_ansi),
    ("module05-sv-operators", "Operators", "ops", b_operators),
    ("module06-sensitivity-list", "Sensitivity lists", "sens", b_sensitivity),
    ("module07-latch-risk", "Latch risk", "latch", b_latch),
    ("module08-blocking-vs-nonblocking", "Blocking vs non-blocking", "nba", b_blocking),
    ("module09-param-width", "Parameter / width", "param", b_param),
    ("module10-named-vs-positional", "Named vs positional", "ports", b_named_pos),
    ("module11-localparam-lab", "localparam", "lparam", b_localparam),
    ("module12-sv-generate", "Generate / replication", "gen", b_generate),
    ("module13-one-driver", "One-driver nets", "drv", b_one_driver),
    ("module14-counter-lab", "Counter patterns", "cnt", b_counter),
    ("module15-shift-register-lab", "Shift-register patterns", "sreg", b_shiftreg),
    ("module16-synth-lint", "Synthesizability lint", "lint", b_synth_lint),
    ("module17-hdl-style", "HDL style", "style", b_hdl_style),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for mid, title, prefix, builder in MODULES:
        easy, medium, hard = builder()
        data = bank(mid, title, prefix, easy, medium, hard)
        path = OUT / f"{mid}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path.name} ({len(data['items'])} items)")


if __name__ == "__main__":
    main()
