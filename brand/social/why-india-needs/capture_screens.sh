#!/usr/bin/env bash
# Refresh product screens for render_why_india_needs.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="$ROOT/brand/social/why-india-needs/screens"
WHATSAPP="$ROOT/brand/social/whatsapp/screens"
HOME="$ROOT/brand/product/home-v1"
mkdir -p "$OUT"

UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
capture() {
  local url="$1" out="$2"
  if command -v google-chrome >/dev/null 2>&1; then
    timeout 25s google-chrome --headless=new --disable-gpu --hide-scrollbars \
      --window-size=390,844 --force-device-scale-factor=3 \
      --user-agent="$UA" --virtual-time-budget=8000 \
      --screenshot="$out" "$url" 2>/dev/null || true
  fi
}

capture "https://barathx.com/" "$OUT/landing-live.png"
capture "https://barathx.com/signup" "$OUT/signup.png"

cp -f "$WHATSAPP/bx-site-arenas.jpg" "$OUT/arenas.jpg"
cp -f "$WHATSAPP/bx-site-live.jpg" "$OUT/live.jpg"
cp -f "$WHATSAPP/bx-site-square-raw.jpg" "$OUT/square.jpg"
cp -f "$HOME/home-returning-user.png" "$OUT/home-returning.png"

[[ -f "$OUT/landing-live.png" ]] || cp -f "$WHATSAPP/bx-site-landing.png" "$OUT/landing-live.png"
[[ -f "$OUT/signup.png" ]] || cp -f "$WHATSAPP/bx-site-signup.png" "$OUT/signup.png"

ls -la "$OUT"
