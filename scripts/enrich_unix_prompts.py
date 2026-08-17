"""Add unique bash code-context snippets so every bank item is substantively distinct."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content" / "learn_unix" / "questions"
NAMES = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
DIRS = ["bin", "src", "logs", "tmp", "build", "docs", "scripts", "cfg"]


def nm(i: int) -> str:
    return NAMES[(i - 1) % len(NAMES)]


def dn(i: int) -> str:
    return DIRS[(i - 1) % len(DIRS)]


def snippet(module: str, difficulty: str, idx: int) -> str:
    """Return a unique one- or two-line shell context for this item index."""
    n = idx
    a, b = nm(idx), nm(idx + 1)
    d = dn(idx)
    base = {
        "module01-vfs-terminal": [
            f"pwd; ls -la ./{d}",
            f"cd /tmp/{a}{n} && pwd",
            f"ls {d}; cd ..; pwd",
            f"# navigate: cd ~/{d}/{a}",
        ],
        "module02-man-help-lab": [
            f"man {a} | head -n {n % 20 + 5}",
            f"{a} --help | grep -i usage",
            f"whatis ls; man 1 ls",
            f"apropos {a} 2>/dev/null | head",
        ],
        "module03-path-abs-rel": [
            f"p=/tmp/{d}/{a}; echo \"$p/{b}.txt\"",
            f"cd ~/{d}; realpath ./{a}",
            f"test -f /var/log/{a}{n}.log && echo ok",
            f"# abs vs rel: ./ {d}/{a} vs /$d/{a}",
        ],
        "module04-wildcards-globs": [
            f"ls {d}/*.{a} 2>/dev/null",
            f"for f in *.log; do echo \"$f\"; done",
            f"printf '%s\\n' {d}/{a}[0-9].txt",
            f"shopt -s nullglob; files=({d}/*); echo ${{#files[@]}}",
        ],
        "module05-file-types-lab": [
            f"ls -l {d}/{a}; file {d}/{a}",
            f"ln -s ../{b} {d}/link{n}",
            f"stat {d}/{a} | head",
            f"test -L {d}/{a} && readlink {d}/{a}",
        ],
        "module06-realpath-resolve": [
            f"realpath {d}/{a}",
            f"readlink -f {d}/link{n} 2>/dev/null",
            f"realpath -e /tmp/{a}/{b} || echo missing",
            f"# resolve: {d}/../{a}/{b}",
        ],
        "module07-permissions": [
            f"chmod u+x scripts/{a}{n}.sh",
            f"umask; ls -l {d}/{a}",
            f"chmod 600 secrets/{a}.key",
            f"command -v {a}; echo \"$PATH\" | tr ':' '\\n' | head",
        ],
        "module08-dotfiles-lab": [
            f"ls -a ~ | head; test -f ~/.bashrc && echo has_bashrc",
            f"mkdir -p ~/.config/{a}",
            f"chmod 600 ~/.ssh/id_rsa 2>/dev/null",
            f"# XDG: ${{XDG_CONFIG_HOME:-$HOME/.config}}/{a}",
        ],
        "module09-ps-kill-lab": [
            f"ps -o pid,ppid,cmd | head -n {n % 10 + 5}",
            f"pgrep -a {a} || true",
            f"kill -TERM {n + 1000} 2>/dev/null || true",
            f"ps aux | grep -i [{a[0]}]{a[1:]} || true",
        ],
        "module10-job-control-lab": [
            f"sleep {n % 5 + 2} & jobs -l",
            f"sleep 30 & bg; jobs",
            f"# fg %1 / bg %1 / disown",
            f"nohup sleep {n} >/tmp/{a}.out 2>&1 &",
        ],
        "module11-pipes": [
            f"grep -i error {d}/{a}.log | head",
            f"cmd() {{ echo hi; }}; cmd | tee /tmp/{a}{n}.out",
            f"printf 'a\\nb\\n' | xargs -n1 echo",
            f"ls {d} 2>&1 | tee /tmp/{a}.log >/dev/null",
        ],
        "module12-sort-uniq-cut": [
            f"sort {d}/{a}.txt | uniq -c | sort -nr | head",
            f"cut -d, -f1,3 {d}/{a}.csv | head",
            f"sort -k2,2n {d}/{a}.tsv",
            f"sort -u {d}/{a}.txt | wc -l",
        ],
        "module13-here-doc-lab": [
            f"cat <<EOF\\nhello {a}{n}\\nEOF",
            f"ssh -G localhost <<<\"# probe {n}\" 2>/dev/null | head",
            f"cat <<'EOF' > /tmp/{a}.conf\\nkey={n}\\nEOF",
            f"tr a-z A-Z <<< \"{a}{n}\"",
        ],
        "module14-shell-history": [
            f"history | tail -n {n % 15 + 5}",
            f"# Ctrl-R then type: {a}",
            f"HISTTIMEFORMAT='%F %T ' history | tail",
            f"echo \"last: !!  last-arg: !$\"  # history expansion demo",
        ],
        "module15-alias-lab": [
            f"alias ll='ls -l'; type ll",
            f"{a}() {{ echo \"args: $*\"; }}; {a} {n} {b}",
            f"unalias ll 2>/dev/null; alias | head",
            f"command ls >/dev/null; type -a ls",
        ],
        "module16-scripting": [
            f"for f in {d}/*.log; do echo \"$f\"; done",
            f"if [ -f \"{d}/{a}\" ]; then echo yes; fi",
            f"case ${{1:-x}} in {a}) echo a;; *) echo other;; esac",
            f"NAME=\"${{1:-World{n}}}\"; echo \"$NAME\"",
        ],
        "module17-exit-status-lab": [
            f"true && echo ok; false || echo fail; echo status=$?",
            f"cmd() {{ return {n % 3}; }}; cmd; echo $?",
            f"set -o pipefail; false | true; echo $?",
            f"test -d {d} && exit 0 || exit 1",
        ],
        "module18-safe-scripting": [
            f"set -euo pipefail; f=$(mktemp); echo hi >\"$f\"; rm -f -- \"$f\"",
            f"printf '%s\\0' {d}/* | xargs -0 -n1 echo",
            f"# quote: rm -rf -- \"${{dir}}\"",
            f"command -v jq >/dev/null || {{ echo missing; exit 127; }}",
        ],
        "module19-project-archives": [
            f"tar -czf /tmp/{a}{n}.tar.gz {d}",
            f"diff -u {d}/{a}.old {d}/{a}.new | head",
            f"sed 's/foo/bar/' {d}/{a}.txt | head",
            f"tar -tzf /tmp/{a}.tar.gz | head",
        ],
        "module20-zip-vs-tar": [
            f"tar -czf /tmp/{a}.tar.gz {d}; tar -tzf /tmp/{a}.tar.gz | head",
            f"zip -r /tmp/{a}{n}.zip {d}; unzip -l /tmp/{a}{n}.zip | head",
            f"# prefer tar.gz for Unix metadata; zip for interop",
            f"tar -C /tmp -xzf /tmp/{a}.tar.gz",
        ],
        "module21-backup-clean": [
            f"cp -a {d} /tmp/backup-{a}-{n}",
            f"make -n clean; ls {d}",
            f"rsync -a --dry-run {d}/ /tmp/{a}-bak/",
            f"# backup then: rm -rf build/",
        ],
        "module22-link-relative": [
            f"ln -s ../{b}/tool {d}/{a}-link",
            f"readlink {d}/{a}-link; realpath {d}/{a}-link || true",
            f"ln -sfr {d}/{a} /tmp/{b}-link{n} 2>/dev/null || ln -s $(realpath {d}/{a}) /tmp/{b}-link{n}",
            f"# move tree and watch relative link break",
        ],
        "module23-workflow": [
            f"make test && make lint && git status -sb",
            f"test -f .env.example && echo env_template_ok",
            f"# pre-push: unit tests + secret scan",
            f"make help 2>/dev/null | head || grep -E '^[a-z].*:' Makefile | head",
        ],
        "module24-make-basics": [
            f"make -n {a}",
            f".PHONY: clean; clean:\\n\\trm -rf build/",
            f"make -j{n % 4 + 2} all",
            f"echo \"target=$@ deps=$^\"",
        ],
        "module25-dry-run-lab": [
            f"make -n clean",
            f"rsync -a --dry-run {d}/ /tmp/{a}/",
            f"DRY_RUN=1; if [ \"$DRY_RUN\" = 1 ]; then echo rm -rf {d}; else rm -rf {d}; fi",
            f"git push --dry-run 2>&1 | head",
        ],
        "module26-log-triage": [
            f"tail -n 50 {d}/{a}.log | grep -i error",
            f"grep -RIn --color=never fail {d} | head",
            f"wc -l {d}/{a}.log; ls -l {d}/{a}.log",
            f"# note: cmd=... status=$? key_line=...",
        ],
        "module27-env-file-lab": [
            f"set -a; [ -f .env ] && . ./.env; set +a; echo \"${{{a.upper()}:-unset}}\"",
            f"grep -E '^[A-Z0-9_]+=' .env.example | cut -d= -f1",
            f"export {a.upper()}={n}; printenv {a.upper()}",
            f"# gitignore .env; commit .env.example",
        ],
    }
    generic_easy = [
        f"cd ~/{d} && pwd && ls",
        f"echo \"lab-{a}-{n}\"",
        f"test -d {d} || mkdir -p {d}",
        f"printf '%s\\n' {a}{n}",
    ]
    generic_med = [
        f"set -euo pipefail; cd {d} || exit 1",
        f"cmd() {{ echo {a}; }}; cmd | tee /tmp/{b}{n}.log",
        f"find {d} -type f -name '*{a}*' 2>/dev/null | head",
        f"# check: status=$? path={d}/{a}",
    ]
    generic_hard = [
        f"set -euo pipefail; trap 'echo ERR' ERR; true",
        f"realpath -m {d}/../{a}/{b} 2>/dev/null || true",
        f"mapfile -t lines < <(printf '%s\\n' {a} {b}); echo ${{#lines[@]}}",
        f"# harden: quote, --, mktemp, pipefail ({n})",
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
        if not prompt.startswith("Given this shell snippet:"):
            it["prompt"] = f"Given this shell snippet:\n```bash\n{ctx}\n```\n{prompt}"
        key = content_key(it)
        salt = 0
        while key in seen:
            salt += 1
            # inject uniqueness into the fenced snippet
            fence = "```bash\n"
            if fence in it["prompt"]:
                it["prompt"] = it["prompt"].replace(
                    fence,
                    f"{fence}# variant {salt}\n",
                    1,
                )
            else:
                it["prompt"] = f"# variant {salt}\n" + it["prompt"]
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
