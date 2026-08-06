# Daily digest — @sharath trending posts

## New-user auto-reply (already live)
On a user’s **first Home post**, `@baratx` auto-replies:

> Welcome to BaratX, @{username}. Glad you’re here — what’s your city, and what should this square never become?

Not on signup alone — only after they post once.

## Daily trending job
- **Who posts:** `@sharath`
- **When:** ~**09:05 IST** every day (in-process scheduler on the API)
- **How many:** **1–2** posts max (quality filter — not one per topic)
- **Source:** Google News RSS across arenas + rotating subtopics
- **Media:** one BaratX-branded PNG per post (saffron theme)
- **Marker:** `#BaratXDaily` (dedupes same-day / similar headlines for 5 days)

## Manual run
Admin → **Run daily digest now**  
or `POST /admin/daily-digest?force=true` with `X-Admin-Secret`.

## Disable
Set `DISABLE_DAILY_DIGEST=1` on Railway if needed.
