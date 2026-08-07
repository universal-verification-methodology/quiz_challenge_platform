#!/usr/bin/env bash
# Serve the quiz challenge platform locally (static site).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PORT="${PORT:-18080}"
HOST="${HOST:-127.0.0.1}"
OPEN_BROWSER="${OPEN_BROWSER:-1}"

pick_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
  elif command -v py >/dev/null 2>&1; then
    echo py
  elif command -v python >/dev/null 2>&1; then
    echo python
  else
    echo ""
  fi
}

PY="$(pick_python)"
if [[ -z "$PY" ]]; then
  echo "error: need python3 (or py / python) on PATH" >&2
  exit 1
fi

URL="http://${HOST}:${PORT}/"
echo "Quiz challenge platform"
echo "  root: $ROOT"
echo "  url:  $URL"
echo "  short quest: ${URL}challenge.html?short=1&restart=1"
echo "  full quest:  ${URL}challenge.html?restart=1"
echo "Ctrl+C to stop."
echo

if [[ "$OPEN_BROWSER" == "1" ]]; then
  if command -v wslview >/dev/null 2>&1; then
    wslview "$URL" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 || true
  elif command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start "" "$URL" >/dev/null 2>&1 || true
  fi
fi

if [[ "$PY" == "py" ]]; then
  exec py -3 -m http.server "$PORT" --bind "$HOST"
else
  exec "$PY" -m http.server "$PORT" --bind "$HOST"
fi
