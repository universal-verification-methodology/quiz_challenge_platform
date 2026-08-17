"""Generate learn_unix challenge banks: 30 items x 3 difficulties per lab module.

Seeds expand formative quiz.json topics with parametric variants (no clone padding).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "learn_unix" / "questions"
SEED_ROOT = Path("d:/proj/designs/digital_learning/courses/learn_unix")
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


def _ctx(i: int) -> dict:
    return {
        "i": i,
        "n": (i % 7) + 2,
        "f": f"file{i}.txt",
        "g": f"log{i}.log",
        "d": f"dir{i}",
        "u": f"user{i}",
        "p": f"/tmp/lab{i}",
        "h": f"/home/user{i}",
        "s": f"script{i}.sh",
        "a": f"archive{i}.tar.gz",
        "z": f"bundle{i}.zip",
        "t": f"target{i}",
        "b": f"backup{i}",
        "m": f"mod{i}",
        "e": f"KEY{i}",
        "v": f"val{i}",
    }


def _fmt(s: str, c: dict) -> str:
    """Replace only exact {key} tokens; leave shell braces like {a,b} untouched."""
    if "{" not in s:
        return s

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        return str(c[key]) if key in c else m.group(0)

    return re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", repl, s)


def M(prompt: str, choices: list[str], answer: int, explain: str, difficulty: str):
    """Parametric MCQ builder; use {i}/{f}/{d}/... in strings."""

    def build(i: int) -> dict:
        c = _ctx(i)
        return mcq("", _fmt(prompt, c), [_fmt(x, c) for x in choices], answer, explain, difficulty)

    return build


def T(prompt: str, answer: bool, explain: str, difficulty: str):
    """Parametric true/false builder."""

    def build(i: int) -> dict:
        return tf("", _fmt(prompt, _ctx(i)), answer, explain, difficulty)

    return build


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


def _ascii_punct(s: str) -> str:
    return (
        s.replace("\u2026", "...")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2192", "->")
        .replace("\u2190", "<-")
    )


def pad(difficulty: str, prefix: str, builders: list) -> list[dict]:
    """Build exactly TARGET unique items; inject context on collision."""
    out: list[dict] = []
    seen: set[str] = set()
    n = 0
    paths = ["~/bin", "/usr/local", "/opt/tools", "./scripts", "/var/log", "/tmp/work"]
    names = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel"]
    while len(out) < TARGET:
        n += 1
        if n > TARGET * 40:
            raise RuntimeError(f"{prefix}/{difficulty}: stuck at {len(out)}/{TARGET}")
        it = dict(builders[(n - 1) % len(builders)](n))
        it["prompt"] = _ascii_punct(str(it.get("prompt") or ""))
        if it.get("explain"):
            it["explain"] = _ascii_punct(str(it["explain"]))
        if it.get("choices"):
            it["choices"] = [_ascii_punct(str(x)) for x in it["choices"]]
        key = content_key(it)
        salt = 0
        while key in seen:
            salt += 1
            p = paths[(n + salt) % len(paths)]
            nm = names[(n + salt) % len(names)]
            it = dict(it)
            it["prompt"] = (
                f"# Review context: `{p}/{nm}` slot {len(out) + 1} variant {salt}\n"
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


def seed_builders(module: str) -> list:
    """Optional formative quiz.json items as easy builders."""
    path = SEED_ROOT / module / "quiz.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out = []
    for raw in data.get("items") or []:
        item = dict(raw)

        def make(it=item):
            def build(_i: int) -> dict:
                x = dict(it)
                x.pop("id", None)
                x["difficulty"] = "easy"
                return x

            return build

        out.append(make())
    return out


# --- topic builders (prefix -> easy, medium, hard) -----------------------

TOPICS: dict[str, tuple[list, list, list]] = {
    "vfs": (
        [
            M("pwd tells you...", ["Your login password", "The current working directory", "All processes", "Only $HOME forever"], 1, "pwd prints the cwd for this shell.", "easy"),
            M("A relative path is resolved against...", ["Always /", "Always $HOME", "The current working directory", "The Git remote"], 2, "Relative paths join to cwd.", "easy"),
            T("The browser vfs-terminal lab writes permanently to your real disk.", False, "It is a sandboxed concept lab.", "easy"),
            M("A good first practice trio is...", ["git push, make, verilator", "pwd, ls, cd", "chmod, chown, sudo", "tar, gzip, scp"], 1, "Navigation starts with pwd, ls, cd.", "easy"),
            M("`ls {d}` typically lists...", ["Running processes", "Directory entries in {d}", "Environment variables", "Git remotes only"], 1, "ls lists directory contents.", "easy"),
            M("`cd {p}` then pwd should show...", ["{p} (or its resolved form)", "Always /", "Always $HOME", "The previous directory only"], 0, "cd changes cwd; pwd confirms it.", "easy"),
            T("`ls` with no args lists the current directory.", True, "Default target is cwd.", "easy"),
            M("`.` means...", ["Parent directory", "Current directory", "Home directory", "Root filesystem"], 1, "Dot is cwd.", "easy"),
            M("`..` means...", ["Current directory", "Parent directory", "Home", "Root"], 1, "Dot-dot is parent.", "easy"),
            M("Hidden files often start with...", ["#", ".", "/", "~"], 1, "Dotfiles are named .something.", "easy"),
        ],
        [
            M("After `cd {d}` fails, cwd is usually...", ["Unchanged", "Forced to /", "Forced to $HOME", "Deleted"], 0, "Failed cd leaves cwd alone.", "medium"),
            M("`ls -a {d}` reveals...", ["Only executables", "Including dot entries like . and ..", "Only symlinks", "Only empty files"], 1, "-a shows all including hidden.", "medium"),
            M("`cd -` typically...", ["Deletes the last directory", "Switches to the previous cwd (OLDPWD)", "Always goes to /", "Clears PATH"], 1, "cd - toggles to OLDPWD.", "medium"),
            T("`ls {f}` on a regular file can print the filename itself.", True, "ls on a file names that file.", "medium"),
            M("Tab completion helps most when...", ["Guessing passwords", "Completing unique path prefixes", "Killing all PIDs", "Formatting disks"], 1, "Completion expands unambiguous prefixes.", "medium"),
            M("In the vfs lab, multiple shells usually...", ["Share one real disk permanently", "Each get an isolated tree view", "Disable ls", "Require root"], 1, "Sandbox sessions are isolated concepts.", "medium"),
            M("`cd {h}/../{u}` resolves relative to...", ["Wherever you started, then those components", "Only /tmp", "Git index", "The man page"], 0, "Each component walks from current path.", "medium"),
            T("Whitespace in paths often needs quoting or escaping.", True, "Spaces break word splitting.", "medium"),
            M("`ls -l` adds...", ["Long/detailed metadata columns", "Recursive delete", "Network mounts only", "Color forced off forever"], 0, "Long listing shows mode, links, owner, size, mtime.", "medium"),
            M("A path that starts with `/` is...", ["Relative", "Absolute (from filesystem root)", "Always a symlink", "Invalid on Unix"], 1, "Leading / means absolute.", "medium"),
        ],
        [
            M("If cwd is deleted out from under you, many tools...", ["Always crash the kernel", "May error on relative ops until you cd elsewhere", "Auto remount /", "Rewrite $HOME"], 1, "Stale cwd can break relative paths.", "hard"),
            M("`ls {d}/{f}` vs `cd {d}; ls {f}` differ mainly in...", ["Whether {f} must be absolute", "The cwd used for any further relative ops", "File ownership", "umask"], 1, "cd changes session state; ls path does not.", "hard"),
            T("VFS labs teach mental models; Track A still needs a real shell.", True, "Browser labs complement, not replace, real Unix.", "hard"),
            M("Why prefer `cd -- '{d}'` style for odd names?", ["Required by POSIX always", "Avoids option/path ambiguity for leading - names", "Disables globbing forever", "Forces root"], 1, "-- ends options so names can start with -.", "hard"),
            M("Symlink loops in a tree walk can cause...", ["Faster ls always", "Traversal tools to hang or error", "Automatic repair", "umask reset"], 1, "Cycles break naive recursion.", "hard"),
            M("Mount points vs ordinary directories: `df`/`find -xdev` matter because...", ["They ignore permissions", "Crossing devices changes space and search scope", "They delete inodes", "They disable cd"], 1, "Filesystem boundaries affect tools.", "hard"),
            T("`pwd -P` (where supported) prints the physical path without symlinks.", True, "-P resolves logical symlink cwd.", "hard"),
            M("Session cwd is process state, so a subshell ` (cd {d}) ` ...", ["Changes the parent shell cwd", "Does not change the parent cwd", "Deletes {d}", "Exports OLDPWD to init"], 1, "Subshell cd is local to the child.", "hard"),
            M("Best recovery when lost in a deep tree...", ["rm -rf /", "pwd; ls; cd .. or cd ~", "Disable networking", "chmod 777 /"], 1, "Orient with pwd/ls, then navigate up or home.", "hard"),
            M("In labs, treating the sandbox like production means...", ["Practice safe habits without real disk risk", "Skip quoting forever", "Always use sudo", "Ignore exit status"], 0, "Transferable habits matter.", "hard"),
        ],
    ),
    "man": (
        [
            M("`cmd --help` usually...", ["Formats the disk", "Prints a short usage summary", "Opens vim", "Disables PATH"], 1, "--help is the quick built-in summary.", "easy"),
            M("`man ls` opens...", ["The password file", "The ls manual page", "A compiler", "Git blame"], 1, "man shows the manual.", "easy"),
            T("man pages are often longer and more complete than --help.", True, "man is the deeper reference.", "easy"),
            M("Section 1 of man typically covers...", ["Kernel syscalls only", "User commands", "Only C library", "Only devices"], 1, "Section 1 is user commands.", "easy"),
            M("If `man {m}` fails, try...", ["rm -rf /", "`{m} --help` or search docs", "Reboot only", "chmod 000"], 1, "Fallback to --help/docs.", "easy"),
            M("`whatis ls` (where available) gives...", ["A one-line description", "Full source code", "Process list", "Disk usage"], 0, "whatis is a short summary.", "easy"),
            T("Scrolling in man often uses less-like keys (q to quit).", True, "Pagers use q to exit.", "easy"),
            M("SYNOPSIS in a man page shows...", ["Only license text", "Typical invocation patterns", "CPU temperature", "Git remotes"], 1, "SYNOPSIS is usage shapes.", "easy"),
            M("Flags like `-a` are documented in...", ["Random tweets only", "OPTIONS / DESCRIPTION sections", "Only /etc/passwd", "Makefile PHONY"], 1, "Options live in the manual.", "easy"),
            M("`man man` teaches...", ["How to use the man system", "Only networking", "Only make", "Disk partitioning only"], 0, "man documents itself.", "easy"),
        ],
        [
            M("`man 5 passwd` targets...", ["User command passwd", "File format docs in section 5", "Section 1 only", "A zip archive"], 1, "Section number selects topic class.", "medium"),
            M("`man -k copy` / apropos typically...", ["Deletes files named copy", "Searches short descriptions for keywords", "Compiles kernels", "Sets umask"], 1, "Keyword search across pages.", "medium"),
            T("Some tools ship only --help and no local man page.", True, "Not every binary has man installed.", "medium"),
            M("SEE ALSO points you to...", ["Related commands/pages", "Only your email", "Only CPU flags", "Trash"], 0, "Cross-references nearby tools.", "medium"),
            M("When --help and man disagree, prefer...", ["Whichever is newer/installed for that build + release notes", "Always ignore both", "Only Reddit", "Random"], 0, "Match the installed version.", "medium"),
            M("`info` pages (GNU) are...", ["Always identical to man", "Another hypertext doc system some tools use", "Only for zip", "Disabled by PATH"], 1, "info is a parallel doc system.", "medium"),
            M("Exit codes in man EXIT STATUS help you...", ["Pick wallpaper", "Interpret automation success/failure", "Set hostname", "Format ext4"], 1, "Documented statuses aid scripts.", "medium"),
            T("Locale can change man language if translations are installed.", True, "MANLANG/LANG affect pages.", "medium"),
            M("Truncated --help often means...", ["Full detail is in man/info/docs", "The command is broken always", "You must reboot", "Disable shell"], 0, "Help is a teaser; man is deeper.", "medium"),
            M("Searching inside a man pager commonly uses...", ["/", "sudo", "chmod +t", "tar -c"], 0, "/ starts a search in less.", "medium"),
        ],
        [
            M("POSIX vs GNU man differences matter when...", ["Writing portable scripts/flags", "Choosing fonts", "Naming hosts only", "Buying RAM"], 0, "Flag sets differ across systems.", "hard"),
            M("`MANPATH` overrides...", ["Where man searches for pages", "Your $HOME always", "umask", "Git user.name"], 0, "MANPATH controls page locations.", "hard"),
            T("Built-in shell help (`help cd`) differs from external `man cd`.", True, "Shell builtins have shell help.", "hard"),
            M("Vendor pages under /opt may need...", ["Deleting /usr", "Adding their man path / modules", "Disabling less", "Root-only ls"], 1, "Third-party trees need MANPATH/modules.", "hard"),
            M("For CI, documenting `tool --help` snapshots helps because...", ["man may be absent in slim images", "It replaces tests", "It disables networking", "It sets umask"], 0, "Minimal images often lack man-db.", "hard"),
            M("Ambiguous names (printf builtin vs /usr/bin/printf) require...", ["Knowing which one you invoked", "Always sudo", "Always reboot", "Ignoring docs"], 0, "Builtins shadow externals.", "hard"),
            M("Compressed pages (.gz) are...", ["Normal; man decompresses via pipeline", "Corrupt always", "Only for zip tools", "Ignored forever"], 0, "man handles gzipped pages.", "hard"),
            T("Reading EXAMPLES sections often beats memorizing every flag.", True, "Examples encode common usage.", "hard"),
            M("When packaging a CLI, provide...", ["--help, man/markdown, and exit-status docs", "Only a logo", "Only a GUI", "Only emoji"], 0, "Discoverability stack.", "hard"),
            M("Offline labs still matter because...", ["Networks fail; local docs remain", "man requires cloud GPUs", "Shells cannot run offline", "pwd needs DNS"], 0, "Local docs are resilient.", "hard"),
        ],
    ),
    "path": (
        [
            M("An absolute path starts with...", ["~ always", "/", "./ only", "A drive letter only on Unix"], 1, "Absolute paths begin at /.", "easy"),
            M("A relative path is interpreted from...", ["Always /", "The current working directory", "Always $HOME", "The kernel"], 1, "Relative = from cwd.", "easy"),
            T("`{h}/docs` is absolute if {h} begins with /.", True, "Leading / makes it absolute.", "easy"),
            M("`./{f}` means...", ["{f} in cwd", "{f} in /", "{f} in $HOME only", "Delete {f}"], 0, "./ anchors to cwd.", "easy"),
            M("`../{f}` looks in...", ["The parent of cwd", "Only /tmp", "Only /etc", "Git objects"], 0, ".. is parent.", "easy"),
            M("~ in many shells expands to...", ["Root /", "Your home directory", "Current dir", "/tmp"], 1, "Tilde is home.", "easy"),
            T("Relative and absolute paths can name the same file.", True, "Different spellings, same inode possible.", "easy"),
            M("Which is absolute?", ["{d}/{f}", "/var/log/{g}", "../{f}", "./{d}"], 1, "Only /var/... starts at root.", "easy"),
            M("Joining paths safely in scripts often uses...", ["String paste without slashes care", "Careful / joining or realpath tools", "Always spaces", "Only tabs"], 1, "Avoid double/missing slashes bugs.", "easy"),
            M("`cd {d}` then `cat {f}` reads...", ["{d}/{f} if {f} is relative", "Always /{f}", "Always $HOME/{f}", "Nothing ever"], 0, "Relative names use new cwd.", "easy"),
        ],
        [
            M("`~{u}` (bash) typically means...", ["Home of {u}", "Always /tmp/{u}", "A man section", "A zip member"], 0, "Tilde-user expands that home.", "medium"),
            M("Trailing slash in `cp -r src/ {d}/` often means...", ["Copy contents vs directory semantics (tool-dependent)", "Delete src", "Force absolute", "Disable recursion"], 0, "Trailing / changes copy meaning.", "medium"),
            T("`$PWD/{f}` builds an absolute path from cwd.", True, "PWD is absolute cwd.", "medium"),
            M("Normalization of `a/./b/../c` yields...", ["a/c (conceptually)", "a/./b/../c unchanged always", "Only /", "Only c"], 0, ". and .. cancel in normalization.", "medium"),
            M("Why prefer absolute paths in cron?", ["Cron cwd is not your interactive cwd", "Cron bans relative always by kernel", "Faster CPU", "Disables PATH"], 0, "Cron starts with a different cwd.", "medium"),
            M("Windows-style `C:\\` paths on Unix are...", ["Normal absolute Unix paths", "Not POSIX absolute paths", "Required by bash", "Same as ~"], 1, "Unix absolute uses /.", "medium"),
            M("`cd \"{d} with spaces\"` needs quotes because...", ["Spaces split words", "cd rejects abs paths", "Quotes set uid", "Quotes clear umask"], 0, "Quoting preserves the name.", "medium"),
            T("Two absolute paths equal as strings may still differ via symlinks.", True, "String equality != inode equality.", "medium"),
            M("Best check that `{p}/{f}` exists as a file...", ["`[ -f \"{p}/{f}\" ]`", "`chmod 777`", "`kill -9 1`", "`umask 000`"], 0, "test -f is the file check.", "medium"),
            M("Relative symlink targets are resolved from...", ["The link's directory, not your cwd alone", "Always /", "Always $HOME", "The man page"], 0, "Symlink relativity is from the link location.", "medium"),
        ],
        [
            M("Canonicalization (`realpath`) is needed when...", ["Comparing paths that may include . .. and symlinks", "Printing colors", "Setting PS1 only", "Naming hosts"], 0, "Canonical forms enable reliable compares.", "hard"),
            M("Bind mounts can make two absolute paths...", ["Always identical strings", "Refer to the same data with different prefixes", "Delete inodes", "Disable ls"], 1, "Multiple mount paths can alias data.", "hard"),
            T("Chroot changes what `/` means for a process tree.", True, "Jail root remaps absolute paths.", "hard"),
            M("`PATH` lookup uses absolute candidates by joining...", ["Each PATH dir + command name", "Only $HOME", "Only /tmp", "Git hooks only"], 0, "PATH search builds abs candidates.", "hard"),
            M("URL-like paths (`file://`) vs FS paths...", ["Are not the same API; tools differ", "Are identical always", "Replace man", "Set umask"], 0, "Do not confuse URI and FS paths.", "hard"),
            M("Race: creating `{p}/{f}` with relative names after cd can fail if...", ["Another process changes your cwd expectations / dirs move", "umask is 022", "man is missing", "PS1 is plain"], 0, "TOCTOU and moving trees bite relative logic.", "hard"),
            M("In containers, absolute host paths...", ["May be invisible unless mounted", "Always equal guest paths", "Replace $HOME", "Disable networking"], 0, "Mounts define visible abs paths.", "hard"),
            T("Lexical `../` removal can escape intended roots without realpath checks.", True, "Lexical join != confined join.", "hard"),
            M("When writing portable Makefiles, prefer...", ["Consistent relative layout from repo root or abs via abspath helpers", "Hard-coded /Users/you only", "Only ~", "Only drive letters"], 0, "Repo-relative or computed abs.", "hard"),
            M("Debug 'file not found' first with...", ["pwd; ls -l; echo path; realpath -e if available", "Immediate mkfs", "Disable SELinux blindly", "Random chmod 777 /"], 0, "Orient then verify the exact path.", "hard"),
        ],
    ),
    "glob": (
        [
            M("`*.txt` matches...", ["Only the literal *.txt file", "Names ending in .txt (glob)", "All binaries", "Only hidden files"], 1, "* globs any string.", "easy"),
            M("`?` in a glob matches...", ["Any single character", "Only digits", "Only /", "Nothing"], 0, "? is one character.", "easy"),
            T("Globs are expanded by the shell before most commands run.", True, "Expansion is shell-side.", "easy"),
            M("`file[123].log` can match...", ["file1.log file2.log file3.log", "Only file[123].log literal always", "All .c files", "Only dirs"], 0, "Bracket classes list choices.", "easy"),
            M("`ls {d}/*.log` lists...", ["Logs under {d}", "Only /var/log", "All processes", "Git blobs"], 0, "Glob limited to that directory pattern.", "easy"),
            M("If a glob matches nothing (nullglob off), bash often...", ["Passes the literal pattern", "Crashes the kernel", "Deletes /", "Opens man"], 0, "Unmatched glob may stay literal.", "easy"),
            T("`*` does not cross `/` in pathname expansion.", True, "Each / segment is separate.", "easy"),
            M("`.*` matches...", ["Hidden names starting with . (and often . and .. caveats)", "Only non-hidden", "Only executables", "Only symlinks"], 0, "Dot-globs target hidden names.", "easy"),
            M("Quote `'*.txt'` to...", ["Force globbing", "Prevent globbing (literal)", "Enable sudo", "Clear PATH"], 1, "Quotes suppress expansion.", "easy"),
            M("`rm {d}/*` deletes...", ["Matching non-hidden entries in {d} (dangerous!)", "Only empty dirs", "Nothing ever", "Only symlinks"], 0, "Broad globs are hazardous.", "easy"),
        ],
        [
            M("`**` recursive glob (globstar) ...", ["May match across directories when enabled", "Is POSIX mandatory everywhere", "Deletes mounts", "Sets umask"], 0, "globstar is a bash option.", "medium"),
            M("`[!0-9]*` matches names that...", ["Do not start with a digit", "Are only digits", "Contain /", "Are empty only"], 0, "! negates a class.", "medium"),
            T("`set -o nullglob` makes unmatched globs expand to nothing.", True, "nullglob drops unmatched patterns.", "medium"),
            M("`failglob` makes unmatched globs...", ["Error instead of literal", "Silent success always", "Call sudo", "Format disks"], 0, "failglob is strict.", "medium"),
            M("Brace expansion `{a,b}{1,2}` is...", ["Not the same as pathname globbing", "Identical to *", "A man section", "A umask"], 0, "Braces expand textually first.", "medium"),
            M("To pass a literal `*` to find's -name, you usually...", ["Quote the pattern so the shell does not expand it", "Always unquote", "Use sudo", "cd /"], 0, "Quote for the child tool.", "medium"),
            M("`ls *.{c,h}` relies on...", ["Brace + glob interplay", "Only cron", "Only zip", "SELinux only"], 0, "Braces produce multiple globs.", "medium"),
            T("Globs do not use regex syntax; `.*` is not 'any chars' like regex.", True, "Glob != regex.", "medium"),
            M("Hidden files and `*` ...", ["`*` usually skips dotfiles", "Always includes dotfiles", "Deletes them", "Chmods them"], 0, "Default * skips ., .., and many dotfiles.", "medium"),
            M("Safe pattern iteration: `for f in {d}/*.txt; do ...`", ["Still handle unmatched literal / nullglob", "Never needs quotes", "Requires root", "Disables errexit"], 0, "Unmatched cases need care.", "medium"),
        ],
        [
            M("GLOBIGNORE can...", ["Filter which matches are returned", "Replace PATH", "Disable man", "Format ext4"], 0, "GLOBIGNORE excludes patterns.", "hard"),
            M("Locale collation affects character ranges like `[a-z]` because...", ["Ranges follow locale order", "Ranges are always ASCII only everywhere", "Globs ignore locale always", "Kernels ban ranges"], 0, "Locales change range meaning.", "hard"),
            T("`dotglob` makes `*` include dotfiles (except . and ..).", True, "dotglob includes hidden.", "hard"),
            M("Nocaseglob makes matches...", ["Case-insensitive (bash)", "Always regex", "Root-only", "Network-only"], 0, "Case folding for globs.", "hard"),
            M("Escaping: `\\*` yields...", ["A literal asterisk for expansion rules", "Recursive delete", "Home", "A pipe"], 0, "Backslash escapes specials.", "hard"),
            M("Why `rm -- *.txt` still needs care?", ["Globs expand before rm; huge lists can overflow", "rm ignores --", "Globs require root", "txt cannot be removed"], 0, "Expansion list length limits.", "hard"),
            M("`find {d} -name '*.log'` vs shell glob...", ["find walks trees; shell expands one level pattern", "Identical always", "find cannot match names", "Shell always recurses"], 0, "Different expansion engines.", "hard"),
            T("extglob enables !(pattern) and other advanced bash globs.", True, "extglob adds extended forms.", "hard"),
            M("Security: untrusted filenames with globs can...", ["Break scripts via unexpected matches", "Only improve safety", "Disable networking", "Set clocks"], 0, "Hostile names exploit careless globs.", "hard"),
            M("Prefer `find -print0 | xargs -0` over naive `*` when...", ["Names may contain spaces/newlines", "All names are ASCII single words guaranteed", "Using only echo", "Reading man"], 0, "Null-delimited pipelines are safer.", "hard"),
        ],
    ),
    "ftype": (
        [
            M("`ls -l` first char `-` usually means...", ["Regular file", "Directory", "Symlink", "Socket"], 0, "- is regular file.", "easy"),
            M("First char `d` means...", ["Device", "Directory", "Door", "Deleted"], 1, "d = directory.", "easy"),
            M("First char `l` means...", ["Lock", "Symbolic link", "Long file", "Library"], 1, "l = symlink.", "easy"),
            T("`file {f}` guesses a file's type from content/headers.", True, "file probes contents.", "easy"),
            M("A hard link...", ["Is another name for the same inode", "Always points across filesystems", "Stores a path string only", "Is a directory always"], 0, "Hard links share inodes.", "easy"),
            M("A symlink stores...", ["A path text pointing elsewhere", "A full inode duplicate always", "Only permissions", "Only owners"], 0, "Symlinks hold a path.", "easy"),
            M("`test -d {d}` checks...", ["{d} is a directory", "{d} is executable only", "{d} is empty only", "{d} is a zip"], 0, "-d directory test.", "easy"),
            M("`test -L {f}` / `-h` checks...", ["Symlink", "Hard link count only", "Size", "Owner"], 0, "-h/-L symlink tests.", "easy"),
            T("Directories are special files that hold entries.", True, "Dirs map names to inodes.", "easy"),
            M("FIFO/pipe type letter is often...", ["p", "c", "b", "s"], 0, "p = named pipe.", "easy"),
        ],
        [
            M("Hard links generally cannot...", ["Cross filesystems / link directories (normally)", "Share data", "Have names", "Have permissions"], 0, "Hard links are same-FS file names.", "medium"),
            M("Breaking a symlink (dangling) means...", ["Target path does not exist", "Inode was duplicated", "umask flipped", "PATH cleared"], 0, "Dangling = missing target.", "medium"),
            T("`stat {f}` shows inode metadata including links and mode.", True, "stat is the metadata tool.", "medium"),
            M("`ln {f} {t}` without -s creates...", ["A hard link", "A symlink", "A zip", "A mount"], 0, "Default ln is hard link.", "medium"),
            M("`ln -s {f} {t}` creates...", ["A symlink named {t}", "A hard link only", "A copy of bytes always", "A user"], 0, "-s = symbolic.", "medium"),
            M("Device files `c`/`b` represent...", ["Character/block devices", "Only symlinks", "Only dirs", "Only sockets"], 0, "Device nodes.", "medium"),
            M("Socket type `s` is used for...", ["IPC sockets in the filesystem namespace", "Only tar", "Only man", "Only make"], 0, "Unix domain sockets.", "medium"),
            T("Removing a hard link name decreases nlink; data remains until nlink 0 and unused.", True, "Last link frees data.", "medium"),
            M("`readlink {t}` prints...", ["The symlink text target", "Always canonical abs path only", "Owner", "umask"], 0, "readlink shows link text.", "medium"),
            M("Why `cp -a` preserves types better than naive cp?", ["It preserves symlinks/attrs more carefully", "It deletes targets", "It disables modes", "It skips dirs"], 0, "Archive mode preserves structure.", "medium"),
        ],
        [
            M("Following vs not following symlinks matters for...", ["Backup, chmod -R, and find policies", "Only font choice", "Only PS1", "Only man section"], 0, "Traversal policy is a design choice.", "hard"),
            M("Hard-linking directories is restricted because...", ["Filesystem cycles / complexity", "Dirs cannot have names", "Inodes cannot be shared ever", "POSIX bans files"], 0, "Cycles and tools assume tree dirs.", "hard"),
            T("`O_NOFOLLOW` open flags avoid opening through symlinks.", True, "Safe open patterns exist.", "hard"),
            M("Across bind mounts, hard links...", ["Still require same underlying filesystem", "Always work across NFS always", "Become symlinks", "Clear uid"], 0, "Hard links need one FS.", "hard"),
            M("Sparse files look small with `du` but...", ["May have large logical size via holes", "Cannot exist", "Are always dirs", "Are always sockets"], 0, "Holes affect apparent size.", "hard"),
            M("`file` can mis-detect when...", ["Content is ambiguous or truncated", "Always for .txt", "Names end in .sh", "umask is 022"], 0, "Heuristics are imperfect.", "hard"),
            M("Replace-through-symlink hazards: writing via link can...", ["Modify the target unexpectedly", "Only create hard links", "Disable SELinux always", "Clear PATH"], 0, "Know whether tools follow links.", "hard"),
            T("inode reuse after unlink can surprise long-lived FDs still open.", True, "Unlinked-but-open files persist.", "hard"),
            M("Detecting hard-linked duplicates often uses...", ["Same device+inode from stat", "Only basename equality", "Only size", "Only mtime"], 0, "dev+ino identifies hard links.", "hard"),
            M("In labs, classifying type before acting prevents...", ["Treating a symlink/dir as a regular file by mistake", "Learning", "Using ls", "Reading man"], 0, "Type checks gate safe ops.", "hard"),
        ],
    ),
    "rpath": (
        [
            M("`realpath {f}` typically prints...", ["A canonical absolute path", "Only the basename", "Owner uid", "umask"], 0, "realpath canonicalizes.", "easy"),
            M("`readlink {t}` without -f prints...", ["Symlink text (may be relative)", "Always physical abs", "Process list", "Man page"], 0, "Plain readlink is the stored text.", "easy"),
            T("Canonical paths help compare whether two names are the same file.", True, "Normalization aids identity checks.", "easy"),
            M("`.` components in paths are removed by realpath because...", ["They are redundant", "They are illegal", "They mean home", "They mean root"], 0, ". is current segment noise.", "easy"),
            M("`..` in realpath walks...", ["To the parent of the prior component", "To $HOME", "To /tmp always", "Nowhere"], 0, ".. climbs one level.", "easy"),
            M("If `{t}` is a symlink to `{f}`, realpath of `{t}` usually...", ["Resolves toward {f}'s canonical path", "Prints only {t}", "Deletes {f}", "Prints umask"], 0, "Resolution follows links.", "easy"),
            T("`readlink -f` (GNU) often behaves like a realpath-style resolve.", True, "-f follows to canonical.", "easy"),
            M("Why resolve before comparing strings?", ["Symlink/. /.. spellings differ", "Strings are always equal", "Kernel bans compares", "Only for zip"], 0, "Spellings vary.", "easy"),
            M("`realpath -e {f}` (GNU) fails if...", ["Final path does not exist", "Path exists", "Path is absolute", "Path is short"], 0, "-e requires existence.", "easy"),
            M("Relative symlink `../{f}` is relative to...", ["The directory containing the link", "Your shell cwd only always", "$HOME only", "/ only"], 0, "Link-relative resolution.", "easy"),
        ],
        [
            M("Logical vs physical cwd (`pwd -L` vs `-P`) differs when...", ["cwd path includes symlinks", "You are root", "umask is 0", "PATH is empty"], 0, "Logical keeps symlink path.", "medium"),
            M("Broken symlink: realpath often...", ["Errors (unless a mode allows missing)", "Creates the target", "Formats disk", "Ignores always successfully"], 0, "Cannot resolve missing targets.", "medium"),
            T("realpath of `/` is `/`.", True, "Root is canonical.", "medium"),
            M("Multiple symlinks in a chain are...", ["Followed until a final non-link (with limits)", "Ignored after the first", "Converted to hard links", "Stored in PATH"], 0, "Chains resolve step by step.", "medium"),
            M("Looping symlinks cause...", ["Detection/error, not infinite success", "Faster resolves", "Auto repair", "Kernel panic always"], 0, "ELOOP-style failures.", "medium"),
            M("`realpath --relative-to={d} {p}` (GNU) prints...", ["A relative path from {d} to {p}", "Always absolute only", "Only basename", "Owner"], 0, "Relative-to helper.", "medium"),
            M("Scripts should quote `\"$(realpath \"$1\")\"` because...", ["Paths can contain spaces", "realpath bans quoting", "It disables glob", "It sets uid"], 0, "Word-splitting risk.", "medium"),
            T("Not all Unixes ship identical realpath flags; check man.", True, "Portability varies.", "medium"),
            M("Resolving inside chroot shows paths...", ["Relative to the chroot view", "Always host true paths", "Only network paths", "Only $HOME"], 0, "Namespace matters.", "medium"),
            M("Prefer realpath when installing symlinks so that...", ["Targets are unambiguous later", "umask resets", "man installs", "make becomes optional"], 0, "Stable targets reduce surprises.", "medium"),
        ],
        [
            M("TOCTOU: realpath then open without care can still race if...", ["The path is replaced between check and use", "umask is 022", "You use abs paths", "You read man"], 0, "Resolve+open atomically when security matters.", "hard"),
            M("Canonicalization across mount namespaces may differ because...", ["Different mounts/views per process", "inodes cannot exist", "PATH is ignored", "Symlinks are banned"], 0, "Namespaces remap visibility.", "hard"),
            T("Lexical path join without filesystem checks can escape a supposed root.", True, "Need realpath confinement carefully.", "hard"),
            M("`O_PATH`/`openat` patterns help when...", ["Resolving relative to a directory FD safely", "Only printing help", "Only zipping", "Only coloring ls"], 0, "FD-relative APIs reduce races.", "hard"),
            M("Why backups may store link text not realpath?", ["Preserve user-intended relative links", "Always wrong", "Faster CPU only", "Required by zip"], 0, "Intent vs canonical tradeoff.", "hard"),
            M("Windows WSL path translation vs Linux realpath...", ["Can disagree; do not mix casually", "Always identical", "Replace each other", "Disable symlinks"], 0, "Hybrid environments differ.", "hard"),
            M("Maximum symlink nest limits exist to...", ["Prevent infinite recursion", "Increase disk space", "Disable man", "Force hard links"], 0, "Safety caps.", "hard"),
            T("Device+inode after resolve is a stronger identity than path strings.", True, "Identity is filesystem object.", "hard"),
            M("In build systems, unclean `..` in deps can...", ["Break reproducibility / confuse caches", "Improve make always", "Clear .PHONY", "Set CC"], 0, "Normalize inputs.", "hard"),
            M("Lab takeaway: print both `readlink` and `realpath` when debugging links because...", ["Text target and final path both matter", "They are always equal", "One deletes the other", "They set permissions"], 0, "Both views teach the bug.", "hard"),
        ],
    ),
    "perm": (
        [
            M("`chmod u+x {s}` does what?", ["Deletes the script", "Adds execute for the owner", "Adds to PATH", "chown to root"], 1, "u+x = owner execute.", "easy"),
            M("Why run `./{s}` instead of `{s}`?", ["Dot-slash required by chmod", "`.` is usually not on PATH", "Only root can run bare names", "Symlinks cannot execute"], 1, "cwd usually omitted from PATH.", "easy"),
            T("umask masks permission bits off when creating new files/dirs.", True, "umask clears bits from creation mode.", "easy"),
            M("Mode 600 typically means...", ["Everyone rw", "Owner rw; group/other none", "Execute only for others", "Sticky bit only"], 1, "600 is rw-------.", "easy"),
            M("r/w/x bits for a directory: x means...", ["Search/enter the directory", "Only read file bytes", "Only delete filesystem", "Only symlink"], 0, "Dir execute is traverse.", "easy"),
            M("`chmod 755 {s}` is commonly...", ["rwxr-xr-x", "rw-------", "r--r--r--", "rwxrwxrwx"], 0, "755 = owner rwx, others rx.", "easy"),
            T("`ls -l` shows permission bits in the mode string.", True, "Mode is in long listing.", "easy"),
            M("PATH lists...", ["Directories searched for commands", "Only man pages", "Only zip files", "Only kernels"], 0, "PATH is command search path.", "easy"),
            M("`which` / `command -v` helps find...", ["Where a command resolves on PATH", "Disk temperature", "umask only", "inode of /"], 0, "Locate executables.", "easy"),
            M("Private keys should often be mode...", ["600 or stricter", "777", "666", "111"], 0, "Secrets stay owner-only.", "easy"),
        ],
        [
            M("umask 022 with create mode 666 yields file mode near...", ["644", "777", "000", "111"], 0, "022 masks write for group/other.", "medium"),
            M("Directory sticky bit (t) on /tmp means...", ["Only file owner (and dir owner/root) can delete their files", "Everyone can delete anything", "No one can create files", "Disables exec"], 0, "Sticky protects others' files.", "medium"),
            T("setuid bits on executables can run as file owner (security-sensitive).", True, "setuid elevates carefully.", "medium"),
            M("`chmod -R` is dangerous because...", ["It recurses into trees / may hit symlinks depending on tool", "It never changes modes", "It clears disks", "It requires offline"], 0, "Recursive chmod scope surprises.", "medium"),
            M("Executable scripts need...", ["A shebang or explicit interpreter + execute bit (policy varies)", "Only 000 mode", "To be named .txt", "Root ownership always"], 0, "Interp + +x common.", "medium"),
            M("Putting `.` on PATH is discouraged because...", ["Cwd trojans can hijack command names", "It speeds nothing harmful", "It breaks ls", "POSIX requires it"], 0, "Security: avoid cwd on PATH.", "medium"),
            M("`chown {u} {f}` changes...", ["Ownership toward {u}", "Only mtime", "Only inode number", "Only symlink text"], 0, "chown sets owner.", "medium"),
            T("ACLs can grant finer permissions beyond ugo bits.", True, "ACLs extend POSIX mode.", "medium"),
            M("Group-writable dirs for teams often use...", ["Shared group + setgid bit patterns", "777 on /", "Disabling PATH", "Sticky on every file"], 0, "setgid dirs keep group.", "medium"),
            M("`umask` in a subshell...", ["Does not change parent umask", "Always changes login umask permanently", "Formats disk", "Clears PATH"], 0, "umask is process state.", "medium"),
        ],
        [
            M("Capability / SELinux labels can deny access even when mode bits allow because...", ["MAC policies override DAC allowances", "Modes are ignored always", "Root is banned", "PATH overrides MAC"], 0, "MAC is another layer.", "hard"),
            M("Race on `chmod` after `creat` without safe flags can briefly expose...", ["Over-permissive modes before chmod", "Nothing ever", "Only man pages", "Only zip"], 0, "Use open modes carefully.", "hard"),
            T("NFS root_squash can map remote root to nobody, surprising permissions.", True, "Remote root is often squashed.", "hard"),
            M("Interpreting `ls -l` symlink line shows mode of...", ["The symlink itself (often 777) while access uses target rules", "Always the target mode in the l line only", "Only umask", "Only ACL deny"], 0, "Symlink modes are special.", "hard"),
            M("PATH hijack defenses include...", ["Absolute paths for privileged scripts + safe PATH", "Always `.` first on PATH", "world-writable ~/bin first", "Disable hashing only"], 0, "Control search order.", "hard"),
            M("`newgrp` / supplementary groups matter when...", ["Access needs a group you have but not effective yet", "umask is 022", "Files are 644", "You use pwd"], 0, "Group membership is nuanced.", "hard"),
            M("Immutable attributes (chattr +i) can block...", ["Even root writes until cleared (Linux)", "Only network", "Only man", "Only make"], 0, "Attrs beyond mode.", "hard"),
            T("Default ACL masks interact with umask/group bits in subtle ways.", True, "ACL mask is a gotcha.", "hard"),
            M("Containers may show modes that...", ["Work inside but map oddly on mounted host volumes", "Always match host uids perfectly", "Ignore execute", "Disable symlinks"], 0, "Uid mapping issues.", "hard"),
            M("Hardening takeaway for `{s}`: ...", ["Least privilege modes + safe PATH + no secrets in world-readable files", "chmod 777 everything", "Disable updates", "Skip reviews"], 0, "Defense in depth.", "hard"),
        ],
    ),
    "dot": (
        [
            M("Dotfiles are typically named like...", [".bashrc / .config/...", "only README.md", "only /etc/passwd", "only Makefile"], 0, "Leading dot hides by default.", "easy"),
            M("`ls` without `-a` usually hides...", ["Dotfiles", "All executables", "All directories", "All symlinks"], 0, "Default ls skips many dot names.", "easy"),
            T("Many tools store user config under ~/.config (XDG).", True, "XDG config home is common.", "easy"),
            M("`.gitignore` is a...", ["Dotfile that can configure Git ignore rules", "Kernel module", "man section 9", "Block device"], 0, "Project dotfiles exist too.", "easy"),
            M("Editing `~/.bashrc` affects...", ["Interactive bash startup (typically)", "The kernel scheduler", "Only cron on Linux always", "Only zip"], 0, "Shell rc files configure shells.", "easy"),
            M("`cd ~` goes to...", ["Your home directory", "/", "/tmp", "Git root always"], 0, "~ is home.", "easy"),
            T("Dot directories like `.git` hold tool state.", True, "Hidden dirs store metadata.", "easy"),
            M("XDG `~/.cache` is meant for...", ["Disposable caches", "Only SSH keys", "Only passwords", "Only kernels"], 0, "Cache vs config vs data.", "easy"),
            M("Copying a project with `cp -r` may miss...", ["Nothing if you include hidden; naive tools sometimes skip dots", "All regular files always", "Only Makefiles", "Only READMEs"], 0, "Watch hidden inclusion.", "easy"),
            M("`mv {f} .{f}` ...", ["Renames to a hidden name", "Deletes permanently", "Sets uid", "Mounts nfs"], 0, "Leading dot hides.", "easy"),
        ],
        [
            M("`ls -a` vs `ls -A` difference often is...", ["-A hides . and .. but shows other dots", "No difference ever", "-A shows only sockets", "-a deletes dots"], 0, "-A omits . and ..", "medium"),
            M("`$XDG_CONFIG_HOME` defaults to...", ["~/.config when unset", "/etc always", "/tmp", "/var/log"], 0, "XDG default config home.", "medium"),
            T("Login vs interactive vs non-interactive shells source different files.", True, "bash startup is layered.", "medium"),
            M("Putting secrets in `~/.bashrc` is risky because...", ["It may be readable/shared/backed up carelessly", "bash cannot read it", "It disables PATH", "It clears umask"], 0, "Prefer restricted secret stores.", "medium"),
            M("Dotfile managers sync...", ["Config repos into home carefully", "Only /boot", "Only man db", "Only zip central dirs"], 0, "Manage configs as code.", "medium"),
            M("`chmod 600 ~/.ssh/id_rsa` matters because...", ["SSH refuses overly open private keys", "SSH requires 777", "It sets PATH", "It disables keys"], 0, "Key permissions are checked.", "medium"),
            M("Project-local `.env` vs home dotfiles...", ["Different scopes: project secrets vs user prefs", "Identical always", "Both are kernels", "Both must be executable"], 0, "Scope separation.", "medium"),
            T("`rsync -a` can include dotfiles when copying trees.", True, "Archive mode includes them.", "medium"),
            M("`DIR/*` skipping dots means backups might...", ["Miss critical .env/.git configs unless handled", "Always include them", "Delete them", "Compress them only"], 0, "Explicit include rules.", "medium"),
            M("Troubleshooting 'config ignored' first check...", ["Which file the tool actually reads + precedence", "Only CPU temp", "Only make -j", "Only zip -l"], 0, "Precedence docs matter.", "medium"),
        ],
        [
            M("XDG Base Directory Spec separates...", ["config, data, cache, state", "Only PATH entries", "Only man sections", "Only GIDs"], 0, "Four+ homes with roles.", "hard"),
            M("Systemd user units often live under...", ["~/.config/systemd/user", "/proc only", "/boot only", "~/.cache only"], 0, "User unit paths.", "hard"),
            T("Some GUIs still use legacy ~/.<app> instead of XDG.", True, "Legacy paths persist.", "hard"),
            M("Secure deletion of a dot secret should consider...", ["Backups, shell history, and editor swap files", "Only rm once without sync", "Only chmod +x", "Only renaming"], 0, "Secrets leak into side channels.", "hard"),
            M("NFS home dotfiles can cause...", ["Latency and lock issues on frequent shell starts", "Faster always", "No side effects", "Disabled bash"], 0, "Network homes hurt rc churn.", "hard"),
            M("Conditional includes in bashrc based on interactive tests prevent...", ["Breaking scp/sftp with stdout noise", "All networking", "man pages", "umask"], 0, "Guard interactive-only code.", "hard"),
            M("Config precedence wars (env > flags > files) require...", ["Reading the tool's order docs", "Guessing", "Always sudo", "Deleting configs"], 0, "Documented precedence.", "hard"),
            T("Storing machine-local paths in shared dotfiles breaks portability.", True, "Parameterize hosts.", "hard"),
            M("Homedir encryption + mistimed mounts can make apps...", ["Create fresh empty configs on the blank mount", "Always wait quietly forever", "Disable ls", "Fix mounts"], 0, "Empty home illusions.", "hard"),
            M("Lab habit: before editing a dotfile...", ["Backup + know which shell session will load it", "chmod 777 first", "Delete $HOME", "Disable networking"], 0, "Safe edit loop.", "hard"),
        ],
    ),
    "ps": (
        [
            M("`ps` shows...", ["A snapshot of processes", "Only disk usage", "Only mounts", "Only man pages"], 0, "ps lists processes.", "easy"),
            M("`kill PID` by default sends...", ["SIGTERM", "SIGKILL", "SIGSTOP", "SIGINT only"], 0, "Default is TERM.", "easy"),
            T("SIGKILL (9) cannot be caught; use as last resort.", True, "KILL is non-catchable.", "easy"),
            M("`ps aux` / `ps -ef` styles are for...", ["Richer process listings", "Formatting disks", "Setting umask", "Zip listing"], 0, "Common full listings.", "easy"),
            M("PID means...", ["Process ID", "Parent inode", "Permission ID", "Pipe ID"], 0, "PID identifies a process.", "easy"),
            M("PPID means...", ["Parent process ID", "Primary PATH id", "Pretty print id", "Package id"], 0, "Parent PID.", "easy"),
            T("Ctrl-C typically sends SIGINT to the foreground process group.", True, "Keyboard interrupt signal.", "easy"),
            M("`kill -l` lists...", ["Signal names/numbers", "Logged-in users only", "Open files only", "Mounts"], 0, "Signal catalog.", "easy"),
            M("`pgrep {m}` helps find...", ["PIDs matching a name pattern", "Disk labels", "Only zombies always", "Man sections"], 0, "Name to PID.", "easy"),
            M("A zombie process has...", ["Exited but not yet waited on by parent", "Infinite CPU always", "No PID", "Only network sockets"], 0, "Zombies await reaping.", "easy"),
        ],
        [
            M("`kill -15` vs `kill -9`...", ["15 TERM allows cleanup; 9 KILL forces", "Identical always", "15 is stronger", "9 is catchable"], 0, "Prefer TERM then escalate.", "medium"),
            M("`ps -o pid,ppid,cmd` customizes...", ["Output columns", "Signals", "umask", "PATH"], 0, "Format strings.", "medium"),
            T("`pkill` can signal processes by name (careful!).", True, "Name-based signaling.", "medium"),
            M("Process groups and sessions matter for...", ["Job control and signal delivery", "Only zip", "Only make colors", "Only man"], 0, "Signals target groups.", "medium"),
            M("`top`/`htop` differ from ps mainly by...", ["Interactive continuous view", "Being unable to show PID", "Disabling kill", "Requiring offline"], 0, "Live monitors.", "medium"),
            M("Orphaned processes are typically...", ["Reparented (often to init/systemd)", "Deleted from disk", "Converted to files", "Hidden from ps"], 0, "Reparenting.", "medium"),
            M("`nice`/`renice` adjust...", ["CPU scheduling priority", "File modes", "Symlink text", "Man sections"], 0, "Niceness.", "medium"),
            T("Sending signals you do not own usually fails with EPERM.", True, "Permission checks apply.", "medium"),
            M("`/proc/{n}/status` on Linux exposes...", ["Process state details", "Only ZIP headers", "Only make rules", "Only bash aliases"], 0, "procfs introspection.", "medium"),
            M("Before kill -9 on a DB, prefer...", ["Graceful TERM + check logs", "Immediate -9 always", "rm data dir", "Disable disks"], 0, "Graceful shutdown first.", "medium"),
        ],
        [
            M("SIGSTOP vs SIGTSTP...", ["STOP is unblockable; TSTP is terminal stop (job control)", "Identical", "Both are kill", "Both ignore tty"], 0, "Different stop signals.", "hard"),
            M("Kill process groups with...", ["Negative PID / kill -- -PGID patterns", "Only kill 1 always", "Only pkill -9 $$", "chmod"], 0, "Group-targeted kills.", "hard"),
            T("Threads may share a TGID while having different TIDs (Linux).", True, "Thread vs process ids.", "hard"),
            M("ptrace/debugger attaches can make kill behavior...", ["Interact differently / stop for tracing", "Impossible", "Always reboot", "Clear logs"], 0, "Tracing changes state.", "hard"),
            M("cgroup freezer / OOM killer are...", ["Other ways the system stops workloads", "Shell aliases", "man macros", "zip methods"], 0, "Beyond kill(1).", "hard"),
            M("Zombie accumulation often indicates...", ["Parent not wait()ing", "Too much RAM always", "Bad umask", "Missing man"], 0, "Reap children.", "hard"),
            M("Container PID namespaces mean host `kill`...", ["May not see/kill guest PIDs the same way", "Always works with guest PIDs", "Disables namespaces", "Sets CAP_SYS"], 0, "Namespaces isolate PIDs.", "hard"),
            T("SIGHUP historically hung up terminals; daemons may reload on HUP.", True, "HUP reused for reload.", "hard"),
            M("Safe automation uses...", ["Explicit PIDs/files + TERM timeouts + escalation policy", "pkill -9 -f .", "killall -9", "Random PIDs"], 0, "Controlled stop recipes.", "hard"),
            M("Lab skill: map symptoms -> `ps`/`pgrep` -> signal choice.", ["Yes: observe then act", "No: always -9 first", "No: reboot only", "No: chmod 777"], 0, "Observe-signal loop.", "hard"),
        ],
    ),
    "job": (
        [
            M("`command &` runs command...", ["In the background", "Only as root", "With nice -20 always", "Detached from disk"], 0, "& backgrounds.", "easy"),
            M("`jobs` lists...", ["Active jobs of the shell", "Cron for all users", "Kernel threads only", "Zip members"], 0, "Shell job table.", "easy"),
            T("Ctrl-Z typically sends SIGTSTP and suspends the foreground job.", True, "Terminal stop.", "easy"),
            M("`bg` resumes a suspended job...", ["In the background", "As a new login", "Only with -9", "In another user"], 0, "bg continues in background.", "easy"),
            M("`fg` brings a job...", ["To the foreground", "To init", "To cron", "To zip"], 0, "fg foregrounds.", "easy"),
            M("Job ids often look like...", ["%1, %2, ...", "Only PIDs", "Only inodes", "Only ports"], 0, "%n job specs.", "easy"),
            T("A foreground job receives terminal keyboard signals.", True, "TTY signals go foreground group.", "easy"),
            M("`disown` can...", ["Remove a job from the shell's job table", "Unlink files", "Clear umask", "Format disks"], 0, "disown detaches from job control.", "easy"),
            M("Why background a long `make`?", ["Keep using the shell for other commands", "Speed the CPU clock", "Disable errors", "Skip deps"], 0, "Concurrency of interactive use.", "easy"),
            M("`jobs -l` also shows...", ["PIDs", "Only names", "Only exit codes forever", "Mounts"], 0, "Long job listing includes PIDs.", "easy"),
        ],
        [
            M("`fg %2` foregrounds...", ["Job number 2", "PID 2 always", "Nice 2", "TTY 2"], 0, "%2 is job id.", "medium"),
            M("Background jobs writing to the terminal may...", ["Be stopped with SIGTTOU depending on tty settings", "Always print freely forever", "Crash the kernel", "Clear PATH"], 0, "TTY output stops possible.", "medium"),
            T("`set -m` enables monitor mode / job control in scripts (bash).", True, "Monitor mode for jobs.", "medium"),
            M("Pipeline job control treats...", ["The pipeline as a related process group (typically)", "Each command as unrelated always", "Only the last PID", "Only the first file"], 0, "Pipelines are job units.", "medium"),
            M("`wait %1` waits for...", ["That job to finish", "All cron jobs", "Network only", "man rebuild"], 0, "wait on job spec.", "medium"),
            M("SIGHUP on shell exit can kill background jobs unless...", ["nohup/disown/systemd-run etc.", "They are named .sh", "umask is 0", "They use echo"], 0, "HUP policies.", "medium"),
            M("`nohup cmd &` commonly...", ["Ignores HUP and often redirects output to nohup.out", "Disables all signals", "Requires root", "Clears jobs"], 0, "Classic detach pattern.", "medium"),
            T("Job control is tied to interactive shells with a controlling terminal.", True, "Needs a tty context.", "medium"),
            M("Suspend vs terminate...", ["Suspend keeps state; terminate ends", "Identical", "Suspend is -9", "Terminate is Ctrl-Z"], 0, "Different intents.", "medium"),
            M("Finding a lost background PID: use...", ["jobs -l / ps / pgrep", "Only ls", "Only chmod", "Only tar"], 0, "Cross-check job table and ps.", "medium"),
        ],
        [
            M("Orphaned process groups after shell death...", ["May continue under new parent depending on setup", "Always vanish instantly", "Become directories", "Hold man locks"], 0, "Lifecycle continues.", "hard"),
            M("tmux/screen sessions differ from `&` because...", ["They provide detachable terminals/sessions", "They disable processes", "They replace kill", "They clear PATH"], 0, "Session persistence.", "hard"),
            T("Modern preference for long services is often systemd/user units over raw nohup.", True, "Supervisors beat ad-hoc &.", "hard"),
            M("Race: `bg` then immediate `kill %1` can fail if...", ["Job state changed / id reused patterns", "PIDs are 32-bit", "umask wrong", "man missing"], 0, "Job ids are ephemeral.", "hard"),
            M("Pipeline with `cmd1 | cmd2 &` backgrounds...", ["The whole pipeline job", "Only cmd1", "Only cmd2", "Nothing"], 0, "One job for the pipe.", "hard"),
            M("stty tostop influences...", ["Whether background writers get SIGTTOU", "File modes", "Symlink resolution", "make -j"], 0, "TTY stop policy.", "hard"),
            M("Non-interactive CI shells often...", ["Lack job control; use wait/PIDs explicitly", "Always support fg/bg", "Require Ctrl-Z", "Need disown"], 0, "CI != interactive.", "hard"),
            T("Process group leadership affects which PID receives tty signals.", True, "Foreground PGID matters.", "hard"),
            M("Debugging stuck 'Stopped' jobs: check...", ["tty tostop + attempts to read/write terminal", "Only CPU gov", "Only zip", "Only ACL"], 0, "Stopped often means tty policy.", "hard"),
            M("Lab takeaway: prefer explicit logging redirects when using `&`.", ["Yes: avoid buried tty stops / lost output", "No: print raw to tty always", "No: skip redirects", "No: use -9"], 0, "Redirect background I/O.", "hard"),
        ],
    ),
    "pipe": (
        [
            M("In `cmd1 | cmd2`, what happens?", ["cmd2 stdout becomes cmd1 stdin", "cmd1 stdout becomes cmd2 stdin", "Both write only to disk", "Pipe deletes cmd1"], 1, "Left stdout feeds right stdin.", "easy"),
            M("`grep -i error {g}` means...", ["Exact lowercase only", "Case-insensitive match for error", "Invert match", "Count only"], 1, "-i ignores case.", "easy"),
            T("`command > {f}` overwrites; `command >> {f}` appends.", True, "> truncates; >> appends.", "easy"),
            M("`2>&1` typically means...", ["Ignore errors", "Send stderr to the same place as stdout", "Run two shells", "Disable pipes"], 1, "Merge stderr into stdout dest.", "easy"),
            M("`cat {f} | cmd` is often replaceable by...", ["`cmd < {f}` or `cmd {f}` if supported", "Only tee", "Only zip", "Only sudo"], 0, "Useless cat pattern.", "easy"),
            M("`tee {f}` copies stdin to...", ["Stdout and {f}", "Only stderr", "Only /dev/null", "Only man"], 0, "tee tees.", "easy"),
            T("Pipes connect processes, not temporary disk files by default.", True, "In-memory/kernel pipe buffers.", "easy"),
            M("`cmd > {f} 2>&1` redirects...", ["Both stdout and stderr to {f}", "Only stderr", "Only stdout leaving stderr", "Neither"], 0, "Order merges then writes.", "easy"),
            M("`xargs` turns stdin items into...", ["Command arguments", "Signals", "Users", "Mounts"], 0, "xargs builds argv.", "easy"),
            M("`cmd < {f}` connects...", ["{f} to cmd stdin", "{f} to stdout", "stderr only", "PATH"], 0, "Input redirection.", "easy"),
        ],
        [
            M("`cmd 2>{g} >{f}` vs `>{f} 2>&1` differ because...", ["Redirection order matters", "Order never matters", "Both identical always", "Shell ignores 2>"], 0, "Order is significant.", "medium"),
            M("`|&` (bash) pipes...", ["Stdout and stderr together", "Only signals", "Only exit codes", "Only fds 3+"], 0, "|& = 2>&1 |", "medium"),
            T("`set -o pipefail` makes pipelines fail if any stage fails (bash).", True, "pipefail is not default in bash.", "medium"),
            M("`xargs -0` pairs with...", ["NUL-delimited input for safe names", "Only JSON", "Only YAML", "Only tabs"], 0, "Null-safe xargs.", "medium"),
            M("`cmd1 | cmd2` exit status without pipefail is often...", ["That of cmd2", "Always cmd1", "Always 0", "Average of both"], 0, "Last command status by default.", "medium"),
            M("`grep -v` inverts match so you can...", ["Filter out lines", "Enable color only", "Sort", "chmod"], 0, "Invert match.", "medium"),
            M("Here-string `cmd <<< \"$var\"` feeds...", ["var as stdin", "var as argv only", "stderr", "PATH"], 0, "Here-string stdin.", "medium"),
            T("`/dev/null` discards data redirected into it.", True, "Bit bucket.", "medium"),
            M("Deadlock risk in complex fd redirection appears when...", ["Processes wait on each other for pipes/FIFOs", "Using only echo", "Using pwd", "Reading man"], 0, "Careful with bidirectional FIFOs.", "medium"),
            M("`stdbuf`/`pv` sometimes help when...", ["Pipeline buffering hides progress", "Disabling CPU", "Clearing umask", "Naming hosts"], 0, "Buffering control.", "medium"),
        ],
        [
            M("SIGPIPE happens when...", ["Writing to a pipe with no readers", "Reading /etc/passwd", "Calling pwd", "Setting PS1"], 0, "Writer gets SIGPIPE.", "hard"),
            M("`xargs -P` parallel runs can break tools that...", ["Are not concurrency-safe on shared outputs", "Only print help", "Use abs paths", "Read man"], 0, "Parallelism needs safe sinks.", "hard"),
            T("Process substitution `<(cmd)` exposes cmd output as a filename.", True, "<( ) is bash process subst.", "hard"),
            M("`exec >{f} 2>&1` in a script...", ["Redirects the rest of the shell's stdout/stderr", "Only affects one external cmd", "Disables pipes forever globally for all users", "Clears PATH"], 0, "exec can rebind shell fds.", "hard"),
            M("Atomic replace patterns use `>tmp && mv` because...", ["Avoid readers seeing partial files", "Faster always", "Required by POSIX echo", "Disables NFS"], 0, "Publish complete outputs.", "hard"),
            M("Binary data through pipes is fine if...", ["Tools are binary-safe and you avoid newline assumptions", "You always use grep", "You use ls", "You set umask 0"], 0, "Text tools != binary safe.", "hard"),
            M("Closing unused pipe ends in custom programs prevents...", ["Hangs waiting for EOF", "All networking", "man access", "make"], 0, "EOF needs all writers closed.", "hard"),
            T("`coproc` (bash) sets up async pipes to a coprocess.", True, "Advanced bidirectional async.", "hard"),
            M("Why `cat huge | grep` may be slower than `grep huge`?", ["Extra process + copying", "grep cannot read files", "Pipes encrypt", "Kernels ban file grep"], 0, "Avoid useless cats.", "hard"),
            M("Lab habit: sketch fd wiring before complex `2>&1 | tee`.", ["Yes: order and merges confuse", "No: trial only", "No: skip stderr", "No: always -9"], 0, "Draw the fds.", "hard"),
        ],
    ),
    "sort": (
        [
            M("`sort {f}` sorts...", ["Lines of {f}", "Only filenames in PATH", "Signals", "Users by uid only"], 0, "sort orders lines.", "easy"),
            M("`uniq` usually expects...", ["Adjacent duplicate lines (often after sort)", "Random order always fine", "Binary only", "Zip only"], 0, "uniq collapses neighbors.", "easy"),
            T("`sort | uniq` is a common unique-lines pipeline.", True, "Sort then uniq.", "easy"),
            M("`cut -d, -f1 {f}` takes...", ["Field 1 with comma delimiter", "First byte only always", "Last line", "Inode"], 0, "cut selects fields.", "easy"),
            M("`sort -n` sorts...", ["Numerically", "By file size on disk only", "By mtime only", "Randomly"], 0, "Numeric sort.", "easy"),
            M("`sort -r` ...", ["Reverses order", "Removes duplicates", "Recurses dirs", "Rewrites PATH"], 0, "Reverse.", "easy"),
            T("`uniq -c` prefixes counts of adjacent duplicates.", True, "Count mode.", "easy"),
            M("`cut -c1-3` selects...", ["Characters 1-3", "Fields 1-3 always", "Lines 1-3", "PIDs"], 0, "Character ranges.", "easy"),
            M("To unique without caring about adjacent requirement use...", ["`sort -u`", "Only uniq alone on random", "chmod", "pwd"], 0, "sort -u unique sorts.", "easy"),
            M("`sort -k2 {f}` sorts by...", ["Key starting at field 2", "Only filename", "Only inode", "Only mode"], 0, "Key fields.", "easy"),
        ],
        [
            M("`sort -t: -k3,3n /etc/passwd` sorts by...", ["UID numeric with : delimiter", "Username only", "Shell only", "GECOS only"], 0, "Field+numeric keys.", "medium"),
            M("`uniq -d` shows...", ["Only duplicated adjacent lines", "All unique lines", "Only empty", "Only numbers"], 0, "Duplicate reporters.", "medium"),
            T("`LC_ALL=C sort` often gives byte-wise stable tooling behavior.", True, "C locale = byte order.", "medium"),
            M("`cut` cannot easily re-order fields like awk because...", ["cut selects; awk is a fuller language", "cut sorts", "cut kills PIDs", "cut mounts"], 0, "Use awk for complex field ops.", "medium"),
            M("`sort -u` vs `sort | uniq` ...", ["Often similar unique outcome; options differ", "Opposite", "One deletes files", "One needs root"], 0, "Related uniqueness tools.", "medium"),
            M("`sort -z` / `uniq -z` deal with...", ["NUL-terminated records", "Only zip", "Only gzip", "Only tar"], 0, "Zero-terminated lines.", "medium"),
            M("Stable sort (`sort -s`) preserves...", ["Order of equal keys", "File modes", "Symlinks", "PIDs"], 0, "Stability.", "medium"),
            T("`comm` compares two sorted files column-wise.", True, "comm needs sorted inputs.", "medium"),
            M("Huge sorts may use...", ["Temp files under $TMPDIR", "Only RAM forever always", "Only /boot", "Only GPU"], 0, "External sort spills.", "medium"),
            M("`paste` / `join` complement cut when...", ["Merging columns/files", "Killing jobs", "Setting umask", "Reading man only"], 0, "Column merge tools.", "medium"),
        ],
        [
            M("Locale-aware sort can surprise because...", ["Letters order differently than byte order", "sort ignores locale always", "Numbers never sort", "UTF-8 banned"], 0, "Locales change collation.", "hard"),
            M("`sort -V` version sort helps with...", ["names like v2 vs v10", "Only PIDs", "Only modes", "Only zip methods"], 0, "Version sorting.", "hard"),
            T("`uniq` without sort can miss duplicates that are not adjacent.", True, "Adjacency requirement.", "hard"),
            M("Memory blow-ups from `sort` huge logs: mitigate by...", ["Filtering first / parallel chunk strategies", "Always loading whole GUI", "Disabling TMPDIR", "Using ls"], 0, "Reduce then sort.", "hard"),
            M("`cut -d ''` empty delim issues show...", ["cut delimiter limitations; use awk sometimes", "cut supports regex always", "cut sorts", "cut kills"], 0, "Know cut limits.", "hard"),
            M("Key ranges `-k2,2` vs `-k2` differ because...", ["End field bounds the key", "Identical always", "One needs root", "One disables locale"], 0, "Specify end field.", "hard"),
            M("Binary safety: classic line tools break on...", ["Embedded NULs / non-text", "ASCII digits", "LF-only text", "Short lines"], 0, "Text model assumptions.", "hard"),
            T("`sort --parallel` can speed CPU-bound sorts when I/O allows.", True, "Parallel sort option.", "hard"),
            M("Deterministic builds want...", ["C locale + explicit sort keys", "Random LANG", "Skip sort", "Rely on ls order"], 0, "Reproducible ordering.", "hard"),
            M("Lab tip: validate with `sort {f} | uniq -c | sort -nr | head`.", ["Yes: frequency triage pattern", "No: random", "No: chmod first", "No: kill"], 0, "Classic triage pipe.", "hard"),
        ],
    ),
    "heredoc": (
        [
            M("A here-doc `cat <<EOF` ... `EOF` feeds...", ["Multi-line stdin to cat", "Only argv", "Only stderr", "Only PATH"], 0, "Here-doc is stdin content.", "easy"),
            M("A here-string `<<<\"hi\"` feeds...", ["A string as stdin", "A file always", "A signal", "A user"], 0, "Here-string one liner.", "easy"),
            T("The closing EOF marker must usually be alone at line start.", True, "Delimiter rules.", "easy"),
            M("`<<'EOF'` quotes the delimiter so that...", ["No parameter expansion in the body", "Expansion always happens", "Body is ignored", "Shell exits"], 0, "Quoted heredoc is literal.", "easy"),
            M("`<<-EOF` allows...", ["Stripping leading tabs from body lines", "Deleting files", "Only zip", "Only root"], 0, "Indented heredoc form.", "easy"),
            M("Here-docs are great for...", ["Embedding multi-line scripts/configs", "Replacing ps", "Formatting disks", "Setting hostname only"], 0, "Inline documents.", "easy"),
            T("Unquoted `<<EOF` expands `$vars` inside the body.", True, "Expansion in unquoted heredoc.", "easy"),
            M("`ssh host <<EOF` ... can run...", ["Remote commands from local heredoc", "Only local ls", "Only man", "Only make"], 0, "Remote stdin scripting.", "easy"),
            M("Common delimiter names are...", ["EOF, END, MARKER...", "Only PID", "Only umask", "Only PATH"], 0, "Any marker word works.", "easy"),
            M("Here-doc vs file redirect...", ["Here-doc needs no temp file for small content", "Here-doc always writes /etc", "Identical to >>", "Requires root"], 0, "Inline without temp.", "easy"),
        ],
        [
            M("If marker is `EOF` but body contains a line `EOF`...", ["It terminates early", "It is ignored always", "It expands PATH", "It sudoes"], 0, "Choose rare markers.", "medium"),
            M("`cat <<EOF >{f}` writes heredoc to...", ["{f}", "Only stdout", "Only stderr", "/dev/null always"], 0, "Redirect the consumer.", "medium"),
            T("`sudo tee {f} <<EOF` is a pattern to write root-owned files.", True, "tee elevates writes.", "medium"),
            M("Tabs vs spaces with `<<-` ...", ["Only tabs are stripped, not spaces", "Spaces strip too always", "Nothing strips", "Only newlines strip"], 0, "Tab-only strip.", "medium"),
            M("Here-string encoding caveats appear with...", ["Trailing newlines / binary", "Only ASCII letters", "Only digits", "Only tabs"], 0, "Strings vs exact bytes.", "medium"),
            M("Expanding command substitutions in heredocs can...", ["Run commands while building stdin", "Only print help", "Disable shell", "Mount nfs"], 0, "Unquoted bodies execute expansions.", "medium"),
            M("YAML/HTML heredocs often use quoted markers to...", ["Avoid accidental `$` expansion", "Force expansion", "Call sudo", "Sort lines"], 0, "Literal bodies.", "medium"),
            T("Some languages' `<<` is not a shell heredoc (context matters).", True, "Syntax collision across langs.", "medium"),
            M("`ssh` + heredoc + interactive prompts can...", ["Deadlock waiting for input", "Always succeed", "Format disks", "Clear known_hosts"], 0, "Avoid mixed interactive.", "medium"),
            M("Debugging: `cat -A <<EOF` helps see...", ["Hidden characters in the body", "PIDs", "umask", "GPU"], 0, "Show nonprintables.", "medium"),
        ],
        [
            M("Pipefail + heredoc fed pipelines still need...", ["Status of each stage considered", "Ignoring exit codes", "Root", "Disabled bash"], 0, "Pipeline status rules apply.", "hard"),
            M("Large heredocs in hot loops can...", ["Bloat script parse/memory vs external files", "Speed infinitely", "Clear disks", "Disable caches"], 0, "Prefer files when huge.", "hard"),
            T("Here-docs are portable across POSIX sh with care on expansions.", True, "Core feature is portable.", "hard"),
            M("`<<EOF` inside functions still...", ["Expands under current shell rules when run", "Is delayed forever", "Requires root", "Ignores quotes"], 0, "Normal expansion timing.", "hard"),
            M("CRLF line endings can break closing markers because...", ["Marker won't match exactly", "Shell ignores markers", "EOF becomes root", "Tabs become spaces"], 0, "Exact marker match.", "hard"),
            M("Nesting heredocs / mixing with process subst is...", ["Easy to misread; prefer clarity", "Required style", "Faster always", "Forbidden by kernel"], 0, "Keep readable.", "hard"),
            M("Security: unquoted heredocs with untrusted data risk...", ["Injection via expansions", "Only slower CPU", "Only color loss", "Only locale"], 0, "Quote or sanitize.", "hard"),
            T("`exec <<EOF` can rebind shell stdin to a heredoc (rare/advanced).", True, "exec applies to shell fds.", "hard"),
            M("CI: generating files with heredocs beats...", ["Many echo lines with escaping hell", "Using printf ever", "Using cat files", "Using make"], 0, "Heredoc for multi-line gen.", "hard"),
            M("Lab check: verify no accidental leading spaces before closing `EOF`.", ["Yes: spaces break termination", "No: spaces fine always", "No: only tabs break", "No: ignore"], 0, "Marker must match exactly.", "hard"),
        ],
    ),
    "hist": (
        [
            M("Shell history typically records...", ["Previous commands", "Only man pages", "Only kernel logs", "Only zip lists"], 0, "History = past commands.", "easy"),
            M("Ctrl-R often starts...", ["Reverse incremental search", "Reboot", "rm -rf", "Rename"], 0, "Reverse-i-search.", "easy"),
            T("`history` builtin prints recent commands (bash).", True, "history lists them.", "easy"),
            M("`!!` expands to...", ["The previous command", "Login name", "Home", "PID 1"], 0, "Bang-bang last command.", "easy"),
            M("`!$` often means...", ["Last argument of previous command", "First arg", "Exit status", "umask"], 0, "Last word reuse.", "easy"),
            M("Up-arrow usually...", ["Recalls previous lines", "Sends SIGKILL", "Clears disk", "Opens man"], 0, "Linear history nav.", "easy"),
            T("History can leak secrets if you typed passwords on the CLI.", True, "Avoid secret argv.", "easy"),
            M("`HISTFILE` points to...", ["Where history is stored", "PATH", "umask", "PS1"], 0, "History file path.", "easy"),
            M("`history -c` ...", ["Clears the in-memory list (careful)", "Formats disk", "Clears /tmp only", "Resets uid"], 0, "Clear history.", "easy"),
            M("Searching history helps you...", ["Reuse complex commands safely", "Increase RAM clock", "Disable SELinux", "Skip man"], 0, "Productivity + accuracy.", "easy"),
        ],
        [
            M("`HISTCONTROL=ignoredups` skips...", ["Recording consecutive duplicates", "All commands", "All files", "All signals"], 0, "Dedup consecutive.", "medium"),
            M("`HISTSIZE` vs `HISTFILESIZE` ...", ["Memory list vs on-disk size limits", "Identical always", "Users vs groups", "PIDs vs PPIDs"], 0, "Two different caps.", "medium"),
            T("`set -o histverify` lets you edit expanded history before running.", True, "Verify bang expansions.", "medium"),
            M("`!grep` re-runs last command starting with grep because...", ["Prefix history expansion", "grep builtin always", "Kernel rule", "make rule"], 0, "Bang prefix.", "medium"),
            M("Multi-line commands in history may...", ["Store with escaped newlines / depend on options", "Never appear", "Become zip", "Clear PATH"], 0, "Multiline storage quirks.", "medium"),
            M("`history -a` appends...", ["New lines to HISTFILE now", "All of /etc", "Only aliases", "Only jobs"], 0, "Flush to disk.", "medium"),
            M("Shared history across sessions needs...", ["Careful append/reload options", "Disabling HISTFILE", "Root only", "Only tmux"], 0, "Concurrent sessions collide.", "medium"),
            T("`ignorespace` can omit commands starting with a space from history.", True, "Leading space trick.", "medium"),
            M("fc command can...", ["List/edit/re-run history ranges", "Format disks", "Mount nfs", "Set ACL only"], 0, "fc = fix command.", "medium"),
            M("Security policy may disable history to...", ["Reduce forensic leakage on shared accounts", "Speed CPU", "Break bash", "Clear man"], 0, "Trade ops vs privacy.", "medium"),
        ],
        [
            M("History expansion `!` conflicts with...", ["Some commands' own ! meanings; disable with set +H", "Only zip", "Only make", "Only pwd"], 0, "set +H disables.", "hard"),
            M("Timestamped history (`HISTTIMEFORMAT`) helps...", ["Audit when a command ran", "Sort files", "Set umask", "Color ls"], 0, "Temporal audit.", "hard"),
            T("Async prompts / multiple bash instances can interleave HISTFILE writes.", True, "Race on history file.", "hard"),
            M("Reading HISTFILE from untrusted home risks...", ["Command injection if replayed carelessly", "Only slow IO", "Only locale", "Only colors"], 0, "Treat history as data.", "hard"),
            M("`shopt -s histappend` is recommended because...", ["Appends rather than overwrites HISTFILE on exit", "Deletes history", "Disables Ctrl-R", "Clears PS1"], 0, "Avoid clobber.", "hard"),
            M("Zsh vs bash history features differ; portability means...", ["Not relying on one shell's widgets in docs", "Identical always", "Only Ctrl-R exists nowhere", "Bang always same"], 0, "Shell-specific UX.", "hard"),
            M("Secret managers beat typing tokens because...", ["Tokens won't land in HISTFILE/ps", "History encrypts argv", "Shells ban env", "SSH refuses keys"], 0, "Keep secrets out of argv/history.", "hard"),
            T("`LEADPIPE`/options aside, reverse-search needs readline-style editing.", True, "Editing mode dependent.", "hard"),
            M("Compliance redaction pipelines sometimes...", ["Scrub HISTFILE patterns on logout", "Expand HISTSIZE infinitely", "Force ignoredups off", "Disable tty"], 0, "Policy scrubbing.", "hard"),
            M("Lab drill: recover a prior pipeline via Ctrl-R then tweak args.", ["Yes: search then edit", "No: retype always", "No: use -9", "No: reboot"], 0, "Search-edit-run.", "hard"),
        ],
    ),
    "alias": (
        [
            M("An alias is...", ["A short name expanding to a command string", "A kernel syscall", "A filesystem type", "A signal"], 0, "Alias = shorthand.", "easy"),
            M("`alias ll='ls -l'` creates...", ["ll as ls -l", "A user ll", "A directory", "A man page"], 0, "Simple alias.", "easy"),
            T("Shell functions can take arguments more cleanly than aliases.", True, "Functions > aliases for args.", "easy"),
            M("`unalias ll` ...", ["Removes alias ll", "Deletes /ll", "Kills PID ll", "Clears PATH"], 0, "unalias drops it.", "easy"),
            M("`type ll` often shows...", ["Whether ll is alias/function/file", "Only disk usage", "Only umask", "Only jobs"], 0, "type explains command kind.", "easy"),
            M("Aliases usually apply to...", ["Interactive shells sourcing rc files", "The kernel scheduler", "Cron by default always", "make always"], 0, "Often interactive-only.", "easy"),
            T("`\\ls` can bypass an ls alias.", True, "Backslash avoids alias.", "easy"),
            M("Defining `greet() { echo Hi \"$1\"; }` creates...", ["A function", "An alias only", "A signal", "A mount"], 0, "Function syntax.", "easy"),
            M("Prefer functions when you need...", ["Positional parameters / logic", "Only renaming ls", "Faster disks", "Root"], 0, "Functions for logic.", "easy"),
            M("`alias` with no args lists...", ["Defined aliases", "All processes", "All files in /", "All signals"], 0, "List aliases.", "easy"),
        ],
        [
            M("Aliases are not expanded in scripts by default (bash) unless...", ["expand_aliases / interactive modes", "Always expanded", "Root runs them", "They end in .sh"], 0, "Scripts skip aliases by default.", "medium"),
            M("Recursive alias pitfalls happen when...", ["Alias body includes its own name without care", "You use functions", "You use abs paths", "You read man"], 0, "Alias loops.", "medium"),
            T("`command ls` bypasses aliases/functions and seeks PATH/builtin rules.", True, "command builtin escapes.", "medium"),
            M("Exporting functions (`export -f` bash) allows...", ["Child bash to see them", "Kernels to run them", "make to become bash", "zip to expand"], 0, "Function export is bash-specific.", "medium"),
            M("Store shared aliases in a file and `source` it to...", ["Reuse across shells", "Compile them", "chmod automatically", "Clear history"], 0, "Source shared libs.", "medium"),
            M("`alias sudo='sudo '` trick allows...", ["Alias expansion of the next word", "Root without password always", "Disabling sudo", "Clearing logs"], 0, "Trailing-space alias quirk.", "medium"),
            M("Debug unexpected behavior with...", ["`type -a cmd` and `declare -f`", "Only reboot", "Only chmod 777", "Only tar"], 0, "Introspect definitions.", "medium"),
            T("Functions can be recursive; aliases are simple text replacements.", True, "Different mechanisms.", "medium"),
            M("Name collisions: function shadowing a binary means...", ["Function wins in shell lookup order", "Binary always wins", "Both run", "Shell errors always"], 0, "Lookup order matters.", "medium"),
            M("Team style guides often restrict aliases in committed scripts because...", ["Non-portable interactive conveniences", "Aliases are faster", "Functions illegal", "POSIX bans functions"], 0, "Scripts should be explicit.", "medium"),
        ],
        [
            M("Completion + aliases interaction can confuse because...", ["Completion may complete real command not alias intent", "Aliases disable completion always", "Kernels expand aliases", "PATH clears"], 0, "UX mismatch.", "hard"),
            M("Security: aliasing `rm` to interactive rm helps humans but...", ["Fails in scripts / false sense of safety", "Protects cron always", "Stops rootkits", "Encrypts disks"], 0, "Not a security boundary.", "hard"),
            T("Zsh global aliases can expand anywhere, unlike bash word-position aliases.", True, "Shell-specific power.", "hard"),
            M("`DEBUG` traps / `extdebug` can trace...", ["Function execution paths", "Only zip", "Only make -n", "Only man"], 0, "Deep debug hooks.", "hard"),
            M("Dynamic `alias` creation from untrusted input is...", ["Injection-prone", "Recommended", "Required by POSIX", "Faster"], 0, "Do not eval untrusted.", "hard"),
            M("Portable scripts should use...", ["Functions or explicit commands, not bash aliases", "Only aliases", "Only global aliases", "Only `~`"], 0, "Portability first.", "hard"),
            M("Lazy-loading functions via stubs can...", ["Speed shell startup", "Break `type`", "Disable PATH", "Clear PS1 always"], 0, "Deferred define pattern.", "hard"),
            T("`unset -f name` removes a function definition.", True, "unset -f.", "hard"),
            M("When documenting onboarding, prefer...", ["Dotfiles repo with commented functions", "Secret undocumented aliases only", "Shadowing coreutils silently", "Disabling history"], 0, "Teachable configs.", "hard"),
            M("Lab: replace a brittle alias with a function that quotes \"$@\".", ["Yes: correct arg passing", "No: aliases pass $@ better", "No: skip quoting", "No: use eval"], 0, "\"$@\" in functions.", "hard"),
        ],
    ),
    "script": (
        [
            M("`for f in *.log; do ...; done` typically...", ["Deletes every log", "Runs body once per matching file", "Compiles Verilog", "Disables shebang"], 1, "for iterates words/files.", "easy"),
            M("`if [ -f \"$file\" ]; then` checks...", ["String empty", "Path exists as regular file", "User is root", "Git installed"], 1, "-f regular file test.", "easy"),
            T("`case ... esac` is clearer than long if/elif chains for one value.", True, "case multi-way branch.", "easy"),
            M("`NAME=\"${1:-World}\"` means...", ["Always World", "Use $1 if set/nonempty else World", "Delete $1", "Require two args"], 1, ":- default.", "easy"),
            M("Shebang `#!/usr/bin/env bash` helps...", ["Find bash on PATH", "Disable scripts", "Set umask 0", "Clear PATH"], 0, "env locates interpreter.", "easy"),
            M("`while read -r line; do ...; done < {f}` reads...", ["Lines from {f}", "Only PIDs", "Only signals", "Only zip"], 0, "Line loop.", "easy"),
            T("`exit` ends the shell/script with a status.", True, "exit returns status.", "easy"),
            M("`[[ $a == $b ]]` (bash) is...", ["A safer/extended test form vs legacy [", "A redirect", "A signal", "A mount"], 0, "[[ keyword.", "easy"),
            M("`for i in $(seq 1 {n}); do` needs care because...", ["Word splitting / seq portability", "seq is a kernel", "Loops illegal", "for bans numbers"], 0, "Prefer bash `{1..n}` carefully.", "easy"),
            M("`break` / `continue` ...", ["Control loop flow", "Kill PID 1", "Clear history", "Mount nfs"], 0, "Loop controls.", "easy"),
        ],
        [
            M("`select` menus are...", ["Interactive choice loops (bash)", "Only for make", "Only for zip", "Signals"], 0, "select builtin.", "medium"),
            M("`until cmd; do ...; done` loops while...", ["cmd fails (non-zero)", "cmd succeeds", "Forever always", "Never"], 0, "until = while not.", "medium"),
            T("`read -r` avoids interpreting backslashes.", True, "raw read.", "medium"),
            M("Arithmetic `((i={n}))` / `$((...))` provide...", ["Integer arithmetic", "Floating only", "String joins only", "Signals"], 0, "Arithmetic evaluation.", "medium"),
            M("`shift` drops...", ["$1 and renumbers params", "PATH entries", "History", "Jobs"], 0, "shift params.", "medium"),
            M("IFS tweaks change...", ["Field splitting behavior", "File modes", "PIDs", "Man sections"], 0, "IFS is critical.", "medium"),
            M("`return` in a function differs from `exit` because...", ["return leaves function; exit leaves shell", "Identical always", "return reboots", "exit only from functions"], 0, "Scope of leaving.", "medium"),
            T("Quoted `\"$@\"` preserves argument boundaries.", True, "Essential quoting.", "medium"),
            M("`getopts` parses...", ["Short options portably-ish", "Only long GNU always", "Only env files", "Only make"], 0, "getopts builtin.", "medium"),
            M("Subshell `( cd {d} && cmd )` isolates...", ["Directory changes from parent", "Network", "umask of system", "Man db"], 0, "Subshell scope.", "medium"),
        ],
        [
            M("`set -euo pipefail` is a common strict mode because...", ["Fail fast on errors/unset/pipe fails", "It disables scripts", "It requires root", "It clears PATH"], 0, "Strict bash mode.", "hard"),
            M("`local` vars in bash functions prevent...", ["Leaking into global scope", "All recursion", "Exit codes", "Signals"], 0, "local scoping.", "hard"),
            T("`mapfile`/`readarray` can slurp lines into arrays.", True, "Array reads.", "hard"),
            M("Namerefs (`declare -n`) are powerful but...", ["Easy to misuse / shadow", "Required by POSIX", "Faster than ints always", "Disable set -u"], 0, "Careful indirection.", "hard"),
            M("Process substitution in loops can...", ["Avoid temp files for streaming", "Replace functions", "Clear aliases", "Setuid"], 0, "Advanced I/O.", "hard"),
            M("Trap `ERR`/`EXIT` enables...", ["Cleanup handlers", "Faster CPU", "Disabled history", "Forced fg"], 0, "Traps for safety.", "hard"),
            M("Avoid `eval` on untrusted strings because...", ["Code injection", "Slower echo", "Breaks pwd", "Clears PS1 only"], 0, "eval is dangerous.", "hard"),
            T("POSIX sh lacks many bash arrays/[[ features; write accordingly.", True, "Portability subset.", "hard"),
            M("Debugging with `set -x` prints...", ["Expanded commands as run", "Only man", "Only zip", "Only jobs"], 0, "xtrace.", "hard"),
            M("Lab: rewrite nested ifs into case for `$1` subcommands.", ["Yes: clearer dispatch", "No: if always clearer", "No: use eval", "No: use goto"], 0, "case dispatch.", "hard"),
        ],
    ),
    "exit": (
        [
            M("Exit status 0 usually means...", ["Success", "Failure", "Signal 0 only", "Permission denied"], 0, "0 = success.", "easy"),
            M("`echo $?` prints...", ["Exit status of the previous command", "PID", "UID", "umask"], 0, "$? is last status.", "easy"),
            T("`cmd1 && cmd2` runs cmd2 only if cmd1 succeeds.", True, "Short-circuit AND.", "easy"),
            M("`cmd1 || cmd2` runs cmd2 when...", ["cmd1 fails", "cmd1 succeeds", "Always", "Never"], 0, "Short-circuit OR.", "easy"),
            M("Non-zero exit typically means...", ["Failure / not-true condition", "Success", "Need reboot", "Need root always"], 0, "Non-zero = fail.", "easy"),
            M("`false; echo $?` often shows...", ["1", "0", "127", "255 always"], 0, "false fails.", "easy"),
            T("`true` exits 0.", True, "true succeeds.", "easy"),
            M("In `if cmd; then`, the if tests...", ["cmd's exit status", "cmd's stdout only", "cmd's name", "PATH"], 0, "if uses status.", "easy"),
            M("`exit {n}` from a script sets...", ["The script's status to {n}", "umask to {n}", "UID to {n}", "Nice to {n}"], 0, "Script exit code.", "easy"),
            M("Command not found often yields status...", ["127", "0", "1 always only", "2 only for grep"], 0, "127 common for not found.", "easy"),
        ],
        [
            M("`set -e` aborts on...", ["Failing commands (with many exceptions)", "Successful commands", "Only echoes", "Only aliases"], 0, "errexit.", "medium"),
            M("Pipeline status without pipefail is...", ["Usually the last command's status", "Always first", "Always 0", "Bitwise OR always"], 0, "Last stage wins by default.", "medium"),
            T("`cmd1 && cmd2 || cmd3` can surprise; prefer if/else.", True, "Ambiguous chaining.", "medium"),
            M("`! cmd` negates...", ["Exit status for the purposes of the shell", "Stdout bytes", "File modes", "PIDs"], 0, "Status negation.", "medium"),
            M("`return {n}` in sourced scripts/functions...", ["Sets that status without always exiting the login shell", "Always reboots", "Clears PATH", "Formats"], 0, "return vs exit.", "medium"),
            M("Timeouts killing commands may yield...", ["Statuses related to signals (e.g. 128+sig)", "Always 0", "Always 1", "Always 127"], 0, "Signal exit encoding.", "medium"),
            M("`set -o errexit` is another name for...", ["set -e", "set -x", "set -u", "set -m"], 0, "errexit alias.", "medium"),
            T("`if ! cmd; then` runs then-branch when cmd fails.", True, "Negated if.", "medium"),
            M("Documenting exit codes in --help helps...", ["Automation handle failures", "CPU turbo", "Font rendering", "Only humans never scripts"], 0, "Contract for callers.", "medium"),
            M("`wait $pid; echo $?` reports...", ["Status of that waited child", "Parent always 0", "umask", "Nice"], 0, "wait status.", "medium"),
        ],
        [
            M("`set -e` exceptions include...", ["Failing commands in `if`/`while` tests etc.", "No exceptions ever", "Only echo", "Only pwd"], 0, "Know errexit nuances.", "hard"),
            M("Signal exit status convention often...", ["128 + signal number", "Always 1", "Always 255", "Negative only"], 0, "128+n pattern.", "hard"),
            T("`pipefail` makes failure in any pipeline stage visible.", True, "Critical for CI.", "hard"),
            M("`trap 'cleanup; exit 1' ERR` ties...", ["Errors to cleanup", "Only signals INT", "Only success", "Only aliases"], 0, "ERR trap patterns.", "hard"),
            M("Subshell failures `(cmd)` with set -e ...", ["Have subtle inheritance rules; test explicitly", "Always identical to non-subshell", "Never fail", "Always exit login"], 0, "Subshell+errexit quirks.", "hard"),
            M("Why prefer `cmd || exit 1` at critical steps?", ["Explicit failure handling readability", "Faster CPU", "Required by ls", "Disables set -e"], 0, "Explicit beats magic.", "hard"),
            M("Makefile recipes and shell `set -e` interaction...", ["Make checks recipe status; shell flags still matter inside", "Make ignores all statuses", "set -e disables make", "Identical to cmake"], 0, "Two layers of status.", "hard"),
            T("POSIX leaves some status meanings implementation-defined beyond 0.", True, "Portable code treats 0 vs non-0.", "hard"),
            M("Masking failures with `cmd || true` is OK when...", ["Failure is expected/ignored intentionally", "Always", "Never documented", "In setuid only"], 0, "Intentional ignore.", "hard"),
            M("Lab: assert status with `cmd; test $? -eq 0`.", ["Yes: explicit check", "No: ignore $?", "No: only print", "No: reboot on fail"], 0, "Assert statuses.", "hard"),
        ],
    ),
    "safe": (
        [
            M("Quoting `\"$var\"` prevents...", ["Word splitting / globbing surprises", "All bugs forever", "Exit status", "Signals"], 0, "Quote expansions.", "easy"),
            M("`set -u` errors on...", ["Unset variable use", "Set variables", "Only aliases", "Only functions"], 0, "nounset.", "easy"),
            T("Never parse `ls` output for scripting file lists.", True, "ls is for humans.", "easy"),
            M("Prefer `\"$@\"` over `$*` because...", ["It preserves arguments", "It is shorter always", "It disables quoting", "It clears PATH"], 0, "$@ correctness.", "easy"),
            M("Temporary files should use...", ["`mktemp`", "Fixed /tmp/a.txt always", "Only $RANDOM name alone", "World-writable fixed names"], 0, "mktemp is safer.", "easy"),
            M("`rm -rf \"$dir\"` dangers rise when...", ["$dir is empty/untrusted", "dir is quoted absolute specific", "You use dry-run first", "You confirm path"], 0, "Empty expand disasters.", "easy"),
            T("`read -r` + IFS= is a safer line-read pattern.", True, "Classic safe read.", "easy"),
            M("Check commands exist with...", ["`command -v`", "Only which always portable", "Only ls /bin", "Only type -P on all sh"], 0, "command -v portable-ish.", "easy"),
            M("Avoid `eval` unless...", ["You fully control/validate input", "Always for speed", "Parsing ls", "Expanding globs"], 0, "eval last resort.", "easy"),
            M("Shebang + `set -euo pipefail` helps...", ["Catch mistakes early", "Hide errors", "Disable traps", "Force interactive"], 0, "Strict defaults.", "easy"),
        ],
        [
            M("TOCTOU races mean...", ["Time-of-check vs time-of-use gaps", "Only timezone bugs", "Only man typos", "Only make -j"], 0, "Check then use races.", "medium"),
            M("Create dirs with `mkdir -p` and modes via...", ["`mkdir -m` / umask awareness", "chmod 777 always after", "Ignoring modes", "Sticky on /"], 0, "Safe dir create.", "medium"),
            T("Use `--` to end options before arbitrary filenames.", True, "-- stops option parsing.", "medium"),
            M("`find ... -exec cmd {} +` is often safer/faster than...", ["Parsing ls | xargs without -0", "Using abs paths", "Using functions", "Using case"], 0, "find -exec batches.", "medium"),
            M("World-writable directories + predictable names enable...", ["Symlink planting attacks", "Faster mktemp", "Safer rm", "Better man"], 0, "Predictable names are risky.", "medium"),
            M("ShellCheck helps by...", ["Static-linting common shell pitfalls", "Replacing tests", "Formatting disks", "Setting PS1"], 0, "Lint your shell.", "medium"),
            M("Restrict PATH in privileged scripts to...", ["Trusted absolute directories", "`.` first", "~/Downloads first", "Empty PATH"], 0, "Trusted PATH.", "medium"),
            T("Quote here-doc delimiters when embedding untrusted text.", True, "Prevent expansion injection.", "medium"),
            M("`trap cleanup EXIT` should be...", ["Idempotent and signal-safe-ish", "Calling sudo rm -rf /", "Clearing disks", "Disabling networking always"], 0, "Safe cleanup.", "medium"),
            M("Prefer arrays in bash for lists because...", ["Avoid IFS splitting hell", "Arrays are POSIX", "Faster than CPU", "They setuid"], 0, "Arrays hold words.", "medium"),
        ],
        [
            M("privilege dropping patterns matter when...", ["Scripts start as root then run untrusted phases", "Always for echo", "Only for ls colors", "Never on Unix"], 0, "Least privilege.", "hard"),
            M("Environment sanitization (`env -i`) helps because...", ["Inherited env can change behavior/security", "Env is unused by shells", "It disables PATH forever usefully without reset", "It clears disks"], 0, "Clean env.", "hard"),
            T("Atomic `mv` publish replaces avoid partial reads of outputs.", True, "Atomic rename publish.", "hard"),
            M("Auto-yes to prompts (`yes |`) is dangerous when...", ["Commands have destructive confirmations", "Printing help", "Using pwd", "Reading man"], 0, "Don't blind-confirm.", "hard"),
            M("Capability-aware safety means...", ["Mode bits alone may be insufficient under MAC", "chmod 777 fixes MAC", "SELinux ignores paths", "Root always bypasses hardware"], 0, "Defense layers.", "hard"),
            M("Locale + parsing numbers/files can break when...", ["User LANG changes decimal/field rules", "C locale only ever", "ASCII digits banned", "UTF-8 absent always"], 0, "Force C locale for parsers.", "hard"),
            M("Secure temp on shared /tmp uses...", ["mktemp + correct umask + careful cleanup", "Fixed names", "777 dirs with common files", "Symlink to /etc"], 0, "Temp hygiene.", "hard"),
            T("Argument vectors remain visible in `ps`; don't put secrets there.", True, "ps leaks argv.", "hard"),
            M("CI secret masking still requires...", ["Not echoing secrets / careful debug traces", "set -x always with secrets", "Printing env", "Storing in history"], 0, "Redact debug.", "hard"),
            M("Lab mantra: validate, quote, fail fast, least privilege.", ["Yes", "No: skip quote", "No: ignore status", "No: world write"], 0, "Safe scripting pillars.", "hard"),
        ],
    ),
    "proj": (
        [
            M("A clear project layout helps...", ["Find sources, tests, docs, scripts", "Speed the CPU clock", "Disable git", "Replace make"], 0, "Layout = navigability.", "easy"),
            M("`tar -czf {a} {d}` typically...", ["Creates a gzip-compressed archive of {d}", "Deletes {d}", "Formats disk", "Starts a server"], 0, "Create tar.gz.", "easy"),
            T("`diff -u a b` shows a unified diff.", True, "Unified diff format.", "easy"),
            M("`sed 's/foo/bar/' {f}` ...", ["Replaces first foo with bar per line (default)", "Compiles foo", "Chmods bar", "Mounts foo"], 0, "Basic sed substitute.", "easy"),
            M("README at repo root should explain...", ["How to build/run/test", "Only authors' birthdays", "Only CPU temps", "Only secrets"], 0, "Onboarding docs.", "easy"),
            M("`tar -tzf {a}` lists...", ["Archive contents", "Only PIDs", "Only users", "Only mounts"], 0, "List tarball.", "easy"),
            T("`patch` applies diff output to update files.", True, "patch consumes diffs.", "easy"),
            M("Keeping build outputs out of git usually uses...", [".gitignore", "chmod 000", "disabling PATH", "sticky on /"], 0, "Ignore artifacts.", "easy"),
            M("`sed -i` (GNU) edits...", ["Files in place (carefully)", "Only stdout forever", "Only man", "Only zip"], 0, "In-place sed.", "easy"),
            M("src/ tests/ docs/ scripts/ is a...", ["Common layout pattern", "Kernel requirement", "Zip-only tree", "Forbidden structure"], 0, "Conventional dirs.", "easy"),
        ],
        [
            M("`diff -ruN old/ new/` is useful for...", ["Directory trees / missing files treated helpfully", "Only binary identical", "Killing jobs", "Setting PS1"], 0, "Recursive diff.", "medium"),
            M("`tar --exclude` helps omit...", ["build/ or secrets from archives", "All files always", "Only README", "Only Makefile"], 0, "Exclude patterns.", "medium"),
            T("`sed -E` enables extended regex on many sed builds.", True, "Extended regex flag.", "medium"),
            M("Canonical project scripts live under...", ["scripts/ or tools/ with --help", "Random /tmp only", "Only ~/.cache", "Only /proc"], 0, "Discoverable scripts.", "medium"),
            M("`git apply` vs `patch` ...", ["Different tools; know which your workflow uses", "Identical always", "One formats disks", "One clears PATH"], 0, "Tool choice.", "medium"),
            M("Reproducible archives may need...", ["Sorted file order + stable timestamps (tools permitting)", "Random order", "Including .git always", "World secrets"], 0, "Reproducible tarballs.", "medium"),
            M("`diff` exit status 1 often means...", ["Differences found", "Identical files", "Crash", "Permission ok only"], 0, "1 = differ.", "medium"),
            T("Binary files need specialized diff tooling; text diff may junk.", True, "Binary != text diff.", "medium"),
            M("Keep generated code documented so that...", ["Contributors know not to hand-edit", "Git bans them", "make ignores them", "sed deletes them"], 0, "Generated vs source.", "medium"),
            M("`rsync -a` for project sync preserves...", ["Permissions/times/symlinks better than naive cp", "Only names", "Only zip methods", "Only owners if root always"], 0, "Archive rsync.", "medium"),
        ],
        [
            M("Patch fuzz failures often mean...", ["Context drifted; rebase/regenerate diff", "Disk full only", "umask wrong only", "PATH empty only"], 0, "Context mismatch.", "hard"),
            M("Sed in-place without backup on macOS/BSD differs because...", ["-i requires backup-suffix args differently", "sed identical everywhere", "GNU required by POSIX", "-i bans files"], 0, "Portable -i is tricky.", "hard"),
            T("Tar bombs extract many files into cwd; inspect with -t first.", True, "List before extract.", "hard"),
            M("SBOM / license files belong in layout because...", ["Compliance and reuse clarity", "They speed make -j", "They replace README", "They clear secrets"], 0, "Legal hygiene.", "hard"),
            M("Large media should use...", ["LFS/external storage patterns, not giant git blobs", "Always commit raw 4GB", "Only tar in git", "Only zip in git"], 0, "Store large assets wisely.", "hard"),
            M("Unified diffs with enough context help...", ["Humans and patch apply robustness", "Shrink files always", "Hide changes", "Disable review"], 0, "Context is clarity.", "hard"),
            M("Deterministic `sed` transforms in CI should...", ["Pin inputs/locale and fail on mismatch", "Rely on random LANG", "Ignore exit status", "Pipe to true always"], 0, "Deterministic edits.", "hard"),
            T("Archive signing/checksums protect integrity beyond mere compression.", True, "Integrity layer.", "hard"),
            M("Monorepo layouts need...", ["Clear package boundaries + tool docs", "One flat directory of 10k files only", "No README", "Secrets in root"], 0, "Scale structure.", "hard"),
            M("Lab: generate a unified diff, apply to a copy, re-diff empty.", ["Yes: round-trip validates", "No: skip verify", "No: use rm", "No: chmod 777"], 0, "Diff round-trip.", "hard"),
        ],
    ),
    "tar": (
        [
            M("`tar` originally packs...", ["Multiple files into one archive stream", "Only zip encryption", "Only man pages", "Only signals"], 0, "Tape archive tool.", "easy"),
            M("`zip {z} {f}` creates...", ["A zip archive including {f}", "A tar only", "A user", "A signal"], 0, "zip creates .zip.", "easy"),
            T("`.tar.gz` is often a tar stream compressed with gzip.", True, "tarball+gzip.", "easy"),
            M("`tar -xzf {a}` typically...", ["Extracts gzip tar", "Creates zip", "Formats disk", "Kills PID"], 0, "Extract tar.gz.", "easy"),
            M("Zip stores...", ["Per-member compression commonly", "Only one stream always like tar+gzip", "Only permissions forever identical to tar", "Only symlinks as hard links"], 0, "Zip member model differs.", "easy"),
            M("`unzip -l {z}` lists...", ["Zip contents", "Only PIDs", "Only users", "Only mounts"], 0, "List zip.", "easy"),
            T("Tar preserves Unix permissions/ownership better in many workflows than classic zip.", True, "Tar friendlier to Unix metadata.", "easy"),
            M("Choose zip when...", ["Recipients expect .zip / partial extract UX", "You need exact Linux ownership always", "You only have tar", "You ban compression"], 0, "Interop scenarios.", "easy"),
            M("Choose tar.gz when...", ["Unix trees/permissions/symlinks matter", "Only Windows notepad users", "You need per-file password zip features only", "You hate gzip"], 0, "Unix tree shipping.", "easy"),
            M("`tar -c` means...", ["Create", "Compress only", "Chmod", "Cat"], 0, "c = create.", "easy"),
        ],
        [
            M("`tar -C {d}` changes...", ["Directory before archiving/extracting", "umask", "PATH", "PS1"], 0, "-C chdir.", "medium"),
            M("Zip encryption features are...", ["Common in zip tooling; tar usually relies on outer encryption", "Identical to tar", "Forbidden", "Kernel-only"], 0, "Different crypto UX.", "medium"),
            T("`tar --absolute-names` can be dangerous on extract.", True, "Absolute paths in archives risk.", "medium"),
            M("Sparse files: tar options may...", ["Preserve holes better than naive zip workflows", "Always destroy holes", "Convert to dirs", "Clear modes"], 0, "Sparse handling.", "medium"),
            M("`gzip -k` / separate compress vs `tar -z` ...", ["Different pipelines; know your flags", "Identical always", "One deletes tar tool", "One requires root"], 0, "Composition styles.", "medium"),
            M("Update vs recreate archives...", ["Tool-specific; zip update differs from rewriting tar.gz", "Always same", "Forbidden", "Only for man"], 0, "Update semantics differ.", "medium"),
            M("Symlinks in zip vs tar...", ["Support varies; verify on your tools", "Always identical", "Zip always follows", "Tar always ignores"], 0, "Test symlink policies.", "medium"),
            T("`zip -r` recurses directories.", True, "Recursive zip.", "medium"),
            M("Streaming tar over ssh is common because...", ["Tar is stream-friendly", "Zip cannot exist on pipes ever", "SSH bans zip", "make requires tar"], 0, "Tar streams well.", "medium"),
            M("CRC/tests: `zip -T` / tar extract dry checks help...", ["Validate archives", "Speed CPU", "Clear history", "Setuid"], 0, "Integrity smoke tests.", "medium"),
        ],
        [
            M("Zip slip vulnerabilities involve...", ["Extracting `../` paths outside target dir", "Only slow inflate", "Only missing CRC", "Only large files"], 0, "Path traversal on extract.", "hard"),
            M("Reproducible zip/tar needs...", ["Stable ordering, timestamps, user metadata policies", "Random mtimes", "Including build/ always", "Different uid each run"], 0, "Bit-for-bit archives.", "hard"),
            T("pax/ustar/gnu tar formats differ in metadata limits.", True, "Format dialects.", "hard"),
            M("Long paths / unicode names may...", ["Break older zip/tar tooling", "Always work identically", "Disable UTF-8", "Require root"], 0, "Name edge cases.", "hard"),
            M("Solid compression (some formats) vs zip members...", ["Changes random-access extract tradeoffs", "Identical", "Only affects man", "Only affects PATH"], 0, "Compression architecture.", "hard"),
            M("Hard links in tar can be stored specially so that...", ["Extract restores link relations", "They become two full copies always", "They become symlinks always", "They are dropped always"], 0, "Tar hardlink records.", "hard"),
            M("When distributing to mixed OS teams...", ["Publish both or document opener tools", "Only tar.gz always", "Only zip always", "Only 7z always"], 0, "Audience-driven format.", "hard"),
            T("Outer `gpg` encryption around tar.gz is a common Unix pattern.", True, "Encrypt the stream.", "hard"),
            M("Benchmarking zip vs tar+zstd should measure...", ["Ratio, speed, and metadata needs", "Only file extension aesthetics", "Only man length", "Only GitHub icons"], 0, "Measure real goals.", "hard"),
            M("Lab: create both `{a}` and `{z}`, compare metadata with list commands.", ["Yes: compare capabilities", "No: pick randomly", "No: skip list", "No: chmod 777"], 0, "Compare formats hands-on.", "hard"),
        ],
    ),
    "bak": (
        [
            M("A backup before clean-build helps you...", ["Recover if clean deletes needed artifacts", "Speed make always", "Disable git", "Skip tests"], 0, "Safety copy first.", "easy"),
            M("`make clean` typically...", ["Removes build outputs", "Deletes source forever by design always", "Formats disk", "Creates users"], 0, "Clean target removes products.", "easy"),
            T("Version control is not a full substitute for backup of uncommitted work.", True, "Uncommitted data needs care.", "easy"),
            M("`cp -a {d} {b}` copies...", ["Tree with attributes more carefully", "Only names", "Only empty dirs", "Only symlinks text as files always"], 0, "Archive copy.", "easy"),
            M("Clean-build means...", ["Remove outputs then rebuild from sources", "Only reboot", "Only chmod", "Only zip"], 0, "From-scratch build.", "easy"),
            M("Before `rm -rf build/`, consider...", ["Dry-run listing / backups", "Skipping ls", "Using sudo always", "Disabling networking"], 0, "Look before delete.", "easy"),
            T("Timestamped backup dirs reduce overwrite risk.", True, "Unique backup names.", "easy"),
            M("`rsync -a --delete` is powerful because...", ["It can mirror deletions too", "It never deletes", "It only zips", "It clears PATH"], 0, "Mirror sync danger/power.", "easy"),
            M("Keep backups off the same failing disk when possible to...", ["Survive disk loss", "Speed CPU", "Skip checksums", "Avoid man"], 0, "Separate media.", "easy"),
            M("`make distclean` (when provided) often removes...", ["More generated files than clean", "Only README", "Only .git", "Only /usr"], 0, "Deeper clean.", "easy"),
        ],
        [
            M("Incremental backups differ from full by...", ["Storing changes since a baseline", "Always copying everything identically", "Deleting sources", "Skipping checksums always"], 0, "Incremental strategy.", "medium"),
            M("Verify backups with...", ["Test restore / checksums", "Only ls the backup name", "Only trust cp exit 0", "Only zip size vibes"], 0, "Restore tests.", "medium"),
            T("Clean builds catch missing generated-file commits.", True, "Fresh tree reveals gaps.", "medium"),
            M("`git clean -fdx` is dangerous because...", ["It deletes untracked files including ignored", "It only lists", "It commits", "It pushes"], 0, "Know git clean flags.", "medium"),
            M("Backup exclusion lists should omit...", ["Secrets carefully policy-wise + huge caches intentionally", "All source", "All docs", "All tests"], 0, "Exclude thoughtfully.", "medium"),
            M("Atomic backup publish uses...", ["Write to temp then rename", "Partial overwrite in place", "Appending randomly", "chmod 777 first"], 0, "Atomic replace.", "medium"),
            M("Out-of-tree builds help clean by...", ["Keeping objects outside sources", "Deleting sources", "Disabling make", "Forcing zip"], 0, "Separate build dir.", "medium"),
            T("Snapshots (zfs/lvm/cloud) are another backup class.", True, "System snapshots.", "medium"),
            M("Retention policies decide...", ["How long backups are kept", "CPU governor", "PS1 color", "Man width"], 0, "Retention.", "medium"),
            M("Before deleting `{b}`, confirm...", ["Newest good backup exists elsewhere", "Nothing", "Only that name is long", "That rm is aliased"], 0, "Never delete last copy.", "medium"),
        ],
        [
            M("Backup consistency for live DBs may need...", ["Quiesce/snapshots/agent-aware dumps", "Only cp -r while writing", "Only tar without locks", "Only zip -r data/"], 0, "Consistent images.", "hard"),
            M("Ransomware resilience includes...", ["Offline/immutable backup copies", "Only local world-writable shares", "Only one NAS share mounted RW everywhere", "Disabling checksums"], 0, "Offline copies.", "hard"),
            T("Clean rebuild + artifact hashes detects non-reproducible builds.", True, "Hash compare.", "hard"),
            M("`make clean` that deletes `$(HOME)` due to bad vars shows why...", ["Expand/echo recipes before rm", "Variables are safe always", "clean should use sudo", "PATH must include ."], 0, "Echo destructive paths.", "hard"),
            M("Cross-region backup lag means RPO/RTO...", ["Define acceptable data loss/time-to-restore", "Are font settings", "Are umask aliases", "Are man sections"], 0, "Disaster metrics.", "hard"),
            M("Deduplicating backup systems still need...", ["Periodic full restore drills", "No restores ever", "Only incremental forever without checks", "Disabled auth"], 0, "Drill restores.", "hard"),
            M("Container layers vs host backups...", ["Different contents; back up volumes explicitly", "Image backup includes all volumes always", "Host backup unused", "Skip both"], 0, "Volume awareness.", "hard"),
            T("Encryption at rest for backups protects stolen media.", True, "Encrypt backups.", "hard"),
            M("CI cache clearing is a form of clean-build that...", ["Surfaces hidden cache dependencies", "Should be never done", "Replaces unit tests", "Formats runners' disks randomly"], 0, "Cache hygiene.", "hard"),
            M("Lab: backup `{d}`, run clean, restore, diff.", ["Yes: prove the loop", "No: trust clean", "No: skip restore", "No: rm backup first"], 0, "Backup-clean-restore.", "hard"),
        ],
    ),
    "link": (
        [
            M("A relative symlink target is resolved from...", ["The directory containing the symlink", "Your cwd only always", "$HOME only", "/tmp only"], 0, "Link's directory is the base.", "easy"),
            M("`ln -s ../bin/tool {t}` stores...", ["The text `../bin/tool`", "An absolute resolved path always", "A hard link inode only", "A copy of bytes"], 0, "Stores path text.", "easy"),
            T("Moving a relative symlink can break it if the target path no longer lines up.", True, "Relative links are location-sensitive.", "easy"),
            M("Absolute symlink targets start with...", ["/", "./", "../", "~ always expanded in the link text by ln"], 0, "Absolute link text.", "easy"),
            M("`readlink {t}` helps debug by showing...", ["Stored target text", "Only final file bytes", "Owner only", "umask"], 0, "See the text.", "easy"),
            M("Dangling link means...", ["Target missing", "Too many hard links", "Directory sticky", "SUID"], 0, "Broken pointer.", "easy"),
            T("`ls -l` shows arrow to target for symlinks.", True, "Long listing shows target.", "easy"),
            M("Prefer relative links inside repos when...", ["The whole tree moves together", "Links must survive any rearrange of parents differently", "Crossing to /usr always", "Pointing to /etc"], 0, "Repo-relative portability.", "easy"),
            M("Prefer absolute links when...", ["Target is a fixed system path", "The repo relocates often as a unit", "You only have relative dirs", "You hate realpath"], 0, "Fixed system targets.", "easy"),
            M("`realpath {t}` after linking checks...", ["Final resolved path", "Only link text", "Only mode", "Only owner"], 0, "Verify resolution.", "easy"),
        ],
        [
            M("Creating `ln -s {f} {t}` while cwd differs from link dir...", ["Still stores the string you typed; may not be what you meant", "Auto-rewrites to absolute always", "Fails always", "Converts to hard link"], 0, "String is literal.", "medium"),
            M("`ln -sr` (GNU) can create...", ["Relative links computed for you", "Only hard links", "Only absolute", "Only directories"], 0, "Relative smart link.", "medium"),
            T("Packaging that relocates prefix breaks careless absolute links.", True, "Prefixes move.", "medium"),
            M("Symlink farms for version switches often use...", ["`current` -> versioned dir pattern", "Hard links only", "Duplicate full trees only", "Only PATH edits"], 0, "current pointer pattern.", "medium"),
            M("Windows/mac vs Linux symlink privileges differ; tests should...", ["Run on the target OS", "Assume identical", "Skip links", "Use only hard links"], 0, "Platform differences.", "medium"),
            M("Backup tools may copy link text or follow; know flags because...", ["Restores can explode or preserve intent differently", "All tools identical", "Links cannot be backed up", "Tar bans links"], 0, "Follow vs preserve.", "medium"),
            M("`chmod` on symlink without -h often affects...", ["The target, not the link (platform-dependent nuances)", "Only the link mode always", "Neither", "Only directories"], 0, "chmod follows by default often.", "medium"),
            T("Relative links with many `../` are hard to review; prefer shorter forms.", True, "Readable beats clever.", "medium"),
            M("Detect cycles with...", ["realpath/readlink loops detection / find -L care", "Only ls colors", "Only pwd", "Only du"], 0, "Cycle detection.", "medium"),
            M("When publishing dirs, rewrite links if...", ["Install prefix differs from build layout", "Names are short", "Using tar", "Using zip"], 0, "Relocate-aware links.", "medium"),
        ],
        [
            M("Race replacing a symlink atomically uses...", ["`ln -sfn` into place / rename swap patterns", "rm then ln with gaps", "chmod only", "touch only"], 0, "Atomic symlink replace.", "hard"),
            M("Security: luring through attacker-controlled symlink can...", ["Redirect writes to sensitive targets", "Only slow IO", "Only change colors", "Only affect man"], 0, "Symlink attacks.", "hard"),
            T("`openat` + `O_NOFOLLOW` mitigates some symlink follow races.", True, "Safe open flags.", "hard"),
            M("Container bind mounts + symlinks escaping...", ["Can surprise path confinement", "Are impossible", "Only affect zip", "Only affect make"], 0, "Escape via links.", "hard"),
            M("Git and symlinks: on Windows clones may...", ["Materialize as text files depending on settings", "Always be real links", "Become hard links", "Be deleted"], 0, "core.symlinks behavior.", "hard"),
            M("Build systems recording symlink digests must decide...", ["Hash text vs referent content", "Always skip", "Always follow network", "Always use size 0"], 0, "Hash policy.", "hard"),
            M("Recursive delete following links can...", ["Destroy targets outside the tree", "Only delete link text files harmlessly always", "Never follow", "Only clear modes"], 0, "Dangerous follow deletes.", "hard"),
            T("Relative link correctness can be unit-tested via temp trees + realpath.", True, "Test link layouts.", "hard"),
            M("Tooling that canonicalizes before storing may...", ["Convert intentional relatives to absolutes unexpectedly", "Improve portability always", "Disable links", "Clear targets"], 0, "Preserve intent.", "hard"),
            M("Lab: move a directory containing relative links and watch breaks.", ["Yes: feel the pitfall", "No: only read docs", "No: use absolute only always without understanding", "No: skip"], 0, "Experience the break.", "hard"),
        ],
    ),
    "flow": (
        [
            M("A pre-push checklist often includes...", ["Tests/lint/build sanity", "Only wallpaper choice", "Only reboot", "Only zip -r /"], 0, "Verify before push.", "easy"),
            M("`make` in a workflow usually...", ["Builds/tests via documented targets", "Replaces git", "Formats the kernel", "Clears $HOME"], 0, "Make as task runner.", "easy"),
            T("Checking `.env.example` exists helps onboard env expectations.", True, "Env template.", "easy"),
            M("Before push, `git status` shows...", ["Uncommitted/untracked changes", "Only remote CPU", "Only man", "Only zip"], 0, "Status first.", "easy"),
            M("Document required tools in...", ["README / CONTRIBUTING", "Only binary blobs", "Only /proc", "Only sticky /tmp"], 0, "Tooling docs.", "easy"),
            M("Fast feedback loops prefer...", ["Local tests before remote CI wait", "Only cloud", "Skipping tests", "Pushing secrets"], 0, "Shift left.", "easy"),
            T("Make targets like `test` / `lint` standardize commands.", True, "Common verbs.", "easy"),
            M("Env checklist includes...", ["Required variables present (not necessarily secret values in git)", "Committing all secrets", "Disabling PATH", "Deleting README"], 0, "Vars present.", "easy"),
            M("`make help` (if provided) lists...", ["Available targets", "Only PIDs", "Only users", "Only signals"], 0, "Self-documenting make.", "easy"),
            M("Pre-push hooks can...", ["Block bad pushes locally", "Replace CI entirely always", "Format disks", "Clear remotes"], 0, "Local gates.", "easy"),
        ],
        [
            M("CI should mirror local `make test` to avoid...", ["Works-on-my-machine drift", "Faster laptops", "Better docs", "More aliases"], 0, "Parity.", "medium"),
            M("Caching in CI must still allow...", ["Clean rebuild paths when needed", "Infinite stale caches", "Skipping locks", "Secret prints"], 0, "Cache + clean.", "medium"),
            T("Pin tool versions for reproducible workflows.", True, "Version pins.", "medium"),
            M("Changelog / PR checklist items catch...", ["Human process gaps automation misses", "CPU bugs only", "Disk firmware only", "GPU only"], 0, "Process checks.", "medium"),
            M("Feature flags in env let you...", ["Toggle behavior without recompile sometimes", "Hide README", "Disable make", "Clear git"], 0, "Env toggles.", "medium"),
            M("Secret scanning pre-push helps stop...", ["Accidental credential commits", "All bugs", "Slow tests", "Large binaries only"], 0, "Scan secrets.", "medium"),
            M("Matrix testing across versions belongs in...", ["CI workflow config", "Only local once", "Only README emoji", "Only tar"], 0, "CI matrices.", "medium"),
            T("Documenting required umask/file modes is rare but matters for tools.", True, "Environment assumptions.", "medium"),
            M("Failing fast locally with `make lint` reduces...", ["Round-trips to CI", "Code quality", "Test coverage needs", "README size"], 0, "Local lint.", "medium"),
            M("Workflow diagrams should show...", ["Build -> test -> package -> deploy gates", "Only editor themes", "Only office seats", "Only snack schedule"], 0, "Stage gates.", "medium"),
        ],
        [
            M("Hermetic builds aim to...", ["Control inputs so outputs reproduce", "Maximize network fetches always", "Rely on ambient tools only", "Skip lockfiles"], 0, "Hermeticity.", "hard"),
            M("Policy-as-code gates (OPA etc.) extend checklists by...", ["Automating compliance rules", "Replacing tests", "Deleting make", "Hiding logs"], 0, "Automated policy.", "hard"),
            T("Supply-chain attestations pair with release workflows.", True, "Attest artifacts.", "hard"),
            M("Flaky tests undermine checklists because...", ["They train people to ignore failures", "They speed CI", "They improve signal", "They pin versions"], 0, "Fix flakes.", "hard"),
            M("Monorepo affected-target selection must...", ["Still allow full builds periodically", "Only build nothing", "Skip tests always", "Ignore deps"], 0, "Selective + periodic full.", "hard"),
            M("Emergency hotfix workflow should still...", ["Record exceptions and follow-up CI", "Skip all reviews forever", "Disable logging", "Push --force to main casually"], 0, "Controlled exceptions.", "hard"),
            M("Env var sprawl is managed by...", ["Namespacing, docs, and validation schemas", "Exporting everything global", "Putting secrets in PS1", "Committing .env with values"], 0, "Govern env surface.", "hard"),
            T("Reproducible release tags include tool versions and content hashes.", True, "Release metadata.", "hard"),
            M("Local hooks vs CI: defense in depth means...", ["Both; either can be bypassed alone", "Only hooks", "Only CI", "Neither"], 0, "Multiple gates.", "hard"),
            M("Lab: write a 5-line pre-push checklist and run it once for real.", ["Yes: practice the gate", "No: memorize only", "No: skip", "No: automate secretly without docs"], 0, "Habit formation.", "hard"),
        ],
    ),
    "make": (
        [
            M("Make primarily reads...", ["A Makefile with targets, deps, recipes", "Only PATH", "Only git messages", "Only history"], 0, "Makefile drives make.", "easy"),
            M("Mark `clean` as `.PHONY` so that...", ["Make runs it even if a file named clean exists", "Make ignores it forever", "Tabs become spaces", "help disables"], 0, "PHONY = action targets.", "easy"),
            T("Bare `make` builds the default goal (often first/all).", True, "Default goal.", "easy"),
            M("Recipe lines must be indented with...", ["A real tab", "Two spaces only", "Markdown backticks", "No indent"], 0, "Tab required.", "easy"),
            M("`target: deps` means...", ["Build target when older than deps / missing", "Always delete deps", "Ignore deps", "Only link"], 0, "Dependency rule.", "easy"),
            M("`make -n` / `--dry-run` ...", ["Prints recipes without running them", "Formats disks", "Deletes targets", "Requires root"], 0, "Dry run.", "easy"),
            T("Variables like `CC=gcc` parameterize toolchains.", True, "Make variables.", "easy"),
            M("`$@` in a recipe is...", ["The target name", "All deps", "First dep only", "The Makefile path"], 0, "Automatic var $@.", "easy"),
            M("`$^` typically expands to...", ["All prerequisites", "Only the target", "Only the first source stem", "The shell PID"], 0, "$^ all prereqs.", "easy"),
            M("`make {t}` builds...", ["Target {t}", "Only clean", "Only help", "Only zip"], 0, "Named target.", "easy"),
        ],
        [
            M("Pattern rule `%.o: %.c` teaches Make how to...", ["Build objects from C sources", "Zip files", "Kill jobs", "Set umask"], 0, "Pattern rules.", "medium"),
            M("`make -j{n}` runs...", ["Up to {n} jobs in parallel", "Exactly one recipe forever", "Only clean", "Only help"], 0, "Parallel make.", "medium"),
            T("`$(MAKE)` recursive invocation is preferred over bare `make`.", True, "Use $(MAKE).", "medium"),
            M("Order-only prerequisites `|` are for...", ["Deps that shouldn't force rebuild by timestamp alone", "Phony only", "Deleting targets", "Setting PATH"], 0, "Order-only.", "medium"),
            M("`VPATH` / `vpath` search for...", ["Prerequisites in other dirs", "Man pages", "Only libraries in /lib forever", "History"], 0, "VPATH search.", "medium"),
            M("Immediate vs deferred expansion (`:=` vs `=`) matters when...", ["RHS has costly/functions side effects", "Names are short", "Using tabs", "Using PHONY"], 0, "Expansion timing.", "medium"),
            M("`include` other makefiles to...", ["Share rules/config", "Disable make", "Clear targets", "Force zip"], 0, "include.", "medium"),
            T("A missing include can be tolerated with `-include`.", True, "Optional include.", "medium"),
            M("Secondary expansion / complex eval is...", ["Powerful but easy to overcomplicate", "Required for hello world", "Faster always", "POSIX mandatory everywhere"], 0, "Keep makefiles readable.", "medium"),
            M("Silent recipes start with `@` to...", ["Suppress echo of the command", "Disable errors", "Force -j", "Skip deps"], 0, "@ silences.", "medium"),
        ],
        [
            M("Correct parallel builds require...", ["Complete dependency edges", "More -j only", "Disabling PHONY", "Ignoring headers"], 0, "Deps enable -j.", "hard"),
            M("Generated headers need careful rules to avoid...", ["Incomplete first builds / races", "Faster rebuilds only", "Smaller logs", "Better colors"], 0, "Genfile deps.", "hard"),
            T("`make -B` forces rebuild ignoring timestamps.", True, "Unconditional remake.", "hard"),
            M("Recursive make considered harmful often because...", ["Lost global dependency graph", "It is faster always", "It bans VPATH", "It clears PHONY"], 0, "Non-recursive patterns preferred.", "hard"),
            M("`$(wildcard ...)` evaluated at parse can miss...", ["Files created later during the build", "All existing files", "Only dirs", "Only PHONY"], 0, "Wildcard timing.", "hard"),
            M("Jobserver protocols matter when...", ["Nested makes share -j tokens", "Using only -j1", "No recursion", "Only cmake"], 0, "Jobserver.", "hard"),
            M("Remaking makefiles themselves can cause...", ["Restart of make with updated rules", "Kernel panic always", "Deleted sources", "Disabled PATH"], 0, "Makefile remake.", "hard"),
            T("POSIX make is a subset; GNU extensions need documentation.", True, "Portability note.", "hard"),
            M("Ensuring recipes fail correctly uses...", ["set -e in shell / make's fail-on-error defaults awareness", "Appending `|| true` everywhere", "Ignoring statuses", "Using -k always in CI"], 0, "Fail loud.", "hard"),
            M("Lab: add a `help` target that greps ## comments.", ["Yes: self-documenting Makefile", "No: hide targets", "No: only README", "No: skip"], 0, "Document targets.", "hard"),
        ],
    ),
    "dry": (
        [
            M("Dry-run means...", ["Show what would happen without doing it", "Delete faster", "Skip reading docs", "Force root"], 0, "Rehearse without effect.", "easy"),
            M("`make -n` is a dry-run for...", ["Make recipes", "rm only", "chmod only", "kill only"], 0, "make dry-run.", "easy"),
            T("Many CLIs offer `--dry-run` / `-n` flags.", True, "Common pattern.", "easy"),
            M("Before `rm -rf`, a dry mindset says...", ["List/match first", "Add sudo first", "Disable networking first", "chmod 777 first"], 0, "Preview deletes.", "easy"),
            M("`rsync --dry-run` shows...", ["What would transfer/delete", "Only version", "Only man", "Only speed"], 0, "rsync preview.", "easy"),
            M("Dry-run matters most when commands are...", ["Destructive or expensive", "Only pwd", "Only echo hi", "Only date"], 0, "High-impact ops.", "easy"),
            T("Printing the expanded command is a form of dry-run.", True, "Echo plans.", "easy"),
            M("`git push --dry-run` checks...", ["What would be pushed", "Deletes remotes", "Formats", "Clears hooks"], 0, "Push rehearsal.", "easy"),
            M("In scripts, a `DRY_RUN=1` guard can...", ["Print instead of execute", "Force root", "Clear PATH", "Disable set -e"], 0, "Dry-run switch.", "easy"),
            M("Why dry-run before prod apply?", ["Catch mistakes cheaply", "Slow intentionally always", "Satisfy fonts", "Skip reviews"], 0, "Cheap mistakes.", "easy"),
        ],
        [
            M("Dry-run fidelity gaps happen when...", ["Preview path differs from execute path", "Flags are identical", "Tools are pure echo", "Nothing changes ever"], 0, "Preview must match reality.", "medium"),
            M("`terraform plan` is essentially...", ["A dry-run of infra changes", "An apply", "A destroy always", "A format only"], 0, "Plan before apply.", "medium"),
            T("Some tools' dry-run still contacts servers (read-only).", True, "Side effects vary.", "medium"),
            M("Make -n may not show...", ["Recipes of targets it considers up to date", "Any variables", "Any targets", "Tabs"], 0, "Up-to-date silence.", "medium"),
            M("Wrapping dangerous cmds with `echo` first helps but watch...", ["Quoting differences vs real execution", "Echo disables disks", "Echo setsuid", "Echo clears PATH"], 0, "Echo != eval parity.", "medium"),
            M("Permission errors may appear only on execute, so dry-run...", ["Might succeed while apply fails", "Guarantees apply works", "Sets modes", "Clears ACL"], 0, "Authz at apply time.", "medium"),
            M("Batch delete: `find ... -print` before `-delete` is...", ["A dry mindset", "Slower wrongly", "Required by kernel", "Forbidden"], 0, "Print then delete.", "medium"),
            T("CI can run dry-run modes on PRs and apply on main.", True, "Pipeline stages.", "medium"),
            M("Idempotent tools make dry-run nicer because...", ["Re-running apply is safer", "First run always fails", "State is random", "Logs disappear"], 0, "Idempotency.", "medium"),
            M("Document whether dry-run is deep or shallow so that...", ["Users know residual risk", "Users skip apply", "Logs shrink", "Make speeds"], 0, "Honest docs.", "medium"),
        ],
        [
            M("Partial dry-runs that skip hidden side effects are...", ["Dangerous false confidence", "Better than full", "Required", "Identical to apply"], 0, "False confidence.", "hard"),
            M("Time-dependent dry-runs can mismatch apply when...", ["State changes between plan and apply", "Clocks are NTP synced only", "Files are static forever", "No network"], 0, "Plan-apply race.", "hard"),
            T("Transactional apply with rollback beats dry-run alone for some systems.", True, "Transactions.", "hard"),
            M("Security: dry-run output may leak...", ["Sensitive planned values", "Only public data always", "Nothing ever", "Only timings"], 0, "Redact plans.", "hard"),
            M("Ensuring dry-run code paths share logic with apply avoids...", ["Drift bugs", "Faster CI", "Smaller binaries", "Better fonts"], 0, "One code path.", "hard"),
            M("`set -x` traces are not dry-run because...", ["They still execute", "They never execute", "They only print help", "They clear disks"], 0, "xtrace executes.", "hard"),
            M("Filesystem snapshots enable a stronger pattern:...", ["Apply then roll back if needed", "Skip backups", "Disable checks", "Always dry-run forever"], 0, "Snapshot rollback.", "hard"),
            T("Orchestrators often separate diff/plan permissions from apply permissions.", True, "Least privilege stages.", "hard"),
            M("When a tool lacks dry-run, you can...", ["Operate on a copy/staging first", "Run as root on prod immediately", "Disable logs", "Ignore backups"], 0, "Staging substitute.", "hard"),
            M("Lab: implement DRY_RUN in a tiny script wrapping rm/mv.", ["Yes: practice the guard", "No: always run live", "No: use -9", "No: skip"], 0, "Build the habit.", "hard"),
        ],
    ),
    "log": (
        [
            M("Log triage starts by...", ["Finding error/fail lines near the failure time", "Deleting all logs", "Rebooting first always", "Ignoring timestamps"], 0, "Search near failure.", "easy"),
            M("`grep -i error {g}` finds...", ["Case-insensitive error lines", "Only exact ERROR", "Only warnings", "Only PIDs"], 0, "Case-insensitive search.", "easy"),
            T("Exit status plus logs together explain failures better than either alone.", True, "Status + logs.", "easy"),
            M("`tail -n 50 {g}` shows...", ["Last 50 lines", "First 50 lines", "Only errors", "Only dates"], 0, "tail end of file.", "easy"),
            M("`less +/error {g}` jumps toward...", ["Matching error", "EOF only", "Binary only", "Man only"], 0, "Search in less.", "easy"),
            M("Timestamps in logs help you...", ["Correlate events", "Set umask", "Color ls", "Name hosts"], 0, "Time correlation.", "easy"),
            T("Increasing verbosity (`-v`) can aid triage temporarily.", True, "More detail.", "easy"),
            M("Distinguish stdout vs stderr when...", ["Errors may be on stderr only", "They are identical always", "Logs ban stderr", "make merges always silently"], 0, "Check both streams.", "easy"),
            M("`journalctl` (systemd) is for...", ["System/journal logs", "Only zip", "Only make", "Only history"], 0, "Journal queries.", "easy"),
            M("A minimal triage note includes...", ["Command, status, key log lines", "Only 'failed'", "Only screenshots of desktop", "Only emoji"], 0, "Reproducible notes.", "easy"),
        ],
        [
            M("`grep -RIn error .` recursively finds...", ["Matches with file:line", "Only filenames", "Only binary", "Only dirs"], 0, "Recursive grep.", "medium"),
            M("Rate-limited logs can hide...", ["Repeated critical errors", "All successes", "Timestamps", "PIDs always"], 0, "Rate limits obscure.", "medium"),
            T("`set -x` traces may flood logs; use briefly.", True, "xtrace volume.", "medium"),
            M("Correlate multi-service failures using...", ["Shared request IDs / timestamps", "Only hostnames", "Only colors", "Only file size"], 0, "Correlation IDs.", "medium"),
            M("Binary/core dumps complement logs when...", ["Crash needs stack evidence", "Logs already perfect", "Disk full only", "Network only"], 0, "Cores for crashes.", "medium"),
            M("`dmesg` helps for...", ["Kernel/driver level clues", "App ASCII only", "Make recipes only", "Zip lists"], 0, "Kernel ring buffer.", "medium"),
            M("Log rotation may mean the active file...", ["Is new/empty while history is archived", "Never changes name", "Deletes evidence always", "Disables grep"], 0, "Check rotated files.", "medium"),
            T("Structured JSON logs enable easier field queries.", True, "Structured logging.", "medium"),
            M("Redact secrets in logs because...", ["Logs are widely retained/shared", "Logs are never stored", "Encryption is automatic always", "grep bans secrets"], 0, "Don't log secrets.", "medium"),
            M("First useful question: ...", ["What changed recently?", "What font?", "What snack?", "What wallpaper?"], 0, "Change hypothesis.", "medium"),
        ],
        [
            M("Heisenbugs that vanish under debug logs suggest...", ["Timing/race sensitivity", "Fixed root cause", "Impossible bugs", "Only UI issues"], 0, "Probe effect.", "hard"),
            M("Clock skew across hosts breaks...", ["Timestamp correlation", "grep -i", "tail -n", "less"], 0, "Sync clocks.", "hard"),
            T("Sampling/aggregation pipelines can drop the exact failing event.", True, "Cardinality limits.", "hard"),
            M("Core + debug symbols needed because...", ["Addresses map to functions", "Logs include source always", "Kernels ban cores", "Make embeds all source"], 0, "Symbols for stacks.", "hard"),
            M("Privilege-separated logs may hide fields unless...", ["You have access to the right stream", "You use sudo rm", "You disable SELinux casually", "You chmod 777 /var"], 0, "Access boundaries.", "hard"),
            M("Causal graphs beat single-line greps when...", ["Failures cascade across services", "One process always", "No network", "Only local echo"], 0, "Distributed causality.", "hard"),
            M("Preserve failure artifacts in CI by...", ["Uploading logs/binaries on failure", "Deleting on fail", "Only printing 'failed'", "Disabling artifacts"], 0, "Keep evidence.", "hard"),
            T("Log injection via unsanitized user agents can forge fake events.", True, "Validate/encode.", "hard"),
            M("After fix, add a regression test/log assert so that...", ["The failure mode is detected next time", "Logs grow forever uselessly", "CI slows without value", "Alerts mute"], 0, "Lock the fix.", "hard"),
            M("Lab: take a failing command, capture status+tail, write 3-line hypothesis.", ["Yes: structured triage", "No: reboot only", "No: rm logs", "No: ignore status"], 0, "Practice triage notes.", "hard"),
        ],
    ),
    "env": (
        [
            M("A `.env` file typically stores...", ["Key=value configuration for apps", "Compiled binaries", "Man pages", "Kernel modules"], 0, ".env = config pairs.", "easy"),
            M("`.env` should usually be...", ["Gitignored if it holds secrets", "Committed with production secrets", "World-executable", "Named Makefile"], 0, "Don't commit secrets.", "easy"),
            T("`.env.example` documents required keys without secret values.", True, "Template without secrets.", "easy"),
            M("`export {e}={v}` sets...", ["An environment variable in the shell", "A man section", "A umask only", "A signal"], 0, "export publishes env.", "easy"),
            M("`echo ${e}` prints...", ["The value of {e}", "Only PID", "Only cwd", "Only mode"], 0, "Expand env/shell var.", "easy"),
            M("Apps often load `.env` via...", ["Libraries/loaders, not magic by the kernel", "The CPU microcode", "man automatically", "zip central directory"], 0, "Loaders read .env.", "easy"),
            T("Environment variables are process state inherited by children.", True, "Inheritance model.", "easy"),
            M("Spaces in values usually need...", ["Quotes", "Tabs only", "Root", "Sticky bit"], 0, "Quote values.", "easy"),
            M("`unset {e}` removes...", ["Variable {e} from the environment/shell", "A file named {e}", "User {e}", "Signal {e}"], 0, "unset clears.", "easy"),
            M("Prefer `.env.example` keys matching...", ["What the app actually reads", "Random old keys", "Only PATH", "Only HOME"], 0, "Keep templates accurate.", "easy"),
        ],
        [
            M("Precedence often is...", ["Process env / flags override file defaults (tool-specific)", "File always wins", "Random", "Only Makefile"], 0, "Know override order.", "medium"),
            M("Multiline values in `.env` are...", ["Tool-dependent; check your loader", "Universal identical", "Forbidden by kernels", "Stored in PATH"], 0, "Dialect differences.", "medium"),
            T("`set -a; source .env; set +a` can export sourced vars (careful).", True, "allexport pattern.", "medium"),
            M("Never `source` untrusted `.env` because...", ["It can execute shell code if not a strict parser", "source only reads integers", "env files cannot harm", "bash ignores source"], 0, "Parsing vs sourcing.", "medium"),
            M("Docker `--env-file` loads...", ["Env pairs into the container", "Tar archives", "Man pages", "Make rules"], 0, "Container env files.", "medium"),
            M("Differentiate config vs secrets by...", ["Separate stores / permissions / injection methods", "Putting both in README", "Using the same 777 file", "Exporting in PS1"], 0, "Split secret handling.", "medium"),
            M("Empty string vs unset can...", ["Change app behavior differently", "Always identical", "Crash kernel", "Clear disks"], 0, "Empty != unset.", "medium"),
            T("Shell startup files exporting secrets risk leakage to child processes.", True, "Broad inheritance.", "medium"),
            M("`env` command runs a program with...", ["A modified environment", "Only root", "Cleared disks", "Disabled networking always"], 0, "env wrapper.", "medium"),
            M("CI secret variables should be...", ["Masked/scoped, not printed", "Echoed in logs for debug always", "Committed", "World-readable files"], 0, "CI secret hygiene.", "medium"),
        ],
        [
            M("12-factor style prefers env config because...", ["Deploy-time binding without rebuild", "It replaces all files", "It disables 12-factor", "It bans Docker"], 0, "Env as config.", "hard"),
            M("Env size limits can break...", ["Large values / many keys", "Only short ASCII", "Only PATH", "Only HOME"], 0, "ARG_MAX/env limits.", "hard"),
            T("Dotenv parsers disagree on export keyword, comments, and expansion.", True, "Dialect hell.", "hard"),
            M("Secret managers inject at runtime to avoid...", ["Long-lived plaintext .env on disk", "All configuration", "TLS", "IAM"], 0, "Runtime inject.", "hard"),
            M("Windows vs Unix env case sensitivity means...", ["Portability bugs on key case", "Identical always", "Bash ignores case always", "Make bans env"], 0, "Case rules differ.", "hard"),
            M("Cleaning env for tests (`env -i`) needs...", ["Re-supplying required vars explicitly", "No vars ever", "Only HOME deleted", "Only PATH deleted"], 0, "Minimal + explicit.", "hard"),
            M("Expansion of `$OTHER` inside .env values may...", ["Happen in some loaders, not others", "Always happen identically", "Never happen", "Only in make"], 0, "Expansion divergence.", "hard"),
            T("Leaking env via `/proc/self/environ` is a reason to drop secrets after read.", True, "Proc environ visibility.", "hard"),
            M("Feature flags in env should be...", ["Documented typed values, not tribal lore", "Random strings undocumented", "Only in chat", "Only in history"], 0, "Document flags.", "hard"),
            M("Lab: create `.env.example`, gitignore `.env`, load safely in a script.", ["Yes: complete literacy loop", "No: commit secrets", "No: source blindly untrusted", "No: skip example"], 0, "End-to-end env literacy.", "hard"),
        ],
    ),
}


MODULES = [
    ("module01-vfs-terminal", "Virtual filesystem terminal", "vfs", "vfs-terminal"),
    ("module02-man-help-lab", "man / --help discoverability", "man", "man-help-lab"),
    ("module03-path-abs-rel", "Absolute vs relative paths", "path", "path-abs-rel"),
    ("module04-wildcards-globs", "Globs & wildcards", "glob", "wildcards-globs"),
    ("module05-file-types-lab", "File types & links", "ftype", "file-types-lab"),
    ("module06-realpath-resolve", "realpath / readlink", "rpath", "realpath-resolve"),
    ("module07-permissions", "Permissions, umask, PATH", "perm", "permissions"),
    ("module08-dotfiles-lab", "Dotfiles & config homes", "dot", "dotfiles-lab"),
    ("module09-ps-kill-lab", "Process list & signals", "ps", "ps-kill-lab"),
    ("module10-job-control-lab", "Job control", "job", "job-control-lab"),
    ("module11-pipes", "Pipes, redirection, xargs", "pipe", "pipes"),
    ("module12-sort-uniq-cut", "sort / uniq / cut", "sort", "sort-uniq-cut"),
    ("module13-here-doc-lab", "Here-doc / here-string", "heredoc", "here-doc-lab"),
    ("module14-shell-history", "Shell history & reverse-search", "hist", "shell-history"),
    ("module15-alias-lab", "Alias & functions", "alias", "alias-lab"),
    ("module16-scripting", "Script control flow", "script", "scripting"),
    ("module17-exit-status-lab", "Exit status & && / ||", "exit", "exit-status-lab"),
    ("module18-safe-scripting", "Safe scripting", "safe", "safe-scripting"),
    ("module19-project-archives", "Project layout, archives, sed & diff", "proj", "project-archives"),
    ("module20-zip-vs-tar", "tar vs zip", "tar", "zip-vs-tar"),
    ("module21-backup-clean", "Backup & clean-build", "bak", "backup-clean"),
    ("module22-link-relative", "Relative symlink pitfalls", "link", "link-relative"),
    ("module23-workflow", "Pre-push / Make / env checklist", "flow", "workflow"),
    ("module24-make-basics", "Makefile basics", "make", "make-basics"),
    ("module25-dry-run-lab", "Dry-run mindset", "dry", "dry-run-lab"),
    ("module26-log-triage", "Log / failure triage", "log", "log-triage"),
    ("module27-env-file-lab", ".env literacy", "env", "env-file-lab"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for mid, title, prefix, _tool in MODULES:
        easy, medium, hard = TOPICS[prefix]
        seeded = seed_builders(mid)
        easy = list(seeded) + list(easy)
        data = bank(mid, title, prefix, easy, medium, hard)
        path = OUT / f"{mid}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # count by difficulty
        counts = {"easy": 0, "medium": 0, "hard": 0}
        for it in data["items"]:
            counts[it["difficulty"]] = counts.get(it["difficulty"], 0) + 1
        summary.append((path.name, len(data["items"]), counts))
        print(f"wrote {path.name} ({len(data['items'])} items: {counts['easy']}e/{counts['medium']}m/{counts['hard']}h)")
    print(f"\nDone: {len(summary)} modules, TARGET={TARGET} per difficulty")


if __name__ == "__main__":
    main()
