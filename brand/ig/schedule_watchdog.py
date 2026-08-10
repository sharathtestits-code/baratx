#!/usr/bin/env python3
"""Fallback: if Railway misses an IST slot by 5 minutes, post grunge+founder caption once."""
from __future__ import annotations
import json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app import instagram_publish as ip  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
LOG = Path.home() / ".config" / "baratx" / "ig-watchdog.log"
SLOTS = ((9, 0, "morning"), (13, 30, "midday"), (20, 0, "evening"))
STATE = Path.home() / ".config" / "baratx" / "ig-watchdog-state.json"


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(IST).isoformat()} {msg}"
    print(line, flush=True)
    LOG.open("a").write(line + "\n")


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s))


def recent_media_within(minutes: int = 25) -> bool:
    token = ip._env("INSTAGRAM_ACCESS_TOKEN")
    uid = ip._env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    url = (
        f"{ip.GRAPH}/{uid}/media?fields=id,timestamp&limit=1&access_token="
        + urllib.parse.quote(token)
    )
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read().decode()).get("data") or []
    if not data:
        return False
    ts = datetime.fromisoformat(data[0]["timestamp"].replace("Z", "+00:00")).astimezone(IST)
    return datetime.now(IST) - ts <= timedelta(minutes=minutes)


def main() -> None:
    log("watchdog started (fallback only)")
    state = load_state()
    while True:
        now = datetime.now(IST)
        for h, m, pack in SLOTS:
            key = f"{now.date().isoformat()}-{pack}"
            if state.get(key):
                continue
            target = now.replace(hour=h, minute=m, second=0, microsecond=0)
            # Only act 5–20 minutes after slot
            if not (timedelta(minutes=5) <= now - target <= timedelta(minutes=20)):
                continue
            if recent_media_within(25):
                log(f"skip {pack}: recent media exists (Railway likely posted)")
                state[key] = "skipped-recent"
                save_state(state)
                continue
            try:
                result = ip.publish_carousel(pack=pack)
                log(f"fallback published {pack}: {json.dumps(result)}")
                state[key] = "published"
            except Exception as exc:  # noqa: BLE001
                log(f"fallback FAILED {pack}: {exc}")
                state[key] = f"failed:{exc}"
            save_state(state)
        time.sleep(60)


if __name__ == "__main__":
    main()
