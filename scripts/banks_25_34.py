"""Challenge banks for learn_digital modules 25, 27–34 (skip 26 setup/hold).

Each bank: 30 easy + 30 medium + 30 hard. Prompts must NOT include (v1)/variant labels.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_digital" / "questions"
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


def _bank(module: str, title: str, prefix: str, easy_b: list, med_b: list, hard_b: list) -> dict:
    items = pad("easy", prefix, easy_b) + pad("medium", prefix, med_b) + pad("hard", prefix, hard_b)
    return {"module": module, "title": title, "items": items}


# ---------------------------------------------------------------------------
# module25 — Clock-edge stepper
# ---------------------------------------------------------------------------
def clock_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "D flip-flop: when does Q capture D?",
                "A positive-edge FF copies D into Q at which moment?",
                "Edge-triggered capture of D into Q happens…",
                "When is q <= d performed for a posedge D FF?",
            ][(i - 1) % 4],
            [
                "Any time D changes",
                "On posedge clk",
                "On negedge clk only",
                "When reset is low",
            ],
            1,
            "q <= d on posedge clk.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter workflow after setting D=1: next action is…",
                "Poke D high, then what advances the sequential state?",
                "Lab rhythm for a D FF: poke data, then…",
                "To see Q follow a poked D=1 you must…",
            ][(i - 1) % 4],
            [
                "Wait for Q to update immediately",
                "Advance a posedge of clk",
                "Toggle reset only",
                "Change the clock period",
            ],
            1,
            "Poke first, then clock edge.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Enable register with EN=0 on posedge…",
                "If EN is low at the capturing edge, Q…",
                "Clocked enable off: what happens to Q?",
                "With EN=0, a posedge typically…",
            ][(i - 1) % 4],
            [
                "Forces Q to follow D",
                "Holds Q (no capture)",
                "Toggles Q",
                "Drives Q to X",
            ],
            1,
            "if (en) q <= d — EN off holds.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "A 2-stage pipeline needs two posedges after D changes before Q2 sees it.",
                "Pipeline stage 2 lags the input by two clock edges.",
                "q1 <= d; q2 <= q1 implies one cycle delay per stage.",
                "Changing D updates both pipeline stages on the same edge.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Each stage advances one edge; two stages need two edges.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Sequential logic samples inputs…",
                "Unlike combo gates, registers update…",
                "Edge-triggered blocks ignore D changes until…",
                "What event makes a D FF sample?",
            ][(i - 1) % 4],
            [
                "On every input wiggle",
                "On a clock edge",
                "Only at power-up",
                "Whenever EN is low",
            ],
            1,
            "Samples on clock edges, not continuous D motion.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                f"After reset clears a counter, it increments on…",
                "Counters advance their count primarily on…",
                "A free-running counter steps when…",
                "Post-reset, the next count update needs…",
            ][(i - 1) % 4],
            [
                "An asynchronous D change alone",
                "A clock edge (with enable if used)",
                "Only a mid-cycle reset pulse",
                "Removing the clock tree",
            ],
            1,
            "Counters are edge-triggered after reset clears.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Shift-register chains move bits…",
                "In a shift chain, data advances…",
                "Each FF in a shift register captures on…",
                "Bit motion through a shift chain is paced by…",
            ][(i - 1) % 4],
            [
                "Combinationally without clocks",
                "One stage per clock edge",
                "Only when reset asserts",
                "Whenever D floats",
            ],
            1,
            "Each edge advances one stage.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Changing D alone does not update Q before the clock edge.",
                "Expecting Q to track D mid-cycle is a common pitfall.",
                "Level-sensitive latches and edge-triggered flops behave the same.",
                "Reset and enable are evaluated with data on the capturing edge.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Edge FFs hold until the edge; latches differ; enable/reset matter on that edge.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Browser clock-step labs teach literacy; real silicon still needs…",
                "Manual posedge poking does not replace which real concerns?",
                "Beyond stepping, designs still require…",
                "Which topics remain after learning edge capture in a lab?",
            ][(i - 1) % 4],
            [
                "Setup/hold and CDC rules",
                "Only ASCII tables",
                "Removing all clocks",
                "Never using enable",
            ],
            0,
            "Setup, hold, and CDC still apply in real designs.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "On the same capturing edge, which also matter with D?",
                "Besides D, edge sampling often considers…",
                "What co-conditions share the capture edge with data?",
                "A complete edge update may involve D plus…",
            ][(i - 1) % 4],
            [
                "Reset and enable polarity/state",
                "Only package pin names",
                "Baud rate alone",
                "K-map grouping size",
            ],
            0,
            "Reset and enable are evaluated on the same edge as data.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Best description of a register with synchronous enable?",
                "Clock-enable register semantics are closest to…",
                "When EN is qualified inside @(posedge clk)…",
                "Which model matches if (en) q <= d?",
            ][(i - 1) % 4],
            [
                "Free-running clk; load only when EN=1",
                "AND-gating clk in the testbench only",
                "Q updates whenever D changes",
                "Async clear every mid-cycle",
            ],
            0,
            "Clk runs; enable gates the load.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "A pipeline of depth N typically needs N edges for an input to appear at the last stage.",
                "Two FF stages imply at least two clock edges of latency.",
                "Posedge stepping and continuous combo evaluation are identical.",
                "Truth tables in the lab record poke and edge events in time order.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Latency is one edge per stage; combo is not edge-paced.",
            "hard",
        ),
    ]
    return _bank("module25-clock-stepper", "Clock-edge stepper", "clock", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module27 — Reset timelines
# ---------------------------------------------------------------------------
def reset_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Synchronous reset is typically…",
                "Sync reset samples rst_n…",
                "Where does synchronous reset usually live in RTL?",
                "A sync reset clears Q…",
            ][(i - 1) % 4],
            [
                "Only on the clock edge",
                "With no clock in the sensitivity list",
                "The same as $finish",
                "In analog continuous time only",
            ],
            0,
            "if (!rst_n) inside @(posedge clk).",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "If rst_n falls between clock edges…",
                "Mid-cycle active-low reset: async vs sync?",
                "Between edges, asserting rst_n low…",
                "Starter mid-cycle divergence shows…",
            ][(i - 1) % 4],
            [
                "Async can clear immediately; sync waits for posedge",
                "Both always ignore reset",
                "Sync always clears first",
                "The clock stops forever",
            ],
            0,
            "Async clears now; sync waits for the edge.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "rst_n naming usually means…",
                "The _n suffix on reset conventionally signals…",
                "Active-low reset asserts when…",
                "rst_n = 0 typically…",
            ][(i - 1) % 4],
            [
                "Active-low reset — clear when rst_n is 0",
                "Reset never asserts",
                "Reset is LVDS only",
                "The net must stay undriven Z",
            ],
            0,
            "n = negative / active-low.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "After a mid-cycle reset assert, async Q can be 0 while sync Q is still 1.",
                "Async reset can clear between edges; sync cannot.",
                "Synchronous and asynchronous reset always match mid-cycle.",
                "Both styles clear when rst_n is low at a posedge.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Mid-cycle: async clears; sync waits. At posedge with rst_n low, both clear.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Asynchronous reset sensitivity typically includes…",
                "Async clear lists which event besides clk?",
                "negedge rst_n in the always list means…",
                "Async reset can fire…",
            ][(i - 1) % 4],
            [
                "negedge rst_n (active-low)",
                "Only posedge of data",
                "UART framing edges",
                "Nothing — async never lists rst",
            ],
            0,
            "Async reset reacts to rst_n edges between clocks.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "A short mid-cycle rst_n pulse may be…",
                "If sync reset deasserts before the sampling edge…",
                "Sync reset can miss a brief pulse because…",
                "Which reset style ignores a pulse that ends before posedge?",
            ][(i - 1) % 4],
            [
                "Ignored by sync reset if gone before the edge",
                "Always captured by sync reset",
                "Required for async FIFO depth",
                "Impossible in HDL",
            ],
            0,
            "Sync samples only at the edge.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "After releasing rst_n high, new data captures…",
                "Release reset, then Q loads D on…",
                "Post-reset data entry needs…",
                "Once rst_n is deasserted, capture resumes on…",
            ][(i - 1) % 4],
            [
                "A later clock edge (for sync paths)",
                "Immediately with no edge",
                "Only package bonding",
                "Never again",
            ],
            0,
            "Release then capture on a subsequent edge.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Do not assume sync and async behave the same off the edge.",
                "rst_n high means reset is asserted for active-low naming.",
                "At a posedge with rst_n still low, both sync and async typically clear.",
                "Recovery/removal timing matters when releasing async reset near a clock edge.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 1 else False,
            "Active-low asserts at 0; styles diverge mid-cycle; recovery matters on release.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Releasing async reset too close to a clock edge risks…",
                "Async reset recovery/removal checks protect against…",
                "A classic async-reset pitfall near clk is…",
                "Which concern appears when deasserting async rst near an edge?",
            ][(i - 1) % 4],
            [
                "Recovery/removal timing violations",
                "Automatic Gray encoding",
                "Baud-rate doubling",
                "Removing the need for clocks",
            ],
            0,
            "Need recovery time between reset release and the clock edge.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Real SoCs still need beyond toy FF pairs…",
                "Reset literacy labs omit which production concerns?",
                "Which infrastructure sits above single-FF reset demos?",
                "Production reset design also covers…",
            ][(i - 1) % 4],
            [
                "Reset trees, CDC, and recovery checks",
                "Only ASCII fonts",
                "Deleting STA",
                "Never using sync reset",
            ],
            0,
            "Trees, CDC, and recovery/removal still apply.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Best RTL sketch for sync active-low reset?",
                "Which always-block shape matches synchronous rst_n?",
                "Sync reset idiom is closest to…",
                "Pick the sync-reset pattern.",
            ][(i - 1) % 4],
            [
                "always @(posedge clk) if (!rst_n) q<=0; else q<=d;",
                "always @(*) q = ~rst_n;",
                "assign clk = rst_n & d;",
                "always @(negedge d) q<=1;",
            ],
            0,
            "Reset sampled inside the clocked block.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Async reset can clear Q with no intervening clock edge.",
                "Sync reset cannot clear between edges without a sampling edge.",
                "Active-low naming means the net is never driven.",
                "Both FFs clear when rst_n is low at the shared posedge.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Async mid-cycle clear is real; naming is polarity, not undriven.",
            "hard",
        ),
    ]
    return _bank("module27-reset-timelines", "Reset timelines", "reset", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module28 — Clock enable
# ---------------------------------------------------------------------------
def clken_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Preferred RTL style for conditional updates?",
                "Default way to skip loads without gating clk?",
                "Cleanest conditional register update uses…",
                "Which pattern keeps a free-running clock?",
            ][(i - 1) % 4],
            [
                "Clock enable (if ce) on free-running clk",
                "Raw AND gate on clk always",
                "No clock at all",
                "Only async reset",
            ],
            0,
            "Clean clk; if (ce) q <= d.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "CE=0 on a clock-enable flop means…",
                "With clock enable low at posedge…",
                "Enable off on a CE register…",
                "Holding without stopping clk looks like…",
            ][(i - 1) % 4],
            [
                "q holds (no load)",
                "q must toggle",
                "clk stops globally",
                "d drives q immediately",
            ],
            0,
            "Enable off → recycle/hold.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "AND-gated clk risk when ce changes while clk=1?",
                "Raw AND of clk and ce can create…",
                "Enable glitch during clk high on gated clocks…",
                "Danger of gating clk with a plain AND?",
            ][(i - 1) % 4],
            [
                "Glitch / spurious edge",
                "Always safer than CE",
                "Only affects reset",
                "Impossible in simulation",
            ],
            0,
            "Raw AND can pulse clk_g.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "ICG cells latch enable when clk is low before AND-gating.",
                "Integrated clock gates reduce raw-AND glitch risk.",
                "Clock enable stops the global clock tree by definition.",
                "CE=1 loads D on each posedge for a free-running clk.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "ICG latches enable safely; CE holds data without stopping clk.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Holding Q with CE differs from gating because…",
                "CE vs gated clock — key distinction?",
                "Clock enable primarily…",
                "Gating clk primarily…",
            ][(i - 1) % 4],
            [
                "CE holds data; gating stops edges",
                "They are identical always",
                "CE deletes setup checks",
                "Gating never risks glitches",
            ],
            0,
            "CE recycles Q; gating removes clock edges.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Why is ce toggling during clk high risky in gated mode?",
                "Mid-high enable change on AND-gated clk can…",
                "Spurious edges appear when…",
                "Gated-clock glitch demo warns about…",
            ][(i - 1) % 4],
            [
                "Creating an unintended clock pulse",
                "Improving hold automatically",
                "Forcing async FIFO Gray pointers",
                "Removing STA forever",
            ],
            0,
            "AND can glitch while clk is high.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Using AND-gated clocks without an ICG cell in silicon…",
                "A pitfall of DIY clock AND gates is…",
                "Preferred when you truly must gate clocks?",
                "Library ICG cells exist mainly to…",
            ][(i - 1) % 4],
            [
                "Invite glitches and STA pain — prefer ICG",
                "Guarantee maximal LFSR period",
                "Replace all resets",
                "Make multi-bit CDC safe alone",
            ],
            0,
            "Use proper ICG; avoid raw AND.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "With CE=1, each posedge loads d into q.",
                "With CE=0, q can still change if d changes mid-cycle.",
                "Preferred RTL default is CE on the data path, not raw AND on clk.",
                "Glitches on gated clocks can cause extra captures.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 1 else False,
            "CE=0 holds through the edge; d mid-cycle does not load.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Real designs with ICGs still need…",
                "Clock-enable literacy labs leave which work for silicon?",
                "Beyond CE demos, production cares about…",
                "Which still applies after choosing CE vs gate?",
            ][(i - 1) % 4],
            [
                "Clock-tree constraints, ICG rules, STA on enables",
                "Only hex fonts",
                "Deleting the clock entirely",
                "Ignoring enable paths in timing",
            ],
            0,
            "Constraints and STA on enable paths remain.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Best always-block sketch for clock enable?",
                "Which matches free-running clk with CE?",
                "RTL idiom if (ce) q <= d sits in…",
                "Pick the CE pattern.",
            ][(i - 1) % 4],
            [
                "always @(posedge clk) if (ce) q <= d;",
                "assign clk = ce & clk;",
                "always @(*) q = d;",
                "always @(negedge ce) clk = 1;",
            ],
            0,
            "Qualify the load, not the clock net.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Power/skip-cycle goals: safest first choice?",
                "To skip updates without clock-tree drama…",
                "When you only need recycle, prefer…",
                "Conditional update without gating clk means…",
            ][(i - 1) % 4],
            [
                "Clock enable on free-running clk",
                "Unlatched AND of clk and ce",
                "Removing all flops",
                "Driving Q from async_in",
            ],
            0,
            "CE first; gate only with proper cells when required.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "ICG latches enable while clk is low, then AND-gates.",
                "Raw AND of clk and ce is the preferred RTL default.",
                "Holding Q is not the same as stopping the clock tree.",
                "Gated-clock glitches can create timing nightmares.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 1 else False,
            "CE/ICG preferred; raw AND is the hazard case.",
            "hard",
        ),
    ]
    return _bank("module28-clock-enable", "Clock enable", "clken", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module29 — CDC / 2-FF sync
# ---------------------------------------------------------------------------
def cdc_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "CDC stands for…",
                "Crossing unrelated clocks is called…",
                "Signal moving between clock domains is…",
                "What does CDC abbreviate?",
            ][(i - 1) % 4],
            [
                "Clock-domain crossing",
                "Clock duty cycle",
                "Combinational delay check",
                "Core debug console",
            ],
            0,
            "Signal crosses unrelated clocks.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Safe single-bit sync output should come from…",
                "In a 2-FF synchronizer, use…",
                "Downstream dst logic should read…",
                "Which node is the safe sync_out?",
            ][(i - 1) % 4],
            [
                "q2 (second dst flop)",
                "q1 only",
                "async_in directly",
                "The source clock",
            ],
            0,
            "q2 samples after settle time.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Multi-bit CDC across unrelated clocks typically needs…",
                "An 8-bit bus through classic 2-FF per bit is…",
                "Safe multi-bit crossing uses…",
                "Instead of per-bit 2-FF on a bus, prefer…",
            ][(i - 1) % 4],
            [
                "Gray code, handshake, or async FIFO",
                "Classic 2-FF on each bit alone",
                "No synchronizer at all",
                "Only one dst flop",
            ],
            0,
            "Bits can skew on separate 2-FF paths.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "FF1 may be metastable after a bad sample near a clock edge.",
                "That metastability risk is why logic uses q2, not q1.",
                "One-FF synchronizers are as safe as two-FF chains.",
                "Never fan q1 into combinational logic in the dst domain.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "q1 can be metastable; one-FF is unsafe; use q2.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Role of the second flop in a 2-FF sync?",
                "Why chain q2 after q1?",
                "Extra destination cycle mainly…",
                "MTBF improves because…",
            ][(i - 1) % 4],
            [
                "Gives settle time before use",
                "Removes the need for any sync",
                "Makes multi-bit buses safe alone",
                "Stops the source clock",
            ],
            0,
            "Second sample after metastability window.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "One-FF sync mode is unsafe because…",
                "Taking sync_out from q1 alone…",
                "Problem with a single destination flop?",
                "Why warn on one-FF CDC?",
            ][(i - 1) % 4],
            [
                "Logic may consume a metastable q1",
                "It doubles max clock frequency always",
                "It forces Gray pointers",
                "It deletes async_in",
            ],
            0,
            "No settle flop before use.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Why can multi-bit 2-FF per bit fail?",
                "Separate sync paths on a bus risk…",
                "Bit skew after independent synchronizers…",
                "Classic multi-bit misuse warning is about…",
            ][(i - 1) % 4],
            [
                "Bits settling on different cycles / illegal codes",
                "Always improving MTBF enough alone",
                "Forcing one-hot FSMs",
                "Removing CDC constraints",
            ],
            0,
            "Skewed bits can form illegal intermediate values.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Two flops improve MTBF but do not make multi-bit buses safe.",
                "Metastability is probabilistic, not impossible.",
                "CDC can be ignored as a pure timing false path forever.",
                "q1 should not fan into dst combinational logic.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Treat CDC seriously; 2-FF is for single-bit control-class signals.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Real CDC work beyond the lab still needs…",
                "Production sync design also covers…",
                "Besides a 2-FF sketch, silicon needs…",
                "Which remains after learning q1/q2?",
            ][(i - 1) % 4],
            [
                "CDC constraints, sync cells, and data protocols",
                "Only deleting clocks",
                "Per-bit 2-FF on every wide bus",
                "Using async_in as dst combo input",
            ],
            0,
            "Constraints, cells, and proper data-path protocols.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Best RTL sketch for a 2-FF single-bit sync?",
                "Which chain matches q1<=async_in; q2<=q1?",
                "Safe sync_out should be…",
                "Pick the two-flop pattern.",
            ][(i - 1) % 4],
            [
                "always @(posedge clk_dst) begin q1<=async_in; q2<=q1; end",
                "assign sync_out = async_in;",
                "always @(*) q2 = async_in;",
                "always @(posedge clk_src) q2 <= q1;",
            ],
            0,
            "Both flops in the destination domain; use q2.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Near-edge sample of async_in into q1 may show…",
                "Lab 'M' on q1 after a risky sample means…",
                "Metastable indication on the first sync flop…",
                "After a bad capture, q1 might be…",
            ][(i - 1) % 4],
            [
                "Metastable / unresolved until it settles",
                "Guaranteed legal Gray code",
                "Identical to q2 always",
                "Driven by the source clock tree",
            ],
            0,
            "First flop can go metastable; wait for q2.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Destination logic should use q2, not q1.",
                "Handshake or async FIFO can carry multi-bit data safely across domains.",
                "Classic 2-FF per bit is sufficient for arbitrary buses.",
                "Source changing while dst samples is the core CDC hazard.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Protocols for multi-bit; 2-FF alone is not enough for buses.",
            "hard",
        ),
    ]
    return _bank("module29-cdc-sync", "CDC / 2-FF sync", "cdc", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module30 — FSM designer
# ---------------------------------------------------------------------------
def fsm_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Moore machine outputs depend on…",
                "In a Moore FSM, Z is a function of…",
                "Moore Z is tied to…",
                "Which inputs determine Moore outputs?",
            ][(i - 1) % 4],
            [
                "Current state only",
                "State and input together",
                "Next-state name only",
                "Reset polarity alone",
            ],
            0,
            "Z is tied to the state node.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Mealy outputs depend on…",
                "Mealy Z is a function of…",
                "Outputs on transition arcs describe…",
                "Which style ties Z to state and input?",
            ][(i - 1) % 4],
            [
                "Current state and current input",
                "State only",
                "FIFO depth",
                "Clock duty cycle",
            ],
            0,
            "Z is on the transition arc.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Moore toggle starter: x=1 does what?",
                "In the two-state Moore toggle, x=1…",
                "When x=0 in the toggle starter…",
                "Toggle FSM on input 1…",
            ][(i - 1) % 4],
            [
                "Flips state (S0↔S1); x=0 holds",
                "Always resets to S0",
                "Ignores input forever",
                "Sets Z without changing state",
            ]
            if (i - 1) % 4 != 2
            else [
                "Holds the current state",
                "Always flips twice",
                "Forces Mealy mode",
                "Clears the clock",
            ],
            0,
            "x=1 toggles; x=0 holds.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Stepping applies one input bit per step and updates state/Z.",
                "One stream bit is like one clock cycle in the lab.",
                "Moore and Mealy output columns mean the same thing in a mixed table.",
                "A transition table lists next state for each state/input pair.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "One bit ≈ one cycle; do not mix Moore/Mealy column meanings.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Mealy pulse preset: Z pulses…",
                "When does a Mealy pulse assert Z?",
                "Arc-associated Z is high…",
                "Mealy detect-style pulse appears…",
            ][(i - 1) % 4],
            [
                "On the transition when the qualifying input arrives",
                "Only as a constant Moore state level forever",
                "Never on arcs",
                "Only during reset",
            ],
            0,
            "Z on the completing transition.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Forgetting a default transition can leave…",
                "Unreachable states are a pitfall when…",
                "Incomplete next-state tables risk…",
                "Safe FSM tables should…",
            ][(i - 1) % 4],
            [
                "Holes / illegal or stuck behavior",
                "Automatic maximal LFSR period",
                "Free CDC for buses",
                "Remove the need for reset",
            ],
            0,
            "Cover defaults; avoid unreachable traps.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Controllers and protocol engines are often…",
                "Sequencers in hardware are typically…",
                "Finite sets of states/inputs/outputs describe…",
                "What machine maps present state + input → next?",
            ][(i - 1) % 4],
            [
                "Finite-state machines",
                "Only ripple adders",
                "Only analog PLLs",
                "Stateless mux trees only",
            ],
            0,
            "FSMs under many names.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "S0 outputs 0 and S1 outputs 1 in the Moore toggle starter.",
                "Stream 1-0-1-1 flips on each 1 and holds on each 0.",
                "Mixing Moore and Mealy rules in one table is recommended.",
                "Real RTL still needs encoding and a defined reset state.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Starter is Moore toggle; do not mix styles casually.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Three-state ring that advances on x=1 is…",
                "A ring of states advancing on input 1 is an example of…",
                "Editable blank tables in the lab let you…",
                "Beyond two-state toggle, FSMs can…",
            ][(i - 1) % 4],
            [
                "A sequenced FSM walked by the input stream",
                "A pure combo XOR tree",
                "An async FIFO Gray pointer alone",
                "A setup-time formula",
            ],
            0,
            "Input-driven state sequencing.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Moore vs Mealy timing downstream may differ because…",
                "Why might glue logic care Moore vs Mealy?",
                "Output on state vs on arc changes…",
                "Pick the practical distinction.",
            ][(i - 1) % 4],
            [
                "Level-from-state vs pulse-on-transition timing",
                "They always have identical waveforms",
                "Only package pin names change",
                "Clocks become optional",
            ],
            0,
            "Mealy can change with input mid-state; Moore waits for state.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Synthesis-friendly FSM RTL still needs…",
                "After drawing bubbles, implementation requires…",
                "Lab literacy leaves which silicon chores?",
                "Which belongs in real FSM RTL?",
            ][(i - 1) % 4],
            [
                "Encoding, reset state, and state registers",
                "Deleting all next-state logic",
                "Driving clocks from outputs casually",
                "Ignoring illegal states always",
            ],
            0,
            "Encode, reset, and register the state.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Next state is determined by present state and inputs.",
                "Output rules differ between Moore and Mealy.",
                "The bit stream stepper is arbitrary analog continuous time.",
                "Leaving a state with no outgoing arcs is a design smell.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Discrete steps ≈ cycles; cover transitions.",
            "hard",
        ),
    ]
    return _bank("module30-fsm-lab", "FSM designer", "fsm", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module31 — State encoding
# ---------------------------------------------------------------------------
def encoding_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Binary encoding of N states needs how many FFs?",
                "Compact binary width for N states is…",
                "Minimum FF count for binary codes is…",
                "ceil(log2 N) counts…",
            ][(i - 1) % 4],
            [
                "ceil(log2 N)",
                "N",
                "N−1",
                "2N",
            ],
            0,
            "Compact minimum-width code.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "One-hot encoding of N states uses…",
                "One-hot width is…",
                "How many flops for one-hot N states?",
                "Exactly one bit high implies…",
            ][(i - 1) % 4],
            [
                "N flip-flops (one bit high)",
                "ceil(log2 N) flip-flops",
                "1 flip-flop total",
                "No flip-flops",
            ],
            0,
            "One FF per state.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Gray codes for consecutive indices differ in…",
                "Adjacent Gray codes change…",
                "Ring-friendly Gray steps have Hamming…",
                "Single-bit adjacency is the hallmark of…",
            ][(i - 1) % 4],
            [
                "Exactly one bit",
                "All bits",
                "No bits",
                "Two N flip-flops",
            ],
            0,
            "Single-bit steps on rings/counters.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "Multi-bit flips on a transition can glitch combinational decode briefly.",
                "Illegal intermediate codes are a hazard during multi-bit changes.",
                "Binary is always best with no trade-offs.",
                "Four states in binary need two flip-flops.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Compact codes can hazard decode; 4 states → 2 bits binary.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "S1→S2 in binary 00,01,10,11 often has Hamming…",
                "Starter: binary S1 to S2 flipping both bits means distance…",
                "Why flag yellow multi-bit arcs?",
                "Hamming distance two on an arc means…",
            ][(i - 1) % 4],
            [
                "Two — both bits can flip",
                "Zero always",
                "Exactly N flops",
                "Gray by definition",
            ],
            0,
            "Both bits flip; decode can glitch.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "One-hot decode of 'are we in S2?' is often…",
                "Advantage of one-hot checks?",
                "One-hot costs more FFs but…",
                "Single-wire state tests come from…",
            ][(i - 1) % 4],
            [
                "A single wire (that state's bit)",
                "Always fewer FFs than binary",
                "Automatic CDC safety",
                "Removing next-state logic",
            ],
            0,
            "One FF per state simplifies decode.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Five states in three binary bits leave…",
                "Unused binary codes require…",
                "Illegal/unused encodings should have…",
                "Why mention recovery for spare codes?",
            ][(i - 1) % 4],
            [
                "Unused codes needing a default next-state",
                "Maximal LFSR period automatically",
                "No possible illegal states",
                "Forced one-hot width of 2",
            ],
            0,
            "Add safe recovery, not hope.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Gray ring steps often have Hamming distance one.",
                "Encoding choice trades area, speed, and glitch risk.",
                "One-hot never flips more than one bit on any arc.",
                "Hamming distance counts how many bits differ between codes.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "One-hot arcs often flip two bits (clear old, set new).",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Do not assume binary is always best because…",
                "Compact codes can still…",
                "When might Gray or one-hot win?",
                "Encoding trade-off example?",
            ][(i - 1) % 4],
            [
                "Multi-bit flips can hazard decode",
                "Binary always maximizes MTBF alone",
                "Binary removes all illegal states",
                "Binary needs N flops always",
            ],
            0,
            "Compact ≠ always safest decode.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Real RTL encoding work still includes…",
                "Beyond the lab tabs, synthesis needs…",
                "Illegal-state handling belongs in…",
                "Which production concern pairs with encoding?",
            ][(i - 1) % 4],
            [
                "Synthesis hints and safe illegal-state recovery",
                "Deleting state registers",
                "Driving clocks from state bits casually",
                "Ignoring Hamming distances",
            ],
            0,
            "Hints + recovery still matter.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                f"Binary width for {4 + (i % 3)} states is at least…",
                f"Minimum bits to encode {5 + (i % 3)} abstract states?",
                f"ceil(log2({3 + (i % 4)})) equals which FF count need?",
                f"How many binary FFs for {8 if i % 2 == 0 else 6} states?",
            ][(i - 1) % 4],
            (
                [str(2), str(3), str(4), str(8)]
                if (i - 1) % 4 == 0
                else [str(2), str(3), str(4), str(5)]
                if (i - 1) % 4 == 1
                else [str(2), str(1 + ((3 + (i % 4) - 1).bit_length())), str(8), str(16)]
                if (i - 1) % 4 == 2
                else (["3", "4", "5", "8"] if i % 2 == 0 else ["2", "3", "4", "6"])
            ),
            (
                0
                if (i - 1) % 4 == 0
                else 1
                if (i - 1) % 4 == 1
                else 1
                if (i - 1) % 4 == 2
                else (0 if i % 2 == 0 else 1)
            ),
            "Binary uses ceil(log2 N) bits.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Abstract states S0/S1/S2 become bit patterns in flip-flops.",
                "Arc tables can highlight multi-bit transitions.",
                "Unused codes can be left without a default next-state safely always.",
                "One-hot uses wider registers than binary for the same N.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Always define recovery for illegal/unused codes.",
            "hard",
        ),
    ]
    return _bank("module31-state-encoding", "State encoding", "encoding", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module32 — Sequence detector
# ---------------------------------------------------------------------------
def seqdet_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "A sequence detector FSM recognizes…",
                "Sequence detectors watch for…",
                "Serial pattern recognition is the job of…",
                "What does a seq detector raise Z for?",
            ][(i - 1) % 4],
            [
                "A specific bit pattern in a serial stream",
                "Only combinational AND gates",
                "DRAM refresh timing",
                "UART stop bits only",
            ],
            0,
            "Pattern in serial input.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter Mealy 1011: Z=1 when…",
                "Mealy detect asserts Z on…",
                "Completing pattern 1011 means…",
                "Final matching bit in Mealy style…",
            ][(i - 1) % 4],
            [
                "The last bit completes the pattern",
                "Every input is 1",
                "State is S0 only",
                "Overlap is disabled",
            ],
            0,
            "Z on final matching bit.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Overlapping detection means…",
                "Overlap allows…",
                "Suffix reuse after a match is…",
                "Why can 10111 match twice for pattern 1011?",
            ][(i - 1) % 4],
            [
                "A suffix of a match can start the next",
                "Patterns never share bits",
                "Z is always 0",
                "Only Moore style works",
            ],
            0,
            "Reuse matched suffix.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "State Sk typically means the first k pattern bits matched.",
                "Prefix-length states track partial matches.",
                "On mismatch you must always hard-reset to S0 with no prefix recovery.",
                "Moore detectors often add a dedicated detect state where Z stays high.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Prefix recovery jumps to the longest proper prefix — not always S0.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "On mismatch, good detectors often…",
                "Prefix recovery means…",
                "After a failed bit, next state should…",
                "Brute-force reset to S0 always…",
            ][(i - 1) % 4],
            [
                "Jump to the longest proper prefix that still fits",
                "Ignore the stream forever",
                "Force Z=1",
                "Switch clocks",
            ],
            0,
            "Reuse partial progress; do not waste matches.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Mealy vs Moore detect timing differs because…",
                "Pulse-on-arc vs level-in-detect-state…",
                "Downstream logic may care about…",
                "Non-overlap mode is…",
            ][(i - 1) % 4],
            [
                "When Z asserts relative to the completing bit / state",
                "Identical waveforms always",
                "Only package names",
                "Required for Gray CDC",
            ]
            if (i - 1) % 4 != 3
            else [
                "A different specification than overlap",
                "The same as maximal LFSR period",
                "Illegal in Mealy machines",
                "Only for ring counters",
            ],
            0,
            "Timing and overlap are part of the spec.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "States empty / 1 / 10 / 101 track…",
                "For pattern 1011, prefix states represent…",
                "Matched-prefix encoding is…",
                "S2 in a 1011 detector usually means…",
            ][(i - 1) % 4],
            [
                "How much of the target pattern matched so far",
                "FIFO occupancy only",
                "Clock enable duty",
                "Reset tree depth",
            ],
            0,
            "Prefix length of the target.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Overlap off changes restart behavior after a match.",
                "Forgetting overlap when a pattern repeats inside itself is a pitfall.",
                "Mealy Z never asserts on the completing transition.",
                "Stream 1011 yields Z history 0,0,0,1 in the Mealy starter.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Mealy asserts on the completing bit; overlap is a real pitfall.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "After detecting 1011 with overlap, an extra 1 may…",
                "Pattern self-overlap example: 10111…",
                "Why sketch overlapping cases carefully?",
                "Longest proper prefix after a match matters because…",
            ][(i - 1) % 4],
            [
                "Seed another partial/full match",
                "Force async reset only",
                "Clear the clock tree",
                "Disable Moore machines",
            ],
            0,
            "Suffix can begin the next detection.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Real seq-detector RTL still needs…",
                "Beyond the browser stepper, implement…",
                "Production checklist for detectors includes…",
                "Which belongs after drawing the Mealy arcs?",
            ][(i - 1) % 4],
            [
                "Encoding, reset state, and test streams",
                "Deleting prefix recovery",
                "Per-bit 2-FF on the pattern itself only",
                "Ignoring overlap specs",
            ],
            0,
            "Encode, reset, and verify streams.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Fill transition for S2 (matched 10) on input 0 vs 1…",
                "From prefix 10, input 1 advances toward…",
                "From prefix 10, input 0 typically…",
                "Partial match 10 for target 1011: next on 1 is…",
            ][(i - 1) % 4],
            [
                "1 → deeper prefix (101); 0 → recovery per table",
                "Both inputs force S0 always with no recovery",
                "Both inputs assert Z immediately",
                "Inputs are ignored until reset",
            ],
            0,
            "Follow the pattern; recover on mismatch.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Moore detect often holds Z in a dedicated state.",
                "Mealy detect often pulses Z on the completing arc.",
                "Prefix recovery is optional and never affects match count.",
                "Non-overlap vs overlap is a specification choice.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Prefix recovery is not optional for correct overlap behavior.",
            "hard",
        ),
    ]
    return _bank("module32-seq-detector", "Sequence detector", "seqdet", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module33 — Ring / Johnson
# ---------------------------------------------------------------------------
def ring_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "Ring counter feedback (4-bit) is…",
                "A ring feeds which bit into q0?",
                "Circulate feedback for a ring means…",
                "Plain (non-inverted) MSB into LSB describes…",
            ][(i - 1) % 4],
            [
                "q[MSB] fed into q0",
                "~q[MSB] fed into q0",
                "Always 1",
                "No feedback",
            ],
            0,
            "Circulate MSB into LSB.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Johnson counter feedback is…",
                "Twisted-ring feedback uses…",
                "Johnson differs from ring by…",
                "~q[MSB] into q0 is…",
            ][(i - 1) % 4],
            [
                "Inverted MSB into q0",
                "MSB unchanged into q0",
                "XOR of all bits",
                "Async reset only",
            ],
            0,
            "Twisted ring: ~q[MSB].",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Starter ring from 0001, one step gives…",
                "One-hot 0001 walking right becomes…",
                "After one ring shift from 0001…",
                "Four-bit ring step: 0001 → …",
            ][(i - 1) % 4],
            [
                "0010",
                "0001",
                "1000",
                "1111",
            ],
            0,
            "One-hot walks (direction per wiring); starter shows 0010.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "4-bit Johnson has useful period 8 (2N).",
                "Twisted ring visits 2N states from a valid start.",
                "Ring period for N-bit one-hot init is typically N.",
                "All-zero is a great init for a ring counter.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Johnson period 2N; ring needs valid one-hot — all-zero can lock.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Why can all-zero lock a ring?",
                "Zero feedback forever happens when…",
                "Invalid ring init risk?",
                "Beware all-zero on a ring because…",
            ][(i - 1) % 4],
            [
                "MSB feedback stays 0 so the register never leaves 0",
                "It forces maximal LFSR period",
                "It invents 2N states automatically",
                "It disables shift enables forever legally",
            ],
            0,
            "No circulating 1 → stuck at zero.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Four ring states from 0001 are…",
                "Full ring period listing starts 0001 then…",
                "One-hot walk sequence (4-bit) is…",
                "After four ring steps from 0001 you return to…",
            ][(i - 1) % 4],
            [
                "0001, 0010, 0100, 1000 (then repeat)",
                "Only 1111 forever",
                "Random PRBS bits",
                "Gray codes of length 2N",
            ],
            0,
            "Circulate the single 1 around.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Johnson from 0000 over 8 steps illustrates…",
                "Why is Johnson period 2N for N bits?",
                "Twisted ring state count on the main cycle is…",
                "Compared with ring period N, Johnson offers…",
            ][(i - 1) % 4],
            [
                "2N distinct states in the main cycle",
                "Exactly N states only",
                "2^N − 1 always",
                "Only one legal state",
            ],
            0,
            "Inversion doubles the tour versus plain ring.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Same shift chain, different feedback tap: ring vs Johnson.",
                "Neither replaces a binary counter when you need all 2^N counts.",
                "Ring needs valid one-hot init; Johnson needs a sensible reset.",
                "Johnson feedback is XOR of all bits like an LFSR.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 3 else False,
            "Johnson uses inverted MSB, not a full LFSR tap set.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Illegal states without recovery are a pitfall because…",
                "Invalid init on ring/Johnson can…",
                "Production counters still need…",
                "Besides stepping demos, designs need…",
            ][(i - 1) % 4],
            [
                "The machine can lock or wander off the intended cycle",
                "Period becomes exactly 2^N − 1 always",
                "CDC becomes free",
                "Clocks become optional",
            ],
            0,
            "Handle illegal states and reset correctly.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "RTL sketch difference ring vs Johnson?",
                "always shift with feedback: ring uses…",
                "Johnson always block feedback expression is…",
                "Pick the feedback contrast.",
            ][(i - 1) % 4],
            [
                "q0<=q[MSB] vs q0<=~q[MSB]",
                "Both use XOR of all taps identically",
                "Both require gated clocks",
                "Both forbid shift registers",
            ],
            0,
            "Invert or not on the recirculating bit.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                f"N={3 + (i % 3)} ring with one-hot init has period…",
                f"Johnson period for N={4 + (i % 2)} is…",
                f"2N for N={5 if i % 2 else 3} equals…",
                "Useful Johnson state count vs ring for same N?",
            ][(i - 1) % 4],
            (
                [str(3 + (i % 3)), str(2 * (3 + (i % 3))), str(2 ** (3 + (i % 3))), "1"]
                if (i - 1) % 4 == 0
                else [str(4 + (i % 2)), str(2 * (4 + (i % 2))), str(2 ** (4 + (i % 2)) - 1), "N"]
                if (i - 1) % 4 == 1
                else (
                    [str(10), str(6), str(8), str(2)]
                    if i % 2
                    else [str(6), str(3), str(8), str(4)]
                )
                if (i - 1) % 4 == 2
                else ["2N vs N", "N vs 2N", "Equal always", "2^N vs 1"]
            ),
            0 if (i - 1) % 4 != 1 else 1,
            "Ring ~N; Johnson ~2N for width N.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "Display order MSB-left (q3…q0) matters when reading patterns.",
                "Timing, enable, and illegal-state handling still apply in silicon.",
                "A ring with all-zero init is guaranteed to leave zero in one cycle.",
                "Feedback box: plain q[MSB] for ring, not-q[MSB] for Johnson.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "All-zero ring stays locked without a circulating 1.",
            "hard",
        ),
    ]
    return _bank("module33-ring-johnson", "Ring / Johnson", "ring", easy_b, med_b, hard_b)


# ---------------------------------------------------------------------------
# module34 — LFSR / PRBS
# ---------------------------------------------------------------------------
def lfsr_bank() -> dict:
    easy_b = [
        lambda i: mcq(
            "",
            [
                "LFSR stands for…",
                "Linear feedback shift register abbreviates to…",
                "Shift + XOR taps describe an…",
                "What does LFSR expand to?",
            ][(i - 1) % 4],
            [
                "Linear feedback shift register",
                "Low-frequency signal router",
                "Latch-free sequential reset",
                "Logic fanout shift rule",
            ],
            0,
            "Shift + XOR taps.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "Maximal n-bit LFSR period is…",
                "All nonzero states once implies period…",
                "2^n − 1 is the period of…",
                "Longest binary LFSR cycle length is…",
            ][(i - 1) % 4],
            [
                "2^n − 1",
                "2^n",
                "n",
                "n!",
            ],
            0,
            "All nonzero states once.",
            "easy",
        ),
        lambda i: mcq(
            "",
            [
                "All-zero seed on an LFSR…",
                "Forbidden lock state is…",
                "Seeding 000…0 causes…",
                "Why never seed all-zero?",
            ][(i - 1) % 4],
            [
                "Locks (feedback stays 0)",
                "Gives maximal period",
                "Doubles PRBS rate",
                "Is required for PRBS",
            ],
            0,
            "Forbidden lock state.",
            "easy",
        ),
        lambda i: tf(
            "",
            [
                "PRBS is a pseudo-random bit stream from the LFSR output.",
                "Often the shifted-out LSB forms the PRBS bit.",
                "PRBS is true random and never repeats.",
                "Maximal polynomials visit every nonzero state before repeating.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "PRBS repeats after the period; not true random.",
            "easy",
        ),
    ]
    med_b = [
        lambda i: mcq(
            "",
            [
                "Starter 4-bit maximal x^4+x+1 with seed 0001 has period…",
                "Measure period for n=4 maximal: expect…",
                "Fifteen steps before seed returns means…",
                "4-bit maximal period equals…",
            ][(i - 1) % 4],
            [
                "15",
                "16",
                "4",
                "8",
            ],
            0,
            "2^4 − 1 = 15.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "Non-maximal polynomial x^4+x^2+1 typically…",
                "Wrong taps shorten the cycle because…",
                "Short vs maximal poly contrast shows…",
                "Pick the effect of a non-maximal poly.",
            ][(i - 1) % 4],
            [
                "Period under 15 for n=4",
                "Guaranteed period 15",
                "Forced all-zero lock forever only",
                "Removes the need for a seed",
            ],
            0,
            "Bad taps → shorter cycle.",
            "medium",
        ),
        lambda i: mcq(
            "",
            [
                "LFSR uses include…",
                "PRBS shows up in…",
                "Common LFSR applications?",
                "Which is a typical LFSR use case?",
            ][(i - 1) % 4],
            [
                "Scramblers, BIST, link training",
                "Only analog PLL lock detect",
                "Replacing all FSMs",
                "Deleting STA",
            ],
            0,
            "Scramblers, BIST, serial-link PRBS.",
            "medium",
        ),
        lambda i: tf(
            "",
            [
                "Fibonacci LFSR XORs selected taps into the next MSB.",
                "Each clock shifts and drops a bit that can feed PRBS.",
                "Maximal taps do not matter if the seed is nonzero.",
                "Nonzero seed is required for a useful cycle.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "Taps and seed both matter; nonzero alone is not enough.",
            "medium",
        ),
    ]
    hard_b = [
        lambda i: mcq(
            "",
            [
                "Real LFSR designs still need…",
                "Beyond the lab stepper, production needs…",
                "Tap tables and seed logic matter because…",
                "Which remains after measuring period in the browser?",
            ][(i - 1) % 4],
            [
                "Known polynomials, seed logic, and RX sync as needed",
                "Only deleting feedback",
                "Seeding all-zero for lock",
                "Using q1 metastable CDC as the PRBS source",
            ],
            0,
            "Use standard taps; handle seed and sync.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                f"Maximal period for n={5 + (i % 3)} is…",
                f"2^{6 + (i % 2)} − 1 equals…",
                f"n={3 + (i % 2)} maximal length is…",
                "Period formula for maximal n-bit LFSR?",
            ][(i - 1) % 4],
            (
                [
                    str(2 ** (5 + (i % 3)) - 1),
                    str(2 ** (5 + (i % 3))),
                    str(5 + (i % 3)),
                    str(2 * (5 + (i % 3))),
                ]
                if (i - 1) % 4 == 0
                else [
                    str(2 ** (6 + (i % 2)) - 1),
                    str(2 ** (6 + (i % 2))),
                    str(6 + (i % 2)),
                    "n!",
                ]
                if (i - 1) % 4 == 1
                else [
                    str(2 ** (3 + (i % 2)) - 1),
                    str(2 ** (3 + (i % 2))),
                    "2N",
                    "N",
                ]
                if (i - 1) % 4 == 2
                else ["2^n − 1", "2^n", "n", "2N"]
            ),
            0,
            "Maximal period is 2^n − 1.",
            "hard",
        ),
        lambda i: mcq(
            "",
            [
                "Why is PRBS not true random?",
                "Pseudo-random means…",
                "After one full maximal period the sequence…",
                "Deterministic repetition is why we say…",
            ][(i - 1) % 4],
            [
                "It repeats after a finite period",
                "It never repeats by definition",
                "It requires analog noise diodes always",
                "It ignores the polynomial",
            ],
            0,
            "Finite period → pseudo, not true random.",
            "hard",
        ),
        lambda i: tf(
            "",
            [
                "All-zero locks because XOR feedback stays zero.",
                "A wrong polynomial can shorten the cycle even with a good seed.",
                "Maximal n-bit LFSR includes the all-zero state in its long cycle.",
                "PRBS bits accumulate as the register shifts each clock.",
            ][(i - 1) % 4],
            True if (i - 1) % 4 != 2 else False,
            "All-zero is excluded from the maximal nonzero tour.",
            "hard",
        ),
    ]
    return _bank("module34-lfsr-lab", "LFSR / PRBS", "lfsr", easy_b, med_b, hard_b)


def build_banks() -> list[dict]:
    return [
        clock_bank(),
        reset_bank(),
        clken_bank(),
        cdc_bank(),
        fsm_bank(),
        encoding_bank(),
        seqdet_bank(),
        ring_bank(),
        lfsr_bank(),
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
            assert it["id"].count("_") >= 2, it["id"]
        assert counts.get("easy", 0) >= 1 and counts.get("medium", 0) >= 1 and counts.get("hard", 0) >= 1, (
            bank["module"],
            counts,
        )
        keys = [content_key(it) + "|" + it["difficulty"] for it in bank["items"]]
        assert len(keys) == len(set(keys)), (bank["module"], "duplicate questions")
        print(path.name, counts, "total", len(bank["items"]))


if __name__ == "__main__":
    main()
