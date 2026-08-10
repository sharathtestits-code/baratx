#!/usr/bin/env python3
"""Post remaining IST peak slots today with grunge carousel + founder captions.

Usage (background):
  python3 brand/ig/schedule_today_posts.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app import instagram_publish  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
LOG = Path.home() / ".config" / "baratx" / "ig-schedule-today.log"
SLOTS = (
    (13, 30, "midday"),
    (20, 0, "evening"),
)


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(IST).isoformat()} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def wait_until(hour: int, minute: int) -> None:
    while True:
        now = datetime.now(IST)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= target:
            return
        wait = (target - now).total_seconds()
        log(f"sleeping {wait:.0f}s until {hour:02d}:{minute:02d} IST")
        time.sleep(min(wait, 60))


def main() -> None:
    log("schedule_today_posts started")
    for hour, minute, pack in SLOTS:
        now = datetime.now(IST)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now > target:
            log(f"skip {pack} — already past {hour:02d}:{minute:02d}")
            continue
        wait_until(hour, minute)
        try:
            result = instagram_publish.publish_carousel(pack=pack)
            log(f"published {pack}: {json.dumps(result)}")
        except Exception as exc:  # noqa: BLE001
            log(f"FAILED {pack}: {exc}")
        time.sleep(30)
    log("schedule_today_posts done")


if __name__ == "__main__":
    main()
