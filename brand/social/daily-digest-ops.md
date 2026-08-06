# Daily digest + welcome replies

## New-user auto-replies (first Home post only)
Two replies — official engagement, **never counts toward Founding rewards**:

1. **@baratx** — Welcome to BaratX… what’s your city…
2. **@sharath** — Hey @{user} — Sharath here. Drop one real take…

## Daily auto-posts (~09:05 IST)
Target **3–5 posts/day** when quality exists (never pad with junk):

- Voices: **@sharath** (founder) + **@baratx** (brand), round-robin
- Arenas: Sports · Politics · Entertainment · News · Spirituality  
  (politics weighted slightly for civic pulse — **not** politics-only)
- Cap: **max 2 posts per arena** so one floor doesn’t own Home
- Score gate: India / civic / debate-shaped headlines; soft-penalize horoscope, listicles, clickbait
- Each post: BaratX-branded PNG + `#BaratXDaily`

If fewer than 3 headlines clear the bar, we post only what passes.

## Rewards exclusion
Likes/replies from `@baratx`, `@sharath`, other seeded officials, and any `blue` / `is_official` account are **ignored** for Founding payable + race like counts.

## Manual
Admin → **Run daily digest now** (`POST /admin/daily-digest?force=true`).

## Infra note (when to expand)
At 3–5 posts/day + PNG cards, **no new server/DB needed**. Scale later when:
- media volume / user uploads grow → object storage (R2/S3) instead of local disk
- concurrent users climb → managed Postgres + connection pooling
- digest reliability matters on multi-instance deploys → move scheduler off the API process (cron / worker)
