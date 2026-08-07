"""Write all learn_digital challenge banks (modules 01-49).

Preserves existing media-backed banks for module01, module13, module26
unless --force-core is passed.

Usage:
  python scripts/generate_all_banks.py
  python scripts/generate_all_banks.py --force-core
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from banks_02_10 import build_banks as build_02_10
from banks_11_24 import build_banks as build_11_24
from banks_25_34 import build_banks as build_25_34
from banks_35_49 import build_banks as build_35_49
from generate_difficulty_banks import kmap_bank, radix_bank, setup_bank

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_digital" / "questions"
CORE = {
    "module01-radix-converter": radix_bank,
    "module13-kmap": kmap_bank,
    "module26-setup-hold": setup_bank,
}


def write_bank(bank: dict) -> None:
    path = OUT / f"{bank['module']}.json"
    path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for it in bank["items"]:
        counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
        assert "(v" not in it["prompt"], it["prompt"]
        assert "variant " not in it["prompt"].lower(), it["prompt"]
    print(path.name, counts, "total", len(bank["items"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--force-core",
        action="store_true",
        help="Overwrite radix/kmap/setup banks (drops media attachments)",
    )
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    banks = []
    banks.extend(build_02_10())
    banks.extend(build_11_24())
    banks.extend(build_25_34())
    banks.extend(build_35_49())

    if args.force_core:
        banks.extend([radix_bank(), kmap_bank(), setup_bank()])
    else:
        for mid, builder in CORE.items():
            path = OUT / f"{mid}.json"
            if not path.exists():
                banks.append(builder())

    for bank in banks:
        write_bank(bank)


if __name__ == "__main__":
    main()
