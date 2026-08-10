#!/usr/bin/env bash
# Bump repo-root VERSION (integer). Prints new MVP label to stdout.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="$ROOT/VERSION"
n="$(tr -d '[:space:]' <"$FILE" 2>/dev/null || echo 0)"
if ! [[ "$n" =~ ^[0-9]+$ ]]; then
  n=0
fi
n=$((n + 1))
printf '%s\n' "$n" >"$FILE"
echo "MVP${n}"
