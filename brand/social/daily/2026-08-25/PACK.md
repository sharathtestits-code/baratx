# Daily pack — 2026-08-25 (IST) · Part 1 · **latest screens only**

**Cadence:** 1 reel/day · WhatsApp + Instagram + X  
**Status:** READY TO PASTE / READY TO FILM  
**Length:** **25.0s** · 9:16  
**Screens source:** `brand/social/whatsapp/screens/live-2026-08-25/` (**today — do not use older live-* folders**)

### Direct download (click)
**https://raw.githubusercontent.com/sharathtestits-code/baratx/cursor/daily-part1-25s-2af5/brand/social/daily/2026-08-25/barathx-part1-25s.mp4**

GitHub file page (Download button):  
https://github.com/sharathtestits-code/baratx/blob/cursor/daily-part1-25s-2af5/brand/social/daily/2026-08-25/barathx-part1-25s.mp4

| Asset | Path |
|-------|------|
| **MP4 (repo)** | `brand/social/daily/2026-08-25/barathx-part1-25s.mp4` |
| Alias | `brand/social/daily/2026-08-25/barathx-daily-reel-25s.mp4` |
| Series copy | `brand/social/instagram/demo-series/PART-01-square-v5/barathx-demo-PART1-25s.mp4` |
| Poster | `barathx-part1-25s-poster.jpg` |
| **Your phone recording script** | `RECORDING-SCRIPT.md` |
| Still screens (today) | `../../whatsapp/screens/live-2026-08-25/` |

> Manual post. Attach trending audio in IG.  
> **Never** reuse PART-01 v4 / old `live-2026-08-19` / `live-2026-08-21` for this cut.

---

## Overlay beats (25s) — latest UI

| t | Beat | Screen |
|---|------|--------|
| 0–2s | Title — BarathX · Features · Part 1 · Square | title card |
| 2–6s | Landing — Agree / Disagree / It depends | `landing-mobile.png` |
| 6–11s | Square — today’s question | `square-mobile.png` |
| 11–16s | Drop a take | `square-compose-mobile.png` |
| 16–20.5s | Live now + takes | `square-engage-mobile.png` |
| 20.5–22.5s | Home hub tease | `home-mobile.png` |
| 22.5–25s | Part 2 → Arenas tomorrow | end card |

---

## Instagram caption

```
Features on BarathX · Part 1 — Square
Today’s question · Drop a take · Live on the Square.

Save this. Part 2 drops tomorrow — Arenas & debates.
Human takes only. No AI slop.

→ https://barathx.com
IG → https://www.instagram.com/getbaratx/
X → https://x.com/getbaratx
WhatsApp channel → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o
Community → https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU

#BarathX #IndiaApp #PublicSquare #BuildInPublic
```

---

## X caption

```
Features on BarathX · Part 1 — Square (25s)

Today’s question. Drop a take. Live on the Square.
Human takes only. No AI slop.

Part 2 tomorrow — Arenas & debates.

→ https://barathx.com
IG https://www.instagram.com/getbaratx/
WA https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o

#BarathX #India #PublicSquare
```

---

## WhatsApp

```
BarathX · Part 1 of 7 (daily)
Square walkthrough — latest UI (25s)

Today’s question · Drop a take · Live on the Square
Human takes only. No AI slop.

Part 2 tomorrow → Arenas & debates

→ https://barathx.com
IG → https://www.instagram.com/getbaratx/
X → https://x.com/getbaratx
Channel → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o
Community → https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU
```

---

## Rebuild (always re-capture first)

```bash
# 1) Fresh screens (local API + Vite must be running for in-app pages)
/tmp/bx-pw/bin/python brand/social/capture_live_screens_today.py

# 2) 25s reel from TODAY folder only
python3 brand/social/instagram/demo-series/render_part01_25s.py
```

Tomorrow: Part 2 Arenas — same 25s rule, new `live-YYYY-MM-DD` capture.
