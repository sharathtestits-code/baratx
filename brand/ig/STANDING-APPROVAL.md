# Standing approval — Instagram schedule

**Approved by founder:** 2026-08-10  
**Account:** @getbarathx  
**Voice / strategy parent:** `brand/SOCIAL-MARKETING-LEAD.md`

## What is approved (no per-post ask)
- Post on IST peak slots: **09:00 / 13:30 / 20:00**
- **Same creative template:** street-grunge Pehchaan collage (`brand/ig/carousel/grunge-what/`)
- Captions may be AI-assisted; must sound like **founder / real human** (lead brief voice rules)
- Privacy line sparingly (prefer midday / one slide only)
- Stay honest we’re early — no fake scale

## What still needs a new ask
- New visual systems (not grunge)
- Putting Founding ₹150 / First 100 back on creative (omitted from current grunge pack)
- New copy that needs a **real moment** (debate clip, real number, screen recording)
- Paid boost / ads
- Deleting or replacing live posts
- Off-schedule extra posts beyond the 3 daily peaks
- X posts (draft OK; founder posts unless separately approved)

## Ops notes
- Publisher: `backend/app/instagram_publish.py` (Railway in-process scheduler)
- Fallback if Railway misses a slot by ~5 min: `brand/ig/schedule_watchdog.py`
- Optional: Cursor **Automations** cron to wake an agent for drafts / watchdog — not a native IG scheduler
- Spelling: **BarathX** (not BharathX)
