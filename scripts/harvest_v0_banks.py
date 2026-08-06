import json
import pathlib

src_root = pathlib.Path(r"D:/proj/designs/digital_learning/courses/learn_digital")
dst_root = pathlib.Path(r"d:/proj/designs/quiz_challenge_platform/content/learn_digital/questions")
modules = [
    "module01-radix-converter",
    "module02-twos-complement",
    "module05-gray-code",
    "module11-truth-table",
    "module13-kmap",
    "module18-mux-decoder",
    "module26-setup-hold",
    "module30-fsm-lab",
]
diffs = ["easy", "medium", "hard"]
for mid in modules:
    quiz = json.loads((src_root / mid / "quiz.json").read_text(encoding="utf-8"))
    items = []
    for i, diff in enumerate(diffs):
        it = dict(quiz["items"][i])
        it["difficulty"] = diff
        items.append(it)
    out = {"module": mid, "title": quiz.get("title", mid), "items": items}
    (dst_root / f"{mid}.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("wrote", mid, len(items))
