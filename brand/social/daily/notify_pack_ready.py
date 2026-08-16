#!/usr/bin/env python3
"""
Send “Your BarathX post is ready” email for a daily pack slot.

Usage:
  python3 brand/social/daily/notify_pack_ready.py --date 2026-08-17 --slot morning
  python3 brand/social/daily/notify_pack_ready.py --date 2026-08-17 --slot evening
  python3 brand/social/daily/notify_pack_ready.py --date 2026-08-17 --slot all

Requires RESEND_API_KEY or SMTP_* on the host (Railway / local).
Falls back to writing brand/social/daily/YYYY-MM-DD/NOTIFY-PREVIEW.md if email is not configured.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from app import email as email_mod  # noqa: E402

DAILY = Path(__file__).resolve().parent


def _section(pack: str, heading: str) -> str:
    """Pull fenced code body under a ### heading."""
    pattern = rf"###\s+{re.escape(heading)}\s*\n```\n(.*?)```"
    m = re.search(pattern, pack, re.S | re.I)
    return (m.group(1).strip() if m else "")


def _images_for_slot(date_dir: Path, slot: str) -> str:
    if slot == "morning":
        names = ["morning-shared.jpg", "morning-linkedin.jpg"]
    else:
        names = ["evening-shared.jpg", "evening-whatsapp.jpg"]
    existing = [n for n in names if (date_dir / n).exists()]
    return ", ".join(existing) if existing else "(images pending)"


def notify_slot(date: str, slot: str) -> bool:
    date_dir = DAILY / date
    pack_path = date_dir / "PACK.md"
    if not pack_path.exists():
        raise SystemExit(f"Missing pack: {pack_path}")
    text = pack_path.read_text(encoding="utf-8")

    # Prefer the slot block: "## Post 1 — Morning" / "## Post 2 — Evening"
    if slot == "morning":
        block_m = re.search(r"## Post 1 — Morning.*?(?=## Post 2|\Z)", text, re.S)
        block = block_m.group(0) if block_m else text
        channels = "WhatsApp + X + LinkedIn"
    else:
        block_m = re.search(r"## Post 2 — Evening.*?(?=## After|\Z)", text, re.S)
        block = block_m.group(0) if block_m else text
        channels = "WhatsApp + X + LinkedIn"

    wa = _section(block, "WhatsApp community / channel")
    x = _section(block, "X")
    li = _section(block, "LinkedIn")
    images = _images_for_slot(date_dir, slot)
    rel = f"brand/social/daily/{date}/PACK.md"

    sent = email_mod.send_daily_pack_ready_email(
        date=date,
        slot=slot,
        channels=channels,
        pack_path=rel,
        wa_body=wa,
        x_body=x,
        li_body=li,
        image_hint=images,
    )

    preview = date_dir / f"NOTIFY-PREVIEW-{slot}.md"
    preview.write_text(
        f"# Notify preview — {date} {slot}\n\n"
        f"Email sent: **{sent}**\n"
        f"To: `{email_mod.SOCIAL_PACK_EMAIL}`\n"
        f"Subject: Your BarathX post is ready — {date} {slot.title()}\n\n"
        f"Images: {images}\n\n"
        f"## WhatsApp\n```\n{wa}\n```\n\n"
        f"## X\n```\n{x}\n```\n\n"
        f"## LinkedIn\n```\n{li}\n```\n",
        encoding="utf-8",
    )
    print(f"sent={sent} preview={preview}")
    return sent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--slot", choices=["morning", "evening", "all"], default="all")
    args = p.parse_args()
    slots = ["morning", "evening"] if args.slot == "all" else [args.slot]
    for s in slots:
        notify_slot(args.date, s)


if __name__ == "__main__":
    main()
