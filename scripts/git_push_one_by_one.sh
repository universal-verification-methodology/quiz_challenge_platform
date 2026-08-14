#!/usr/bin/env bash
# Add, commit, and push files one at a time to reduce git memory pressure.
#
# Usage:
#   ./scripts/git_push_one_by_one.sh --path content/learn_verilog/media/videos
#   ./scripts/git_push_one_by_one.sh --path content/learn_verilog/media/videos --dry-run
#   ./scripts/git_push_one_by_one.sh --from-list files.txt
#   ./scripts/git_push_one_by_one.sh --path content/learn_verilog/questions --no-push
#
# Options:
#   --path DIR       Root directory to scan (default: repo root, tracked changes only)
#   --glob PAT       Only files matching PAT (find -name), e.g. '*.mp4'
#   --from-list FILE Read one path per line from FILE (relative to repo root)
#   --branch NAME    Push to this branch (default: current branch)
#   --remote NAME    Remote name (default: origin)
#   --dry-run        Print actions only; do not add/commit/push
#   --no-push        Add + commit each file, but skip push
#   --limit N        Stop after N files
#   --include-untracked  Also pick up untracked files under --path (default: on)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATH_ARG=""
GLOB=""
LIST_FILE=""
BRANCH="$(git branch --show-current 2>/dev/null || true)"
REMOTE="origin"
DRY_RUN=0
NO_PUSH=0
LIMIT=0
INCLUDE_UNTRACKED=1

usage() {
  sed -n '2,12p' "$0"
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) PATH_ARG="${2:-}"; shift 2 ;;
    --glob) GLOB="${2:-}"; shift 2 ;;
    --from-list) LIST_FILE="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --remote) REMOTE="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-push) NO_PUSH=1; shift ;;
    --limit) LIMIT="${2:-0}"; shift 2 ;;
    --include-untracked) INCLUDE_UNTRACKED=1; shift ;;
    --tracked-only) INCLUDE_UNTRACKED=0; shift ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown option: $1" >&2; usage 1 ;;
  esac
done

if [[ -z "$BRANCH" ]]; then
  echo "error: not inside a git repo or detached HEAD" >&2
  exit 1
fi

collect_files() {
  local -n _out=$1
  _out=()

  if [[ -n "$LIST_FILE" ]]; then
    if [[ ! -f "$LIST_FILE" ]]; then
      echo "error: list file not found: $LIST_FILE" >&2
      exit 1
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line//$'\r'/}"
      [[ -z "$line" || "$line" =~ ^# ]] && continue
      if [[ -f "$line" ]]; then
        _out+=("$line")
      else
        echo "warn: skip missing file from list: $line" >&2
      fi
    done < "$LIST_FILE"
    return
  fi

  if [[ -n "$PATH_ARG" ]]; then
    if [[ ! -d "$PATH_ARG" ]]; then
      echo "error: path not found: $PATH_ARG" >&2
      exit 1
    fi
    local find_args=(find "$PATH_ARG" -type f)
    [[ -n "$GLOB" ]] && find_args+=(-name "$GLOB")
    mapfile -t _out < <("${find_args[@]}" | sort)
    return
  fi

  # Default: changed files in working tree (modified + optional untracked).
  local status_lines=()
  mapfile -t status_lines < <(git status --porcelain)
  for line in "${status_lines[@]}"; do
    [[ -z "$line" ]] && continue
    local code="${line:0:2}"
    local file="${line:3}"
    # Rename: "old -> new" — take new path.
    if [[ "$file" == *" -> "* ]]; then
      file="${file##* -> }"
    fi
    if [[ "$code" == "??" && "$INCLUDE_UNTRACKED" -eq 0 ]]; then
      continue
    fi
    if [[ -f "$file" ]]; then
      _out+=("$file")
    fi
  done
}

should_skip() {
  local f="$1"
  if git check-ignore -q "$f" 2>/dev/null; then
    return 0
  fi
  if [[ -n "$GLOB" && "$f" != $GLOB ]]; then
    # shellcheck disable=SC2254
    case "$(basename "$f")" in
      $GLOB) ;;
      *) return 0 ;;
    esac
  fi
  return 1
}

FILES=()
collect_files FILES

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files to process."
  exit 0
fi

echo "Repo:   $ROOT"
echo "Branch: $BRANCH"
echo "Remote: $REMOTE"
echo "Files:  ${#FILES[@]}"
echo

count=0
ok=0
skip=0
fail=0

for file in "${FILES[@]}"; do
  if should_skip "$file"; then
    echo "SKIP (ignored/filtered): $file"
    skip=$((skip + 1))
    continue
  fi

  count=$((count + 1))
  if [[ "$LIMIT" -gt 0 && "$count" -gt "$LIMIT" ]]; then
    echo "Limit $LIMIT reached; stopping."
    break
  fi

  msg="Add/update: $file"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN [$count] git add -- $file"
    echo "DRY-RUN [$count] git commit -m \"$msg\""
    if [[ "$NO_PUSH" -eq 0 ]]; then
      echo "DRY-RUN [$count] git push $REMOTE $BRANCH"
    fi
    ok=$((ok + 1))
    continue
  fi

  echo "[$count/${#FILES[@]}] add: $file"
  git add -- "$file"

  # Commit only if this file is staged (skip if already committed / unchanged).
  if git diff --cached --quiet -- "$file"; then
    echo "  skip commit (nothing staged for this file)"
    skip=$((skip + 1))
    continue
  fi

  git commit -m "$msg"

  if [[ "$NO_PUSH" -eq 0 ]]; then
    echo "  push: $REMOTE $BRANCH"
    if ! git push "$REMOTE" "$BRANCH"; then
      echo "  FAIL push for: $file" >&2
      fail=$((fail + 1))
      continue
    fi
  fi

  ok=$((ok + 1))
done

echo
echo "Done. ok=$ok skip=$skip fail=$fail processed=$count"
exit $(( fail > 0 ? 1 : 0 ))
