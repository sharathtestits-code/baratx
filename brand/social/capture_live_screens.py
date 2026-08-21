#!/usr/bin/env python3
"""Capture live mobile screenshots from barathx.com for soft-launch social stills."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "whatsapp" / "screens" / "live-2026-08-19"
OUT.mkdir(parents=True, exist_ok=True)

# Mobile viewport similar to prior captures
VP = {"width": 390, "height": 844, "device_scale_factor": 2}

SHOTS = [
    ("landing-mobile.png", "https://barathx.com/", None),
    ("get-app-mobile.png", "https://barathx.com/get-app/", None),
    ("signup-mobile.png", "https://barathx.com/signup", None),
    ("login-mobile.png", "https://barathx.com/login?method=phone", None),
    ("login-email-mobile.png", "https://barathx.com/login?method=email", None),
    ("search-mobile.png", "https://barathx.com/search", None),
    ("explore-mobile.png", "https://barathx.com/search", None),  # Explore = Search in product
    ("home-mobile.png", "https://barathx.com/home", None),
    ("feed-or-root-mobile.png", "https://barathx.com/feed", None),
    ("arenas-mobile.png", "https://barathx.com/arenas", None),
    ("spaces-mobile.png", "https://barathx.com/spaces", None),
    ("rewards-mobile.png", "https://barathx.com/rewards", None),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VP["width"], "height": VP["height"]},
            device_scale_factor=VP["device_scale_factor"],
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
            is_mobile=True,
            has_touch=True,
        )
        page = context.new_page()
        for name, url, wait_sel in SHOTS:
            print(f"→ {name} {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception as exc:  # noqa: BLE001
                print(f"  warn goto: {exc}")
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(1800)
            if wait_sel:
                try:
                    page.wait_for_selector(wait_sel, timeout=8000)
                except Exception:
                    pass
            # Dismiss cookie/banners if any
            for sel in ("button:has-text('Accept')", "button:has-text('Got it')"):
                try:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=500):
                        loc.click(timeout=1000)
                except Exception:
                    pass
            out = OUT / name
            page.screenshot(path=str(out), full_page=False)
            print(f"  wrote {out} ({out.stat().st_size} bytes)")
        browser.close()
    print(f"Done → {OUT}")


if __name__ == "__main__":
    main()
