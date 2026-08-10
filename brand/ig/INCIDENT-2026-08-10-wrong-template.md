# Incident — 2026-08-10 midday post used wrong template + BaratX spelling

## What went out
- Permalink: https://www.instagram.com/p/Db2iQ7Mm75K/
- Media ID: 18063727133507285
- Time: 2026-08-10 ~13:30 IST (Railway peak slot)
- Creative: OLD plain 10-slide pack from `main` `brand/carousel/export` (cream/peach)
- Brand on slides: **BaratX** (missing h) e.g. slide 06/10 — wrong
- Caption text used BarathX — still wrong overall because images dominate

## Root cause
`origin/main` `instagram_publish.py` hardcodes:
- `DEFAULT_IMAGE_BASE` → `main/brand/carousel/export`
- `slide-01.png` … `slide-10.png`
- Does **not** honor `INSTAGRAM_IMAGE_BASE` when scheduler calls `publish_carousel(pack=...)`
Railway variable changes redeployed **main**, wiping earlier `railway up` of the grunge publisher.

## Mitigation done
- `DISABLE_INSTAGRAM_SCHEDULE=1` on prod
- Redeployed grunge publisher (`cursor/ig-carousel-what-is-2af5`) via `railway up`
- Set `INSTAGRAM_IMAGE_BASE` / `SLIDE_COUNT=6` / `SLIDE_EXT=jpg`
- Graph DELETE failed (permission #10) — founder must delete manually in IG app

## Do not re-enable schedule until
Grunge + BarathX publisher is on **main** (or Railway always deploys the fixed branch).
