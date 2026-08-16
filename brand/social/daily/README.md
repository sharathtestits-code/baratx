# Daily social packs — WhatsApp + X + LinkedIn

Each day folder: `brand/social/daily/YYYY-MM-DD/`

## Cadence (you post manually)

| IST slot | Channels | Job |
|----------|----------|-----|
| **09:00** | WhatsApp + X + LinkedIn | Trend hook → pain → signup |
| **20:00** | WhatsApp + X + LinkedIn | Highlight / human-first → signup |

**2 posts/day × 3 channels.** You paste yourself. Automation only prepares the pack + emails **“Your BarathX post is ready.”**

## Folder contents

- `PACK.md` — paste-ready copy for WA / X / LinkedIn (morning + evening)
- `APPROVAL.md` — mockup checklist (while awaiting your OK)
- `morning-*.jpg` / `evening-*.jpg` — creatives
- `NOTIFY-PREVIEW-*.md` — local copy of the ready email if mail isn’t configured

## Render mockups

```bash
# With APPROVE ribbon (for your review)
python3 brand/social/daily/render_daily_crosspost.py --date YYYY-MM-DD

# Final (no ribbon) after you say approve
python3 brand/social/daily/render_daily_crosspost.py --date YYYY-MM-DD --approve
```

## Email notification

```bash
python3 brand/social/daily/notify_pack_ready.py --date YYYY-MM-DD --slot morning
python3 brand/social/daily/notify_pack_ready.py --date YYYY-MM-DD --slot evening
```

Env (Railway / local): `RESEND_API_KEY` or SMTP_*, optional `SOCIAL_PACK_EMAIL` (defaults to `hello@barathx.com`).

## Automation

See [AUTOMATION.md](./AUTOMATION.md) — Cursor Automation 2×/day (09:00 + 20:00 IST).
