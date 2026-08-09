# Full QA execution — 2026-08-09 (late)

**Environment:** `https://qa.barathx.com` · API `https://baratx-qa.up.railway.app`  
**Source:** Product QA pass (reported to engineering)

## Results

| Layer | Result |
|-------|--------|
| API catalog | **86 PASS · 0 FAIL · 59 SKIP** |
| UI walkthrough | Login, Square, post, arenas, communities, rewards, settings, profile, logout, admin **PASS** |
| DEF-001…007 | **CLOSED** |

SKIP = Google/Phone OTP, image upload, coach marks, Live Talk deep, IG/ops, Capacitor.

## New defect

**DEF-008 (P0)** — Hard navigation / refresh to `/notifications`, `/bookmarks`, `/messages`, `/lists`, `/arenas`, `/spaces` hits API JSON instead of SPA. Fixed in engineering via document-navigation SPA shell (`app/spa_serve.py` + middleware).
