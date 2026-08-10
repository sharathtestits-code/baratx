#!/usr/bin/env bash
# Print current MVP label from VERSION (e.g. MVP1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
n="$(tr -d '[:space:]' <"$ROOT/VERSION" 2>/dev/null || echo 1)"
if ! [[ "$n" =~ ^[0-9]+$ ]]; then
  n=1
fi
echo "MVP${n}"
