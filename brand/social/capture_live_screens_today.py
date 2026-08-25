#!/usr/bin/env python3
"""Capture FRESH mobile screens for today's social creatives.

ALWAYS capture into live-YYYY-MM-DD. Never point reels at older live-* folders.

Sources:
  - Production https://barathx.com — guest landing / login / signup
  - Local latest UI http://127.0.0.1:5173 — authenticated Square / Home / Arenas / Live / menu
    (requires local API on :8000 with OFFICIAL_ACCOUNT_PASSWORD seed login)
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
TODAY = date.today().isoformat()
OUT = ROOT / "brand" / "social" / "whatsapp" / "screens" / f"live-{TODAY}"
OUT.mkdir(parents=True, exist_ok=True)

VP = {"width": 390, "height": 844}
DSF = 2
LOCAL = "http://127.0.0.1:5173"
PROD = "https://barathx.com"
API = "http://127.0.0.1:8000"
SEED_USER = "baratx"
SEED_PASS = os.environ.get("OFFICIAL_ACCOUNT_PASSWORD", "BarathXSeed2026!")


def api_token() -> str:
    req = urllib.request.Request(
        f"{API}/auth/login/email",
        data=json.dumps({"email": SEED_USER, "password": SEED_PASS}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())["access_token"]


def shot(page, name: str) -> None:
    path = OUT / name
    page.wait_for_timeout(700)
    page.screenshot(path=str(path), full_page=False, type="png")
    print(f"  wrote {path.name} ({path.stat().st_size} bytes)")


def goto(page, url: str) -> None:
    print(f"→ {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
    except Exception as exc:  # noqa: BLE001
        print(f"  warn: {exc}")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(900)


def dismiss(page) -> None:
    for sel in (
        "button:has-text('Got it')",
        "button:has-text('Skip')",
        "button:has-text('Continue')",
        "button[aria-label='Close']",
    ):
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=400):
                loc.click(timeout=800)
                page.wait_for_timeout(300)
        except Exception:
            pass


def main() -> None:
    token = api_token()
    print(f"OUT={OUT}")
    init = f"""
      localStorage.setItem('iv_token', {json.dumps(token)});
      localStorage.setItem('bx_nav_tour_done', '1');
      localStorage.setItem('bx_security_trust_seen_v1', '1');
      localStorage.setItem('security_trust_seen', '1');
      localStorage.setItem('bx_tour_done', '1');
      localStorage.setItem('plaza_tour_done', '1');
      localStorage.setItem('bx_onboarding_done', '1');
      localStorage.setItem('theme_onboarding_done', '1');
    """
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
        "Mobile/15E148 Safari/604.1"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        guest = browser.new_context(
            viewport=VP, device_scale_factor=DSF, is_mobile=True, has_touch=True, user_agent=ua
        )
        page = guest.new_page()
        for name, url in (
            ("landing-mobile.png", f"{PROD}/"),
            ("login-mobile.png", f"{PROD}/login"),
            ("signup-mobile.png", f"{PROD}/signup"),
        ):
            goto(page, url)
            dismiss(page)
            shot(page, name)
        guest.close()

        auth = browser.new_context(
            viewport=VP, device_scale_factor=DSF, is_mobile=True, has_touch=True, user_agent=ua
        )
        auth.add_init_script(init)
        apage = auth.new_page()

        for name, path in (
            ("home-mobile.png", "/home"),
            ("square-mobile.png", "/feed"),
            ("feed-mobile.png", "/feed"),
            ("arenas-mobile.png", "/arenas"),
            ("live-mobile.png", "/spaces"),
            ("spaces-mobile.png", "/spaces"),
            ("search-mobile.png", "/search"),
            ("explore-mobile.png", "/search"),
            ("rewards-mobile.png", "/rewards"),
        ):
            goto(apage, LOCAL + path)
            dismiss(apage)
            shot(apage, name)

        # Square scroll beats
        goto(apage, f"{LOCAL}/feed")
        dismiss(apage)
        shot(apage, "square-mobile.png")
        apage.evaluate("window.scrollTo(0, 380)")
        shot(apage, "square-compose-mobile.png")
        apage.evaluate("window.scrollTo(0, 820)")
        shot(apage, "square-engage-mobile.png")
        apage.evaluate("window.scrollTo(0, 1300)")
        shot(apage, "square-feed-deep-mobile.png")

        goto(apage, f"{LOCAL}/home")
        dismiss(apage)
        try:
            apage.locator("button[aria-label='Open menu']").click(force=True, timeout=2000)
            apage.wait_for_timeout(700)
            shot(apage, "menu-mobile.png")
        except Exception as exc:  # noqa: BLE001
            print(f"  menu warn: {exc}")

        browser.close()

    (OUT / "README.md").write_text(
        f"# Live screens — {TODAY}\n\n"
        "Captured fresh today. Social creatives for this day MUST use this folder.\n"
        "Do not fall back to older `live-*` directories.\n",
        encoding="utf-8",
    )
    print(f"Done → {OUT}")


if __name__ == "__main__":
    main()
