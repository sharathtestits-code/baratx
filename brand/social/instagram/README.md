# BarathX Instagram — 2–3×/day carousel

## Live
- Account: **[@getbaratx](https://www.instagram.com/getbaratx/)**
- First API carousel: https://www.instagram.com/p/DbvegDEGn5V/

## Cadence (IST peak times)
| Slot | Time | Pack |
|------|------|------|
| Morning | **09:00** | `morning` |
| Midday | **13:30** | `evening` |
| Evening | **20:00** | `evening` |

Max **3 posts/day**. Disable with `DISABLE_INSTAGRAM_SCHEDULE=1`.

## Music / trending audio — important
Instagram’s Graph API **cannot** attach trending Reels music to feed carousels (or API Reels).  
Music must be baked into a video file, or added manually in the IG app.

**What we do now:** auto-post **photo carousels** with viral captions/hashtags.  
**For trending music:** post a Reel manually in IG and add audio there, or later we build a Reel video with licensed/own audio embedded.

## Env (Railway API service — required for auto schedule)
```bash
INSTAGRAM_ACCESS_TOKEN=...          # Page access token
INSTAGRAM_BUSINESS_ACCOUNT_ID=...   # e.g. 17841441378296886
# optional
DISABLE_INSTAGRAM_SCHEDULE=0
```

Local agent also reads `~/.config/baratx/instagram.env`.

## Manual / one-shot publish
```bash
python3 brand/social/instagram/post_carousel.py --pack morning
python3 brand/social/instagram/post_carousel.py --pack evening
```

Slides are fetched by Meta from GitHub raw on **main**:
`https://raw.githubusercontent.com/sharathtestits-code/baratx/main/brand/ig/carousel/<pack>/slide-0N.jpg`

## Assets (product UI carousels)
Canonical packs live under `brand/ig/carousel/{signup-excite,how-it-works,launch-pain}/`.

**Hard rule:** slides must use **current** plaza UI from
`brand/social/whatsapp/screens/live-2026-08-16/` — never retired
`brand/carousel/screens/*` demo feeds (old sidebar Home / `@carouseldemo`).

Regenerate (approved dark + saffron + real screens):

```bash
python3 brand/ig/render_product_carousels.py
```

Scheduler pulls from **main** GitHub raw URLs — merge regenerated slides before expecting auto-posts to change.

Manual publish (needs `ADMIN_SECRET` + IG env on API):

```bash
curl -X POST 'https://baratx-production.up.railway.app/admin/instagram-carousel?pack=morning' \
  -H "X-Admin-Secret: $ADMIN_SECRET"
```
