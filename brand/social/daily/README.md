# Daily social packs — WhatsApp + X + LinkedIn

Each day folder: `brand/social/daily/YYYY-MM-DD/`

## Cadence (you post manually)

| IST slot | Channels | Job |
|----------|----------|-----|
| **09:00** | WhatsApp + X + LinkedIn | Trend hook → feature of the day → signup |
| **20:00** | WhatsApp + X + LinkedIn | Same feature + evening template → signup |

**2 posts/day × 3 channels.** You paste yourself. Automation only prepares the pack + emails **“Your BarathX post is ready.”** It does **not** post to WhatsApp.

## What rotates each day

- **Feature of the day** — Square · Arenas · Live · Explore · Human-first · Founding 100 · Soft launch (`features.py`)
- **Still template** — different layout per feature (+ LinkedIn / WA evening variants)
- **Trend hook** — live India headline/topic from prod `/trending`
- **~20s reel** — `barathx-daily-reel-20s.mp4` (9:16)

## One-command build

```bash
# Draft stills (MOCKUP ribbon) + video + email/preview
python3 brand/social/daily/build_daily_pack.py --notify

# Finals after you approve
python3 brand/social/daily/build_daily_pack.py --date YYYY-MM-DD --approve --notify
```

Overrides: `--feature square|arenas|live|explore|human_first|founding|soft_launch` · `--trend "…"` · `--slot morning|evening|all` · `--skip-video` · `--skip-stills`

## Folder contents

- `PACK.md` — paste-ready copy for WA / X / LinkedIn (morning + evening)
- `APPROVAL.md` — checklist
- `morning-*.jpg` / `evening-*.jpg` — creatives (feature + trend template)
- `barathx-daily-reel-20s.mp4` — ~20s 9:16 reel
- `NOTIFY-PREVIEW-*.md` — local copy of the ready email if mail isn’t configured

## Email notification

```bash
python3 brand/social/daily/notify_pack_ready.py --date YYYY-MM-DD --slot morning
python3 brand/social/daily/notify_pack_ready.py --date YYYY-MM-DD --slot evening
```

Env (Railway / GitHub Actions secrets):

- `RESEND_API_KEY` (or `SMTP_*`)
- optional `SOCIAL_PACK_EMAIL` (defaults to `sharathtestits@gmail.com`)
- optional Railway: `POST /admin/social-pack-notify` with `X-Admin-Secret`

## Automation

- **GitHub Action:** `.github/workflows/daily-social-pack.yml` — cron **09:00** + **20:00 IST**, builds pack + emails + commits folder
- **Cursor Automation:** optional companion — see [AUTOMATION.md](./AUTOMATION.md)
