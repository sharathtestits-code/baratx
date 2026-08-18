#!/usr/bin/env python3
"""
Build a full BarathX daily social pack (DRAFT ONLY — never posts to WhatsApp/X/LinkedIn).

Creates for IST date:
  - PACK.md (WA + X + LinkedIn paste copy)
  - stills (feature + trending template)
  - ~20s 9:16 reel
  - email notify “Your BarathX post is ready” (or NOTIFY-PREVIEW if mail unset)

Usage:
  python3 brand/social/daily/build_daily_pack.py
  python3 brand/social/daily/build_daily_pack.py --date 2026-08-18 --slot all --approve --notify
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
DAILY = Path(__file__).resolve().parent
sys.path.insert(0, str(DAILY))

from features import Feature, feature_by_key, feature_for_date  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
PROD_TRENDING = "https://baratx-production.up.railway.app/trending?q=trending%20in%20india&limit=6"


def _today_ist() -> date:
    return datetime.now(IST).date()


def fetch_trend_hook() -> str:
    """Best-effort India headline/topic from live API."""
    try:
        req = urllib.request.Request(
            PROD_TRENDING,
            headers={"User-Agent": "Mozilla/5.0", "X-BarathX-Client": "web"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        headlines = data.get("headlines") or []
        topics = data.get("topics") or []
        if headlines:
            title = (headlines[0].get("title") or "").strip()
            if title:
                return title
        if topics:
            name = (topics[0].get("name") or "").strip()
            if name:
                return name
    except Exception as exc:  # noqa: BLE001
        print(f"trend fetch failed: {exc}")
    return "India is talking — leave a take on the record"


def write_pack_md(
    *,
    out_dir: Path,
    d: date,
    feature: Feature,
    trend: str,
) -> Path:
    founding_line = (
        "100 Founding spots, earned by opening a debate that gets real engagement, not by signing up."
        if feature.founding_ok
        else "Human takes only. No AI slop."
    )
    trend_short = trend if len(trend) <= 90 else trend[:87] + "…"

    pack = f"""# Daily pack — {d.isoformat()} (IST)

**Cadence:** 2 posts/day · WhatsApp + X + LinkedIn  
**Status:** READY TO PASTE (draft only — you post manually)  
**Feature of the day:** `{feature.key}` · **{feature.name}**  
**Trend hook:** {trend_short}  
**Stills template:** `{feature.template}`  
**Video:** `barathx-daily-reel-20s.mp4` (~20s · 9:16)

> Automation prepares this pack + emails you. It does **not** post to WhatsApp, X, or LinkedIn.

---

## Post 1 — Morning (≈ 09:00 IST)

**Images / video**
| Channel | File |
|---------|------|
| WhatsApp + X | `morning-shared.jpg` |
| LinkedIn | `morning-linkedin.jpg` |
| Reel (WA Status / Reels / Shorts / X) | `barathx-daily-reel-20s.mp4` |

### WhatsApp community / channel
```
{trend_short}

BarathX · {feature.name}
{feature.one_liner}

{chr(10).join('• ' + b for b in feature.bullets)}

{founding_line}

Android soft launch: https://barathx.com/get-app/
(Phone OTP — fastest way in)

→ https://barathx.com
```

### X
```
{trend_short}

BarathX · {feature.name}
{feature.one_liner}

{founding_line}

Android soft launch (APK):
https://barathx.com/get-app/
Phone OTP to join.

→ https://barathx.com

{feature.hashtags}
```

### LinkedIn
```
India hook: {trend_short}

Product focus today: {feature.name}

{feature.one_liner}

{chr(10).join('• ' + b for b in feature.bullets)}

Soft launch is open:
• Web: https://barathx.com
• Android APK (sideload): https://barathx.com/get-app/
• Fastest login: phone OTP

{founding_line}

{feature.hashtags} #BuildInPublic
```

---

## Post 2 — Evening (≈ 20:00 IST)

**Images / video**
| Channel | File |
|---------|------|
| X + LinkedIn | `evening-shared.jpg` |
| WhatsApp | `evening-whatsapp.jpg` |
| Reel | `barathx-daily-reel-20s.mp4` |

### WhatsApp community / channel
```
Tonight on BarathX — {feature.name}.

{feature.one_liner}

Trend still moving: {trend_short}

Square · Arenas · Live · Explore
{founding_line}

Get the Android soft-launch build:
https://barathx.com/get-app/
Then Continue with phone.

→ https://barathx.com
```

### X
```
Tonight · {feature.name}

{feature.one_liner}

{trend_short}

Human first. No AI slop.

Android soft launch:
https://barathx.com/get-app/
Phone OTP → you’re in.

{feature.hashtags}
```

### LinkedIn
```
Evening build note — {feature.name}

{feature.one_liner}

Why it matters with today’s India conversation:
{trend_short}

{chr(10).join('• ' + b for b in feature.bullets)}

Soft launch distribution (manual paste — no auto-post):
• X + LinkedIn + WhatsApp today
• Android APK: https://barathx.com/get-app/
• Login with phone OTP

Web: https://barathx.com

{feature.hashtags}
```

---

## After you post (manual)

- [ ] WhatsApp Channel: https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o
- [ ] WhatsApp Community: https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU
- [ ] X (paste from this pack)
- [ ] LinkedIn (paste from this pack)
- [ ] Optional: IG Reels with `barathx-daily-reel-20s.mp4`
"""
    path = out_dir / "PACK.md"
    path.write_text(pack, encoding="utf-8")
    (out_dir / "APPROVAL.md").write_text(
        f"# Approval — {d.isoformat()}\n\n"
        f"Feature: **{feature.name}** (`{feature.key}`)\n"
        f"Trend: {trend_short}\n\n"
        "- [x] morning-shared.jpg\n"
        "- [x] morning-linkedin.jpg\n"
        "- [x] evening-shared.jpg\n"
        "- [x] evening-whatsapp.jpg\n"
        "- [x] barathx-daily-reel-20s.mp4\n",
        encoding="utf-8",
    )
    return path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


def notify(date_str: str, slot: str) -> None:
    run(
        [
            sys.executable,
            str(DAILY / "notify_pack_ready.py"),
            "--date",
            date_str,
            "--slot",
            slot,
        ]
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Build daily WA/X/LI pack + email notify (no auto-post)")
    p.add_argument("--date", default="", help="IST YYYY-MM-DD (default: today IST)")
    p.add_argument("--feature", default="", help="Override feature key")
    p.add_argument("--trend", default="", help="Override trend hook")
    p.add_argument("--approve", action="store_true", help="Final stills (no mockup ribbon)")
    p.add_argument("--notify", action="store_true", help="Email / write notify preview")
    p.add_argument("--slot", choices=["morning", "evening", "all"], default="all")
    p.add_argument("--skip-video", action="store_true")
    p.add_argument("--skip-stills", action="store_true")
    args = p.parse_args()

    d = date.fromisoformat(args.date) if args.date else _today_ist()
    date_str = d.isoformat()
    feature = feature_by_key(args.feature) or feature_for_date(d)
    trend = args.trend.strip() or fetch_trend_hook()
    out_dir = DAILY / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building pack {date_str} feature={feature.key} trend={trend[:80]!r}")
    write_pack_md(out_dir=out_dir, d=d, feature=feature, trend=trend)

    if not args.skip_stills:
        cmd = [
            sys.executable,
            str(DAILY / "render_daily_crosspost.py"),
            "--date",
            date_str,
            "--feature",
            feature.key,
            "--trend",
            trend,
        ]
        if args.approve:
            cmd.append("--approve")
        run(cmd)

    if not args.skip_video:
        run(
            [
                sys.executable,
                str(DAILY / "render_daily_reel.py"),
                "--date",
                date_str,
                "--feature",
                feature.key,
                "--trend",
                trend,
            ]
        )

    if args.notify:
        notify(date_str, args.slot)

    print(f"Done → {out_dir.relative_to(ROOT)}")
    print("Reminder: pack is for YOU to paste. No WhatsApp/X/LinkedIn auto-post.")


if __name__ == "__main__":
    main()
