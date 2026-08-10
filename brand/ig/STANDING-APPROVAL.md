# Standing approval — Instagram schedule

**Approved by founder:** 2026-08-10  
**Account:** @getbarathx

## What is approved (no per-post ask)
- Post on IST peak slots: **09:00 / 13:30 / 20:00**
- **Same creative template:** street-grunge Pehchaan collage (`brand/ig/carousel/grunge-what/`)
- Captions may be AI-assisted; must sound like **founder / real human** (not corporate)
- Privacy line sparingly (prefer midday / one slide only)

## What still needs a new ask
- New visual systems (not grunge)
- Paid boost / ads
- Deleting or replacing live posts
- Off-schedule extra posts beyond the 3 daily peaks

## Ops notes
- Publisher: `backend/app/instagram_publish.py` (Railway in-process scheduler)
- Fallback if Railway misses a slot by ~5 min: `brand/ig/schedule_watchdog.py`
- Spelling: **BarathX** (not BharathX)
